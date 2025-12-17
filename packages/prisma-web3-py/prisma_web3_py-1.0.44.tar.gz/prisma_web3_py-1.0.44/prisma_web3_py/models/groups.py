"""
Groups model - represents Telegram groups.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class Groups(Base):
    """
    Groups model representing Telegram groups.

    Corresponds to Prisma model: Groups
    Table: Groups
    """

    __tablename__ = "Groups"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Group info
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)

    # Timestamps
    added_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now()
    )

    # Table constraints
    __table_args__ = (
        Index('Groups_id_idx', 'id'),
        {'schema': 'public'}
    )

    def __repr__(self):
        return f"<Groups(id={self.id}, chat_id={self.chat_id}, title={self.title})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "title": self.title,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
