"""
PreSignal repository with specialized query methods.
"""

from typing import Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import logging
from prisma_web3_py.utils.datetime import utc_now_naive

from .base_repository import BaseRepository
from ..models.pre_signal import PreSignal, SignalStatus
from ..models.token import Token

logger = logging.getLogger(__name__)


class PreSignalRepository(BaseRepository[PreSignal]):
    """
    Repository for PreSignal model operations.

    Automatically normalizes chain names to CoinGecko standard format.
    """

    def __init__(self):
        super().__init__(PreSignal)

    def _normalize_chain(self, chain: Optional[str]) -> Optional[str]:
        """
        Normalize chain name to standard format.

        Args:
            chain: Chain name or abbreviation (e.g., 'sol', 'solana')

        Returns:
            Standardized chain name (e.g., 'solana')

        Example:
            >>> self._normalize_chain('sol')
            'solana'
            >>> self._normalize_chain('eth')
            'ethereum'
        """
        if chain is None or chain == "":
            return chain
        # Lazy import to avoid circular dependency
        from ..utils.chain_config import ChainConfig
        return ChainConfig.get_standard_name(chain)

    async def create_pre_signal(
        self,
        session: AsyncSession,
        source: str,
        chain: str,
        token_address: str,
        signal_type: str,
        channel_calls: int = 0,
        multi_signals: int = 0,
        kol_discussions: int = 0,
        token_narrative: Optional[str] = None
    ) -> Optional[PreSignal]:
        """
        Create a new pre-signal.

        Automatically normalizes chain name to standard format.

        Args:
            session: Database session
            source: Signal source
            chain: Blockchain name or abbreviation (e.g., 'sol', 'solana')
            token_address: Token contract address
            signal_type: Type of signal
            channel_calls: Number of channel calls (default: 0)
            multi_signals: Number of multi signals (default: 0)
            kol_discussions: Number of KOL discussions (default: 0)
            token_narrative: Optional token narrative

        Returns:
            PreSignal instance or None if failed

        Example:
            >>> await repo.create_pre_signal(session, 'source1', 'sol', '0x...', 'type1')
            # 'sol' is auto-converted to 'solana'
        """
        # Normalize chain name
        normalized_chain = self._normalize_chain(chain)

        pre_signal = PreSignal(
            source=source,
            chain=normalized_chain,
            token_address=token_address,
            signal_type=signal_type,
            channel_calls=channel_calls,
            multi_signals=multi_signals,
            kol_discussions=kol_discussions,
            token_narrative=token_narrative,
            status=SignalStatus.OPEN
        )
        session.add(pre_signal)
        await session.flush()
        await session.refresh(pre_signal)
        logger.debug(f"Created PreSignal with ID: {pre_signal.id}")
        return pre_signal

    async def get_pre_signals_by_token(
        self,
        session: AsyncSession,
        chain: str,
        token_address: str,
        hours: Optional[int] = None,
        status: Optional[SignalStatus] = None
    ) -> List[PreSignal]:
        """
        Get pre-signals for a specific token.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            chain: Blockchain name or abbreviation (e.g., 'sol', 'solana')
            token_address: Token contract address
            hours: Filter by time window in hours (optional)
            status: Filter by status (optional)

        Returns:
            List of pre-signals

        Example:
            >>> await repo.get_pre_signals_by_token(session, 'sol', '0x...')  # Works!
        """
        # Normalize chain name
        normalized_chain = self._normalize_chain(chain)

        query = select(PreSignal).where(
            PreSignal.chain == normalized_chain,
            PreSignal.token_address == token_address
        )

        if hours is not None:
            time_threshold = utc_now_naive() - timedelta(hours=hours)
            query = query.where(PreSignal.created_at >= time_threshold)

        if status is not None:
            query = query.where(PreSignal.status == status)

        query = query.options(
            selectinload(PreSignal.token)
        ).order_by(PreSignal.created_at.desc())

        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_pre_signal_with_token(
        self,
        session: AsyncSession,
        signal_id: int
    ) -> Optional[PreSignal]:
        """
        Get pre-signal by ID with token relationship loaded.

        Args:
            session: Database session
            signal_id: PreSignal ID

        Returns:
            PreSignal instance or None if not found
        """
        query = select(PreSignal).where(
            PreSignal.id == signal_id
        ).options(
            selectinload(PreSignal.token)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_recent_pre_signals(
        self,
        session: AsyncSession,
        hours: int = 1,
        limit: int = 10,
        signal_types: Optional[List[str]] = None,
        status: Optional[SignalStatus] = None
    ) -> List[PreSignal]:
        """
        Get recent pre-signals within time window.

        Args:
            session: Database session
            hours: Time window in hours
            limit: Maximum number of results
            signal_types: Filter by signal types (optional)
            status: Filter by status (optional)

        Returns:
            List of recent pre-signals
        """
        time_threshold = utc_now_naive() - timedelta(hours=hours)

        query = select(PreSignal).where(
            PreSignal.created_at >= time_threshold
        )

        if signal_types:
            query = query.where(PreSignal.signal_type.in_(signal_types))

        if status is not None:
            query = query.where(PreSignal.status == status)

        query = query.options(
            selectinload(PreSignal.token)
        ).order_by(
            PreSignal.created_at.desc()
        ).limit(limit)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def update_pre_signal_status(
        self,
        session: AsyncSession,
        signal_id: int,
        status: SignalStatus
    ) -> bool:
        """
        Update pre-signal status.

        Args:
            session: Database session
            signal_id: PreSignal ID
            status: New status

        Returns:
            True if successful, False otherwise
        """
        return await self.update_by_id(
            session,
            signal_id,
            status=status,
            updated_at=utc_now_naive()
        )

    async def get_pre_signal_counts_by_type(
        self,
        session: AsyncSession,
        chain: Optional[str] = None,
        hours: int = 24,
        status: Optional[SignalStatus] = None
    ) -> dict:
        """
        Get pre-signal counts grouped by signal type.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            chain: Filter by chain or abbreviation (e.g., 'sol', 'solana')
            hours: Time window in hours
            status: Filter by status (optional)

        Returns:
            Dictionary with signal_type as key and count as value
        """
        time_threshold = utc_now_naive() - timedelta(hours=hours)

        query = (
            select(PreSignal.signal_type, func.count(PreSignal.id))
            .where(PreSignal.created_at >= time_threshold)
            .group_by(PreSignal.signal_type)
        )

        if chain:
            # Normalize chain name
            normalized_chain = self._normalize_chain(chain)
            query = query.where(PreSignal.chain == normalized_chain)

        if status is not None:
            query = query.where(PreSignal.status == status)

        result = await session.execute(query)
        return dict(result.all())

    async def get_trending_tokens_by_pre_signals(
        self,
        session: AsyncSession,
        chain: Optional[str] = None,
        signal_type: Optional[str] = None,
        hours: int = 24,
        limit: int = 20,
        status: Optional[SignalStatus] = None
    ) -> List[tuple[Token, int]]:
        """
        Get trending tokens based on pre-signal frequency.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            chain: Filter by chain or abbreviation (e.g., 'sol', 'solana')
            signal_type: Filter by signal type (optional)
            hours: Time window in hours
            limit: Maximum number of results
            status: Filter by status (optional)

        Returns:
            List of (Token, pre_signal_count) tuples
        """
        time_threshold = utc_now_naive() - timedelta(hours=hours)

        query = (
            select(
                Token,
                func.count(PreSignal.id).label('pre_signal_count')
            )
            .join(
                PreSignal,
                (Token.chain == PreSignal.chain) &
                (Token.token_address == PreSignal.token_address)
            )
            .where(PreSignal.created_at >= time_threshold)
            .group_by(Token.id)
            .order_by(func.count(PreSignal.id).desc())
            .limit(limit)
        )

        if chain:
            # Normalize chain name
            normalized_chain = self._normalize_chain(chain)
            query = query.where(Token.chain == normalized_chain)

        if signal_type:
            query = query.where(PreSignal.signal_type == signal_type)

        if status is not None:
            query = query.where(PreSignal.status == status)

        result = await session.execute(query)
        return [(row[0], row[1]) for row in result.all()]

    async def get_pre_signals_by_source(
        self,
        session: AsyncSession,
        source: str,
        hours: Optional[int] = None,
        limit: int = 100,
        status: Optional[SignalStatus] = None
    ) -> List[PreSignal]:
        """
        Get pre-signals from a specific source.

        Args:
            session: Database session
            source: Signal source
            hours: Filter by time window in hours (optional)
            limit: Maximum number of results
            status: Filter by status (optional)

        Returns:
            List of pre-signals
        """
        query = select(PreSignal).where(PreSignal.source == source)

        if hours is not None:
            time_threshold = utc_now_naive() - timedelta(hours=hours)
            query = query.where(PreSignal.created_at >= time_threshold)

        if status is not None:
            query = query.where(PreSignal.status == status)

        query = query.options(
            selectinload(PreSignal.token)
        ).order_by(
            PreSignal.created_at.desc()
        ).limit(limit)

        result = await session.execute(query)
        return list(result.scalars().all())
