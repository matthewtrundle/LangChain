from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from enum import Enum
import uuid

class PositionStatus(Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    PENDING = "PENDING"

class Protocol(Enum):
    RAYDIUM = "raydium"
    ORCA = "orca"
    METEORA = "meteora"

@dataclass
class Position:
    """Core position model"""
    # Identity
    id: str
    user_wallet: str
    pool_address: str
    protocol: Protocol
    
    # Entry data
    entry_timestamp: datetime
    entry_price_a: Decimal
    entry_price_b: Decimal
    entry_amount_a: Decimal
    entry_amount_b: Decimal
    entry_lp_tokens: Decimal
    entry_tx_hash: str
    entry_value_usd: Decimal
    
    # Current state
    status: PositionStatus
    current_amount_a: Optional[Decimal] = None
    current_amount_b: Optional[Decimal] = None
    fees_earned_a: Decimal = Decimal('0')
    fees_earned_b: Decimal = Decimal('0')
    
    # Exit data
    exit_timestamp: Optional[datetime] = None
    exit_price_a: Optional[Decimal] = None
    exit_price_b: Optional[Decimal] = None
    exit_amount_a: Optional[Decimal] = None
    exit_amount_b: Optional[Decimal] = None
    exit_tx_hash: Optional[str] = None
    exit_value_usd: Optional[Decimal] = None
    
    # Token metadata
    token_a_symbol: str = ""
    token_b_symbol: str = ""
    token_a_mint: str = ""
    token_b_mint: str = ""
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_sync: Optional[datetime] = None
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'Position':
        """Create Position from database row"""
        return cls(
            id=str(row['id']),
            user_wallet=row['user_wallet'],
            pool_address=row['pool_address'],
            protocol=Protocol(row['protocol']),
            entry_timestamp=row['entry_timestamp'],
            entry_price_a=Decimal(str(row['entry_price_a'])),
            entry_price_b=Decimal(str(row['entry_price_b'])),
            entry_amount_a=Decimal(str(row['entry_amount_a'])),
            entry_amount_b=Decimal(str(row['entry_amount_b'])),
            entry_lp_tokens=Decimal(str(row['entry_lp_tokens'])),
            entry_tx_hash=row['entry_tx_hash'],
            entry_value_usd=Decimal(str(row['entry_value_usd'])),
            status=PositionStatus(row['status']),
            current_amount_a=Decimal(str(row['current_amount_a'])) if row.get('current_amount_a') else None,
            current_amount_b=Decimal(str(row['current_amount_b'])) if row.get('current_amount_b') else None,
            fees_earned_a=Decimal(str(row.get('fees_earned_a', 0))),
            fees_earned_b=Decimal(str(row.get('fees_earned_b', 0))),
            exit_timestamp=row.get('exit_timestamp'),
            exit_price_a=Decimal(str(row['exit_price_a'])) if row.get('exit_price_a') else None,
            exit_price_b=Decimal(str(row['exit_price_b'])) if row.get('exit_price_b') else None,
            exit_amount_a=Decimal(str(row['exit_amount_a'])) if row.get('exit_amount_a') else None,
            exit_amount_b=Decimal(str(row['exit_amount_b'])) if row.get('exit_amount_b') else None,
            exit_tx_hash=row.get('exit_tx_hash'),
            exit_value_usd=Decimal(str(row['exit_value_usd'])) if row.get('exit_value_usd') else None,
            token_a_symbol=row['token_a_symbol'],
            token_b_symbol=row['token_b_symbol'],
            token_a_mint=row['token_a_mint'],
            token_b_mint=row['token_b_mint'],
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
            last_sync=row.get('last_sync')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_wallet': self.user_wallet,
            'pool_address': self.pool_address,
            'protocol': self.protocol.value,
            'entry_timestamp': self.entry_timestamp.isoformat() if self.entry_timestamp else None,
            'entry_price_a': float(self.entry_price_a),
            'entry_price_b': float(self.entry_price_b),
            'entry_amount_a': float(self.entry_amount_a),
            'entry_amount_b': float(self.entry_amount_b),
            'entry_lp_tokens': float(self.entry_lp_tokens),
            'entry_tx_hash': self.entry_tx_hash,
            'entry_value_usd': float(self.entry_value_usd),
            'status': self.status.value,
            'current_amount_a': float(self.current_amount_a) if self.current_amount_a else None,
            'current_amount_b': float(self.current_amount_b) if self.current_amount_b else None,
            'fees_earned_a': float(self.fees_earned_a),
            'fees_earned_b': float(self.fees_earned_b),
            'exit_timestamp': self.exit_timestamp.isoformat() if self.exit_timestamp else None,
            'exit_price_a': float(self.exit_price_a) if self.exit_price_a else None,
            'exit_price_b': float(self.exit_price_b) if self.exit_price_b else None,
            'exit_amount_a': float(self.exit_amount_a) if self.exit_amount_a else None,
            'exit_amount_b': float(self.exit_amount_b) if self.exit_amount_b else None,
            'exit_tx_hash': self.exit_tx_hash,
            'exit_value_usd': float(self.exit_value_usd) if self.exit_value_usd else None,
            'token_a_symbol': self.token_a_symbol,
            'token_b_symbol': self.token_b_symbol,
            'token_a_mint': self.token_a_mint,
            'token_b_mint': self.token_b_mint,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }
    
    @property
    def pair_name(self) -> str:
        """Get trading pair name"""
        return f"{self.token_a_symbol}-{self.token_b_symbol}"
    
    @property
    def is_active(self) -> bool:
        """Check if position is active"""
        return self.status == PositionStatus.ACTIVE


@dataclass
class PositionSnapshot:
    """Point-in-time snapshot of position metrics"""
    id: str
    position_id: str
    timestamp: datetime
    
    # Prices at snapshot
    price_a: Decimal
    price_b: Decimal
    
    # Calculated values
    value_usd: Decimal
    fees_earned_usd: Decimal
    impermanent_loss_usd: Decimal
    impermanent_loss_percent: Decimal
    net_pnl_usd: Decimal
    net_pnl_percent: Decimal
    
    # Pool metrics
    pool_tvl: Optional[Decimal] = None
    pool_apy: Optional[Decimal] = None
    pool_volume_24h: Optional[Decimal] = None
    
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'PositionSnapshot':
        """Create PositionSnapshot from database row"""
        return cls(
            id=str(row['id']),
            position_id=str(row['position_id']),
            timestamp=row['timestamp'],
            price_a=Decimal(str(row['price_a'])),
            price_b=Decimal(str(row['price_b'])),
            value_usd=Decimal(str(row['value_usd'])),
            fees_earned_usd=Decimal(str(row['fees_earned_usd'])),
            impermanent_loss_usd=Decimal(str(row['impermanent_loss_usd'])),
            impermanent_loss_percent=Decimal(str(row['impermanent_loss_percent'])),
            net_pnl_usd=Decimal(str(row['net_pnl_usd'])),
            net_pnl_percent=Decimal(str(row['net_pnl_percent'])),
            pool_tvl=Decimal(str(row['pool_tvl'])) if row.get('pool_tvl') else None,
            pool_apy=Decimal(str(row['pool_apy'])) if row.get('pool_apy') else None,
            pool_volume_24h=Decimal(str(row['pool_volume_24h'])) if row.get('pool_volume_24h') else None,
            created_at=row.get('created_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'position_id': self.position_id,
            'timestamp': self.timestamp.isoformat(),
            'price_a': float(self.price_a),
            'price_b': float(self.price_b),
            'value_usd': float(self.value_usd),
            'fees_earned_usd': float(self.fees_earned_usd),
            'impermanent_loss_usd': float(self.impermanent_loss_usd),
            'impermanent_loss_percent': float(self.impermanent_loss_percent),
            'net_pnl_usd': float(self.net_pnl_usd),
            'net_pnl_percent': float(self.net_pnl_percent),
            'pool_tvl': float(self.pool_tvl) if self.pool_tvl else None,
            'pool_apy': float(self.pool_apy) if self.pool_apy else None,
            'pool_volume_24h': float(self.pool_volume_24h) if self.pool_volume_24h else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }