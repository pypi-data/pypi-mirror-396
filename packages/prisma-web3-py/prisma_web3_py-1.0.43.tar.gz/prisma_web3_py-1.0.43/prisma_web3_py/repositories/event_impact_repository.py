"""EventImpacts 仓储封装。

该模块提供对事件收益归因（EventImpacts）表的增删改查接口，
用于创建事件价格快照、回填多时间窗口价格以及生成简单统计视图。

注意：
EventImpacts.created_at 在 Postgres 中通常是 ``timestamp without time zone``，
若数据库时区非 UTC，直接用 ``datetime.utcnow()`` 推导阈值会导致窗口判断整体偏移，
从而出现 5m/15m/1h/4h 回填任务长期“无可更新记录”的假象。
因此本仓储在做时间阈值过滤时，优先使用数据库的 ``now()`` 作为基准时间。
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import uuid

from ..models.event_impacts import EventImpacts
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class EventImpactRepository(BaseRepository[EventImpacts]):
    """EventImpacts 仓储类。

    封装创建、更新与查询事件收益归因记录的常用操作，
    方便在应用层统一维护事件价格表现（t0/多窗口涨跌幅）。
    """

    def __init__(self):
        super().__init__(EventImpacts)

    # ========== CREATE METHODS ==========

    async def create_snapshot(
        self,
        session: AsyncSession,
        source_type: str,
        source_id: str,
        symbol: str,
        priority: str = 'medium',
        snapshot_config: Optional[Dict] = None,
        prices: Optional[Dict[str, float]] = None,
        meta: Optional[Dict] = None,
        analysis_id: Optional[int] = None,
    ) -> Optional[EventImpacts]:
        """创建一条新的事件收益快照。

        Args:
            session: 异步数据库会话。
            source_type: 事件来源类型，例如 ``\"news\"``、``\"twitter\"``。
            source_id: 原始来源标识（如新闻 ID、推文 ID）。
            symbol: 监控的代币符号，会统一转为大写。
            priority: 事件优先级（``critical``/``high``/``medium``/``low``）。
            snapshot_config: 采样窗口配置，缺省使用 15m/1h/4h。
            prices: 初始价格字典，如 ``{\"t0\": 1.0, \"15m\": 1.05}``。
            meta: 附加上下文信息（filter_context、trading_recommendation 等）。
            analysis_id: 关联的 ``AIAnalysisResult.id``，用于统一事件维度 join。

        Returns:
            新创建的 ``EventImpacts`` 实例，若创建失败则返回 ``None``。
        """
        if snapshot_config is None:
            snapshot_config = {
                "t0": "event_time",
                "t5m": 300,    # 5 minutes
                "t15m": 900,   # 15 minutes
                "t1h": 3600,   # 1 hour
                "t4h": 14400,  # 4 hours
            }

        if prices is None:
            prices = {}

        if meta is None:
            meta = {}

        # Normalize symbol to uppercase
        normalized_symbol = symbol.strip().upper()

        # Calculate changes if we have prices
        price_t0 = prices.get('t0')
        price_5m = prices.get('5m')
        price_15m = prices.get('15m')
        price_1h = prices.get('1h')
        price_4h = prices.get('4h')

        change_5m = None
        change_15m = None
        change_1h = None
        change_4h = None

        if price_t0 is not None and price_t0 > 0:
            base = float(price_t0)

            def _pct(p: Optional[float]) -> Optional[float]:
                if p is None:
                    return None
                return (float(p) - base) / base

            change_5m = _pct(price_5m)
            change_15m = _pct(price_15m)
            change_1h = _pct(price_1h)
            change_4h = _pct(price_4h)

        impact = EventImpacts(
            source_type=source_type,
            source_id=source_id,
            analysis_id=analysis_id,
            symbol=normalized_symbol,
            priority=priority,
            snapshot_config=snapshot_config,
            price_t0=price_t0,
            price_5m=price_5m,
            price_15m=price_15m,
            price_1h=price_1h,
            price_4h=price_4h,
            change_5m=change_5m,
            change_15m=change_15m,
            change_1h=change_1h,
            change_4h=change_4h,
            meta=meta
        )

        session.add(impact)
        await session.flush()
        await session.refresh(impact)
        logger.debug(f"Created event impact: ID={impact.id}, symbol={symbol}, priority={priority}")
        return impact

    # ========== UPDATE METHODS ==========

    async def update_snapshot(
        self,
        session: AsyncSession,
        impact_id: uuid.UUID,
        new_prices: Dict[str, float],
        recalculate: bool = True
    ) -> Optional[EventImpacts]:
        """更新指定事件的价格快照。

        通常由定时任务在窗口时间到达后调用，用于回填 15 分钟、1 小时或 4 小时价格。

        Args:
            session: 异步数据库会话。
            impact_id: ``EventImpacts.id`` 主键 UUID。
            new_prices: 新价格字典，例如 ``{\"15m\": 1.02, \"1h\": 1.05}``。
            recalculate: 是否在写入价格后重新计算收益率字段。

        Returns:
            更新后的 ``EventImpacts`` 实例，若记录不存在则返回 ``None``。
        """
        stmt = select(EventImpacts).where(EventImpacts.id == impact_id)
        result = await session.execute(stmt)
        impact = result.scalar_one_or_none()

        if not impact:
            logger.warning(f"Event impact not found: {impact_id}")
            return None

        # Update prices
        if '5m' in new_prices:
            impact.price_5m = new_prices['5m']
        if '15m' in new_prices:
            impact.price_15m = new_prices['15m']
        if '1h' in new_prices:
            impact.price_1h = new_prices['1h']
        if '4h' in new_prices:
            impact.price_4h = new_prices['4h']

        # Recalculate changes
        if recalculate and impact.price_t0 is not None and impact.price_t0 > 0:
            base = float(impact.price_t0)

            def _recalc(current: Optional[float]) -> Optional[float]:
                if current is None:
                    return None
                return (float(current) - base) / base

            if impact.price_5m is not None:
                impact.change_5m = _recalc(float(impact.price_5m))
            if impact.price_15m is not None:
                impact.change_15m = _recalc(float(impact.price_15m))
            if impact.price_1h is not None:
                impact.change_1h = _recalc(float(impact.price_1h))
            if impact.price_4h is not None:
                impact.change_4h = _recalc(float(impact.price_4h))

        await session.flush()
        await session.refresh(impact)
        logger.debug(f"Updated event impact: ID={impact_id}")
        return impact

    async def update_meta(
        self,
        session: AsyncSession,
        impact_id: uuid.UUID,
        meta_update: Dict[str, Any]
    ) -> bool:
        """
        Update meta field of an event impact.

        Args:
            session: Database session
            impact_id: EventImpacts UUID
            meta_update: Dict to merge into meta field

        Returns:
            Success status
        """
        stmt = select(EventImpacts).where(EventImpacts.id == impact_id)
        result = await session.execute(stmt)
        impact = result.scalar_one_or_none()

        if not impact:
            return False

        # Merge meta
        current_meta = impact.meta or {}
        current_meta.update(meta_update)
        impact.meta = current_meta

        await session.flush()
        logger.debug(f"Updated event impact meta: ID={impact_id}")
        return True

    # ========== QUERY METHODS ==========

    async def get_by_id(
        self,
        session: AsyncSession,
        impact_id: uuid.UUID
    ) -> Optional[EventImpacts]:
        """
        Get event impact by UUID.

        Args:
            session: Database session
            impact_id: EventImpacts UUID

        Returns:
            EventImpacts or None
        """
        stmt = select(EventImpacts).where(EventImpacts.id == impact_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_source(
        self,
        session: AsyncSession,
        source_type: str,
        source_id: str
    ) -> Optional[EventImpacts]:
        """
        Get event impact by source reference.

        Args:
            session: Database session
            source_type: Source type ('news', 'twitter', 'manual')
            source_id: Source ID

        Returns:
            EventImpacts or None
        """
        stmt = select(EventImpacts).where(
            and_(
                EventImpacts.source_type == source_type,
                EventImpacts.source_id == source_id
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_priority(
        self,
        session: AsyncSession,
        priority: str,
        begin: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100
    ) -> List[EventImpacts]:
        """
        List event impacts by priority within a time range.

        Used for generating priority-based reports.

        Args:
            session: Database session
            priority: Priority level ('critical', 'high', 'medium', 'low')
            begin: Start time (optional)
            end: End time (optional)
            limit: Result limit

        Returns:
            List of EventImpacts
        """
        stmt = select(EventImpacts).where(EventImpacts.priority == priority)

        if begin:
            stmt = stmt.where(EventImpacts.created_at >= begin)
        if end:
            stmt = stmt.where(EventImpacts.created_at <= end)

        stmt = stmt.order_by(EventImpacts.created_at.desc()).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_symbol(
        self,
        session: AsyncSession,
        symbol: str,
        hours: Optional[int] = None,
        limit: int = 50
    ) -> List[EventImpacts]:
        """
        List event impacts for a specific token.

        Args:
            session: Database session
            symbol: Token symbol
            hours: Optional time range in hours
            limit: Result limit

        Returns:
            List of EventImpacts
        """
        normalized_symbol = symbol.strip().upper()
        stmt = select(EventImpacts).where(EventImpacts.symbol == normalized_symbol)

        if hours:
            since_expr = func.now().cast(DateTime) - timedelta(hours=hours)
            stmt = stmt.where(EventImpacts.created_at >= since_expr)

        stmt = stmt.order_by(EventImpacts.created_at.desc()).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_updates(
        self,
        session: AsyncSession,
        window: str = '4h',
        limit: int = 100
    ) -> List[EventImpacts]:
        """获取指定时间窗口内待回填价格的事件列表。

        通过检查 ``created_at`` 与目标窗口之间的时间差，并判断对应价格字段是否为空，
        找出需要补齐 5 分钟、15 分钟、1 小时或 4 小时价格的记录。

        Args:
            session: 异步数据库会话。
            window: 目标窗口标识（``"5m"``、``"15m"``、``"1h"``、``"4h"``）。
            limit: 返回的最大记录数。

        Returns:
            待更新的 ``EventImpacts`` 列表。
        """
        # Calculate time threshold based on window
        window_seconds = {
            '5m': 300,
            '15m': 900,
            '1h': 3600,
            '4h': 14400,
        }.get(window)

        if window_seconds is None:
            logger.warning("Unsupported window=%s for pending updates", window)
            return []

        # 使用 DB 的 now()，避免 created_at 存储为本地时区时与 UTC-naive 阈值错位
        threshold = func.now().cast(DateTime) - timedelta(seconds=window_seconds)

        # Build query based on window
        if window == '5m':
            stmt = select(EventImpacts).where(
                and_(
                    EventImpacts.created_at <= threshold,
                    EventImpacts.price_5m.is_(None),
                    EventImpacts.price_t0.isnot(None)
                )
            )
        elif window == '15m':
            stmt = select(EventImpacts).where(
                and_(
                    EventImpacts.created_at <= threshold,
                    EventImpacts.price_15m.is_(None),
                    EventImpacts.price_t0.isnot(None)
                )
            )
        elif window == '1h':
            stmt = select(EventImpacts).where(
                and_(
                    EventImpacts.created_at <= threshold,
                    EventImpacts.price_1h.is_(None),
                    EventImpacts.price_t0.isnot(None)
                )
            )
        elif window == '4h':
            stmt = select(EventImpacts).where(
                and_(
                    EventImpacts.created_at <= threshold,
                    EventImpacts.price_4h.is_(None),
                    EventImpacts.price_t0.isnot(None)
                )
            )
        else:
            logger.warning("Unsupported window=%s for pending updates", window)
            return []

        stmt = stmt.order_by(EventImpacts.created_at.asc()).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    # ========== STATISTICS METHODS ==========

    async def get_impact_summary(
        self,
        session: AsyncSession,
        priority: Optional[str] = None,
        hours: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get impact statistics summary.

        Args:
            session: Database session
            priority: Optional priority filter
            hours: Optional time range in hours

        Returns:
            Summary statistics dict
        """
        stmt = select(EventImpacts)

        if priority:
            stmt = stmt.where(EventImpacts.priority == priority)

        if hours:
            since_expr = func.now().cast(DateTime) - timedelta(hours=hours)
            stmt = stmt.where(EventImpacts.created_at >= since_expr)

        result = await session.execute(stmt)
        impacts = list(result.scalars().all())

        if not impacts:
            return {
                'total': 0,
                'by_priority': {},
                'by_symbol': {},
                'avg_change_5m': None,
                'avg_change_15m': None,
                'avg_change_1h': None,
                'avg_change_4h': None
            }

        # Calculate statistics
        total = len(impacts)

        # Count by priority
        by_priority = {}
        for impact in impacts:
            by_priority[impact.priority] = by_priority.get(impact.priority, 0) + 1

        # Count by symbol
        by_symbol = {}
        for impact in impacts:
            by_symbol[impact.symbol] = by_symbol.get(impact.symbol, 0) + 1

        # Average changes
        changes_5m = [float(i.change_5m) for i in impacts if i.change_5m is not None]
        changes_15m = [float(i.change_15m) for i in impacts if i.change_15m is not None]
        changes_1h = [float(i.change_1h) for i in impacts if i.change_1h is not None]
        changes_4h = [float(i.change_4h) for i in impacts if i.change_4h is not None]

        return {
            'total': total,
            'by_priority': by_priority,
            'by_symbol': by_symbol,
            'avg_change_5m': sum(changes_5m) / len(changes_5m) if changes_5m else None,
            'avg_change_15m': sum(changes_15m) / len(changes_15m) if changes_15m else None,
            'avg_change_1h': sum(changes_1h) / len(changes_1h) if changes_1h else None,
            'avg_change_4h': sum(changes_4h) / len(changes_4h) if changes_4h else None,
            'positive_5m': len([c for c in changes_5m if c > 0]),
            'negative_5m': len([c for c in changes_5m if c < 0]),
            'positive_15m': len([c for c in changes_15m if c > 0]),
            'negative_15m': len([c for c in changes_15m if c < 0]),
            'positive_1h': len([c for c in changes_1h if c > 0]),
            'negative_1h': len([c for c in changes_1h if c < 0]),
            'positive_4h': len([c for c in changes_4h if c > 0]),
            'negative_4h': len([c for c in changes_4h if c < 0]),
        }

    async def get_top_performers(
        self,
        session: AsyncSession,
        window: str = '4h',
        priority: Optional[str] = None,
        hours: Optional[int] = None,
        limit: int = 20
    ) -> List[EventImpacts]:
        """按收益率排序的“表现最佳事件”查询。

        Args:
            session: 异步数据库会话。
            window: 统计窗口（``\"5m\"``、``\"15m\"``、``\"1h\"``、``\"4h\"``）。
            priority: 可选优先级过滤条件。
            hours: 可选时间范围（小时），例如最近 24 小时。
            limit: 返回的最大事件数量。

        Returns:
            按收益率从高到低排序的事件列表。
        """
        # Select appropriate change field
        change_field = {
            '5m': EventImpacts.change_5m,
            '15m': EventImpacts.change_15m,
            '1h': EventImpacts.change_1h,
            '4h': EventImpacts.change_4h,
        }.get(window, EventImpacts.change_4h)

        stmt = select(EventImpacts).where(change_field.isnot(None))

        if priority:
            stmt = stmt.where(EventImpacts.priority == priority)

        if hours:
            since_expr = func.now().cast(DateTime) - timedelta(hours=hours)
            stmt = stmt.where(EventImpacts.created_at >= since_expr)

        stmt = stmt.order_by(change_field.desc()).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_worst_performers(
        self,
        session: AsyncSession,
        window: str = '4h',
        priority: Optional[str] = None,
        hours: Optional[int] = None,
        limit: int = 20
    ) -> List[EventImpacts]:
        """按收益率排序的“表现最差事件”查询。

        Args:
            session: 异步数据库会话。
            window: 统计窗口（``\"5m\"``、``\"15m\"``、``\"1h\"``、``\"4h\"``）。
            priority: 可选优先级过滤条件。
            hours: 可选时间范围（小时），例如最近 24 小时。
            limit: 返回的最大事件数量。

        Returns:
            按收益率从低到高排序的事件列表。
        """
        # Select appropriate change field
        change_field = {
            '5m': EventImpacts.change_5m,
            '15m': EventImpacts.change_15m,
            '1h': EventImpacts.change_1h,
            '4h': EventImpacts.change_4h,
        }.get(window, EventImpacts.change_4h)

        stmt = select(EventImpacts).where(change_field.isnot(None))

        if priority:
            stmt = stmt.where(EventImpacts.priority == priority)

        if hours:
            since_expr = func.now().cast(DateTime) - timedelta(hours=hours)
            stmt = stmt.where(EventImpacts.created_at >= since_expr)

        stmt = stmt.order_by(change_field.asc()).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())
