"""
TokenPriceMonitor model - represents price monitoring tasks.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import (
    BigInteger, DateTime, ForeignKey, Index, Integer, Numeric, String, func, text
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .token_analysis_report import TokenAnalysisReport
    from .token_price_history import TokenPriceHistory


class TokenPriceMonitor(Base):
    """
    TokenPriceMonitor model representing price monitoring tasks.

    Corresponds to Prisma model: TokenPriceMonitor
    Table: TokenPriceMonitor
    """

    __tablename__ = "TokenPriceMonitor"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Report reference (unique)
    report_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('public.TokenAnalysisReport.id'),
        unique=True,
        nullable=False
    )

    # Token info
    chain: Mapped[str] = mapped_column(String(50), nullable=False)
    token_address: Mapped[str] = mapped_column(String(100), nullable=False)

    # Price data
    initial_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    highest_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    lowest_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    current_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # Performance metrics
    max_gain_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    max_drawdown_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

    # Monitoring period
    monitor_start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    monitor_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'active'::character varying")
    )

    # Holder data
    initial_holders_count: Mapped[Optional[int]] = mapped_column(Integer)
    current_holders_count: Mapped[Optional[int]] = mapped_column(Integer)
    max_holders_count: Mapped[Optional[int]] = mapped_column(Integer)
    holders_growth_rate_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

    # Task management
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(100))
    source: Mapped[Optional[str]] = mapped_column(String(50))

    # Trigger tracking
    trigger_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    triggered_thresholds: Mapped[Optional[dict]] = mapped_column(
        JSON,
        server_default=text("'{}'::json")
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
    report: Mapped["TokenAnalysisReport"] = relationship(
        "TokenAnalysisReport",
        back_populates="price_monitor",
        lazy="selectin"
    )
    price_history: Mapped[List["TokenPriceHistory"]] = relationship(
        "TokenPriceHistory",
        back_populates="monitor",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Table constraints
    __table_args__ = (
        Index('idx_tpm_chain_token', 'chain', 'token_address'),
        Index('idx_tpm_status_time', 'status', 'monitor_start_time'),
        Index('idx_tpm_report_id', 'report_id'),
        Index('idx_active_monitors_optimized', 'status', 'monitor_start_time'),
        Index('idx_price_monitor_batch_data',
              'report_id', 'initial_price', 'current_price',
              'initial_holders_count', 'current_holders_count',
              'max_holders_count', 'holders_growth_rate_percent'),
        Index('idx_price_monitor_batch_optimized',
              'report_id', 'chain', 'initial_price', 'current_price',
              'initial_holders_count', 'current_holders_count',
              'max_holders_count', 'holders_growth_rate_percent'),
        {'schema': 'public'}
    )

    def __repr__(self):
        return (
            f"<TokenPriceMonitor(id={self.id}, chain={self.chain}, "
            f"token={self.token_address}, status={self.status})>"
        )

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "report_id": self.report_id,
            "chain": self.chain,
            "token_address": self.token_address,
            "initial_price": str(self.initial_price) if self.initial_price else None,
            "current_price": str(self.current_price) if self.current_price else None,
            "highest_price": str(self.highest_price) if self.highest_price else None,
            "lowest_price": str(self.lowest_price) if self.lowest_price else None,
            "max_gain_percent": str(self.max_gain_percent) if self.max_gain_percent else None,
            "max_drawdown_percent": str(self.max_drawdown_percent) if self.max_drawdown_percent else None,
            "status": self.status,
            "monitor_start_time": self.monitor_start_time.isoformat() if self.monitor_start_time else None,
            "monitor_end_time": self.monitor_end_time.isoformat() if self.monitor_end_time else None,
            "current_holders_count": self.current_holders_count,
            "holders_growth_rate_percent": str(self.holders_growth_rate_percent) if self.holders_growth_rate_percent else None,
            "trigger_count": self.trigger_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
