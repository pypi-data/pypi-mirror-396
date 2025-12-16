"""
CryptoNews model - represents cryptocurrency news and articles from various sources.
"""

from datetime import datetime
from typing import Optional, List, Dict
import hashlib
from sqlalchemy import (
    Integer, String, Text, Float, DateTime, Index, UniqueConstraint, func, text
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class CryptoNews(Base):
    """
    CryptoNews model representing cryptocurrency news articles and updates.

    This model stores news from various sources with matched cryptocurrencies,
    stocks, and extracted entities.

    Corresponds to Prisma model: CryptoNews
    Table: CryptoNews
    """

    __tablename__ = "CryptoNews"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # === Basic information ===
    title: Mapped[str] = mapped_column(String, nullable=False, comment="News title")
    category: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="News category (1=exchange, 2=project, etc.)"
    )
    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Source name (TechFlow, ChainCatcher, etc.)"
    )
    source_link: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Original news URL"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="Full news content")
    sector: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="Industry sector (Bitcoin, DeFi, NFT, etc.)"
    )

    # === Deduplication ===
    content_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        comment="SHA256 hash of content for deduplication"
    )

    # === Matched entities (JSONB for flexibility) ===
    matched_currencies: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json"),
        comment='Matched cryptocurrencies: [{"name": "BTC"}, ...]'
    )
    matched_stocks: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json"),
        comment='Matched stocks: [{"name": "TSLA"}, ...]'
    )
    entity_list: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json"),
        comment='Extracted entities: ["OKX", "SEI", ...]'
    )

    # === Additional metadata ===
    tags: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json"),
        comment="Custom tags for categorization"
    )

    # === Timestamps ===
    news_created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        comment="Original news publish time"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="Record creation time"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now(),
        comment="Record update time"
    )

    # === Table constraints and indexes ===
    __table_args__ = (
        # Unique constraint: prevent duplicate imports by URL
        UniqueConstraint('source', 'source_link', name='unique_news_source_link'),

        # Regular indexes
        Index('idx_news_source', 'source'),
        Index('idx_news_sector', 'sector'),
        Index('idx_news_category', 'category'),
        Index('idx_news_created_at', 'news_created_at'),
        Index('idx_news_record_created_at', 'created_at'),
        Index('idx_news_content_hash', 'content_hash'),
        Index('idx_news_time_source', 'news_created_at', 'source'),

        # GIN indexes for JSONB fields
        Index('idx_news_currencies_gin', 'matched_currencies', postgresql_using='gin'),
        Index('idx_news_stocks_gin', 'matched_stocks', postgresql_using='gin'),
        Index('idx_news_entities_gin', 'entity_list', postgresql_using='gin'),
        Index('idx_news_tags_gin', 'tags', postgresql_using='gin'),

        {'schema': 'public'}
    )

    def __repr__(self):
        return f"<CryptoNews(id={self.id}, title={self.title[:50]}..., source={self.source})>"

    @staticmethod
    def generate_content_hash(content: str) -> str:
        """
        Generate SHA256 hash of content for deduplication.

        Args:
            content: News content string

        Returns:
            SHA256 hash as hex string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "source": self.source,
            "source_link": self.source_link,
            "content": self.content,
            "sector": self.sector,
            "content_hash": self.content_hash,
            "matched_currencies": self.matched_currencies or [],
            "matched_stocks": self.matched_stocks or [],
            "entity_list": self.entity_list or [],
            "tags": self.tags or [],
            "news_created_at": self.news_created_at.isoformat() if self.news_created_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_currency_names(self) -> List[str]:
        """
        Get list of matched cryptocurrency names.

        Returns:
            List of currency names (symbols)
        """
        if not self.matched_currencies:
            return []
        return [c.get('name') for c in self.matched_currencies if isinstance(c, dict) and 'name' in c]

    def get_stock_names(self) -> List[str]:
        """
        Get list of matched stock names.

        Returns:
            List of stock names
        """
        if not self.matched_stocks:
            return []
        return [s.get('name') for s in self.matched_stocks if isinstance(s, dict) and 'name' in s]

    def has_currency(self, currency_name: str) -> bool:
        """
        Check if news mentions a specific cryptocurrency.

        Args:
            currency_name: Currency symbol/name to check

        Returns:
            True if currency is mentioned
        """
        return currency_name.upper() in [c.upper() for c in self.get_currency_names()]

    def has_entity(self, entity_name: str) -> bool:
        """
        Check if news mentions a specific entity.

        Args:
            entity_name: Entity name to check

        Returns:
            True if entity is mentioned
        """
        if not self.entity_list:
            return False
        return entity_name.lower() in [e.lower() for e in self.entity_list if isinstance(e, str)]
