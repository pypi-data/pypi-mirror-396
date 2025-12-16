"""
Repositories for database operations.
"""

from .base_repository import BaseRepository
from .token_repository import TokenRepository
from .signal_repository import SignalRepository
from .pre_signal_repository import PreSignalRepository
from .crypto_news_repository import CryptoNewsRepository
from .ai_analysis_repository import AIAnalysisRepository
from .event_impact_repository import EventImpactRepository
from .event_labels_repository import EventLabelsRepository
from .news_semantic_dedup_repository import NewsSemanticDedupRepository

__all__ = [
    "BaseRepository",
    "TokenRepository",
    "SignalRepository",
    "PreSignalRepository",
    "CryptoNewsRepository",
    "AIAnalysisRepository",
    "EventImpactRepository",
    "EventLabelsRepository",
    "NewsSemanticDedupRepository",
]
