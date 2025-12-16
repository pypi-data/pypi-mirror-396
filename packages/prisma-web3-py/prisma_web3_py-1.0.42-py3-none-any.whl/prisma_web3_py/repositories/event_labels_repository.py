"""
EventLabels Repository - Repository for manual event review and labeling.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import uuid
from prisma_web3_py.utils.datetime import utc_now_naive

from ..models.event_labels import EventLabels, LabelType
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class EventLabelsRepository(BaseRepository[EventLabels]):
    """
    Event Labels Repository

    Provides interface for creating and querying manual labels/reviews
    of AI analysis results for quality control and model improvement.
    """

    def __init__(self):
        super().__init__(EventLabels)

    # ========== CREATE METHODS ==========

    async def create_label(
        self,
        session: AsyncSession,
        event_id: int,
        reviewer: str,
        label: str,
        note: Optional[str] = None
    ) -> Optional[EventLabels]:
        """
        Create a new event label/review.

        Args:
            session: Database session
            event_id: AIAnalysisResult ID
            reviewer: Reviewer username/ID
            label: Label type ('accurate', 'miss', 'noise', 'investigate')
            note: Optional review notes

        Returns:
            Created EventLabels object or None
        """
        # Validate label
        if not EventLabels.is_valid_label(label):
            logger.error(
                f"Invalid label '{label}'. "
                f"Valid labels: {EventLabels.get_valid_labels()}"
            )
            return None

        event_label = EventLabels(
            event_id=event_id,
            reviewer=reviewer,
            label=label,
            note=note
        )

        session.add(event_label)
        await session.flush()
        await session.refresh(event_label)
        logger.debug(
            f"Created event label: ID={event_label.id}, "
            f"event_id={event_id}, label={label}"
        )
        return event_label

    async def batch_create_labels(
        self,
        session: AsyncSession,
        labels: List[Dict[str, Any]]
    ) -> List[EventLabels]:
        """
        Create multiple labels in batch.

        Args:
            session: Database session
            labels: List of label dicts with keys: event_id, reviewer, label, note

        Returns:
            List of created EventLabels objects
        """
        created = []
        for label_data in labels:
            label = await self.create_label(
                session=session,
                event_id=label_data['event_id'],
                reviewer=label_data['reviewer'],
                label=label_data['label'],
                note=label_data.get('note')
            )
            if label:
                created.append(label)

        logger.debug("Batch created %d labels", len(created))
        return created

    # ========== QUERY METHODS ==========

    async def get_by_id(
        self,
        session: AsyncSession,
        label_id: uuid.UUID
    ) -> Optional[EventLabels]:
        """
        Get label by UUID.

        Args:
            session: Database session
            label_id: EventLabels UUID

        Returns:
            EventLabels or None
        """
        stmt = select(EventLabels).where(EventLabels.id == label_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_labels_for_event(
        self,
        session: AsyncSession,
        event_id: int
    ) -> List[EventLabels]:
        """
        Get all labels for a specific event.

        Args:
            session: Database session
            event_id: AIAnalysisResult ID

        Returns:
            List of EventLabels
        """
        stmt = select(EventLabels).where(
            EventLabels.event_id == event_id
        ).order_by(EventLabels.created_at.desc())

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_label_type(
        self,
        session: AsyncSession,
        label: str,
        limit: int = 100,
        hours: Optional[int] = None
    ) -> List[EventLabels]:
        """
        Get labels by type.

        Args:
            session: Database session
            label: Label type to filter
            limit: Result limit
            hours: Optional time range in hours

        Returns:
            List of EventLabels
        """
        stmt = select(EventLabels).where(EventLabels.label == label)

        if hours:
            since = utc_now_naive() - timedelta(hours=hours)
            stmt = stmt.where(EventLabels.created_at >= since)

        stmt = stmt.order_by(EventLabels.created_at.desc()).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_reviewer(
        self,
        session: AsyncSession,
        reviewer: str,
        limit: int = 100,
        hours: Optional[int] = None
    ) -> List[EventLabels]:
        """
        Get labels by reviewer.

        Args:
            session: Database session
            reviewer: Reviewer username/ID
            limit: Result limit
            hours: Optional time range in hours

        Returns:
            List of EventLabels
        """
        stmt = select(EventLabels).where(EventLabels.reviewer == reviewer)

        if hours:
            since = utc_now_naive() - timedelta(hours=hours)
            stmt = stmt.where(EventLabels.created_at >= since)

        stmt = stmt.order_by(EventLabels.created_at.desc()).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def has_label(
        self,
        session: AsyncSession,
        event_id: int,
        label: str
    ) -> bool:
        """
        Check if event has specific label.

        Args:
            session: Database session
            event_id: AIAnalysisResult ID
            label: Label type to check

        Returns:
            True if event has the label
        """
        stmt = select(func.count(EventLabels.id)).where(
            and_(
                EventLabels.event_id == event_id,
                EventLabels.label == label
            )
        )
        result = await session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def get_unlabeled_events(
        self,
        session: AsyncSession,
        event_ids: List[int]
    ) -> List[int]:
        """
        Filter event IDs to only those without any labels.

        Args:
            session: Database session
            event_ids: List of AIAnalysisResult IDs to check

        Returns:
            List of event IDs that have no labels
        """
        # Get all event IDs that have labels
        stmt = select(EventLabels.event_id.distinct()).where(
            EventLabels.event_id.in_(event_ids)
        )
        result = await session.execute(stmt)
        labeled_ids = set(result.scalars().all())

        # Return IDs that are not in labeled set
        return [eid for eid in event_ids if eid not in labeled_ids]

    # ========== STATISTICS METHODS ==========

    async def get_label_stats(
        self,
        session: AsyncSession,
        hours: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Get label distribution statistics.

        Args:
            session: Database session
            hours: Optional time range in hours

        Returns:
            Dict mapping label types to counts
        """
        stmt = select(
            EventLabels.label,
            func.count(EventLabels.id).label('count')
        )

        if hours:
            since = utc_now_naive() - timedelta(hours=hours)
            stmt = stmt.where(EventLabels.created_at >= since)

        stmt = stmt.group_by(EventLabels.label)

        result = await session.execute(stmt)
        return {row.label: row.count for row in result}

    async def get_reviewer_stats(
        self,
        session: AsyncSession,
        hours: Optional[int] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get reviewer activity statistics.

        Args:
            session: Database session
            hours: Optional time range in hours
            limit: Result limit

        Returns:
            List of dicts with reviewer stats
        """
        stmt = select(
            EventLabels.reviewer,
            func.count(EventLabels.id).label('total'),
            func.count(EventLabels.id).filter(
                EventLabels.label == LabelType.ACCURATE.value
            ).label('accurate'),
            func.count(EventLabels.id).filter(
                EventLabels.label == LabelType.MISS.value
            ).label('miss'),
            func.count(EventLabels.id).filter(
                EventLabels.label == LabelType.NOISE.value
            ).label('noise'),
            func.count(EventLabels.id).filter(
                EventLabels.label == LabelType.INVESTIGATE.value
            ).label('investigate')
        )

        if hours:
            since = utc_now_naive() - timedelta(hours=hours)
            stmt = stmt.where(EventLabels.created_at >= since)

        stmt = stmt.group_by(EventLabels.reviewer).order_by(
            func.count(EventLabels.id).desc()
        ).limit(limit)

        result = await session.execute(stmt)

        return [
            {
                'reviewer': row.reviewer,
                'total': row.total,
                'accurate': row.accurate or 0,
                'miss': row.miss or 0,
                'noise': row.noise or 0,
                'investigate': row.investigate or 0
            }
            for row in result
        ]

    async def get_accuracy_rate(
        self,
        session: AsyncSession,
        hours: Optional[int] = None
    ) -> Optional[float]:
        """
        Calculate AI accuracy rate based on labels.

        Accuracy = accurate / (accurate + miss + noise)

        Args:
            session: Database session
            hours: Optional time range in hours

        Returns:
            Accuracy rate (0.0-1.0) or None
        """
        stats = await self.get_label_stats(session, hours)

        accurate = stats.get(LabelType.ACCURATE.value, 0)
        miss = stats.get(LabelType.MISS.value, 0)
        noise = stats.get(LabelType.NOISE.value, 0)

        total = accurate + miss + noise
        if total == 0:
            return None

        return accurate / total

    async def get_events_by_label(
        self,
        session: AsyncSession,
        label: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[int]:
        """
        Get event IDs for a specific label type.

        Useful for retrieving events that need attention or are examples of specific cases.

        Args:
            session: Database session
            label: Label type
            limit: Result limit
            offset: Result offset for pagination

        Returns:
            List of event IDs
        """
        stmt = select(EventLabels.event_id).where(
            EventLabels.label == label
        ).order_by(
            EventLabels.created_at.desc()
        ).limit(limit).offset(offset)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_labels(
        self,
        session: AsyncSession,
        hours: int = 24,
        limit: int = 100
    ) -> List[EventLabels]:
        """
        Get recent labels within time range.

        Args:
            session: Database session
            hours: Time range in hours
            limit: Result limit

        Returns:
            List of EventLabels
        """
        since = utc_now_naive() - timedelta(hours=hours)

        stmt = select(EventLabels).where(
            EventLabels.created_at >= since
        ).order_by(EventLabels.created_at.desc()).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def delete_label(
        self,
        session: AsyncSession,
        label_id: uuid.UUID
    ) -> bool:
        """
        Delete a label (use with caution).

        Args:
            session: Database session
            label_id: EventLabels UUID

        Returns:
            Success status
        """
        stmt = select(EventLabels).where(EventLabels.id == label_id)
        result = await session.execute(stmt)
        label = result.scalar_one_or_none()

        if label:
            await session.delete(label)
            await session.flush()
            logger.debug(f"Deleted label: ID={label_id}")
            return True
        return False
