"""
NewsSemanticDedup model - semantic/structured dedup records for news.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String,
    Float,
    DateTime,
    Index,
    text,
    Integer,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class NewsSemanticDedup(Base):
    """
    Stores semantic deduplication entries for news events.

    Fields mirror Prisma model NewsSemanticDedup:
    - embedding stored as JSON array for portability (pgvector optional).
    - event_signature/event_key enable fast structured matching.
    - source_link/crypto_news_id provide traceability to raw news.
    """

    __tablename__ = "NewsSemanticDedup"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_snippet: Mapped[Optional[str]] = mapped_column(String(500))
    event_signature: Mapped[Optional[str]] = mapped_column(String(80))
    event_key: Mapped[Optional[str]] = mapped_column(String(500))
    embedding: Mapped[Optional[list]] = mapped_column(
        JSON, server_default=text("'[]'::json"), comment="Embedding stored as JSON array"
    )
    similarity_hint: Mapped[Optional[float]] = mapped_column(Float)
    source: Mapped[Optional[str]] = mapped_column(String(100))
    source_link: Mapped[Optional[str]] = mapped_column(String(500))
    crypto_news_id: Mapped[Optional[int]] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

    __table_args__ = (
        Index("idx_news_semantic_dedup_timestamp", "timestamp"),
        Index("idx_news_semantic_dedup_signature", "event_signature"),
        Index("idx_news_semantic_dedup_key", "event_key"),
        Index("idx_news_semantic_dedup_source_link", "source_link"),
        Index("idx_news_semantic_dedup_crypto_news_id", "crypto_news_id"),
    )
