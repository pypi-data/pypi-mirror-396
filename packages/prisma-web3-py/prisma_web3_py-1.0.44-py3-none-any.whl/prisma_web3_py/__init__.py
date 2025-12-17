"""
Prisma Web3 Python Package

Async SQLAlchemy implementation of Prisma Web3 database models.
"""

# Core components
from .base import Base
from .config import config
from .database import (
    get_db,
    session_scope,
    configure_engine,
    dispose_engine,
    init_db,
    close_db,
    AsyncSessionLocal,
)

# Models (for direct query usage)
from .models import (
    Token,
    Signal,
    PreSignal,
    SignalStatus,
    TokenMetrics,
    TokenAnalysisReport,
    CryptoNews,
    AIAnalysisResult,
    NewsSemanticDedup,
)

# Repositories (pre-built data access)
from .repositories import (
    BaseRepository,  # For custom repository inheritance
    TokenRepository,
    SignalRepository,
    PreSignalRepository,
    CryptoNewsRepository,
    AIAnalysisRepository,
    NewsSemanticDedupRepository,
)

# Utilities
from .utils import (
    TokenImporter,
    ChainConfig,
)

__version__="1.0.44"

__all__ = [
    # Core
    "Base",
    "config",
    "get_db",
    "session_scope",
    "configure_engine",
    "dispose_engine",
    "init_db",
    "close_db",
    "AsyncSessionLocal",
    "__version__",

    # Models
    "Token",
    "Signal",
    "PreSignal",
    "SignalStatus",
    "TokenMetrics",
    "TokenAnalysisReport",
    "CryptoNews",
    "AIAnalysisResult",
    "NewsSemanticDedup",

    # Repositories
    "BaseRepository",
    "TokenRepository",
    "SignalRepository",
    "PreSignalRepository",
    "CryptoNewsRepository",
    "AIAnalysisRepository",
    "NewsSemanticDedupRepository",

    # Utils
    "TokenImporter",
    "ChainConfig",
]
