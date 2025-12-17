"""
Token repository with specialized query methods.
"""

from typing import Optional, List, Tuple
from datetime import timedelta
import re
from sqlalchemy import select, func, or_, cast, String, text, and_
from sqlalchemy.dialects.postgresql import insert, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import logging
from sqlalchemy.exc import SQLAlchemyError
from prisma_web3_py.utils.datetime import utc_now_naive

from .base_repository import BaseRepository
from ..models.token import Token
from ..models.token_alias import TokenAlias

logger = logging.getLogger(__name__)


_ALIAS_STRIP_PATTERN = re.compile(r"[\s,.;:'\"`~!@#\$%\^&\*\-_+=\[\]{}|/\\]+")


def normalize_alias_key(alias: str) -> str:
    """规范化别名 key，统一大写英文并去除常见标点/空白。

    Args:
        alias: 原始别名文本。

    Returns:
        处理后的规范化 key，若输入为空返回空字符串。
    """

    if not alias:
        return ""
    cleaned = _ALIAS_STRIP_PATTERN.sub("", alias).strip()
    return cleaned.upper() if cleaned else ""


class TokenRepository(BaseRepository[Token]):
    """
    Repository for Token model operations.

    Automatically normalizes chain names to CoinGecko standard format.
    Supports both abbreviations (eth, bsc, sol) and standard names.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(Token)
        self._pg_trgm_available = None  # Cache for pg_trgm availability check

    async def _check_pg_trgm_available(self, session: AsyncSession) -> bool:
        """
        Check if pg_trgm extension is available in the database.

        This method caches the result to avoid repeated checks.

        Args:
            session: Database session

        Returns:
            True if pg_trgm is available, False otherwise
        """
        if self._pg_trgm_available is not None:
            return self._pg_trgm_available

        try:
            # Check if pg_trgm extension exists by querying pg_extension
            result = await session.execute(
                text("SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_trgm'")
            )
            count = result.scalar()
            self._pg_trgm_available = count > 0
        except Exception as e:
            # If check fails, assume pg_trgm is not available
            logger.debug(f"Failed to check pg_trgm availability: {e}")
            self._pg_trgm_available = False

        logger.debug(f"pg_trgm availability: {self._pg_trgm_available}")
        return self._pg_trgm_available

    def _normalize_chain(self, chain: Optional[str]) -> Optional[str]:
        """
        Normalize chain name to standard format.

        Args:
            chain: Chain name or abbreviation (e.g., 'eth', 'ethereum', 'bsc')

        Returns:
            Standardized chain name (e.g., 'ethereum', 'binance-smart-chain')
            or None if input is None

        Example:
            >>> self._normalize_chain('eth')
            'ethereum'
            >>> self._normalize_chain('bsc')
            'binance-smart-chain'
            >>> self._normalize_chain('ethereum')
            'ethereum'
        """
        if chain is None or chain == "":
            return chain
        # Lazy import to avoid circular dependency
        from ..utils.chain_config import ChainConfig
        return ChainConfig.get_standard_name(chain)

    async def get_by_address(
        self,
        session: AsyncSession,
        chain: str,
        token_address: str
    ) -> Optional[Token]:
        """
        Get token by chain and address.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            chain: Chain name or abbreviation (e.g., 'eth', 'ethereum')
            token_address: Token contract address

        Returns:
            Token instance or None

        Example:
            >>> await repo.get_by_address(session, 'eth', '0x...')  # Works!
            >>> await repo.get_by_address(session, 'ethereum', '0x...')  # Also works!
        """
        # Normalize chain name
        normalized_chain = self._normalize_chain(chain)

        result = await session.execute(
            select(Token)
            .where(Token.chain == normalized_chain, Token.token_address == token_address)
            .options(selectinload(Token.signals))
        )
        return result.scalar_one_or_none()

    async def upsert_token(
        self,
        session: AsyncSession,
        token_data: dict
    ) -> Optional[int]:
        """
        Insert or update token information.

        Automatically normalizes chain name to standard format.

        Args:
            session: Database session
            token_data: Dictionary containing token fields
                       chain: Can be abbreviation (e.g., 'bsc') or standard name

        Returns:
            Token ID or None if failed

        Example:
            >>> data = {"chain": "bsc", "token_address": "0x..."}  # bsc auto-converts to binance-smart-chain
            >>> token_id = await repo.upsert_token(session, data)
        """
        token_address = token_data.get("token_address")
        chain = token_data.get("chain", "solana")  # Default to solana standard name

        if not token_address:
            logger.warning("Token address is required for upsert")
            return None

        # Normalize chain name
        normalized_chain = self._normalize_chain(chain)

        # Prepare upsert data
        upsert_data = {
            "token_address": token_address,
            "chain": normalized_chain,
            "name": token_data.get("name"),
            "symbol": token_data.get("symbol"),
            "description": token_data.get("description"),
            "website": token_data.get("website"),
            "telegram": token_data.get("telegram"),
            "twitter": token_data.get("twitter"),
            "decimals": token_data.get("decimals"),
            "updated_at": utc_now_naive(),
        }

        # Remove None values
        upsert_data = {k: v for k, v in upsert_data.items() if v is not None}

        # Execute UPSERT
        stmt = insert(Token).values(upsert_data)
        stmt = stmt.on_conflict_do_update(
            index_elements=['chain', 'token_address'],
            set_=upsert_data
        )
        result = await session.execute(stmt)
        await session.flush()

        # Get token ID
        if result.inserted_primary_key:
            token_id = result.inserted_primary_key[0]
        else:
            # For updates, fetch the ID
            token_query = select(Token.id).where(
                Token.chain == normalized_chain,
                Token.token_address == token_address
            )
            token_result = await session.execute(token_query)
            token_id = token_result.scalar_one()

        logger.debug(f"Upserted token with ID: {token_id}")
        return token_id

    async def get_recent_tokens(
        self,
        session: AsyncSession,
        chain: Optional[str] = None,
        limit: int = 100
    ) -> List[Token]:
        """
        Get recently created tokens.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            chain: Filter by chain name or abbreviation (e.g., 'eth', 'ethereum')
            limit: Maximum number of results

        Returns:
            List of tokens ordered by creation date (most recent first)

        Example:
            >>> await repo.get_recent_tokens(session, 'bsc', 50)  # Works!
        """
        query = select(Token)

        if chain:
            # Normalize chain name
            normalized_chain = self._normalize_chain(chain)
            query = query.where(Token.chain == normalized_chain)

        query = query.order_by(Token.created_at.desc()).limit(limit)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def search_tokens(
        self,
        session: AsyncSession,
        search_term: str,
        chain: Optional[str] = None,
        limit: int = 20
    ) -> List[Token]:
        """
        Search tokens by symbol, name, or address.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            search_term: Search string
            chain: Filter by chain name or abbreviation (e.g., 'sol', 'solana')
            limit: Maximum number of results

        Returns:
            List of matching tokens

        Example:
            >>> await repo.search_tokens(session, "UNI", chain="eth")  # Works!
        """
        search_pattern = f"%{search_term.lower()}%"

        query = select(Token).where(
            or_(
                Token.symbol.ilike(search_pattern),
                Token.name.ilike(search_pattern),
                Token.token_address.ilike(search_pattern)
            )
        )

        if chain:
            # Normalize chain name
            normalized_chain = self._normalize_chain(chain)
            query = query.where(Token.chain == normalized_chain)

        # Order by creation date (most recent first)
        query = query.order_by(Token.created_at.desc()).limit(limit)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_recently_updated_tokens(
        self,
        session: AsyncSession,
        hours: int = 24,
        chain: Optional[str] = None,
        limit: int = 100
    ) -> List[Token]:
        """
        Get recently updated tokens.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            hours: Time window in hours
            chain: Filter by chain name or abbreviation (e.g., 'eth', 'ethereum')
            limit: Maximum number of results

        Returns:
            List of recently updated tokens

        Example:
            >>> await repo.get_recently_updated_tokens(session, hours=24, chain='bsc')  # Works!
        """
        time_threshold = utc_now_naive() - timedelta(hours=hours)

        query = select(Token).where(Token.updated_at >= time_threshold)

        if chain:
            # Normalize chain name
            normalized_chain = self._normalize_chain(chain)
            query = query.where(Token.chain == normalized_chain)

        query = query.order_by(Token.updated_at.desc()).limit(limit)

        result = await session.execute(query)
        return list(result.scalars().all())
        
    async def search_by_symbol(
        self,
        session: AsyncSession,
        symbol: str,
        exact: bool = True
    ) -> List[Token]:
        """
        Search tokens by symbol.

        Args:
            session: Database session
            symbol: Token symbol to search for
            exact: If True, exact match only. If False, case-insensitive LIKE match

        Returns:
            List of matching Token objects

        Example:
            # Exact match
            tokens = await repo.search_by_symbol(session, "BTC", exact=True)

            # Fuzzy match
            tokens = await repo.search_by_symbol(session, "btc", exact=False)
        """
        normalized_symbol = symbol.strip().upper()

        if exact:
            stmt = select(Token).where(
                func.upper(Token.symbol) == normalized_symbol
            )
        else:
            stmt = select(Token).where(
                func.upper(Token.symbol).like(f"%{normalized_symbol}%")
            ).limit(10)

        result = await session.execute(stmt)
        tokens = result.scalars().all()

        logger.debug(
            "search_by_symbol('%s', exact=%s): found %d tokens",
            symbol,
            exact,
            len(tokens),
        )
        return list(tokens)


    async def search_by_name(
        self,
        session: AsyncSession,
        name: str,
        exact: bool = False
    ) -> List[Token]:
        """
        Search tokens by name.

        Args:
            session: Database session
            name: Token name to search for
            exact: If True, exact match. If False, case-insensitive LIKE match (default)

        Returns:
            List of matching Token objects

        Example:
            # Fuzzy match (default)
            tokens = await repo.search_by_name(session, "bitcoin")

            # Exact match
            tokens = await repo.search_by_name(session, "Bitcoin", exact=True)
        """
        normalized_name = name.strip()

        if exact:
            stmt = select(Token).where(
                func.lower(Token.name) == normalized_name.lower()
            )
        else:
            stmt = select(Token).where(
                func.lower(Token.name).like(f"%{normalized_name.lower()}%")
            ).limit(10)

        result = await session.execute(stmt)
        tokens = result.scalars().all()

        logger.debug(
            "search_by_name('%s', exact=%s): found %d tokens",
            name,
            exact,
            len(tokens),
        )
        return list(tokens)


    async def search_by_alias(
        self,
        session: AsyncSession,
        alias: str,
        *,
        lang: Optional[str] = None,
        min_weight: float = 0.0,
    ) -> List[Tuple[TokenAlias, Token]]:
        """
        通过别名表检索 Token 及匹配到的 TokenAlias。

        Args:
            session: 数据库会话
            alias: 待查询的别名原文
            lang: 限定语言，None 则不限制
            min_weight: 最低权重过滤

        Returns:
            (TokenAlias, Token) 元组列表
        """

        normalized_key = normalize_alias_key(alias)
        if not normalized_key:
            return []

        stmt = (
            select(TokenAlias, Token)
            .join(Token, TokenAlias.token_id == Token.id)
            .where(TokenAlias.normalized_key == normalized_key)
        )

        if lang:
            stmt = stmt.where(or_(TokenAlias.lang == lang, TokenAlias.lang.is_(None)))
        if min_weight > 0:
            stmt = stmt.where(TokenAlias.weight >= min_weight)

        result = await session.execute(stmt)
        rows = result.all()

        logger.debug("search_by_alias('%s'): found %d tokens", alias, len(rows))
        return rows

    async def batch_search_aliases(
        self,
        session: AsyncSession,
        aliases: List[str],
        *,
        lang: Optional[str] = None,
        min_weight: float = 0.0,
        limit: int = 200,
    ) -> List[Tuple[TokenAlias, Token]]:
        """批量按别名规范化 key 查询 TokenAlias 与 Token。

        Args:
            session: 数据库会话。
            aliases: 待查询的别名原文列表。
            lang: 限定语言，None 则不限制。
            min_weight: 最低权重过滤。
            limit: 返回结果的最大条数，用于保护查询。

        Returns:
            (TokenAlias, Token) 元组列表，按 normalized_key 去重后查询。
        """
        if not aliases:
            return []

        normalized_keys: List[str] = []
        seen: set[str] = set()
        for alias in aliases:
            normalized = normalize_alias_key(alias)
            if normalized and normalized not in seen:
                seen.add(normalized)
                normalized_keys.append(normalized)

        if not normalized_keys:
            return []

        stmt = (
            select(TokenAlias, Token)
            .join(Token, TokenAlias.token_id == Token.id)
            .where(TokenAlias.normalized_key.in_(normalized_keys))
        )

        if lang:
            stmt = stmt.where(or_(TokenAlias.lang == lang, TokenAlias.lang.is_(None)))
        if min_weight > 0:
            stmt = stmt.where(TokenAlias.weight >= min_weight)

        stmt = stmt.order_by(TokenAlias.weight.desc()).limit(limit)

        result = await session.execute(stmt)
        rows = result.all()

        logger.info(
            "batch_search_aliases: normalized_keys=%d, rows=%d, lang=%s, min_weight=%.2f",
            len(normalized_keys),
            len(rows),
            lang,
            min_weight,
        )
        return rows

    async def get_all_aliases(
        self,
        session: AsyncSession,
        *,
        limit: int = 10000,
        lang: Optional[str] = None,
    ) -> List[TokenAlias]:
        """批量获取别名词典，供缓存/索引使用。"""

        stmt = select(TokenAlias).options(selectinload(TokenAlias.token)).order_by(TokenAlias.weight.desc()).limit(limit)
        if lang:
            stmt = stmt.where(or_(TokenAlias.lang == lang, TokenAlias.lang.is_(None)))
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def bulk_upsert_aliases(
        self,
        session: AsyncSession,
        aliases: List[dict],
    ) -> int:
        """批量写入/更新别名词典，供迁移或同步脚本使用。"""

        if not aliases:
            return 0

        prepared: List[dict] = []
        for entry in aliases:
            alias_text = entry.get("alias")
            normalized_key = normalize_alias_key(alias_text)
            if not alias_text or not normalized_key:
                continue
            prepared.append(
                {
                    "token_id": entry["token_id"],
                    "alias": alias_text,
                    "normalized_key": normalized_key,
                    "alias_type": entry.get("alias_type", "symbol"),
                    "lang": entry.get("lang"),
                    "source": entry.get("source"),
                    "is_preferred": bool(entry.get("is_preferred", False)),
                    "is_deprecated": bool(entry.get("is_deprecated", False)),
                    "weight": float(entry.get("weight", 1.0)),
                }
            )

        if not prepared:
            return 0

        stmt = insert(TokenAlias).values(prepared)
        stmt = stmt.on_conflict_do_update(
            index_elements=[TokenAlias.token_id, TokenAlias.normalized_key, TokenAlias.alias_type],
            set_={
                "alias": stmt.excluded.alias,
                "lang": stmt.excluded.lang,
                "source": stmt.excluded.source,
                "is_preferred": stmt.excluded.is_preferred,
                "is_deprecated": stmt.excluded.is_deprecated,
                "weight": stmt.excluded.weight,
            },
        )

        await session.execute(stmt)
        await session.flush()
        return len(prepared)


    async def fuzzy_search(
        self,
        session: AsyncSession,
        text: str,
        threshold: float = 0.8,
        limit: int = 10
    ) -> List[Token]:
        """
        Fuzzy search tokens using PostgreSQL trigram similarity.

        Requires the pg_trgm extension to be installed:
            CREATE EXTENSION IF NOT EXISTS pg_trgm;

        If pg_trgm is not available, falls back to LIKE matching.

        Args:
            session: Database session
            text: Text to search for
            threshold: Similarity threshold (0.0 to 1.0, default 0.8)
            limit: Maximum number of results

        Returns:
            List of matching Token objects sorted by similarity

        Example:
            # Find tokens similar to "bitcoin"
            tokens = await repo.fuzzy_search(session, "bitcon", threshold=0.7)
        """
        normalized_text = text.strip().lower()

        # Check if pg_trgm is available before attempting to use it
        pg_trgm_available = await self._check_pg_trgm_available(session)

        if pg_trgm_available:
            stmt = select(Token).where(
                or_(
                    func.similarity(func.lower(Token.symbol), normalized_text) >= threshold,
                    func.similarity(func.lower(Token.name), normalized_text) >= threshold,
                    func.similarity(func.lower(Token.coingecko_id), normalized_text) >= threshold,
                )
            ).order_by(
                func.greatest(
                    func.similarity(func.lower(Token.symbol), normalized_text),
                    func.similarity(func.lower(Token.name), normalized_text),
                    func.similarity(func.lower(Token.coingecko_id), normalized_text),
                ).desc()
            ).limit(limit)

            result = await session.execute(stmt)
            tokens = result.scalars().all()

            logger.debug(
                "fuzzy_search('%s', threshold=%s): found %d tokens using pg_trgm",
                text,
                threshold,
                len(tokens),
            )
            return list(tokens)

        logger.debug("pg_trgm not available, using LIKE matching for fuzzy_search")
        stmt = select(Token).where(
            or_(
                func.lower(Token.symbol).like(f"%{normalized_text}%"),
                func.lower(Token.name).like(f"%{normalized_text}%"),
                func.lower(Token.coingecko_id).like(f"%{normalized_text}%"),
            )
        ).limit(limit)

        result = await session.execute(stmt)
        tokens = result.scalars().all()

        logger.debug(
            "fuzzy_search('%s'): found %d tokens using LIKE",
            text,
            len(tokens),
        )
        return list(tokens)

    # ========== BATCH OPERATIONS ==========

    async def batch_get_by_addresses(
        self,
        session: AsyncSession,
        addresses: List[tuple[str, str]]
    ) -> List[Token]:
        """
        Batch get tokens by multiple (chain, address) pairs.

        This is much more efficient than calling get_by_address() multiple times.

        Args:
            session: Database session
            addresses: List of (chain, token_address) tuples
                      Chain can be abbreviation or standard name

        Returns:
            List of Token objects found

        Example:
            >>> addresses = [
            ...     ('eth', '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984'),  # UNI
            ...     ('bsc', '0x...'),
            ...     ('sol', 'oobQ3oX6ubRYMNMahG7VSCe8Z73uaQbAWFn6f22XTgo')
            ... ]
            >>> tokens = await repo.batch_get_by_addresses(session, addresses)
        """
        if not addresses:
            return []

        # Normalize all chain names
        normalized_addresses = [
            (self._normalize_chain(chain), addr)
            for chain, addr in addresses
        ]

        # Build OR conditions for all (chain, address) pairs
        conditions = []
        for chain, addr in normalized_addresses:
            conditions.append(
                and_(Token.chain == chain, Token.token_address == addr)
            )

        stmt = select(Token).where(or_(*conditions))
        result = await session.execute(stmt)
        tokens = list(result.scalars().all())

        logger.debug(f"batch_get_by_addresses: fetched {len(tokens)} tokens")
        return tokens

    async def batch_search_by_names(
        self,
        session: AsyncSession,
        names: List[str],
        *,
        exact: bool = False,
        max_total: int = 200,
    ) -> List[Token]:
        """批量按名称查询 Token，避免重复多次 LIKE/ILIKE 往返。

        Args:
            session: 数据库会话。
            names: Token 名称列表。
            exact: 是否要求精确匹配（默认模糊）。
            max_total: 最大返回条数，保护查询。

        Returns:
            匹配到的 Token 列表。
        """
        if not names:
            return []

        normalized_names: List[str] = []
        seen: set[str] = set()
        for name in names:
            key = name.strip().lower()
            if key and key not in seen:
                seen.add(key)
                normalized_names.append(key)

        if not normalized_names:
            return []

        if exact:
            stmt = select(Token).where(func.lower(Token.name).in_(normalized_names))
        else:
            conditions = [
                func.lower(Token.name).like(f"%{n}%")
                for n in normalized_names
            ]
            stmt = select(Token).where(or_(*conditions)).limit(max_total)

        result = await session.execute(stmt)
        tokens = list(result.scalars().all())

        logger.info(
            "batch_search_by_names: names=%d → tokens=%d (exact=%s, max_total=%d)",
            len(normalized_names),
            len(tokens),
            exact,
            max_total,
        )
        return tokens

    async def batch_search_by_symbols(
        self,
        session: AsyncSession,
        symbols: List[str],
        exact: bool = True
    ) -> List[Token]:
        """
        Batch search tokens by multiple symbols.

        Much more efficient than calling search_by_symbol() multiple times.

        Args:
            session: Database session
            symbols: List of token symbols to search for
            exact: If True, exact match only. If False, fuzzy match

        Returns:
            List of matching Token objects

        Example:
            >>> symbols = ['BTC', 'ETH', 'SOL', 'UNI']
            >>> tokens = await repo.batch_search_by_symbols(session, symbols)
        """
        if not symbols:
            return []

        # Normalize symbols
        normalized_symbols = [s.strip().upper() for s in symbols]

        if exact:
            # Exact match using IN clause
            stmt = select(Token).where(
                func.upper(Token.symbol).in_(normalized_symbols)
            )
        else:
            # Fuzzy match using OR conditions
            conditions = [
                func.upper(Token.symbol).like(f"%{sym}%")
                for sym in normalized_symbols
            ]
            stmt = select(Token).where(or_(*conditions)).limit(100)

        result = await session.execute(stmt)
        tokens = list(result.scalars().all())

        logger.debug(
            f"batch_search_by_symbols: found {len(tokens)} tokens "
            f"for {len(symbols)} symbols"
        )
        return tokens

    async def batch_upsert_tokens(
        self,
        session: AsyncSession,
        tokens_data: List[dict]
    ) -> dict:
        """
        Batch upsert multiple tokens efficiently.

        Uses PostgreSQL's INSERT ... ON CONFLICT for efficient bulk operations.

        Args:
            session: Database session
            tokens_data: List of token data dictionaries
                        Each dict should contain at least: chain, token_address
                        Chain can be abbreviation or standard name

        Returns:
            Dictionary with statistics: {'inserted': int, 'updated': int, 'failed': int}

        Example:
            >>> tokens_data = [
            ...     {
            ...         'chain': 'eth',  # Auto-normalized to 'ethereum'
            ...         'token_address': '0x...',
            ...         'symbol': 'UNI',
            ...         'name': 'Uniswap',
            ...         'decimals': 18
            ...     },
            ...     {
            ...         'chain': 'bsc',  # Auto-normalized to 'binance-smart-chain'
            ...         'token_address': '0x...',
            ...         'symbol': 'CAKE',
            ...         'name': 'PancakeSwap'
            ...     }
            ... ]
            >>> result = await repo.batch_upsert_tokens(session, tokens_data)
            >>> print(f"Inserted: {result['inserted']}, Updated: {result['updated']}")
        """
        if not tokens_data:
            return {'inserted': 0, 'updated': 0, 'failed': 0}

        inserted = 0
        updated = 0
        failed = 0

        try:
            # Prepare all records with normalized chain names
            prepared_records = []
            for token_data in tokens_data:
                try:
                    chain = token_data.get('chain', 'solana')
                    token_address = token_data.get('token_address')

                    if not token_address:
                        logger.warning(f"Skipping token without address: {token_data}")
                        failed += 1
                        continue

                    # Normalize chain name
                    normalized_chain = self._normalize_chain(chain)

                    record = {
                        'chain': normalized_chain,
                        'token_address': token_address,
                        'name': token_data.get('name'),
                        'symbol': token_data.get('symbol'),
                        'description': token_data.get('description'),
                        'website': token_data.get('website'),
                        'telegram': token_data.get('telegram'),
                        'twitter': token_data.get('twitter'),
                        'decimals': token_data.get('decimals'),
                        'coingecko_id': token_data.get('coingecko_id'),
                        'platforms': token_data.get('platforms'),
                        'aliases': token_data.get('aliases'),
                        'updated_at': utc_now_naive(),
                    }

                    # Remove None values
                    record = {k: v for k, v in record.items() if v is not None}
                    prepared_records.append(record)

                except Exception as e:
                    logger.error(f"Error preparing token data: {e}")
                    failed += 1

            if not prepared_records:
                return {'inserted': 0, 'updated': 0, 'failed': failed}

            # Batch upsert using PostgreSQL INSERT ... ON CONFLICT
            stmt = insert(Token).values(prepared_records)

            # Update all fields on conflict except chain and token_address
            update_dict = {
                k: stmt.excluded[k]
                for k in prepared_records[0].keys()
                if k not in ['chain', 'token_address']
            }

            stmt = stmt.on_conflict_do_update(
                index_elements=['chain', 'token_address'],
                set_=update_dict
            )

            result = await session.execute(stmt)
            await session.flush()

            # PostgreSQL doesn't easily tell us insert vs update counts
            # We'll estimate: rowcount represents affected rows
            affected = result.rowcount
            inserted = affected  # Simplification for now

            logger.info(
                f"batch_upsert_tokens: processed {len(prepared_records)} tokens, "
                f"affected {affected} rows, failed {failed}"
            )

            return {
                'inserted': inserted,
                'updated': 0,  # Can't easily distinguish in batch
                'failed': failed,
                'total_processed': len(prepared_records)
            }

        except SQLAlchemyError as e:
            logger.error("Error in batch_upsert_tokens: %s", e)
            raise

    async def batch_search_tokens(
        self,
        session: AsyncSession,
        search_terms: List[str],
        chain: Optional[str] = None,
        limit_per_term: int = 5
    ) -> dict[str, List[Token]]:
        """
        Batch search tokens by multiple search terms.

        Returns results grouped by search term.

        Args:
            session: Database session
            search_terms: List of search strings
            chain: Optional filter by chain (supports abbreviations)
            limit_per_term: Max results per search term

        Returns:
            Dictionary mapping search_term -> List[Token]

        Example:
            >>> terms = ['BTC', 'ethereum', 'solana']
            >>> results = await repo.batch_search_tokens(session, terms, chain='eth')
            >>> print(f"BTC results: {len(results['BTC'])}")
        """
        if not search_terms:
            return {}

        results = {}
        normalized_chain = self._normalize_chain(chain) if chain else None

        try:
            # Build combined search query for all terms
            for term in search_terms:
                search_pattern = f"%{term.lower()}%"

                query = select(Token).where(
                    or_(
                        Token.symbol.ilike(search_pattern),
                        Token.name.ilike(search_pattern),
                        Token.token_address.ilike(search_pattern)
                    )
                )

                if normalized_chain:
                    query = query.where(Token.chain == normalized_chain)

                query = query.order_by(Token.created_at.desc()).limit(limit_per_term)

                result = await session.execute(query)
                results[term] = list(result.scalars().all())

            total_results = sum(len(tokens) for tokens in results.values())
            logger.debug(
                f"batch_search_tokens: found {total_results} total results "
                f"for {len(search_terms)} terms"
            )

            return results

        except SQLAlchemyError as e:
            logger.error("Error in batch_search_tokens: %s", e)
            raise
