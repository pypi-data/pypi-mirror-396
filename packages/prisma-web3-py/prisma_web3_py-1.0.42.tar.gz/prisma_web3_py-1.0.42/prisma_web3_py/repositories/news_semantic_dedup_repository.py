"""
Repository for NewsSemanticDedup entries (semantic + structured dedup for news).
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Sequence

from sqlalchemy import select, desc
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .base_repository import BaseRepository
from ..models import NewsSemanticDedup


class NewsSemanticDedupRepository(BaseRepository[NewsSemanticDedup]):
    """
    Provide upsert + recent query helpers for semantic dedup entries.
    """

    def __init__(self):
        super().__init__(NewsSemanticDedup)

    async def upsert_entry(
        self,
        session: AsyncSession,
        *,
        id: str,
        title: str,
        content_snippet: Optional[str],
        embedding: Sequence[float] | None,
        event_signature: Optional[str],
        event_key: Optional[str],
        timestamp: datetime,
        source: Optional[str] = None,
        similarity_hint: Optional[float] = None,
        source_link: Optional[str] = None,
        crypto_news_id: Optional[int] = None,
    ) -> NewsSemanticDedup:
        """
        Insert or update a dedup entry by id.
        """
        stmt = insert(NewsSemanticDedup).values(
            id=id,
            title=title,
            content_snippet=content_snippet,
            embedding=list(embedding) if embedding is not None else None,
            event_signature=event_signature,
            event_key=event_key,
            timestamp=timestamp,
            source=source,
            similarity_hint=similarity_hint,
            source_link=source_link,
            crypto_news_id=crypto_news_id,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[NewsSemanticDedup.id],
            set_={
                "title": stmt.excluded.title,
                "content_snippet": stmt.excluded.content_snippet,
                "embedding": stmt.excluded.embedding,
                "event_signature": stmt.excluded.event_signature,
                "event_key": stmt.excluded.event_key,
                "timestamp": stmt.excluded.timestamp,
                "source": stmt.excluded.source,
                "similarity_hint": stmt.excluded.similarity_hint,
                "source_link": stmt.excluded.source_link,
                "crypto_news_id": stmt.excluded.crypto_news_id,
            },
        ).returning(NewsSemanticDedup)
        result = await session.execute(
            stmt.execution_options(populate_existing=True)
        )
        entry = result.scalar_one()
        # 确保数据库与当前对象一致；若 RETURNING 未覆盖旧值则强制更新一次
        if entry.timestamp != timestamp or (embedding is not None and entry.embedding != list(embedding)):
            await session.execute(
                select(NewsSemanticDedup)
                .where(NewsSemanticDedup.id == id)
                .with_for_update()
            )
            entry.timestamp = timestamp
            entry.embedding = list(embedding) if embedding is not None else None
            entry.title = title
            entry.content_snippet = content_snippet
            entry.event_signature = event_signature
            entry.event_key = event_key
            entry.source = source
            entry.similarity_hint = similarity_hint
            entry.source_link = source_link
            entry.crypto_news_id = crypto_news_id

        # 防止 identity map 持有旧值，强制刷新关键字段
        await session.flush()
        await session.refresh(entry)
        return entry

    async def query_recent(
        self,
        session: AsyncSession,
        *,
        hours: int = 24,
        limit: int = 200,
        event_signature: Optional[str] = None,
    ) -> List[NewsSemanticDedup]:
        """
        Fetch recent entries within the time window, optionally filtered by signature.
        Results ordered by timestamp desc.
        """
        if hours <= 0:
            return []

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        conditions = [NewsSemanticDedup.timestamp >= cutoff]
        if event_signature:
            conditions.append(NewsSemanticDedup.event_signature == event_signature)

        stmt = (
            select(NewsSemanticDedup)
            .where(*conditions)
            .order_by(desc(NewsSemanticDedup.timestamp))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
