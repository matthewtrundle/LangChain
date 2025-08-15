import os
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import aiohttp
import json
from cachetools import TTLCache

class PriceOracle:
    """Real-time price feeds using Helius API"""
    
    def __init__(self):
        self.helius_api_key = os.getenv("HELIUS_API_KEY")
        if not self.helius_api_key:
            raise ValueError("HELIUS_API_KEY environment variable not set")
        
        self.base_url = f"https://api.helius.xyz/v0"
        self.headers = {"Content-Type": "application/json"}
        
        # Price cache with 10-second TTL
        self.price_cache = TTLCache(maxsize=1000, ttl=10)
        
        # Common token addresses
        self.TOKENS = {
            "SOL": "So11111111111111111111111111111111111111112",
            "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
            "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            "WIF": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
            "JUP": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
            "PYTH": "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3",
            "RENDER": "rndrizKT3MK1iimdxRdWabcF7Zg7AR5T4nud4EkHBof",
        }
    
    async def get_token_price(self, mint: str) -> Optional[float]:
        """Get current token price in USD using Helius"""
        # Check cache first
        if mint in self.price_cache:
            return self.price_cache[mint]
        
        try:
            # For SOL, we can use a direct endpoint
            if mint == self.TOKENS["SOL"]:
                return await self._get_sol_price()
            
            # For other tokens, use Jupiter price API as fallback
            return await self._get_jupiter_price(mint)
            
        except Exception as e:
            print(f"[PriceOracle] Error fetching price for {mint}: {e}")
            return None
    
    async def get_token_prices(self, mints: List[str]) -> Dict[str, float]:
        """Get prices for multiple tokens"""
        tasks = [self.get_token_price(mint) for mint in mints]
        results = await asyncio.gather(*tasks)
        
        return {
            mint: price 
            for mint, price in zip(mints, results) 
            if price is not None
        }
    
    async def _get_sol_price(self) -> float:
        """Get SOL price from multiple sources"""
        try:
            # Try Jupiter first
            async with aiohttp.ClientSession() as session:
                url = "https://price.jup.ag/v4/price?ids=So11111111111111111111111111111111111111112"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        price = data['data']['So11111111111111111111111111111111111111112']['price']
                        self.price_cache[self.TOKENS["SOL"]] = price
                        return price
        except:
            pass
        
        # Fallback to hardcoded recent price
        return 100.0  # Update this periodically
    
    async def _get_jupiter_price(self, mint: str) -> Optional[float]:
        """Get token price from Jupiter API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://price.jup.ag/v4/price?ids={mint}"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if mint in data.get('data', {}):
                            price = data['data'][mint]['price']
                            self.price_cache[mint] = price
                            return price
        except Exception as e:
            print(f"[PriceOracle] Jupiter API error: {e}")
        
        return None
    
    async def get_pool_token_ratio(self, pool_address: str) -> Optional[Tuple[float, float]]:
        """Get token amounts in a pool using Helius"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/addresses/{pool_address}/balances?api-key={self.helius_api_key}"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Parse token balances from response
                        tokens = data.get('tokens', [])
                        if len(tokens) >= 2:
                            return (
                                float(tokens[0]['amount']) / (10 ** tokens[0]['decimals']),
                                float(tokens[1]['amount']) / (10 ** tokens[1]['decimals'])
                            )
        except Exception as e:
            print(f"[PriceOracle] Error fetching pool data: {e}")
        
        return None
    
    def calculate_lp_token_value(
        self,
        amount_a: float,
        amount_b: float,
        price_a: float,
        price_b: float
    ) -> float:
        """Calculate the USD value of LP tokens"""
        value_a = amount_a * price_a
        value_b = amount_b * price_b
        return value_a + value_b
    
    async def get_historical_prices(
        self,
        mint: str,
        start: datetime,
        end: datetime,
        interval: str = "1h"
    ) -> List[Dict[str, any]]:
        """Get historical price data (mock for now)"""
        # TODO: Implement with real historical data source
        # For now, return mock data
        current_price = await self.get_token_price(mint) or 100
        
        data_points = []
        current_time = start
        while current_time <= end:
            # Add some randomness to simulate price movement
            import random
            price_variation = random.uniform(0.95, 1.05)
            data_points.append({
                "timestamp": current_time.isoformat(),
                "price": current_price * price_variation
            })
            current_time += timedelta(hours=1)
        
        return data_points
    
    def get_token_symbol(self, mint: str) -> str:
        """Get token symbol from mint address"""
        # Reverse lookup in our token dict
        for symbol, address in self.TOKENS.items():
            if address == mint:
                return symbol
        
        # Return shortened mint if not found
        return f"{mint[:4]}...{mint[-4:]}"
    
    async def validate_token_mint(self, mint: str) -> bool:
        """Validate if a mint address is valid"""
        try:
            # Check if it's a known token
            if mint in self.TOKENS.values():
                return True
            
            # Try to get price - if successful, it's valid
            price = await self.get_token_price(mint)
            return price is not None
        except:
            return False


# Global price oracle instance
price_oracle = PriceOracle()


# Test function
async def test_price_oracle():
    """Test price oracle functionality"""
    oracle = PriceOracle()
    
    # Test single token
    sol_price = await oracle.get_token_price(oracle.TOKENS["SOL"])
    print(f"SOL Price: ${sol_price}")
    
    # Test multiple tokens
    mints = [oracle.TOKENS["SOL"], oracle.TOKENS["USDC"], oracle.TOKENS["BONK"]]
    prices = await oracle.get_token_prices(mints)
    print(f"Multiple prices: {prices}")
    
    # Test LP value calculation
    lp_value = oracle.calculate_lp_token_value(
        amount_a=1.5,  # 1.5 SOL
        amount_b=150,  # 150 USDC
        price_a=100,   # $100 per SOL
        price_b=1      # $1 per USDC
    )
    print(f"LP Token Value: ${lp_value}")


if __name__ == "__main__":
    asyncio.run(test_price_oracle())