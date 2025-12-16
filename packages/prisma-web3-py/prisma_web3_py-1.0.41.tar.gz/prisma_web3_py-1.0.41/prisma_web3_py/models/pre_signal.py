"""
PreSignal model - represents pre-signals for token analysis.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum
from sqlalchemy import (
    DateTime, ForeignKeyConstraint, Index, Integer, String, Enum as SQLEnum,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .token import Token


class SignalStatus(str, Enum):
    """Signal status enumeration."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class PreSignal(Base):
    """
    PreSignal model representing pre-signals for token analysis.

    Corresponds to Prisma model: PreSignal
    Table: PreSignal
    """

    __tablename__ = "PreSignal"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Signal information
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[SignalStatus] = mapped_column(
        SQLEnum(SignalStatus, name="SignalStatus"),
        nullable=False,
        default=SignalStatus.OPEN
    )

    # Metrics
    channel_calls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    multi_signals: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    kol_discussions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    token_narrative: Mapped[Optional[str]] = mapped_column(String, nullable=True)

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

    # Token reference (foreign key)
    chain: Mapped[str] = mapped_column(String(255), nullable=False)
    token_address: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    token: Mapped["Token"] = relationship(
        "Token",
        back_populates="pre_signals",
        lazy="selectin"
    )

    # Table constraints
    __table_args__ = (
        ForeignKeyConstraint(
            ['chain', 'token_address'],
            ['public.Token.chain', 'public.Token.token_address'],
            name='PreSignal_chain_token_address_fkey'
        ),
        Index('PreSignal_source_idx', 'source'),
        Index('PreSignal_signal_type_idx', 'signal_type'),
        Index('PreSignal_chain_idx', 'chain'),
        Index('PreSignal_chain_token_address_idx', 'chain', 'token_address'),
        {'schema': 'public'}
    )

    def __repr__(self):
        return (
            f"<PreSignal(id={self.id}, type={self.signal_type}, "
            f"source={self.source}, status={self.status})>"
        )

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "source": self.source,
            "signal_type": self.signal_type,
            "status": self.status.value,
            "chain": self.chain,
            "token_address": self.token_address,
            "channel_calls": self.channel_calls,
            "multi_signals": self.multi_signals,
            "kol_discussions": self.kol_discussions,
            "token_narrative": self.token_narrative,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
