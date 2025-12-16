"""
Async usage examples for prisma-web3-py package.
This demonstrates how to use the package in async Python projects.
"""

import asyncio
from prisma_web3_py import get_db, init_db
from prisma_web3_py.models import Token, Signal
from prisma_web3_py.repositories import TokenRepository, SignalRepository


async def example_query_tokens():
    """Query tokens using repository pattern."""
    print("\n=== Example: Query Tokens ===")

    token_repo = TokenRepository()

    async with get_db() as session:
        # Get token by address
        token = await token_repo.get_by_address(
            session,
            chain="ethereum",
            token_address="0x..."
        )
        if token:
            print(f"Found token: {token.symbol} ({token.name})")
        else:
            print("Token not found")

        # Get top scored tokens
        top_tokens = await token_repo.get_top_scored_tokens(
            session,
            chain="ethereum",
            min_score=50.0,
            limit=10
        )
        print(f"\nTop {len(top_tokens)} tokens:")
        for token in top_tokens:
            print(f"  - {token.symbol}: {token.score}")

        # Search tokens
        search_results = await token_repo.search_tokens(
            session,
            search_term="ETH",
            limit=5
        )
        print(f"\nSearch results for 'ETH': {len(search_results)} found")


async def example_upsert_token():
    """Insert or update token information."""
    print("\n=== Example: Upsert Token ===")

    token_repo = TokenRepository()

    async with get_db() as session:
        token_data = {
            "chain": "ethereum",
            "token_address": "0x1234567890abcdef",
            "symbol": "TEST",
            "name": "Test Token",
            "decimals": 18,
            "website": "https://example.com",
        }

        token_id = await token_repo.upsert_token(session, token_data)
        if token_id:
            print(f"Token upserted successfully with ID: {token_id}")
        else:
            print("Failed to upsert token")


async def example_query_signals():
    """Query recent trading signals."""
    print("\n=== Example: Query Signals ===")

    signal_repo = SignalRepository()

    async with get_db() as session:
        # Get recent buy signals
        recent_signals = await signal_repo.get_recent_signals(
            session,
            signal_type="buy",
            hours=24,
            limit=10
        )
        print(f"Found {len(recent_signals)} recent buy signals")

        # Get signal counts by type
        signal_counts = await signal_repo.get_signal_counts_by_type(
            session,
            hours=24
        )
        print(f"\nSignal counts (last 24h):")
        for signal_type, count in signal_counts.items():
            print(f"  {signal_type}: {count}")


async def example_upsert_signal():
    """Create or update a signal."""
    print("\n=== Example: Upsert Signal ===")

    signal_repo = SignalRepository()

    async with get_db() as session:
        signal = await signal_repo.upsert_signal(
            session,
            chain="ethereum",
            token_address="0x1234567890abcdef",
            source="dexscreener",
            signal_type="buy",
            is_first=False
        )
        if signal:
            print(f"Signal upserted: ID={signal.id}, occurrences={signal.occurrence_count}")
        else:
            print("Failed to upsert signal")


async def example_trending_tokens():
    """Get trending tokens by signal frequency."""
    print("\n=== Example: Trending Tokens ===")

    signal_repo = SignalRepository()

    async with get_db() as session:
        trending = await signal_repo.get_trending_tokens_by_signals(
            session,
            hours=24,
            limit=10
        )
        print(f"Top {len(trending)} trending tokens (last 24h):")
        for token, signal_count in trending:
            print(f"  {token.symbol} ({token.chain}): {signal_count} signals")


async def example_complex_operations():
    """Example of complex multi-step operations."""
    print("\n=== Example: Complex Operations ===")

    token_repo = TokenRepository()
    signal_repo = SignalRepository()

    async with get_db() as session:
        # Step 1: Upsert a token
        token_data = {
            "chain": "solana",
            "token_address": "SoL1234...",
            "symbol": "SOL",
            "name": "Solana",
            "decimals": 9,
        }
        token_id = await token_repo.upsert_token(session, token_data)
        print(f"1. Token created/updated: ID={token_id}")

        # Step 2: Add a signal for the token
        signal = await signal_repo.upsert_signal(
            session,
            chain="solana",
            token_address="SoL1234...",
            source="telegram",
            signal_type="buy"
        )
        print(f"2. Signal added: ID={signal.id if signal else 'N/A'}")

        # Step 3: Update token score
        success = await token_repo.update_token_score(
            session,
            chain="solana",
            token_address="SoL1234...",
            score=75.5,
            signal_score=80.0
        )
        print(f"3. Token score updated: {success}")

        # Commit all changes
        await session.commit()
        print("4. All changes committed successfully")


async def main():
    """Run all examples."""
    print("=== Prisma Web3 Python Package - Async Examples ===")
    print("Note: Make sure DATABASE_URL is set in your environment")

    try:
        # Initialize database (optional, only needed for first run)
        # await init_db()

        # Run examples
        await example_query_tokens()
        await example_upsert_token()
        await example_query_signals()
        await example_upsert_signal()
        await example_trending_tokens()
        await example_complex_operations()

        print("\n=== All examples completed successfully ===")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
