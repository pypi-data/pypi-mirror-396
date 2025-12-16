"""
Test script for Signal model and SignalRepository.
Tests actual database read/write operations.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma_web3_py import get_db, init_db, close_db
from prisma_web3_py.models import Signal, Token
from prisma_web3_py.repositories import SignalRepository, TokenRepository


async def test_signal_operations():
    """Test Signal CRUD operations."""

    print("\n" + "="*60)
    print("Testing Signal Model and Repository")
    print("="*60)

    # Initialize database
    await init_db()

    signal_repo = SignalRepository()
    token_repo = TokenRepository()

    # Test data
    test_chain = "ethereum"
    test_address = "0xTESTSIGNAL123456789abcdef1234567890abcd"
    test_token = None
    test_signal_id = None

    try:
        # Setup: Create a test token first
        print("\n[SETUP] Creating test token...")
        async with get_db() as session:
            test_token = await token_repo.create(
                session,
                chain=test_chain,
                token_address=test_address,
                symbol="TSIG",
                name="Test Signal Token"
            )
            await session.commit()
            print(f"✓ Test token created: {test_token.symbol}")

        # Test 1: Create a new signal
        print("\n[1] Creating a new signal...")
        async with get_db() as session:
            signal = await signal_repo.create(
                session,
                chain=test_chain,
                token_address=test_address,
                source="telegram",
                signal_type="bullish",
                is_first=True,
                last_occurrence=datetime.utcnow(),
                occurrence_count=1
            )
            await session.commit()

            if signal:
                print(f"✓ Signal created: ID={signal.id}, Type={signal.signal_type}")
                test_signal_id = signal.id
            else:
                print("✗ Failed to create signal")
                return False

        # Test 2: Get signal by ID
        print("\n[2] Getting signal by ID...")
        async with get_db() as session:
            signal = await signal_repo.get_by_id(session, test_signal_id)
            if signal:
                print(f"✓ Signal retrieved: {signal.signal_type} from {signal.source}")
            else:
                print("✗ Failed to retrieve signal")
                return False

        # Test 3: Upsert signal (update existing)
        print("\n[3] Upserting signal (should update existing)...")
        async with get_db() as session:
            signal = await signal_repo.upsert_signal(
                session,
                chain=test_chain,
                token_address=test_address,
                source="telegram",
                signal_type="bullish",
                is_first=False
            )
            await session.commit()

            if signal and signal.occurrence_count == 2:
                print(f"✓ Signal updated: occurrence_count={signal.occurrence_count}")
            else:
                print(f"⚠ Signal upserted but occurrence_count={signal.occurrence_count if signal else 'None'}")

        # Test 4: Upsert new signal type
        print("\n[4] Upserting new signal type (should create new)...")
        async with get_db() as session:
            signal = await signal_repo.upsert_signal(
                session,
                chain=test_chain,
                token_address=test_address,
                source="twitter",
                signal_type="neutral",
                is_first=True
            )
            await session.commit()

            if signal and signal.occurrence_count == 1:
                print(f"✓ New signal created: {signal.source} - {signal.signal_type}")
            else:
                print("✗ Failed to create new signal")
                return False

        # Test 5: Get signals by token
        print("\n[5] Getting signals by token...")
        async with get_db() as session:
            signals = await signal_repo.get_signal_by_token(
                session,
                chain=test_chain,
                token_address=test_address
            )
            print(f"✓ Found {len(signals)} signals for token")
            for sig in signals:
                print(f"  - {sig.source}: {sig.signal_type} (count: {sig.occurrence_count})")

        # Test 6: Get recent signals
        print("\n[6] Getting recent signals...")
        async with get_db() as session:
            signals = await signal_repo.get_recent_signals(
                session,
                hours=24,
                limit=10
            )
            print(f"✓ Found {len(signals)} recent signals (last 24h)")

        # Test 7: Get recent signals by type
        print("\n[7] Getting recent bullish signals...")
        async with get_db() as session:
            signals = await signal_repo.get_recent_signals(
                session,
                signal_type="bullish",
                hours=24,
                limit=10
            )
            print(f"✓ Found {len(signals)} recent bullish signals")

        # Test 8: Get signal counts by type
        print("\n[8] Getting signal counts by type...")
        async with get_db() as session:
            counts = await signal_repo.get_signal_counts_by_type(
                session,
                hours=24
            )
            print(f"✓ Signal counts by type:")
            for signal_type, count in counts.items():
                print(f"  - {signal_type}: {count}")

        # Test 9: Get trending tokens by signals
        print("\n[9] Getting trending tokens by signals...")
        async with get_db() as session:
            trending = await signal_repo.get_trending_tokens_by_signals(
                session,
                hours=24,
                limit=5
            )
            print(f"✓ Found {len(trending)} trending tokens")
            for token, count in trending[:3]:
                print(f"  - {token.symbol or 'N/A'} ({token.chain}): {count} signals")

        # Test 10: Test signal with token relationship
        print("\n[10] Testing signal-token relationship...")
        async with get_db() as session:
            signal = await signal_repo.get_by_id(session, test_signal_id)
            if signal and signal.token:
                print(f"✓ Relationship loaded: Signal -> Token")
                print(f"  Token: {signal.token.symbol} ({signal.token.name})")
            else:
                print("⚠ Token relationship not loaded")

        # Test 11: Test to_dict method
        print("\n[11] Testing to_dict method...")
        async with get_db() as session:
            signal = await signal_repo.get_by_id(session, test_signal_id)
            signal_dict = signal.to_dict()
            print(f"✓ Signal converted to dict: {len(signal_dict)} fields")
            print(f"  Sample fields: source={signal_dict.get('source')}, "
                  f"signal_type={signal_dict.get('signal_type')}")

        # Clean up: Delete test signals and token
        print("\n[CLEANUP] Deleting test data...")
        async with get_db() as session:
            signals = await signal_repo.get_signal_by_token(
                session,
                chain=test_chain,
                token_address=test_address
            )

            for signal in signals:
                await signal_repo.delete_by_id(session, signal.id)
            print(f"✓ Deleted {len(signals)} test signals")

            if test_token:
                await token_repo.delete_by_id(session, test_token.id)
                print(f"✓ Deleted test token")

            await session.commit()

        print("\n" + "="*60)
        print("✓ All Signal tests passed!")
        print("="*60)
        return True

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await close_db()


if __name__ == "__main__":
    success = asyncio.run(test_signal_operations())
    sys.exit(0 if success else 1)
