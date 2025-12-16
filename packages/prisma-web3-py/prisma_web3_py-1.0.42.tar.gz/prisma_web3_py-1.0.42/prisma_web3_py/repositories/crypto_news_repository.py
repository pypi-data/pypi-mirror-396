"""
CryptoNews repository with specialized query methods.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, func, or_, cast, text
from sqlalchemy.dialects.postgresql import insert, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

from prisma_web3_py.utils.datetime import utc_now_naive, to_naive_utc

from .base_repository import BaseRepository
from ..models.crypto_news import CryptoNews

logger = logging.getLogger(__name__)


class CryptoNewsRepository(BaseRepository[CryptoNews]):
    """
    Repository for CryptoNews model operations.

    Provides specialized query methods for news articles.
    """

    def __init__(self):
        super().__init__(CryptoNews)

    async def create_news(
        self,
        session: AsyncSession,
        title: str,
        category: int,
        source: str,
        content: str,
        source_link: Optional[str] = None,
        sector: Optional[str] = None,
        matched_currencies: Optional[List[dict]] = None,
        matched_stocks: Optional[List[dict]] = None,
        entity_list: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        news_created_at: Optional[datetime] = None
    ) -> Optional[CryptoNews]:
        """
        Create a new crypto news article.

        Automatically generates content_hash for deduplication.

        Args:
            session: Database session
            title: News title
            category: News category
            source: Source name
            content: News content
            source_link: Original URL
            sector: Industry sector
            matched_currencies: List of matched cryptocurrencies
            matched_stocks: List of matched stocks
            entity_list: List of extracted entities
            tags: Custom tags
            news_created_at: Original publish time

        Returns:
            Created CryptoNews instance or None if failed

        Raises:
            IntegrityError: If duplicate (source, source_link) is detected
        """
        try:
            # Generate content hash for deduplication
            content_hash = CryptoNews.generate_content_hash(content)

            news = await self.create(
                session,
                title=title,
                category=category,
                source=source,
                content=content,
                content_hash=content_hash,
                source_link=source_link,
                sector=sector,
                matched_currencies=matched_currencies or [],
                matched_stocks=matched_stocks or [],
                entity_list=entity_list or [],
                tags=tags or [],
                news_created_at=to_naive_utc(news_created_at)
            )
            logger.debug(f"Created CryptoNews with ID: {news.id if news else None}")
            return news
        except IntegrityError as e:
            logger.warning(f"Duplicate news detected: {source} - {source_link}: {e}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error creating crypto news: {e}")
            raise

    async def upsert_news(
        self,
        session: AsyncSession,
        title: str,
        category: int,
        source: str,
        content: str,
        source_link: Optional[str] = None,
        sector: Optional[str] = None,
        matched_currencies: Optional[List[dict]] = None,
        matched_stocks: Optional[List[dict]] = None,
        entity_list: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        news_created_at: Optional[datetime] = None
    ) -> Optional[CryptoNews]:
        """
        Insert or update crypto news article.

        Uses PostgreSQL UPSERT (ON CONFLICT DO UPDATE) to handle duplicates.
        Duplicate detection is based on (source, source_link) unique constraint.

        Args:
            session: Database session
            title: News title
            category: News category
            source: Source name
            content: News content
            source_link: Original URL
            sector: Industry sector
            matched_currencies: List of matched cryptocurrencies
            matched_stocks: List of matched stocks
            entity_list: List of extracted entities
            tags: Custom tags
            news_created_at: Original publish time

        Returns:
            CryptoNews instance (created or updated) or None if failed

        Example:
            >>> news = await repo.upsert_news(
            ...     session,
            ...     title="Title",
            ...     source="TechFlow",
            ...     source_link="https://...",
            ...     content="..."
            ... )
        """
        try:
            # Generate content hash
            content_hash = CryptoNews.generate_content_hash(content)

            # Prepare upsert data
            upsert_data = {
                "title": title,
                "category": category,
                "source": source,
                "content": content,
                "content_hash": content_hash,
                "source_link": source_link,
                "sector": sector,
                "matched_currencies": matched_currencies or [],
                "matched_stocks": matched_stocks or [],
                "entity_list": entity_list or [],
                "tags": tags or [],
                "news_created_at": to_naive_utc(news_created_at),
                "updated_at": utc_now_naive(),
            }

            # Remove None values
            upsert_data = {k: v for k, v in upsert_data.items() if v is not None}

            # Execute UPSERT using PostgreSQL's ON CONFLICT.
            # Prisma creates a UNIQUE INDEX (not a named constraint) for @@unique(map: "unique_news_source_link").
            # Use index_elements so PostgreSQL matches the existing unique index.
            stmt = insert(CryptoNews).values(upsert_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=[CryptoNews.source, CryptoNews.source_link],
                set_=upsert_data
            )
            result = await session.execute(stmt)
            await session.flush()

            # Get the news ID
            if result.inserted_primary_key:
                news_id = result.inserted_primary_key[0]
                logger.debug(f"Inserted new CryptoNews with ID: {news_id}")
            else:
                # For updates, fetch the ID
                news_query = select(CryptoNews.id).where(
                    CryptoNews.source == source,
                    CryptoNews.source_link == source_link
                )
                news_result = await session.execute(news_query)
                news_id = news_result.scalar_one()
                logger.debug(f"Updated existing CryptoNews with ID: {news_id}")

            # Fetch and return the complete news object
            news = await self.get_by_id(session, news_id)
            return news

        except SQLAlchemyError as e:
            logger.error(f"Error upserting crypto news: {e}")
            raise
        
    async def upsert_twitter(
        self,
        session: AsyncSession,
        tweet_id: str,
        tweet_text: str,
        user_name: str,
        tweet_link: Optional[str] = None,
        user_group: Optional[str] = None,
        message_type: Optional[str] = None,
        matched_currencies: Optional[List[str]] = None,
        mentions: Optional[List[str]] = None,
        tweet_time: Optional[datetime] = None,
        title_hint: Optional[str] = None
    ) -> Optional[CryptoNews]:
        """
        插入或更新 Twitter 推文到 CryptoNews 表

        使用 (source, source_link) 作为唯一键进行 upsert

        Args:
            session: 数据库会话
            tweet_id: 推文 ID（从 URL 提取）
            tweet_text: 推文完整文本
            user_name: 推文作者
            tweet_link: 推文链接（用于唯一约束）
            user_group: 用户分组（如 'KOL', 'Exchange'）
            message_type: 消息类型（'reply', 'retweet', 'original' 等）
            matched_currencies: AI 识别的代币列表
            mentions: @提及的用户列表
            tweet_time: 推文发布时间
            title_hint: 用于生成标题的摘要（仅用于 UI 展示，不会单独存储）

        Returns:
            CryptoNews 对象，失败返回 None
        """
        from sqlalchemy.dialects.postgresql import insert

        try:
            # 如果没有 tweet_link，使用 tweet_id 生成一个
            if not tweet_link:
                tweet_link = f"https://x.com/{user_name}/status/{tweet_id}"

            # 构建 entity_list：作者 + 提及的用户
            entity_list = [user_name]
            if mentions:
                entity_list.extend(mentions)
            # 去重
            entity_list = list(set(entity_list))

            # 构建 tags：['twitter', user_group, message_type]
            tags = ['twitter']
            if user_group:
                tags.append(user_group.lower())
            if message_type:
                tags.append(message_type)

            # 构建 title：用户名 + 总结/推文摘要
            if title_hint:
                title = f"{user_name}: {title_hint[:100]}"
            else:
                # 如果没有总结，使用推文前100字符
                title = f"{user_name}: {tweet_text[:100]}"

            # 生成 content_hash 用于去重
            content_hash = CryptoNews.generate_content_hash(tweet_text)

            # 准备插入数据
            values = {
                'title': title,
                'content': tweet_text,
                'source': 'twitter',  # 推文作者作为来源
                'source_link': tweet_link,  # 推文链接（唯一键）
                'category': 1,  # 固定分类（可根据需要调整）
                'sector': user_group or 'Social Media',
                'matched_currencies': matched_currencies or [],
                'matched_stocks': [],  # Twitter 通常不提及股票
                'entity_list': entity_list,
                'tags': tags,
                'news_created_at': to_naive_utc(tweet_time) or utc_now_naive(),
                'content_hash': content_hash,
                'updated_at': utc_now_naive()
            }

            # PostgreSQL upsert
            stmt = insert(CryptoNews).values(**values)

            # 如果 (source, source_link) 存在，则更新
            stmt = stmt.on_conflict_do_update(
                index_elements=['source', 'source_link'],  # 唯一约束
                set_={
                    'title': stmt.excluded.title,
                    'content': stmt.excluded.content,
                    'matched_currencies': stmt.excluded.matched_currencies,
                    'entity_list': stmt.excluded.entity_list,
                    'tags': stmt.excluded.tags,
                    'updated_at': stmt.excluded.updated_at
                }
            ).returning(CryptoNews)

            result = await session.execute(stmt)
            news = result.scalar_one_or_none()

            return news

        except SQLAlchemyError as e:
            logger.error("Error in upsert_twitter: %s", e, exc_info=True)
            raise

    async def check_duplicate_by_hash(
        self,
        session: AsyncSession,
        content_hash: str
    ) -> Optional[CryptoNews]:
        """
        Check if news with same content hash already exists.

        Useful for detecting duplicate content even if source_link is different.

        Args:
            session: Database session
            content_hash: SHA256 hash of content

        Returns:
            Existing news with same hash, or None if not found

        Example:
            >>> content_hash = CryptoNews.generate_content_hash(content)
            >>> duplicate = await repo.check_duplicate_by_hash(session, content_hash)
            >>> if duplicate:
            ...     print(f"Duplicate found: {duplicate.title}")
        """
        try:
            query = select(CryptoNews).where(CryptoNews.content_hash == content_hash)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error checking duplicate by hash: {e}")
            raise

    async def get_recent_news(
        self,
        session: AsyncSession,
        hours: int = 24,
        source: Optional[str] = None,
        sector: Optional[str] = None,
        category: Optional[int] = None,
        limit: int = 100
    ) -> List[CryptoNews]:
        """
        Get recent news within time window.

        Args:
            session: Database session
            hours: Time window in hours (default: 24)
            source: Filter by source (optional)
            sector: Filter by sector (optional)
            category: Filter by category (optional)
            limit: Maximum number of results

        Returns:
            List of recent news
        """
        try:
            time_threshold = utc_now_naive() - timedelta(hours=hours)

            query = select(CryptoNews).where(
                CryptoNews.news_created_at >= time_threshold
            )

            if source:
                query = query.where(CryptoNews.source == source)

            if sector:
                query = query.where(CryptoNews.sector == sector)

            if category is not None:
                query = query.where(CryptoNews.category == category)

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent news: {e}")
            raise

    async def search_by_currency(
        self,
        session: AsyncSession,
        currency_name: str,
        hours: Optional[int] = None,
        limit: int = 50
    ) -> List[CryptoNews]:
        """
        Search news mentioning a specific cryptocurrency.

        Uses PostgreSQL JSONB @> containment operator for efficient array search.

        Args:
            session: Database session
            currency_name: Currency symbol/name to search (case-insensitive)
            hours: Time window in hours (optional)
            limit: Maximum number of results

        Returns:
            List of news mentioning the currency

        Example:
            >>> await repo.search_by_currency(session, "BTC", hours=24)
        """
        try:
            # Normalize currency name (uppercase)
            normalized_name = currency_name.strip().upper()

            # Use PostgreSQL @> operator (containment) for JSONB array search
            # This checks if matched_currencies contains an object with name = normalized_name
            query = select(CryptoNews).where(
                CryptoNews.matched_currencies.op('@>')(
                    cast([{"name": normalized_name}], JSONB)
                )
            )

            if hours is not None:
                time_threshold = utc_now_naive() - timedelta(hours=hours)
                query = query.where(CryptoNews.news_created_at >= time_threshold)

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error("Error searching news by currency '%s': %s", currency_name, e)
            raise

    async def search_by_entity(
        self,
        session: AsyncSession,
        entity_name: str,
        hours: Optional[int] = None,
        limit: int = 50
    ) -> List[CryptoNews]:
        """
        Search news mentioning a specific entity.

        Uses PostgreSQL JSONB @> containment operator for efficient array search.

        Args:
            session: Database session
            entity_name: Entity name to search (case-sensitive)
            hours: Time window in hours (optional)
            limit: Maximum number of results

        Returns:
            List of news mentioning the entity

        Example:
            >>> await repo.search_by_entity(session, "OKX", hours=24)
        """
        try:
            # Normalize entity name (strip whitespace)
            normalized_entity = entity_name.strip()

            # Use PostgreSQL @> operator (containment) for JSONB array search
            # Cast the search value to JSONB to ensure proper type matching
            query = select(CryptoNews).where(
                CryptoNews.entity_list.op('@>')(cast([normalized_entity], JSONB))
            )

            if hours is not None:
                time_threshold = utc_now_naive() - timedelta(hours=hours)
                query = query.where(CryptoNews.news_created_at >= time_threshold)

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error searching news by entity '{entity_name}': {e}")
            raise

    async def search_news(
        self,
        session: AsyncSession,
        search_term: str,
        search_in_content: bool = False,
        limit: int = 50
    ) -> List[CryptoNews]:
        """
        Search news by keyword in title (and optionally content).

        Args:
            session: Database session
            search_term: Search keyword
            search_in_content: Also search in content (slower)
            limit: Maximum number of results

        Returns:
            List of matching news
        """
        try:
            search_pattern = f"%{search_term.lower()}%"

            if search_in_content:
                query = select(CryptoNews).where(
                    or_(
                        CryptoNews.title.ilike(search_pattern),
                        CryptoNews.content.ilike(search_pattern)
                    )
                )
            else:
                query = select(CryptoNews).where(
                    CryptoNews.title.ilike(search_pattern)
                )

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error searching news: {e}")
            raise

    async def get_news_by_source(
        self,
        session: AsyncSession,
        source: str,
        hours: Optional[int] = None,
        limit: int = 100
    ) -> List[CryptoNews]:
        """
        Get news from a specific source.

        Args:
            session: Database session
            source: Source name
            hours: Time window in hours (optional)
            limit: Maximum number of results

        Returns:
            List of news from the source
        """
        try:
            query = select(CryptoNews).where(CryptoNews.source == source)

            if hours is not None:
                time_threshold = utc_now_naive() - timedelta(hours=hours)
                query = query.where(CryptoNews.news_created_at >= time_threshold)

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting news by source: {e}")
            raise

    async def get_news_by_sector(
        self,
        session: AsyncSession,
        sector: str,
        hours: Optional[int] = None,
        limit: int = 100
    ) -> List[CryptoNews]:
        """
        Get news for a specific sector.

        Args:
            session: Database session
            sector: Sector name
            hours: Time window in hours (optional)
            limit: Maximum number of results

        Returns:
            List of news for the sector
        """
        try:
            query = select(CryptoNews).where(CryptoNews.sector == sector)

            if hours is not None:
                time_threshold = utc_now_naive() - timedelta(hours=hours)
                query = query.where(CryptoNews.news_created_at >= time_threshold)

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting news by sector: {e}")
            raise

    async def get_trending_currencies(
        self,
        session: AsyncSession,
        hours: int = 24,
        limit: int = 20
    ) -> List[dict]:
        """
        Get trending cryptocurrencies based on news mentions.

        Uses PostgreSQL jsonb_array_elements to extract and count currency mentions.

        Args:
            session: Database session
            hours: Time window in hours (default: 24)
            limit: Maximum number of results (default: 20)

        Returns:
            List of dicts with currency name and mention count:
            [{"currency": "BTC", "mentions": 15}, ...]

        Example:
            >>> trending = await repo.get_trending_currencies(session, hours=24, limit=10)
            >>> print(f"Top currency: {trending[0]['currency']} with {trending[0]['mentions']} mentions")
        """
        try:
            time_threshold = utc_now_naive() - timedelta(hours=hours)

            # Use PostgreSQL function to unnest JSONB array and count occurrences
            # This is more efficient than fetching all rows and processing in Python
            query = text("""
                SELECT
                    (jsonb_array_elements(matched_currencies)->>'name') as currency_name,
                    COUNT(*) as mention_count
                FROM public."CryptoNews"
                WHERE news_created_at >= :time_threshold
                  AND matched_currencies IS NOT NULL
                  AND jsonb_typeof(matched_currencies) = 'array'
                  AND matched_currencies != '[]'::jsonb
                GROUP BY currency_name
                ORDER BY mention_count DESC
                LIMIT :limit
            """)

            result = await session.execute(
                query,
                {"time_threshold": time_threshold, "limit": limit}
            )

            trending = [
                {"currency": row[0], "mentions": row[1]}
                for row in result.fetchall()
                if row[0] is not None  # Filter out null currency names
            ]

            logger.debug(
                f"get_trending_currencies(hours={hours}): found {len(trending)} currencies"
            )
            return trending

        except SQLAlchemyError as e:
            logger.error(f"Error getting trending currencies: {e}")
            raise

    async def get_trending_entities(
        self,
        session: AsyncSession,
        hours: int = 24,
        limit: int = 20
    ) -> List[dict]:
        """
        Get trending entities based on news mentions.

        Uses PostgreSQL jsonb_array_elements to extract and count entity mentions.

        Args:
            session: Database session
            hours: Time window in hours (default: 24)
            limit: Maximum number of results (default: 20)

        Returns:
            List of dicts with entity name and mention count:
            [{"entity": "OKX", "mentions": 10}, ...]

        Example:
            >>> trending = await repo.get_trending_entities(session, hours=24, limit=10)
        """
        try:
            time_threshold = utc_now_naive() - timedelta(hours=hours)

            # Use PostgreSQL function to unnest JSONB array and count occurrences
            query = text("""
                SELECT
                    jsonb_array_elements_text(entity_list) as entity_name,
                    COUNT(*) as mention_count
                FROM public."CryptoNews"
                WHERE news_created_at >= :time_threshold
                  AND entity_list IS NOT NULL
                  AND jsonb_typeof(entity_list) = 'array'
                  AND entity_list != '[]'::jsonb
                GROUP BY entity_name
                ORDER BY mention_count DESC
                LIMIT :limit
            """)

            result = await session.execute(
                query,
                {"time_threshold": time_threshold, "limit": limit}
            )

            trending = [
                {"entity": row[0], "mentions": row[1]}
                for row in result.fetchall()
                if row[0] is not None
            ]

            logger.debug(
                f"get_trending_entities(hours={hours}): found {len(trending)} entities"
            )
            return trending

        except SQLAlchemyError as e:
            logger.error(f"Error getting trending entities: {e}")
            raise

    async def search_by_tag(
        self,
        session: AsyncSession,
        tag: str,
        hours: Optional[int] = None,
        limit: int = 50
    ) -> List[CryptoNews]:
        """
        Search news by custom tag.

        Uses PostgreSQL JSONB @> containment operator for efficient array search.

        Args:
            session: Database session
            tag: Tag to search for
            hours: Time window in hours (optional)
            limit: Maximum number of results

        Returns:
            List of news with the specified tag

        Example:
            >>> await repo.search_by_tag(session, "defi", hours=24)
        """
        try:
            # Normalize tag (lowercase)
            normalized_tag = tag.strip().lower()

            # Use PostgreSQL @> operator for JSONB array search
            query = select(CryptoNews).where(
                CryptoNews.tags.op('@>')(cast([normalized_tag], JSONB))
            )

            if hours is not None:
                time_threshold = utc_now_naive() - timedelta(hours=hours)
                query = query.where(CryptoNews.news_created_at >= time_threshold)

            query = query.order_by(CryptoNews.news_created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error searching news by tag '{tag}': {e}")
            raise

    async def get_news_statistics(
        self,
        session: AsyncSession,
        hours: int = 24
    ) -> dict:
        """
        Get news statistics for the given time window.

        Args:
            session: Database session
            hours: Time window in hours

        Returns:
            Dictionary with various statistics
        """
        try:
            time_threshold = utc_now_naive() - timedelta(hours=hours)

            # Total count
            total_count_query = select(func.count(CryptoNews.id)).where(
                CryptoNews.news_created_at >= time_threshold
            )
            total_count = await session.execute(total_count_query)

            # Count by source
            source_count_query = (
                select(CryptoNews.source, func.count(CryptoNews.id))
                .where(CryptoNews.news_created_at >= time_threshold)
                .group_by(CryptoNews.source)
            )
            source_counts = await session.execute(source_count_query)

            # Count by sector
            sector_count_query = (
                select(CryptoNews.sector, func.count(CryptoNews.id))
                .where(CryptoNews.news_created_at >= time_threshold)
                .group_by(CryptoNews.sector)
            )
            sector_counts = await session.execute(sector_count_query)

            return {
                "total": total_count.scalar(),
                "by_source": dict(source_counts.all()),
                "by_sector": dict(sector_counts.all()),
                "time_window_hours": hours
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting news statistics: {e}")
            raise
