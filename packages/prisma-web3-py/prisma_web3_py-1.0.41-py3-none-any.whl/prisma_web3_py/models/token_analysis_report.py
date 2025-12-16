"""
TokenAnalysisReport model - represents AI-generated token analysis reports.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    DateTime, ForeignKeyConstraint, Index, Integer, String, Text, func, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .token import Token
    from .token_price_monitor import TokenPriceMonitor


class TokenAnalysisReport(Base):
    """
    TokenAnalysisReport model representing AI-generated analysis reports.

    Corresponds to Prisma model: TokenAnalysisReport
    Table: TokenAnalysisReport
    """

    __tablename__ = "TokenAnalysisReport"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Report data
    social_report_data: Mapped[str] = mapped_column(Text, nullable=False)
    token_report_data: Mapped[str] = mapped_column(Text, nullable=False)

    # Scores
    social_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    token_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Metadata
    workflow_id: Mapped[Optional[str]] = mapped_column(String(255))
    source: Mapped[Optional[str]] = mapped_column(String(255))
    snapshot_id: Mapped[Optional[str]] = mapped_column(String(36))
    analysis_version: Mapped[Optional[str]] = mapped_column(
        String(32),
        server_default=text("'v3.0'::character varying")
    )
    config_hash: Mapped[Optional[str]] = mapped_column(String(64))
    experiment_id: Mapped[Optional[str]] = mapped_column(String(64))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Token reference (foreign key)
    chain: Mapped[str] = mapped_column(String(255), nullable=False)
    token_address: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    token: Mapped["Token"] = relationship(
        "Token",
        back_populates="token_analysis_reports",
        lazy="selectin"
    )
    price_monitor: Mapped[Optional["TokenPriceMonitor"]] = relationship(
        "TokenPriceMonitor",
        back_populates="report",
        uselist=False,
        lazy="selectin"
    )

    # Table constraints
    __table_args__ = (
        ForeignKeyConstraint(
            ['chain', 'token_address'],
            ['public.Token.chain', 'public.Token.token_address'],
            name='TokenAnalysisReport_chain_token_address_fkey'
        ),
        Index('TokenAnalysisReport_chain_token_address_idx', 'chain', 'token_address'),
        Index('TokenAnalysisReport_created_at_idx', 'created_at'),
        Index('TokenAnalysisReport_created_at_source_idx', 'created_at', 'source'),
        Index('TokenAnalysisReport_source_created_at_idx', 'source', 'created_at'),
        Index('TokenAnalysisReport_created_at_source_social_score_token_score_idx',
              'created_at', 'source', 'social_score', 'token_score'),
        Index('TokenAnalysisReport_chain_created_at_source_idx', 'chain', 'created_at', 'source'),
        Index('TokenAnalysisReport_social_score_token_score_created_at_idx',
              'social_score', 'token_score', 'created_at'),
        Index('TokenAnalysisReport_token_address_created_at_idx', 'token_address', 'created_at'),
        Index('TokenAnalysisReport_source_social_score_token_score_idx',
              'source', 'social_score', 'token_score'),
        Index('TokenAnalysisReport_created_at_chain_token_address_idx',
              'created_at', 'chain', 'token_address'),
        Index('idx_token_composite_optimized',
              'chain', 'token_address', 'created_at', 'source'),
        Index('idx_source_time_composite',
              'source', 'created_at', 'chain', 'token_address'),
        Index('idx_time_source_scores',
              'created_at', 'source', 'social_score', 'token_score'),
        Index('idx_token_analysis_24h_stats',
              'created_at', 'source'),
        Index('idx_token_analysis_composite_optimized',
              'chain', 'token_address', 'created_at', 'source'),
        Index('idx_token_analysis_count_optimized',
              'chain', 'token_address', 'id'),
        Index('idx_token_analysis_created_at_only',
              'created_at'),
        Index('idx_token_analysis_dedup_optimized',
              'chain', 'token_address', 'created_at'),
        Index('idx_token_analysis_scores_filter',
              'social_score', 'token_score', 'created_at'),
        Index('idx_token_analysis_single_token',
              'token_address', 'chain', 'created_at'),
        Index('idx_token_analysis_time_scores',
              'created_at', 'social_score', 'token_score'),
        {'schema': 'public'}
    )

    def __repr__(self):
        return (
            f"<TokenAnalysisReport(id={self.id}, chain={self.chain}, "
            f"token={self.token_address}, social_score={self.social_score}, "
            f"token_score={self.token_score})>"
        )

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "chain": self.chain,
            "token_address": self.token_address,
            "social_score": self.social_score,
            "token_score": self.token_score,
            "source": self.source,
            "workflow_id": self.workflow_id,
            "snapshot_id": self.snapshot_id,
            "analysis_version": self.analysis_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
