"""
EventLabels model - Manual labels for AI analysis results review and quality control.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy import (
    String, Integer, DateTime, Index, text, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from ..base import Base


class LabelType(str, Enum):
    """Label type enumeration for event quality assessment."""
    ACCURATE = "accurate"      # AI analysis was accurate
    MISS = "miss"              # AI missed important signals
    NOISE = "noise"            # False positive, not relevant
    INVESTIGATE = "investigate"  # Needs further investigation


class EventLabels(Base):
    """
    Event Labels model for manual review and quality control.

    Used to track human review of AI analysis results for:
    - Quality control and model improvement
    - False positive identification
    - Training data generation
    - Performance metrics

    Corresponds to table: EventLabels
    """

    __tablename__ = "EventLabels"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="Primary key UUID"
    )

    # === Event Reference ===
    event_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Reference to AIAnalysisResult.id"
    )

    # === Review Information ===
    reviewer: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Reviewer username/ID"
    )
    label: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Label type: accurate, miss, noise, investigate"
    )
    note: Mapped[Optional[str]] = mapped_column(
        String,
        comment="Optional review notes/comments"
    )

    # === Timestamp ===
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="Label creation time"
    )

    # === Table constraints and indexes ===
    __table_args__ = (
        # Index for event lookup
        Index('idx_event_labels_event_id', 'event_id'),
        # Index for label filtering
        Index('idx_event_labels_label', 'label'),
        # Index for reviewer statistics
        Index('idx_event_labels_reviewer', 'reviewer'),
        # Index for time-based queries
        Index('idx_event_labels_created_at', 'created_at'),
        # Composite index for event+label queries
        Index('idx_event_labels_event_label', 'event_id', 'label'),

        {'schema': 'public'}
    )

    def __repr__(self):
        return (
            f"<EventLabels(id={self.id}, "
            f"event_id={self.event_id}, "
            f"label={self.label})>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "event_id": self.event_id,
            "reviewer": self.reviewer,
            "label": self.label,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def is_positive_label(self) -> bool:
        """
        Check if label indicates accurate analysis.

        Returns:
            True if label is 'accurate'
        """
        return self.label == LabelType.ACCURATE.value

    def is_negative_label(self) -> bool:
        """
        Check if label indicates problematic analysis.

        Returns:
            True if label is 'miss' or 'noise'
        """
        return self.label in [LabelType.MISS.value, LabelType.NOISE.value]

    def needs_review(self) -> bool:
        """
        Check if label indicates further investigation needed.

        Returns:
            True if label is 'investigate'
        """
        return self.label == LabelType.INVESTIGATE.value

    @classmethod
    def get_valid_labels(cls) -> list:
        """
        Get list of valid label values.

        Returns:
            List of valid label strings
        """
        return [label.value for label in LabelType]

    @classmethod
    def is_valid_label(cls, label: str) -> bool:
        """
        Check if label is valid.

        Args:
            label: Label string to validate

        Returns:
            True if label is valid
        """
        return label in cls.get_valid_labels()
