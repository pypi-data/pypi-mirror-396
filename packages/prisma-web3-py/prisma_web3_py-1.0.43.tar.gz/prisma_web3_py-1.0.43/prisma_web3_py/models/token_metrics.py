"""
TokenMetrics model - represents token market metrics.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    BigInteger, DateTime, Float, ForeignKeyConstraint, Index, Integer,
    Numeric, String, UniqueConstraint, func, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .token import Token


class TokenMetrics(Base):
    """
    TokenMetrics model representing token market metrics and statistics.

    Corresponds to Prisma model: TokenMetrics
    Table: TokenMetrics
    """

    __tablename__ = "TokenMetrics"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Data source
    source: Mapped[Optional[str]] = mapped_column(
        String(255),
        server_default=text("'default'::character varying")
    )

    # Market data
    price: Mapped[Optional[float]] = mapped_column(Float)
    market_cap: Mapped[Optional[float]] = mapped_column(Float)
    fully_diluted_valuation: Mapped[Optional[float]] = mapped_column(Float)
    liquidity: Mapped[Optional[float]] = mapped_column(Float)
    volume_24h: Mapped[Optional[float]] = mapped_column(Float)

    # Holder data
    holder_count: Mapped[Optional[int]] = mapped_column(Integer)
    holders_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Transaction data
    swaps: Mapped[Optional[int]] = mapped_column(Integer)
    buys: Mapped[Optional[int]] = mapped_column(Integer)
    sells: Mapped[Optional[int]] = mapped_column(Integer)
    tx_count: Mapped[Optional[int]] = mapped_column(Integer)

    # Price changes
    price_change_1h: Mapped[Optional[float]] = mapped_column(Float)
    price_change_24h: Mapped[Optional[float]] = mapped_column(Float)

    # Transaction breakdown
    transactions_1h_buys: Mapped[Optional[int]] = mapped_column(Integer)
    transactions_1h_sells: Mapped[Optional[int]] = mapped_column(Integer)
    transactions_24h_buys: Mapped[Optional[int]] = mapped_column(Integer)
    transactions_24h_sells: Mapped[Optional[int]] = mapped_column(Integer)

    # Smart money
    smart_buy_24h: Mapped[Optional[int]] = mapped_column(Integer)
    smart_sell_24h: Mapped[Optional[int]] = mapped_column(Integer)

    # Liquidity info
    initial_liquidity: Mapped[Optional[float]] = mapped_column(Float)
    liquidity_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    pair_address: Mapped[Optional[str]] = mapped_column(String(255))
    reserve: Mapped[Optional[float]] = mapped_column(Float)

    # Timestamps
    timestamp: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    # Token reference (foreign key)
    chain: Mapped[str] = mapped_column(String(255), nullable=False)
    token_address: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    token: Mapped["Token"] = relationship(
        "Token",
        back_populates="token_metrics",
        lazy="selectin"
    )

    # Table constraints
    __table_args__ = (
        UniqueConstraint('chain', 'token_address', name='TokenMetrics_chain_token_address_key'),
        ForeignKeyConstraint(
            ['chain', 'token_address'],
            ['public.Token.chain', 'public.Token.token_address'],
            name='TokenMetrics_chain_token_address_fkey'
        ),
        Index('TokenMetrics_timestamp_idx', 'timestamp'),
        {'schema': 'public'}
    )

    def __repr__(self):
        return (
            f"<TokenMetrics(id={self.id}, chain={self.chain}, "
            f"token={self.token_address}, price={self.price})>"
        )

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "source": self.source,
            "chain": self.chain,
            "token_address": self.token_address,
            "price": self.price,
            "market_cap": self.market_cap,
            "fully_diluted_valuation": self.fully_diluted_valuation,
            "liquidity": self.liquidity,
            "volume_24h": self.volume_24h,
            "holder_count": self.holder_count,
            "swaps": self.swaps,
            "buys": self.buys,
            "sells": self.sells,
            "price_change_1h": self.price_change_1h,
            "price_change_24h": self.price_change_24h,
            "smart_buy_24h": self.smart_buy_24h,
            "smart_sell_24h": self.smart_sell_24h,
            "timestamp": self.timestamp,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
