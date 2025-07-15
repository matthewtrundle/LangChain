import requests
import json
from typing import Dict, List, Optional, Any
from config import Config

class HeliusClient:
    def __init__(self):
        self.api_key = Config.HELIUS_API_KEY
        self.rpc_url = Config.HELIUS_RPC_URL
        self.base_url = "https://api.helius.xyz/v0"
        
    def make_rpc_request(self, method: str, params: List[Any]) -> Dict:
        """Make a JSON-RPC request to Helius"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        response = requests.post(
            self.rpc_url,
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"RPC request failed: {response.status_code}")
            
        return response.json()
    
    def get_token_accounts(self, owner: str) -> List[Dict]:
        """Get all token accounts for an owner"""
        result = self.make_rpc_request(
            "getTokenAccountsByOwner",
            [
                owner,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                {"encoding": "jsonParsed"}
            ]
        )
        return result.get("result", {}).get("value", [])
    
    def get_recent_transactions(self, account: str, limit: int = 10) -> List[Dict]:
        """Get recent transactions for an account"""
        result = self.make_rpc_request(
            "getSignaturesForAddress",
            [account, {"limit": limit}]
        )
        return result.get("result", [])
    
    def get_account_info(self, account: str) -> Dict:
        """Get account information"""
        result = self.make_rpc_request(
            "getAccountInfo",
            [account, {"encoding": "jsonParsed"}]
        )
        return result.get("result", {})
    
    def get_token_supply(self, mint: str) -> Dict:
        """Get token supply information"""
        result = self.make_rpc_request(
            "getTokenSupply",
            [mint]
        )
        return result.get("result", {})
    
    def get_token_largest_accounts(self, mint: str) -> List[Dict]:
        """Get largest token holders"""
        result = self.make_rpc_request(
            "getTokenLargestAccounts",
            [mint]
        )
        return result.get("result", {}).get("value", [])
    
    def search_programs(self, program_ids: List[str]) -> List[Dict]:
        """Search for transactions by program IDs"""
        url = f"{self.base_url}/addresses/{','.join(program_ids)}/transactions"
        params = {
            "api-key": self.api_key,
            "limit": 100
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Program search failed: {response.status_code}")
            
        return response.json()
    
    def get_nft_metadata(self, mint_accounts: List[str]) -> List[Dict]:
        """Get NFT metadata for multiple mints"""
        url = f"{self.base_url}/token-metadata"
        params = {
            "api-key": self.api_key
        }
        
        payload = {
            "mintAccounts": mint_accounts
        }
        
        response = requests.post(url, params=params, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Metadata request failed: {response.status_code}")
            
        return response.json()

# Known Solana DeFi program IDs
PROGRAM_IDS = {
    "RAYDIUM_AMM": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    "RAYDIUM_LIQUIDITY": "RVKd61ztZW9GUwhRbbLoYVRE5Xf1B2tVscKqwZqXgEr",
    "ORCA": "9W959DqEETiGZocYWCQPaJ6skhUS3WVYaRFrNQfNQFNJ",
    "METEORA": "Eo7WjKq67rjJQSYxS6z3YkapzY3eMj6Xy8X5EQVn5UaB",
    "JUPITER": "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",
}