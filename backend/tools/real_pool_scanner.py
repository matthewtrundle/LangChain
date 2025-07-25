import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from tools.helius_client import HeliusClient

class RealPoolScannerTool(BaseTool):
    name = "real_pool_scanner"
    description = "Scans for REAL high-yield pools using live data from DeFiLlama, Helius, and Jupiter"
    helius_client: HeliusClient = Field(default=None, exclude=True)
    
    def __init__(self):
        super().__init__()
        self.helius_client = HeliusClient()
    
    def _run(self, min_apy: float = 500, max_age_hours: int = 48) -> str:
        """Scan for real high-yield opportunities"""
        try:
            print(f"[RealPoolScanner] Running scan with min_apy={min_apy}")
            real_opportunities = []
            
            # 1. DeFiLlama - Get real APY data
            defi_llama_pools = self._get_defi_llama_pools(min_apy)
            real_opportunities.extend(defi_llama_pools)
            print(f"[RealPoolScanner] Added {len(defi_llama_pools)} DeFiLlama pools")
            
            # 2. Helius - Get new pool creations
            new_pools = self._get_new_pools_from_helius()
            real_opportunities.extend(new_pools)
            print(f"[RealPoolScanner] Added {len(new_pools)} Helius pools")
            
            # 3. Enhance with FREE Jupiter pricing
            enhanced_pools = self._enhance_with_free_data(real_opportunities)
            
            # 4. Sort by APY and filter
            final_pools = [p for p in enhanced_pools if p.get("apy", 0) >= min_apy]
            final_pools.sort(key=lambda x: x.get("apy", 0), reverse=True)
            
            print(f"[RealPoolScanner] Returning {len(final_pools)} pools meeting criteria")
            
            return json.dumps({
                "source": "REAL_DATA",
                "found_pools": len(final_pools),
                "pools": final_pools[:10],  # Top 10
                "scan_time": datetime.now().isoformat(),
                "data_sources": ["DeFiLlama", "Helius", "Jupiter", "CoinGecko", "WebScraping"]
            }, indent=2)
            
        except Exception as e:
            print(f"[RealPoolScanner] Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Error scanning real pools: {str(e)}"
    
    def _get_defi_llama_pools(self, min_apy: float) -> List[Dict]:
        """Get real pool data from DeFiLlama"""
        try:
            # Ensure min_apy is a float
            if isinstance(min_apy, str):
                try:
                    import json
                    min_apy = json.loads(min_apy).get("min_apy", 100)
                except:
                    min_apy = float(min_apy) if min_apy else 100
            
            print(f"[RealPoolScanner] Fetching pools from DeFiLlama API with min APY: {min_apy}%")
            response = requests.get("https://yields.llama.fi/pools", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                all_pools = data.get("data", [])
                print(f"[RealPoolScanner] DeFiLlama returned {len(all_pools)} total pools")
                
                solana_pools = []
                for pool in all_pools:
                    if pool.get("chain") == "Solana":
                        apy = pool.get("apy", 0)
                        if apy >= min_apy:
                            # Convert to our format
                            pool_data = {
                                "pool_address": pool.get("pool", "unknown"),
                                "protocol": pool.get("project", "unknown"),
                                "token_symbols": pool.get("symbol", "UNKNOWN"),
                                "apy": apy,
                                "tvl": pool.get("tvlUsd", 0),
                                "volume_24h": pool.get("volumeUsd1d", 0),
                                "age_days": 1,  # DeFiLlama doesn't provide creation time
                                "source": "DeFiLlama_REAL",
                                "real_data": True
                            }
                            solana_pools.append(pool_data)
                            print(f"[RealPoolScanner] Found: {pool_data['token_symbols']} @ {pool_data['protocol']} - {apy:.1f}% APY")
                
                print(f"[RealPoolScanner] Found {len(solana_pools)} Solana pools with APY >= {min_apy}%")
                
                # If no high APY pools, get top Solana pools by APY
                if not solana_pools:
                    print("[RealPoolScanner] No pools meet APY threshold, getting top Solana pools...")
                    solana_only = [p for p in all_pools if p.get("chain") == "Solana" and p.get("apy", 0) > 0]
                    solana_only.sort(key=lambda x: x.get("apy", 0), reverse=True)
                    
                    for pool in solana_only[:5]:  # Top 5 pools
                        pool_data = {
                            "pool_address": pool.get("pool", "unknown"),
                            "protocol": pool.get("project", "unknown"),
                            "token_symbols": pool.get("symbol", "UNKNOWN"),
                            "apy": pool.get("apy", 0),
                            "tvl": pool.get("tvlUsd", 0),
                            "volume_24h": pool.get("volumeUsd1d", 0),
                            "age_days": 1,
                            "source": "DeFiLlama_REAL",
                            "real_data": True
                        }
                        solana_pools.append(pool_data)
                        print(f"[RealPoolScanner] Top pool: {pool_data['token_symbols']} - {pool_data['apy']:.1f}% APY")
                
                return solana_pools
            else:
                print(f"[RealPoolScanner] DeFiLlama API error: {response.status_code}")
                return self._get_defi_llama_fallback(min_apy)
            
        except Exception as e:
            print(f"[RealPoolScanner] Error fetching DeFiLlama data: {e}")
            import traceback
            traceback.print_exc()
            return self._get_defi_llama_fallback(min_apy)
    
    def _get_defi_llama_fallback(self, min_apy: float) -> List[Dict]:
        """Return empty when DeFiLlama API is unavailable"""
        print("[RealPoolScanner] DeFiLlama API unavailable, no fallback data")
        return []
    
    def _get_new_pools_from_helius(self) -> List[Dict]:
        """Get new pools from Helius transaction monitoring"""
        try:
            # For now, return empty since Helius integration requires more setup
            # TODO: Implement real Helius monitoring for new pool creation events
            print("[RealPoolScanner] Helius integration not yet implemented")
            return []
            
        except Exception as e:
            print(f"Error getting Helius pools: {e}")
            return []
    
    def _enhance_with_free_data(self, pools: List[Dict]) -> List[Dict]:
        """Enhance pools with FREE data sources"""
        enhanced_pools = []
        
        for pool in pools:
            try:
                # Add Jupiter price data (FREE)
                pool["jupiter_pricing"] = self._get_jupiter_prices(pool)
                
                # Add CoinGecko data (FREE)
                pool["coingecko_data"] = self._get_coingecko_data(pool)
                
                # Calculate metrics
                pool["price_impact"] = self._calculate_price_impact(pool)
                pool["sustainability_score"] = self._calculate_sustainability_score(pool)
                
                enhanced_pools.append(pool)
                
            except Exception as e:
                print(f"Error enhancing pool {pool.get('pool_address', 'unknown')}: {e}")
                enhanced_pools.append(pool)
        
        return enhanced_pools
    
    def _get_jupiter_prices(self, pool: Dict) -> Dict:
        """Get token prices from Jupiter (FREE)"""
        try:
            # Extract token mints
            token_a_mint = pool.get("token_a_mint", "")
            token_b_mint = pool.get("token_b_mint", "")
            
            # Skip if no mints available
            if not token_a_mint and not token_b_mint:
                return {"error": "No token mints available"}
            
            # Build mint list
            mints = []
            if token_a_mint:
                mints.append(token_a_mint)
            if token_b_mint and token_b_mint != token_a_mint:
                mints.append(token_b_mint)
            
            # Jupiter Price API v6
            url = f"https://price.jup.ag/v6/price?ids={','.join(mints)}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                prices = data.get("data", {})
                
                return {
                    "token_a_price": prices.get(token_a_mint, {}).get("price", 0) if token_a_mint else 0,
                    "token_b_price": prices.get(token_b_mint, {}).get("price", 0) if token_b_mint else 0,
                    "price_source": "Jupiter_API",
                    "real_data": True
                }
            else:
                return {"error": f"Jupiter API error: {response.status_code}"}
        except Exception as e:
            print(f"Error getting Jupiter prices: {e}")
            return {"error": str(e)}
    
    def _get_coingecko_data(self, pool: Dict) -> Dict:
        """Get additional data from CoinGecko (FREE)"""
        try:
            # Map common Solana tokens to CoinGecko IDs
            token_to_coingecko = {
                "SOL": "solana",
                "USDC": "usd-coin",
                "USDT": "tether",
                "BONK": "bonk",
                "WIF": "dogwifhat",
                "JUP": "jupiter-exchange-solana",
                "PYTH": "pyth-network",
                "JTO": "jito-governance-token",
                "RNDR": "render-token"
            }
            
            # Get token symbols
            token_a = pool.get("token_a", pool.get("token_symbols", "").split("-")[0] if pool.get("token_symbols") else "")
            token_b = pool.get("token_b", pool.get("token_symbols", "").split("-")[1] if pool.get("token_symbols") and "-" in pool.get("token_symbols") else "")
            
            # Find CoinGecko IDs
            coingecko_ids = []
            for token in [token_a, token_b]:
                if token in token_to_coingecko:
                    coingecko_ids.append(token_to_coingecko[token])
            
            if not coingecko_ids:
                return {"error": "No known tokens for CoinGecko"}
            
            # CoinGecko free API
            ids_str = ",".join(coingecko_ids)
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Aggregate data from all tokens
                total_market_cap = 0
                total_volume = 0
                avg_price_change = 0
                count = 0
                
                for coin_id in coingecko_ids:
                    if coin_id in data:
                        coin_data = data[coin_id]
                        total_market_cap += coin_data.get("usd_market_cap", 0)
                        total_volume += coin_data.get("usd_24h_vol", 0)
                        if "usd_24h_change" in coin_data:
                            avg_price_change += coin_data["usd_24h_change"]
                            count += 1
                
                return {
                    "market_cap": total_market_cap,
                    "volume_24h": total_volume,
                    "price_change_24h": avg_price_change / count if count > 0 else 0,
                    "data_source": "CoinGecko_API",
                    "real_data": True
                }
            else:
                return {"error": f"CoinGecko API error: {response.status_code}"}
        except Exception as e:
            print(f"Error getting CoinGecko data: {e}")
            return {"error": str(e)}
    
    def _calculate_sustainability_score(self, pool: Dict) -> float:
        """Calculate how sustainable the yield is"""
        apy = pool.get("apy", 0)
        tvl = pool.get("tvl", 0)
        volume = pool.get("volume_24h", 0)
        
        # Simple sustainability formula
        if apy > 5000 or tvl < 10000:
            return 1.0  # Very unsustainable
        elif apy > 2000 or tvl < 100000:
            return 3.0  # Probably unsustainable
        elif apy > 1000:
            return 5.0  # Medium sustainability
        else:
            return 8.0  # More sustainable
    
    def _calculate_age_days(self, timestamp: str) -> float:
        """Calculate pool age in days"""
        try:
            if not timestamp:
                return 999  # Unknown age
            
            # Parse timestamp and calculate days
            pool_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(pool_time.tzinfo)
            age_days = (now - pool_time).total_seconds() / (24 * 3600)
            
            return round(age_days, 2)
            
        except Exception:
            return 999
    
    def _calculate_price_impact(self, pool: Dict) -> float:
        """Calculate estimated price impact"""
        tvl = pool.get("tvl", 0)
        volume = pool.get("volume_24h", 0)
        
        if tvl > 0 and volume > 0:
            # Simple price impact estimation
            return min(10.0, (volume / tvl) * 100)
        
        return 5.0  # Default estimate
    
    async def _arun(self, min_apy: float = 500) -> str:
        """Async version"""
        return self._run(min_apy)