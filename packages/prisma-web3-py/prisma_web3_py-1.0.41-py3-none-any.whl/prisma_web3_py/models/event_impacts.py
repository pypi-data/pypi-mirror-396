"""EventImpacts ORM 模型。

该模块定义事件收益归因（EventImpacts）表的 SQLAlchemy 映射，
用于跟踪单个事件在多个时间窗口下的价格表现，服务于通知效果评估与策略迭代。
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    String,
    Numeric,
    DateTime,
    Index,
    Integer,
    text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from ..base import Base


class EventImpacts(Base):
    """事件收益归因模型。

    该模型用于记录单条事件在若干时间窗口下的价格快照与涨跌幅，
    目前支持的窗口包括 t0、5 分钟、15 分钟、1 小时与 4 小时，历史上保留了 30 分钟与 24 小时字段。

    对应数据库表：``EventImpacts``。
    """

    __tablename__ = "EventImpacts"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="Primary key UUID"
    )

    # === Source Information ===
    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="事件来源：news、twitter、manual 等",
    )
    source_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="原始来源标识（例如 CryptoNews.id 或外部事件 ID）",
    )
    analysis_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="关联的 AIAnalysisResult 主键 ID（可选）",
    )

    # === Token & Priority ===
    symbol: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="主监控代币符号（大写）",
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="事件优先级：critical、high、medium、low",
    )

    # === Snapshot Configuration ===
    snapshot_config: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        server_default=text("'{}'::jsonb"),
        comment='采样窗口配置，例如 {"t0": "event_time", "t5m": 300, "t15m": 900, "t1h": 3600, "t4h": 14400}',
    )

    # === Price Snapshots ===
    price_t0: Mapped[Optional[float]] = mapped_column(
        Numeric(20, 8),
        comment="事件发生时刻（t0）的价格",
    )
    price_5m: Mapped[Optional[float]] = mapped_column(
        Numeric(20, 8),
        comment="事件发生后 5 分钟的价格",
    )
    price_15m: Mapped[Optional[float]] = mapped_column(
        Numeric(20, 8),
        comment="事件发生后 15 分钟的价格",
    )
    price_1h: Mapped[Optional[float]] = mapped_column(
        Numeric(20, 8),
        comment="事件发生后 1 小时的价格",
    )
    price_4h: Mapped[Optional[float]] = mapped_column(
        Numeric(20, 8),
        comment="事件发生后 4 小时的价格",
    )

    # === Price Changes (Percentage) ===
    change_5m: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 4),
        comment="5 分钟窗口相对 t0 的收益率：(price_5m - price_t0) / price_t0",
    )
    change_15m: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 4),
        comment="15 分钟窗口相对 t0 的收益率：(price_15m - price_t0) / price_t0",
    )
    change_1h: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 4),
        comment="1 小时窗口相对 t0 的收益率",
    )
    change_4h: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 4),
        comment="4 小时窗口相对 t0 的收益率",
    )
    # === Volatility (Optional) ===
    # 早期的 30 分钟波动度字段已移除，保持轻量

    # === Additional Context ===
    meta: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        server_default=text("'{}'::jsonb"),
        comment="附加上下文字段，例如 filter_context、trading_recommendation 摘要等",
    )

    # === Timestamps ===
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="记录创建时间",
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now(),
        comment="记录更新时间",
    )

    # === Table constraints and indexes ===
    __table_args__ = (
        # Index for source lookup
        Index('idx_event_impact_source', 'source_type', 'source_id'),
        Index('idx_event_impact_analysis_id', 'analysis_id'),
        # Index for time-based queries
        Index('idx_event_impact_created_at', 'created_at'),
        # Index for priority filtering
        Index('idx_event_impact_priority', 'priority'),
        # Index for symbol lookup
        Index('idx_event_impact_symbol', 'symbol'),
        # Composite index for priority reports
        Index('idx_event_impact_priority_time', 'priority', 'created_at'),
        # GIN index for JSONB meta field
        Index('idx_event_impact_meta_gin', 'meta', postgresql_using='gin'),

        {'schema': 'public'}
    )

    def __repr__(self):
        return (
            f"<EventImpact(id={self.id}, "
            f"symbol={self.symbol}, "
            f"priority={self.priority}, "
            f"change_15m={self.change_15m})>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """将 ORM 实例转换为普通字典。

        Returns:
            包含主要字段的字典表示，便于日志与调试。
        """
        return {
            "id": str(self.id),
            "source_type": self.source_type,
            "source_id": self.source_id,
            "analysis_id": self.analysis_id,
            "symbol": self.symbol,
            "priority": self.priority,
            "snapshot_config": self.snapshot_config or {},
            "price_t0": float(self.price_t0) if self.price_t0 is not None else None,
            "price_5m": float(self.price_5m) if self.price_5m is not None else None,
            "price_15m": float(self.price_15m) if self.price_15m is not None else None,
            "price_1h": float(self.price_1h) if self.price_1h is not None else None,
            "price_4h": float(self.price_4h) if self.price_4h is not None else None,
            "change_5m": float(self.change_5m) if self.change_5m is not None else None,
            "change_15m": float(self.change_15m) if self.change_15m is not None else None,
            "change_1h": float(self.change_1h) if self.change_1h is not None else None,
            "change_4h": float(self.change_4h) if self.change_4h is not None else None,
            "meta": self.meta or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def calculate_change(self, price_current: float, price_base: Optional[float] = None) -> Optional[float]:
        """计算相对于基准价格的涨跌幅。

        Args:
            price_current: 当前价格。
            price_base: 基准价格，缺省为 ``price_t0``。

        Returns:
            涨跌幅百分比（例如 0.05 表示 +5%），若无法计算则返回 ``None``。
        """
        if price_base is None:
            price_base = self.price_t0

        if price_base is None or price_base == 0:
            return None

        return float((price_current - float(price_base)) / float(price_base))

    def is_positive_impact(self, threshold: float = 0.05) -> bool:
        """判断事件是否产生正向价格影响。

        Args:
            threshold: 最小涨幅阈值（默认 5%）。

        Returns:
            任一窗口的收益率高于阈值时返回 ``True``。
        """
        changes = [
            self.change_5m,
            self.change_15m,
            self.change_1h,
            self.change_4h,
        ]
        return any(c is not None and float(c) > threshold for c in changes)

    def is_negative_impact(self, threshold: float = -0.05) -> bool:
        """判断事件是否产生负向价格影响。

        Args:
            threshold: 最大跌幅阈值（默认 -5%）。

        Returns:
            任一窗口的收益率低于阈值时返回 ``True``。
        """
        changes = [
            self.change_15m,
            self.change_1h,
            self.change_4h,
        ]
        return any(c is not None and float(c) < threshold for c in changes)

    def get_max_impact(self) -> Optional[float]:
        """获取所有窗口中绝对值最大的收益率。

        Returns:
            最大绝对涨跌幅，若均为空则返回 ``None``。
        """
        changes = [
            abs(float(c))
            for c in [
                self.change_15m,
                self.change_1h,
                self.change_4h,
            ]
            if c is not None
        ]
        return max(changes) if changes else None

    def has_complete_snapshot(self) -> bool:
        """检查主要价格快照是否已全部补齐。

        当前主要窗口为 t0、15 分钟、1 小时与 4 小时。

        Returns:
            当以上窗口均有价格时返回 ``True``。
        """
        return all(
            [
                self.price_t0 is not None,
                self.price_15m is not None,
                self.price_1h is not None,
                self.price_4h is not None,
            ]
        )
