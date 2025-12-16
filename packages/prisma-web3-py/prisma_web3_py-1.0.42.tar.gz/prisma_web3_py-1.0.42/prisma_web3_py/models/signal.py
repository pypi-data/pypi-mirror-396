"""
Signal model - represents trading signals for tokens.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    Boolean, DateTime, ForeignKeyConstraint, Index, Integer, String,
    UniqueConstraint, func, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .token import Token


class Signal(Base):
    """
    Signal model representing trading signals for tokens.

    Corresponds to Prisma model: Signal
    Table: Signal
    """

    __tablename__ = "Signal"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Signal information
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(255), nullable=False)
    is_first: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false")
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
    last_occurrence: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Occurrence tracking
    occurrence_count: Mapped[Optional[int]] = mapped_column(Integer)

    # Token reference (foreign key)
    chain: Mapped[str] = mapped_column(String(255), nullable=False)
    token_address: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    token: Mapped["Token"] = relationship(
        "Token",
        back_populates="signals",
        lazy="selectin"
    )

    # Table constraints
    __table_args__ = (
        UniqueConstraint(
            'chain',
            'token_address',
            'source',
            'signal_type',
            name='Signal_chain_token_address_source_signal_type_key'
        ),
        ForeignKeyConstraint(
            ['chain', 'token_address'],
            ['public.Token.chain', 'public.Token.token_address'],
            name='Signal_chain_token_address_fkey'
        ),
        Index('Signal_last_occurrence_idx', 'last_occurrence'),
        Index('Signal_source_idx', 'source'),
        Index('Signal_signal_type_idx', 'signal_type'),
        Index('Signal_chain_idx', 'chain'),
        {'schema': 'public'}
    )

    def __repr__(self):
        return (
            f"<Signal(id={self.id}, type={self.signal_type}, "
            f"source={self.source}, chain={self.chain}, "
            f"token={self.token_address})>"
        )

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "source": self.source,
            "signal_type": self.signal_type,
            "is_first": self.is_first,
            "chain": self.chain,
            "token_address": self.token_address,
            "last_occurrence": self.last_occurrence.isoformat() if self.last_occurrence else None,
            "occurrence_count": self.occurrence_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
