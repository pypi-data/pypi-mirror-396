"""
Example usage of PreSignalRepository.

This example demonstrates how to use the PreSignalRepository to manage
pre-signals in the database.
"""

import asyncio
from prisma_web3_py import get_db
from prisma_web3_py.models import PreSignal, SignalStatus
from prisma_web3_py.repositories import PreSignalRepository


async def main():
    """Main example function."""

    # Initialize repository
    pre_signal_repo = PreSignalRepository()

    # Example 1: Create a new pre-signal
    print("=== Creating a new pre-signal ===")
    async with get_db() as session:
        pre_signal = await pre_signal_repo.create_pre_signal(
            session=session,
            source="telegram",
            chain="ethereum",
            token_address="0x1234567890abcdef1234567890abcdef12345678",
            signal_type="bullish",
            channel_calls=5,
            multi_signals=3,
            kol_discussions=2,
            token_narrative="Strong community support and upcoming partnership announcement"
        )

        if pre_signal:
            print(f"Created pre-signal with ID: {pre_signal.id}")
            print(f"Status: {pre_signal.status}")
            print(f"Signal Type: {pre_signal.signal_type}")

        await session.commit()

    # Example 2: Get recent pre-signals
    print("\n=== Getting recent pre-signals (last 24 hours) ===")
    async with get_db() as session:
        recent_signals = await pre_signal_repo.get_recent_pre_signals(
            session=session,
            hours=24,
            limit=10,
            status=SignalStatus.OPEN
        )

        print(f"Found {len(recent_signals)} recent pre-signals")
        for signal in recent_signals[:3]:  # Show first 3
            print(f"- ID: {signal.id}, Type: {signal.signal_type}, Source: {signal.source}")

    # Example 3: Get pre-signals by token
    print("\n=== Getting pre-signals for a specific token ===")
    async with get_db() as session:
        token_signals = await pre_signal_repo.get_pre_signals_by_token(
            session=session,
            chain="ethereum",
            token_address="0x1234567890abcdef1234567890abcdef12345678",
            hours=48,
            status=SignalStatus.OPEN
        )

        print(f"Found {len(token_signals)} pre-signals for this token")
        for signal in token_signals:
            print(f"- ID: {signal.id}, Created: {signal.created_at}")

    # Example 4: Get pre-signal counts by type
    print("\n=== Getting pre-signal counts by type ===")
    async with get_db() as session:
        counts = await pre_signal_repo.get_pre_signal_counts_by_type(
            session=session,
            hours=24,
            status=SignalStatus.OPEN
        )

        print("Pre-signal counts by type (last 24 hours):")
        for signal_type, count in counts.items():
            print(f"- {signal_type}: {count}")

    # Example 5: Get trending tokens by pre-signals
    print("\n=== Getting trending tokens by pre-signals ===")
    async with get_db() as session:
        trending = await pre_signal_repo.get_trending_tokens_by_pre_signals(
            session=session,
            hours=24,
            limit=10,
            status=SignalStatus.OPEN
        )

        print(f"Top {len(trending)} trending tokens by pre-signals:")
        for token, count in trending[:5]:  # Show top 5
            print(f"- {token.symbol} ({token.chain}): {count} pre-signals")

    # Example 6: Get pre-signals by source
    print("\n=== Getting pre-signals from Telegram ===")
    async with get_db() as session:
        telegram_signals = await pre_signal_repo.get_pre_signals_by_source(
            session=session,
            source="telegram",
            hours=24,
            limit=10,
            status=SignalStatus.OPEN
        )

        print(f"Found {len(telegram_signals)} pre-signals from Telegram")
        for signal in telegram_signals[:3]:  # Show first 3
            print(f"- ID: {signal.id}, Type: {signal.signal_type}, Token: {signal.token_address}")

    # Example 7: Get pre-signal with token details
    print("\n=== Getting pre-signal with token details ===")
    if pre_signal:
        async with get_db() as session:
            detailed_signal = await pre_signal_repo.get_pre_signal_with_token(
                session=session,
                signal_id=pre_signal.id
            )

            if detailed_signal and detailed_signal.token:
                print(f"Pre-signal ID: {detailed_signal.id}")
                print(f"Token: {detailed_signal.token.symbol} ({detailed_signal.token.name})")
                print(f"Chain: {detailed_signal.token.chain}")
                print(f"Signal Type: {detailed_signal.signal_type}")
                print(f"Channel Calls: {detailed_signal.channel_calls}")
                print(f"Multi Signals: {detailed_signal.multi_signals}")
                print(f"KOL Discussions: {detailed_signal.kol_discussions}")

    # Example 8: Update pre-signal status
    print("\n=== Updating pre-signal status ===")
    if pre_signal:
        async with get_db() as session:
            success = await pre_signal_repo.update_pre_signal_status(
                session=session,
                signal_id=pre_signal.id,
                status=SignalStatus.CLOSED
            )

            if success:
                print(f"Successfully updated pre-signal {pre_signal.id} to CLOSED")
                await session.commit()
            else:
                print("Failed to update pre-signal status")

    # Example 9: Using base repository methods
    print("\n=== Using base repository methods ===")
    async with get_db() as session:
        # Get by ID
        signal = await pre_signal_repo.get_by_id(session, pre_signal.id if pre_signal else 1)
        if signal:
            print(f"Retrieved signal by ID: {signal.id}")

        # Count signals
        count = await pre_signal_repo.count(
            session,
            chain="ethereum",
            signal_type="bullish"
        )
        print(f"Total bullish pre-signals on Ethereum: {count}")

        # Filter by criteria
        filtered = await pre_signal_repo.filter_by(
            session,
            source="telegram",
            status=SignalStatus.OPEN,
            limit=5
        )
        print(f"Found {len(filtered)} open pre-signals from Telegram")


if __name__ == "__main__":
    asyncio.run(main())
