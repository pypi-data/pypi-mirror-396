"""
Base repository class with common CRUD operations.
"""

from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..base import Base

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing common database operations.

    Args:
        model: SQLAlchemy model class
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.logger = logger

    def _normalize_chain(self, chain: Optional[str]) -> Optional[str]:
        """
        Normalize chain name to standard format.

        This is a default implementation that subclasses can override.
        Returns the chain as-is by default.

        Args:
            chain: Chain name or abbreviation

        Returns:
            Standardized chain name or original chain
        """
        return chain

    def _prepare_kwargs(self, kwargs: dict) -> dict:
        """
        Prepare kwargs before creating/updating a record.

        Automatically normalizes chain field if present.

        Args:
            kwargs: Model field values

        Returns:
            Prepared kwargs with normalized values
        """
        # Create a copy to avoid modifying the original
        prepared = kwargs.copy()

        # Normalize chain if present and model has chain field
        if 'chain' in prepared and hasattr(self.model, 'chain'):
            prepared['chain'] = self._normalize_chain(prepared['chain'])

        return prepared

    async def create(self, session: AsyncSession, **kwargs) -> ModelType:
        """
        Create a new record.

        Automatically normalizes chain field if present.

        Args:
            session: Database session
            **kwargs: Model field values

        Returns:
            Created model instance
        """
        prepared_kwargs = self._prepare_kwargs(kwargs)
        instance = self.model(**prepared_kwargs)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance

    async def get_by_id(self, session: AsyncSession, id: int) -> Optional[ModelType]:
        """
        Get record by ID.

        Args:
            session: Database session
            id: Record ID

        Returns:
            Model instance or None if not found
        """
        result = await session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        session: AsyncSession,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[ModelType]:
        """
        Get all records with optional pagination.

        Args:
            session: Database session
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of model instances
        """
        query = select(self.model)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def filter_by(
        self,
        session: AsyncSession,
        limit: Optional[int] = None,
        **filters
    ) -> List[ModelType]:
        """
        Filter records by criteria.

        Args:
            session: Database session
            limit: Maximum number of records
            **filters: Field name and value pairs

        Returns:
            List of matching model instances
        """
        conditions = [
            getattr(self.model, key) == value
            for key, value in filters.items()
            if hasattr(self.model, key)
        ]

        query = select(self.model).where(*conditions)
        if limit:
            query = query.limit(limit)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def update_by_id(
        self,
        session: AsyncSession,
        id: int,
        **updates
    ) -> bool:
        """
        Update record by ID.

        Args:
            session: Database session
            id: Record ID
            **updates: Field name and value pairs to update

        Returns:
            True if successful, False otherwise
        """
        instance = await self.get_by_id(session, id)
        if not instance:
            return False
        prepared_updates = self._prepare_kwargs(updates)
        for key, value in prepared_updates.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await session.flush()
        return True

    async def delete_by_id(self, session: AsyncSession, id: int) -> bool:
        """
        Delete record by ID.

        Args:
            session: Database session
            id: Record ID

        Returns:
            True if successful, False otherwise
        """
        instance = await self.get_by_id(session, id)
        if not instance:
            return False
        await session.delete(instance)
        await session.flush()
        return True

    async def count(self, session: AsyncSession, **filters) -> int:
        """
        Count records matching filters.

        Args:
            session: Database session
            **filters: Field name and value pairs

        Returns:
            Number of matching records
        """
        conditions = [
            getattr(self.model, key) == value
            for key, value in filters.items()
            if hasattr(self.model, key)
        ]

        query = select(func.count()).select_from(self.model)
        if conditions:
            query = query.where(*conditions)

        result = await session.execute(query)
        return result.scalar_one()
