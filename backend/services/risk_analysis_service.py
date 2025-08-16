"""
Risk Analysis Service
Automatically analyzes all discovered pools and maintains risk scores
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import aiohttp
from decimal import Decimal

from tools.degen_scorer import DegenScorerTool
from tools.enhanced_pool_validator import enhanced_validator
from utils.cache import api_cache
from database.connection import get_db_connection

logger = logging.getLogger(__name__)

class RiskAnalysisService:
    def __init__(self):
        self.scorer = DegenScorerTool()
        self.validator = enhanced_validator
        self.analysis_interval = 300  # 5 minutes
        self.batch_size = 10
        self._running = False
        
    async def start(self):
        """Start the risk analysis service"""
        self._running = True
        logger.info("Risk Analysis Service started")
        
        # Run initial analysis for all pools
        await self.analyze_all_pools()
        
        # Start continuous monitoring
        while self._running:
            try:
                await asyncio.sleep(self.analysis_interval)
                await self.analyze_recent_pools()
            except Exception as e:
                logger.error(f"Error in risk analysis loop: {e}")
                await asyncio.sleep(30)  # Wait before retry
    
    async def stop(self):
        """Stop the service"""
        self._running = False
        logger.info("Risk Analysis Service stopped")
    
    async def analyze_all_pools(self):
        """Analyze all pools that haven't been analyzed recently"""
        logger.info("Starting analysis of all pools...")
        
        conn = await get_db_connection()
        try:
            # Get pools that need analysis (not analyzed in last hour)
            query = """
                SELECT DISTINCT p.pool_address, p.protocol, p.token_a_symbol, 
                       p.token_b_symbol, p.token_a_mint, p.token_b_mint
                FROM pools_enhanced p
                LEFT JOIN pool_risk_analysis r ON p.pool_address = r.pool_address
                WHERE r.analyzed_at IS NULL 
                   OR r.analyzed_at < NOW() - INTERVAL '1 hour'
                ORDER BY p.discovered_at DESC
                LIMIT 100
            """
            
            pools = await conn.fetch(query)
            logger.info(f"Found {len(pools)} pools to analyze")
            
            # Process in batches
            for i in range(0, len(pools), self.batch_size):
                batch = pools[i:i + self.batch_size]
                await self._analyze_batch(batch)
                await asyncio.sleep(1)  # Rate limiting
                
        finally:
            await conn.close()
    
    async def analyze_recent_pools(self):
        """Analyze recently discovered pools"""
        logger.info("Checking for recent pools to analyze...")
        
        conn = await get_db_connection()
        try:
            # Get pools discovered in last 10 minutes
            query = """
                SELECT DISTINCT p.pool_address, p.protocol, p.token_a_symbol, 
                       p.token_b_symbol, p.token_a_mint, p.token_b_mint
                FROM pools_enhanced p
                WHERE p.discovered_at > NOW() - INTERVAL '10 minutes'
                  AND NOT EXISTS (
                      SELECT 1 FROM pool_risk_analysis r 
                      WHERE r.pool_address = p.pool_address 
                        AND r.analyzed_at > NOW() - INTERVAL '10 minutes'
                  )
            """
            
            pools = await conn.fetch(query)
            if pools:
                logger.info(f"Found {len(pools)} recent pools to analyze")
                await self._analyze_batch(pools)
                
        finally:
            await conn.close()
    
    async def _analyze_batch(self, pools: List[Dict]):
        """Analyze a batch of pools"""
        tasks = []
        for pool in pools:
            task = self._analyze_single_pool(pool)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log any errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to analyze pool {pools[i]['pool_address']}: {result}")
    
    async def _analyze_single_pool(self, pool_record: Dict) -> Optional[Dict]:
        """Analyze a single pool and store results"""
        pool_address = pool_record['pool_address']
        
        try:
            # Fetch current pool data
            pool_data = await self._fetch_pool_data(pool_record)
            if not pool_data:
                logger.warning(f"No data found for pool {pool_address}")
                return None
            
            # Run risk analysis
            risk_analysis = self._calculate_risk_scores(pool_data)
            
            # Store in database
            await self._store_risk_analysis(pool_address, risk_analysis)
            
            # Update cache
            cache_key = f"risk_analysis:{pool_address}"
            api_cache.set(cache_key, risk_analysis, expire=600)  # 10 min cache
            
            logger.info(f"Analyzed pool {pool_address}: Risk={risk_analysis['overall_risk_score']}, Rating={risk_analysis['risk_rating']}")
            return risk_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing pool {pool_address}: {e}")
            return None
    
    async def _fetch_pool_data(self, pool_record: Dict) -> Optional[Dict]:
        """Fetch current pool data from various sources"""
        pool_address = pool_record['pool_address']
        
        # Check cache first
        cached = api_cache.get(f"pool_data:{pool_address}")
        if cached and cached.get('timestamp', 0) > datetime.now().timestamp() - 300:
            return cached
        
        # Fetch fresh data
        pool_data = {
            'pool_address': pool_address,
            'protocol': pool_record['protocol'],
            'token_a': pool_record['token_a_symbol'],
            'token_b': pool_record['token_b_symbol'],
            'token_symbols': f"{pool_record['token_a_symbol']}-{pool_record['token_b_symbol']}",
        }
        
        # Try to get data from Raydium API
        if pool_record['protocol'] == 'raydium':
            raydium_data = await self._fetch_raydium_data(pool_address)
            if raydium_data:
                pool_data.update(raydium_data)
        
        # Get additional metrics
        pool_data['timestamp'] = datetime.now().timestamp()
        
        # Cache the data
        api_cache.set(f"pool_data:{pool_address}", pool_data, expire=300)
        
        return pool_data
    
    async def _fetch_raydium_data(self, pool_address: str) -> Optional[Dict]:
        """Fetch data from Raydium API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.raydium.io/v2/main/pairs",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        pools = await response.json()
                        for pool in pools:
                            if pool.get('ammId') == pool_address:
                                liquidity = float(pool.get('liquidity', 0))
                                volume_24h = float(pool.get('volume24h', 0))
                                
                                # Calculate APY
                                apy = 0
                                if liquidity > 0:
                                    daily_fees = volume_24h * 0.0025
                                    daily_yield = (daily_fees / liquidity) * 100
                                    apy = daily_yield * 365
                                
                                return {
                                    'apy': round(apy, 2),
                                    'tvl': round(liquidity, 2),
                                    'volume_24h': round(volume_24h, 2),
                                    'volume_7d': float(pool.get('volume7d', 0)),
                                    'price_change_24h': float(pool.get('price24hChange', 0)),
                                }
        except Exception as e:
            logger.error(f"Error fetching Raydium data: {e}")
        
        return None
    
    def _calculate_risk_scores(self, pool_data: Dict) -> Dict:
        """Calculate comprehensive risk scores"""
        # Basic validation
        validated = self.validator.validate_pool(pool_data)
        if not validated:
            # Pool failed validation - highest risk
            return {
                'overall_risk_score': 100,
                'risk_rating': 'AVOID',
                'degen_score': 100,
                'rug_risk_score': 100,
                'sustainability_score': 0,
                'recommendation': 'Pool failed basic validation checks. Avoid.'
            }
        
        # Get metrics
        apy = float(pool_data.get('apy', 0))
        tvl = float(pool_data.get('tvl', 0))
        volume_24h = float(pool_data.get('volume_24h', 0))
        volume_7d = float(pool_data.get('volume_7d', 0))
        
        # Calculate individual scores
        risk_scores = {
            'apy': apy,
            'tvl': tvl,
            'volume_24h': volume_24h,
            'volume_7d': volume_7d,
        }
        
        # Degen score (0-100, higher = more degen)
        degen_score = 0
        if apy > 5000:
            degen_score += 40
        elif apy > 2000:
            degen_score += 30
        elif apy > 1000:
            degen_score += 20
        elif apy > 500:
            degen_score += 10
        
        if tvl < 10000:
            degen_score += 30
        elif tvl < 50000:
            degen_score += 20
        elif tvl < 100000:
            degen_score += 10
        
        # Rug risk score
        rug_risk = 0
        if tvl < 5000:
            rug_risk += 40
        if volume_24h < tvl * 0.01:  # Less than 1% daily volume
            rug_risk += 30
        if 'SAFE' in pool_data.get('token_symbols', '').upper() or \
           'MOON' in pool_data.get('token_symbols', '').upper():
            rug_risk += 20
        
        # Sustainability score (0-10, higher = better)
        sustainability = 10
        if apy > 2000:
            sustainability -= 4
        elif apy > 1000:
            sustainability -= 2
        
        if tvl < 50000:
            sustainability -= 2
        
        volume_ratio = volume_24h / tvl if tvl > 0 else 0
        if volume_ratio < 0.1:
            sustainability -= 2
        elif volume_ratio > 5:
            sustainability -= 3  # Possible wash trading
        
        sustainability = max(0, sustainability)
        
        # Impermanent loss risk
        il_risk = min(80, apy / 50) if apy > 0 else 20  # Higher APY usually = higher volatility
        
        # Overall risk score
        overall_risk = (
            degen_score * 0.3 +
            rug_risk * 0.4 +
            (100 - sustainability * 10) * 0.2 +
            il_risk * 0.1
        )
        
        # Determine rating
        if overall_risk >= 80:
            risk_rating = 'EXTREME'
            recommendation = 'Extremely high risk. Only for experienced degens.'
        elif overall_risk >= 60:
            risk_rating = 'HIGH'
            recommendation = 'High risk pool. Proceed with extreme caution.'
        elif overall_risk >= 40:
            risk_rating = 'MODERATE'
            recommendation = 'Moderate risk. Monitor closely and consider position size.'
        elif overall_risk >= 20:
            risk_rating = 'LOW'
            recommendation = 'Relatively low risk. Still requires monitoring.'
        else:
            risk_rating = 'SAFE'
            recommendation = 'Low risk pool with stable metrics.'
        
        return {
            'overall_risk_score': int(overall_risk),
            'degen_score': int(degen_score),
            'rug_risk_score': int(rug_risk),
            'sustainability_score': round(sustainability, 1),
            'liquidity_score': min(10, tvl / 100000 * 10) if tvl > 0 else 0,
            'volume_score': min(10, volume_ratio * 10) if volume_ratio > 0 else 0,
            'impermanent_loss_risk': int(il_risk),
            'volatility_24h': min(100, abs(pool_data.get('price_change_24h', 0)) * 2),
            'risk_rating': risk_rating,
            'recommendation': recommendation,
            'volume_to_tvl_ratio': round(volume_ratio, 4),
            **risk_scores
        }
    
    async def _store_risk_analysis(self, pool_address: str, analysis: Dict):
        """Store risk analysis in database"""
        conn = await get_db_connection()
        try:
            query = """
                INSERT INTO pool_risk_analysis (
                    pool_address, analyzed_at, overall_risk_score, degen_score,
                    rug_risk_score, sustainability_score, liquidity_score,
                    volume_score, impermanent_loss_risk, volatility_24h,
                    risk_rating, recommendation, apy, tvl, volume_24h,
                    volume_7d, volume_to_tvl_ratio
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                ON CONFLICT (pool_address) 
                DO UPDATE SET 
                    analyzed_at = $2,
                    overall_risk_score = $3,
                    degen_score = $4,
                    rug_risk_score = $5,
                    sustainability_score = $6,
                    liquidity_score = $7,
                    volume_score = $8,
                    impermanent_loss_risk = $9,
                    volatility_24h = $10,
                    risk_rating = $11,
                    recommendation = $12,
                    apy = $13,
                    tvl = $14,
                    volume_24h = $15,
                    volume_7d = $16,
                    volume_to_tvl_ratio = $17
            """
            
            await conn.execute(
                query,
                pool_address,
                datetime.now(),
                analysis['overall_risk_score'],
                analysis['degen_score'],
                analysis['rug_risk_score'],
                analysis['sustainability_score'],
                analysis.get('liquidity_score', 0),
                analysis.get('volume_score', 0),
                analysis['impermanent_loss_risk'],
                analysis.get('volatility_24h', 0),
                analysis['risk_rating'],
                analysis['recommendation'],
                analysis.get('apy', 0),
                analysis.get('tvl', 0),
                analysis.get('volume_24h', 0),
                analysis.get('volume_7d', 0),
                analysis.get('volume_to_tvl_ratio', 0)
            )
            
        finally:
            await conn.close()

# Global instance
risk_analysis_service = RiskAnalysisService()