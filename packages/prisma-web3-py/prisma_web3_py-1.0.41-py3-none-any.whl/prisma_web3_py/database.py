"""
Database module for async SQLAlchemy setup.

This module now follows the SQLAlchemy 2.x async recommendations:
    * Engine + sessionmaker are built via a factory so tests can override URLs.
    * Unit of work is expressed with `session.begin()` to manage commits.
    * A lightweight session scope helper is provided for request/task usage.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError

from .base import Base
from .config import config

logger = logging.getLogger(__name__)

# Default pool settings (can be overridden in tests or env)
DEFAULT_ENGINE_KWARGS = {
    "echo": False,
    "pool_pre_ping": True,
    "pool_size": int(os.getenv("DB_POOL_SIZE", "50")),
    "max_overflow": int(os.getenv("DB_POOL_OVERFLOW", "100")),
    "pool_timeout": float(os.getenv("DB_POOL_TIMEOUT", "90")),
}

# Globals kept for backward compatibility with callers that import these names.
engine: AsyncEngine
AsyncSessionLocal: async_sessionmaker[AsyncSession]


def _build_engine(database_url: Optional[str] = None, **engine_kwargs) -> Tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """
    Construct a new async engine + sessionmaker pair.

    Args:
        database_url: Optional explicit URL (defaults to config.database_url)
        **engine_kwargs: Engine overrides (e.g., pool sizes for tests)
    """
    url = database_url or config.database_url
    kwargs = {**DEFAULT_ENGINE_KWARGS, **engine_kwargs}
    eng = create_async_engine(url, **kwargs)
    session_maker = async_sessionmaker(
        bind=eng,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    return eng, session_maker


def configure_engine(database_url: Optional[str] = None, **engine_kwargs) -> None:
    """
    Reconfigure the global engine/sessionmaker (useful for tests).

    Note: If you need to dispose an existing engine, call dispose_engine() first.
    """
    global engine, AsyncSessionLocal
    engine, AsyncSessionLocal = _build_engine(database_url, **engine_kwargs)


async def dispose_engine() -> None:
    """Dispose the current engine (used by tests/shutdown hooks)."""
    try:
        await engine.dispose()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to dispose engine cleanly: %s", exc)


async def init_db():
    """
    Initialize database, create all tables if they don't exist.

    Prefer running Prisma migrations out-of-band; this helper is a fallback.
    """
    logger.info("Initializing database...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@asynccontextmanager
async def session_scope(readonly: bool = False) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an AsyncSession with SQLAlchemy 2.x unit-of-work semantics.

    The context manager commits on success and rolls back on exceptions.
    Set readonly=True to avoid committing (e.g., for GET handlers).
    """
    async with AsyncSessionLocal() as session:
        try:
            if readonly:
                async with session.begin():
                    yield session
            else:
                async with session.begin():
                    yield session
        except Exception:
            await session.rollback()
            raise


# Backward-compatible alias used across hawkfi_trader.
get_db = session_scope


# Initialize defaults on import
configure_engine()


async def close_db():
    """Close database engine and all connections."""
    await dispose_engine()
    logger.info("Database connections closed.")
