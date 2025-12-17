"""
AIAnalysisResult 模型：统一存储来自各渠道的 AI 分析结果。
"""

from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import (
    Integer, String, Float, Boolean, DateTime, Index, UniqueConstraint, func, text
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class AIAnalysisResult(Base):
    """
    AIAnalysisResult SQLAlchemy 模型，对应 Prisma ``AIAnalysisResult`` 表。

    用于存储 Twitter/新闻/Telegram 等渠道的 AI 分析结果，包含内容要素、情绪与市场影响、
    结构化事件信息以及通知状态等字段，便于后续查询和聚合。
    """

    __tablename__ = "AIAnalysisResult"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # === Source Information ===
    source_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Source type: twitter, news, telegram, discord"
    )
    source_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Original data ID: tweet_id, news_id, etc."
    )
    source_link: Mapped[Optional[str]] = mapped_column(
        String,
        comment="Original content URL"
    )

    # === Content Information ===
    content_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Content type: tweet, news_article, telegram_message"
    )
    content_text: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Original text content (for reference)"
    )
    author: Mapped[Optional[str]] = mapped_column(
        String,
        comment="Author/username"
    )
    author_group: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="User group: KOL, exchange, whale"
    )

    # === Token Recognition (JSONB) ===
    tokens: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json"),
        comment='Identified tokens: [{symbol, name, chain, coingecko_id}]'
    )

    # === Sentiment Analysis (Common) ===
    sentiment: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="Sentiment: positive, negative, neutral"
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Confidence score 0.0-1.0"
    )
    summary: Mapped[Optional[str]] = mapped_column(
        String,
        comment="AI-generated summary"
    )
    reasoning: Mapped[Optional[str]] = mapped_column(
        String,
        comment="AI reasoning"
    )
    key_points: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json"),
        comment="Key points list"
    )

    # === Classification / Impact ===
    importance_score: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Importance score 0-10"
    )
    market_impact_label: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="Market impact: bullish, bearish, neutral"
    )
    market_impact_score: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Market impact intensity 0-1"
    )
    event_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="Event type: bullish_event, bearish_event, fud, fomo, neutral_report"
    )
    event_key: Mapped[Optional[str]] = mapped_column(
        String(512),
        comment="Structured event key (actor+action+asset+scenario+time_bucket)"
    )
    thread_id: Mapped[Optional[str]] = mapped_column(
        String(512),
        comment="Event thread identifier for progression narratives"
    )
    scenario: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="Scenario classification (e.g., onchain_whale/security_incident)"
    )
    actor: Mapped[Optional[str]] = mapped_column(
        String(200),
        comment="Main actor/entity driving the event"
    )
    actor_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="Normalized actor role"
    )
    action_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="Normalized action type"
    )
    magnitude_value: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Event magnitude numeric value"
    )
    magnitude_unit: Mapped[Optional[str]] = mapped_column(
        String(30),
        comment="Event magnitude unit (USD/TOKEN_UNITS/PERCENT/...)"
    )
    event_struct: Mapped[Optional[dict]] = mapped_column(
        JSON,
        server_default=text("'{}'::json"),
        comment="Full structured event payload"
    )
    duplicate_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="Dedup type: none | semantic | multi_source"
    )
    canonical_event_id: Mapped[Optional[str]] = mapped_column(
        String(80),
        comment="Pointer to canonical event for coverage merging"
    )
    coverage_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        server_default=text("1"),
        comment="Number of coverages aggregated into this record"
    )
    coverage_sources: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json"),
        comment="Distinct sources contributing to the coverage"
    )

    # === Scoring & Decision Context ===
    decision_score: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Unified decision score (0-1) used by filter/push"
    )
    score_breakdown: Mapped[Optional[dict]] = mapped_column(
        JSON,
        server_default=text("'{}'::json"),
        comment="Score breakdown for importance score"
    )
    filter_context: Mapped[Optional[dict]] = mapped_column(
        JSON,
        server_default=text("'{}'::json"),
        comment="Filtering thresholds and reasons"
    )
    final_signal: Mapped[Optional[dict]] = mapped_column(
        JSON,
        server_default=text("'{}'::json"),
        comment="Final orchestrated signal payload"
    )
    trading_recommendation: Mapped[Optional[dict]] = mapped_column(
        JSON,
        server_default=text("'{}'::json"),
        comment="Full trading recommendation payload"
    )
    event_factors: Mapped[Optional[dict]] = mapped_column(
        JSON,
        server_default=text("'{}'::json"),
        comment="Parsed event factors from semantic parser"
    )
    macro_implied_tokens: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json"),
        comment="Implied tokens for macro topics"
    )
    notification_priority: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="Notification priority: critical/high/medium/low"
    )
    duplicate_reason: Mapped[Optional[str]] = mapped_column(
        String(200),
        comment="Dedup reason when filtered"
    )
    similar_ids: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json"),
        comment="Matched source IDs when dedup triggered"
    )

    # === Notification Management ===
    should_notify: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        comment="Whether to send notification"
    )
    notified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        comment="Actual notification time"
    )
    notification_sent: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        comment="Notification sent status"
    )

    # === Metadata ===
    model_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="AI model used (e.g., 'deepseek/deepseek-v3.2-exp')"
    )
    analysis_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="Analysis version (for tracking model iterations)"
    )

    # === Timestamps ===
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
        # Unique constraint: prevent duplicate analysis
        UniqueConstraint('source_type', 'source_id', name='unique_analysis_source'),

        # Regular indexes
        Index('idx_analysis_source_type_id', 'source_type', 'source_id'),
        Index('idx_analysis_created_at', 'created_at'),
        Index('idx_analysis_notify_pending', 'should_notify', 'notified_at'),
        Index('idx_analysis_sentiment', 'sentiment'),
        Index('idx_analysis_author', 'author'),
        Index('idx_analysis_event_key', 'event_key'),
        Index('idx_analysis_thread_id', 'thread_id'),
        Index('idx_analysis_canonical_event_id', 'canonical_event_id'),
        Index('idx_analysis_scenario', 'scenario'),

        # GIN indexes for JSONB fields
        Index('idx_analysis_tokens_gin', 'tokens', postgresql_using='gin'),
        Index('idx_analysis_key_points_gin', 'key_points', postgresql_using='gin'),

        {'schema': 'public'}
    )

    def __repr__(self):
        return (
            f"<AIAnalysisResult(id={self.id}, "
            f"type={self.source_type}, "
            f"sentiment={self.sentiment})>"
        )

    @property
    def importance_level(self) -> Optional[str]:
        """根据 ``importance_score`` 派生的重要性等级，兼容旧逻辑。"""
        score = self.importance_score
        if score is None:
            return None
        if score >= 8:
            return "critical"
        if score >= 5:
            return "high"
        if score >= 3:
            return "medium"
        return "low"

    def to_dict(self) -> dict:
        """将模型转换为字典，便于序列化。"""
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "source_link": self.source_link,
            "content_type": self.content_type,
            "content_text": self.content_text,
            "author": self.author,
            "author_group": self.author_group,
            "tokens": self.tokens or [],
            "sentiment": self.sentiment,
            "confidence": self.confidence,
            "summary": self.summary,
            "reasoning": self.reasoning,
            "key_points": self.key_points or [],
            "importance_score": self.importance_score,
            "decision_score": self.decision_score,
            "market_impact_label": self.market_impact_label,
            "market_impact_score": self.market_impact_score,
            "event_type": self.event_type,
            "event_key": self.event_key,
            "thread_id": self.thread_id,
            "scenario": self.scenario,
            "actor": self.actor,
            "actor_type": self.actor_type,
            "action_type": self.action_type,
            "magnitude_value": self.magnitude_value,
            "magnitude_unit": self.magnitude_unit,
            "event_struct": self.event_struct or {},
            "duplicate_type": self.duplicate_type,
            "canonical_event_id": self.canonical_event_id,
            "coverage_count": self.coverage_count,
            "coverage_sources": self.coverage_sources or [],
            "score_breakdown": self.score_breakdown,
            "filter_context": self.filter_context,
            "final_signal": self.final_signal,
            "trading_recommendation": self.trading_recommendation,
            "event_factors": self.event_factors,
            "macro_implied_tokens": self.macro_implied_tokens or [],
            "notification_priority": self.notification_priority,
            "duplicate_reason": self.duplicate_reason,
            "similar_ids": self.similar_ids or [],
            "should_notify": self.should_notify,
            "notified_at": self.notified_at.isoformat() if self.notified_at else None,
            "notification_sent": self.notification_sent,
            "model_name": self.model_name,
            "analysis_version": self.analysis_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_token_symbols(self) -> List[str]:
        """
        从 ``tokens`` 字段提取代币符号列表。

        Returns:
            代币符号组成的列表。
        """
        if not self.tokens:
            return []
        return [t.get('symbol') for t in self.tokens if isinstance(t, dict) and 'symbol' in t]

    def has_token(self, symbol: str) -> bool:
        """
        判断分析结果是否提及指定代币。

        Args:
            symbol: 要检测的代币符号。

        Returns:
            当提及该代币时返回 True。
        """
        return symbol.upper() in [s.upper() for s in self.get_token_symbols()]

    def is_high_confidence(self, threshold: float = 0.7) -> bool:
        """
        判断分析结果的置信度是否高于阈值。

        Args:
            threshold: 置信度阈值（默认 0.7）。

        Returns:
            当置信度大于等于阈值时返回 True。
        """
        return self.confidence is not None and self.confidence >= threshold

    def is_high_importance(self) -> bool:
        """
        判断是否被标记为高重要性。

        Returns:
            importance_score 达到高重要性阈值时返回 True。
        """
        return (self.importance_score or 0.0) >= 5.0
