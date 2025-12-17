"""
TokenPriceHistory model - represents historical price data points.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    BigInteger, DateTime, ForeignKey, Index, Integer, Numeric, String, func, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .token_price_monitor import TokenPriceMonitor


class TokenPriceHistory(Base):
    """
    TokenPriceHistory model representing historical price data points.

    Corresponds to Prisma model: TokenPriceHistory
    Table: TokenPriceHistory
    """

    __tablename__ = "TokenPriceHistory"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Monitor reference
    monitor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('public.TokenPriceMonitor.id', ondelete='CASCADE'),
        nullable=False
    )

    # Token info
    chain: Mapped[str] = mapped_column(String(50), nullable=False)
    token_address: Mapped[str] = mapped_column(String(100), nullable=False)

    # Price and market data
    price_usd: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    volume_24h: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    market_cap: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    liquidity_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))

    # Holder data
    holders_count: Mapped[Optional[int]] = mapped_column(Integer)
    top_100_concentration: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    top_10_concentration: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

    # Recording time
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Data source
    data_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'dexscreener'::character varying")
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now()
    )

    # Relationships
    monitor: Mapped["TokenPriceMonitor"] = relationship(
        "TokenPriceMonitor",
        back_populates="price_history",
        lazy="selectin"
    )

    # Table constraints
    __table_args__ = (
        Index('idx_tph_monitor_time', 'monitor_id', 'recorded_at'),
        Index('idx_tph_chain_token_time', 'chain', 'token_address', 'recorded_at'),
        Index('idx_recent_prices_optimized', 'chain', 'token_address', 'recorded_at', 'price_usd'),
        Index('idx_time_chain_token', 'recorded_at', 'chain', 'token_address'),
        Index('idx_price_history_monitor_optimized', 'monitor_id', 'recorded_at', 'price_usd'),
        Index('idx_price_history_time_optimized', 'chain', 'token_address', 'recorded_at'),
        Index('idx_price_history_time_token_optimized',
              'chain', 'token_address', 'recorded_at', 'price_usd'),
        {'schema': 'public'}
    )

    def __repr__(self):
        return (
            f"<TokenPriceHistory(id={self.id}, monitor_id={self.monitor_id}, "
            f"price={self.price_usd}, recorded_at={self.recorded_at})>"
        )

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "monitor_id": self.monitor_id,
            "chain": self.chain,
            "token_address": self.token_address,
            "price_usd": str(self.price_usd),
            "volume_24h": str(self.volume_24h) if self.volume_24h else None,
            "market_cap": str(self.market_cap) if self.market_cap else None,
            "liquidity_usd": str(self.liquidity_usd) if self.liquidity_usd else None,
            "holders_count": self.holders_count,
            "top_100_concentration": str(self.top_100_concentration) if self.top_100_concentration else None,
            "top_10_concentration": str(self.top_10_concentration) if self.top_10_concentration else None,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "data_source": self.data_source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
