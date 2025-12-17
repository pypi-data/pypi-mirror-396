"""
Signal repository with specialized query methods.
"""

from typing import Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import logging
from prisma_web3_py.utils.datetime import utc_now_naive

from .base_repository import BaseRepository
from ..models.signal import Signal
from ..models.token import Token

logger = logging.getLogger(__name__)


class SignalRepository(BaseRepository[Signal]):
    """
    Repository for Signal model operations.

    Automatically normalizes chain names to CoinGecko standard format.
    """

    def __init__(self):
        super().__init__(Signal)

    def _normalize_chain(self, chain: Optional[str]) -> Optional[str]:
        """
        Normalize chain name to standard format.

        Args:
            chain: Chain name or abbreviation (e.g., 'sol', 'solana')

        Returns:
            Standardized chain name (e.g., 'solana')
        """
        if chain is None or chain == "":
            return chain
        # Lazy import to avoid circular dependency
        from ..utils.chain_config import ChainConfig
        return ChainConfig.get_standard_name(chain)

    async def get_recent_signals(
        self,
        session: AsyncSession,
        signal_type: Optional[str] = None,
        chain: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Signal]:
        """
        Get recent signals within specified time window.

        Args:
            session: Database session
            signal_type: Filter by signal type (optional)
            chain: Filter by chain (optional)
            hours: Time window in hours
            limit: Maximum number of results

        Returns:
            List of recent signals
        """
        time_threshold = utc_now_naive() - timedelta(hours=hours)

        query = (
            select(Signal)
            .where(Signal.last_occurrence >= time_threshold)
            .options(selectinload(Signal.token))
        )

        if signal_type:
            query = query.where(Signal.signal_type == signal_type)

        if chain:
            # Normalize chain name
            normalized_chain = self._normalize_chain(chain)
            query = query.where(Signal.chain == normalized_chain)

        query = query.order_by(Signal.last_occurrence.desc()).limit(limit)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_signal_by_token(
        self,
        session: AsyncSession,
        chain: str,
        token_address: str,
        signal_type: Optional[str] = None
    ) -> List[Signal]:
        """
        Get signals for a specific token.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            chain: Blockchain name or abbreviation (e.g., 'sol', 'solana')
            token_address: Token contract address
            signal_type: Filter by signal type (optional)

        Returns:
            List of signals for the token
        """
        # Normalize chain name
        normalized_chain = self._normalize_chain(chain)

        query = select(Signal).where(
            Signal.chain == normalized_chain,
            Signal.token_address == token_address
        )

        if signal_type:
            query = query.where(Signal.signal_type == signal_type)

        query = query.order_by(Signal.last_occurrence.desc())

        result = await session.execute(query)
        return list(result.scalars().all())

    async def upsert_signal(
        self,
        session: AsyncSession,
        chain: str,
        token_address: str,
        source: str,
        signal_type: str,
        is_first: bool = False
    ) -> Optional[Signal]:
        """
        Insert or update signal occurrence.

        Automatically normalizes chain name to standard format.

        Args:
            session: Database session
            chain: Blockchain name or abbreviation (e.g., 'sol', 'solana')
            token_address: Token contract address
            source: Signal source
            signal_type: Type of signal
            is_first: Whether this is the first occurrence

        Returns:
            Signal instance or None if failed
        """
        # Normalize chain name
        normalized_chain = self._normalize_chain(chain)

        # Check if signal exists
        existing = await session.execute(
            select(Signal).where(
                Signal.chain == normalized_chain,
                Signal.token_address == token_address,
                Signal.source == source,
                Signal.signal_type == signal_type
            )
        )
        signal = existing.scalar_one_or_none()

        now = utc_now_naive()

        if signal:
            # Update existing signal
            signal.last_occurrence = now
            signal.occurrence_count = (signal.occurrence_count or 0) + 1
            signal.updated_at = now
        else:
            # Create new signal
            signal = Signal(
                chain=normalized_chain,
                token_address=token_address,
                source=source,
                signal_type=signal_type,
                is_first=is_first,
                last_occurrence=now,
                occurrence_count=1
            )
            session.add(signal)

        await session.flush()
        await session.refresh(signal)
        return signal

    async def get_signal_counts_by_type(
        self,
        session: AsyncSession,
        chain: Optional[str] = None,
        hours: int = 24
    ) -> dict:
        """
        Get signal counts grouped by type.

        Args:
            session: Database session
            chain: Filter by chain (optional)
            hours: Time window in hours

        Returns:
            Dictionary with signal_type as key and count as value
        """
        time_threshold = utc_now_naive() - timedelta(hours=hours)

        query = (
            select(Signal.signal_type, func.count(Signal.id))
            .where(Signal.last_occurrence >= time_threshold)
            .group_by(Signal.signal_type)
        )

        if chain:
            # Normalize chain name
            normalized_chain = self._normalize_chain(chain)
            query = query.where(Signal.chain == normalized_chain)

        result = await session.execute(query)
        return dict(result.all())

    async def get_trending_tokens_by_signals(
        self,
        session: AsyncSession,
        chain: Optional[str] = None,
        signal_type: Optional[str] = None,
        hours: int = 24,
        limit: int = 20
    ) -> List[tuple[Token, int]]:
        """
        Get trending tokens based on signal frequency.

        Args:
            session: Database session
            chain: Filter by chain (optional)
            signal_type: Filter by signal type (optional)
            hours: Time window in hours
            limit: Maximum number of results

        Returns:
            List of (Token, signal_count) tuples
        """
        time_threshold = utc_now_naive() - timedelta(hours=hours)

        query = (
            select(
                Token,
                func.count(Signal.id).label('signal_count')
            )
            .join(Signal, (Token.chain == Signal.chain) & (Token.token_address == Signal.token_address))
            .where(Signal.last_occurrence >= time_threshold)
            .group_by(Token.id)
            .order_by(func.count(Signal.id).desc())
            .limit(limit)
        )

        if chain:
            # Normalize chain name
            normalized_chain = self._normalize_chain(chain)
            query = query.where(Token.chain == normalized_chain)

        if signal_type:
            query = query.where(Signal.signal_type == signal_type)

        result = await session.execute(query)
        return [(row[0], row[1]) for row in result.all()]
