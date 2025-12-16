"""
Test script for PreSignal model and PreSignalRepository.
Tests actual database read/write operations.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma_web3_py import get_db, init_db, close_db
from prisma_web3_py.models import PreSignal, SignalStatus, Token
from prisma_web3_py.repositories import PreSignalRepository, TokenRepository


async def test_pre_signal_operations():
    """Test PreSignal CRUD operations."""

    print("\n" + "="*60)
    print("Testing PreSignal Model and Repository")
    print("="*60)

    # Initialize database
    await init_db()

    pre_signal_repo = PreSignalRepository()
    token_repo = TokenRepository()

    # Test data
    test_chain = "ethereum"
    test_address = "0xTESTPRESIG123456789abcdef1234567890abc"
    test_token = None
    test_pre_signal_id = None

    try:
        # Setup: Create a test token first
        print("\n[SETUP] Creating test token...")
        async with get_db() as session:
            test_token = await token_repo.create(
                session,
                chain=test_chain,
                token_address=test_address,
                symbol="TPRE",
                name="Test PreSignal Token"
            )
            await session.commit()
            print(f"✓ Test token created: {test_token.symbol}")

        # Test 1: Create a new pre-signal
        print("\n[1] Creating a new pre-signal...")
        async with get_db() as session:
            pre_signal = await pre_signal_repo.create_pre_signal(
                session,
                source="telegram",
                chain=test_chain,
                token_address=test_address,
                signal_type="bullish",
                channel_calls=5,
                multi_signals=3,
                kol_discussions=2,
                token_narrative="Strong community support and upcoming partnership"
            )
            await session.commit()

            if pre_signal:
                print(f"✓ PreSignal created: ID={pre_signal.id}")
                print(f"  Type: {pre_signal.signal_type}, Status: {pre_signal.status.value}")
                print(f"  Metrics: calls={pre_signal.channel_calls}, "
                      f"multi={pre_signal.multi_signals}, kol={pre_signal.kol_discussions}")
                test_pre_signal_id = pre_signal.id
            else:
                print("✗ Failed to create pre-signal")
                return False

        # Test 2: Get pre-signal by ID
        print("\n[2] Getting pre-signal by ID...")
        async with get_db() as session:
            pre_signal = await pre_signal_repo.get_by_id(session, test_pre_signal_id)
            if pre_signal:
                print(f"✓ PreSignal retrieved: {pre_signal.signal_type} from {pre_signal.source}")
            else:
                print("✗ Failed to retrieve pre-signal")
                return False

        # Test 3: Get pre-signal with token relationship
        print("\n[3] Getting pre-signal with token relationship...")
        async with get_db() as session:
            pre_signal = await pre_signal_repo.get_pre_signal_with_token(
                session,
                test_pre_signal_id
            )
            if pre_signal and pre_signal.token:
                print(f"✓ PreSignal with token loaded")
                print(f"  Token: {pre_signal.token.symbol} ({pre_signal.token.name})")
            else:
                print("⚠ Token relationship not loaded")

        # Test 4: Create another pre-signal with different source
        print("\n[4] Creating another pre-signal (Twitter)...")
        async with get_db() as session:
            pre_signal2 = await pre_signal_repo.create_pre_signal(
                session,
                source="twitter",
                chain=test_chain,
                token_address=test_address,
                signal_type="neutral",
                channel_calls=2,
                multi_signals=1,
                kol_discussions=1
            )
            await session.commit()
            print(f"✓ Second PreSignal created: ID={pre_signal2.id}")

        # Test 5: Get pre-signals by token
        print("\n[5] Getting pre-signals by token...")
        async with get_db() as session:
            pre_signals = await pre_signal_repo.get_pre_signals_by_token(
                session,
                chain=test_chain,
                token_address=test_address
            )
            print(f"✓ Found {len(pre_signals)} pre-signals for token")
            for ps in pre_signals:
                print(f"  - {ps.source}: {ps.signal_type} (status: {ps.status.value})")

        # Test 6: Get pre-signals by token with time filter
        print("\n[6] Getting recent pre-signals for token (last 24h)...")
        async with get_db() as session:
            pre_signals = await pre_signal_repo.get_pre_signals_by_token(
                session,
                chain=test_chain,
                token_address=test_address,
                hours=24
            )
            print(f"✓ Found {len(pre_signals)} pre-signals in last 24h")

        # Test 7: Get recent pre-signals globally
        print("\n[7] Getting recent pre-signals globally...")
        async with get_db() as session:
            pre_signals = await pre_signal_repo.get_recent_pre_signals(
                session,
                hours=24,
                limit=10
            )
            print(f"✓ Found {len(pre_signals)} recent pre-signals")

        # Test 8: Get recent pre-signals by type
        print("\n[8] Getting recent bullish pre-signals...")
        async with get_db() as session:
            pre_signals = await pre_signal_repo.get_recent_pre_signals(
                session,
                hours=24,
                signal_types=["bullish"],
                limit=10
            )
            print(f"✓ Found {len(pre_signals)} recent bullish pre-signals")

        # Test 9: Get pre-signals by source
        print("\n[9] Getting pre-signals from Telegram...")
        async with get_db() as session:
            pre_signals = await pre_signal_repo.get_pre_signals_by_source(
                session,
                source="telegram",
                hours=24,
                limit=10
            )
            print(f"✓ Found {len(pre_signals)} pre-signals from Telegram")

        # Test 10: Get pre-signal counts by type
        print("\n[10] Getting pre-signal counts by type...")
        async with get_db() as session:
            counts = await pre_signal_repo.get_pre_signal_counts_by_type(
                session,
                hours=24
            )
            print(f"✓ PreSignal counts by type:")
            for signal_type, count in counts.items():
                print(f"  - {signal_type}: {count}")

        # Test 11: Get trending tokens by pre-signals
        print("\n[11] Getting trending tokens by pre-signals...")
        async with get_db() as session:
            trending = await pre_signal_repo.get_trending_tokens_by_pre_signals(
                session,
                hours=24,
                limit=5
            )
            print(f"✓ Found {len(trending)} trending tokens")
            for token, count in trending[:3]:
                print(f"  - {token.symbol or 'N/A'} ({token.chain}): {count} pre-signals")

        # Test 12: Update pre-signal status
        print("\n[12] Updating pre-signal status to CLOSED...")
        async with get_db() as session:
            success = await pre_signal_repo.update_pre_signal_status(
                session,
                test_pre_signal_id,
                SignalStatus.CLOSED
            )
            await session.commit()

            if success:
                print("✓ PreSignal status updated")

                # Verify update
                pre_signal = await pre_signal_repo.get_by_id(session, test_pre_signal_id)
                print(f"  New status: {pre_signal.status.value}")
            else:
                print("✗ Failed to update status")

        # Test 13: Get pre-signals by status
        print("\n[13] Getting OPEN pre-signals...")
        async with get_db() as session:
            pre_signals = await pre_signal_repo.get_pre_signals_by_token(
                session,
                chain=test_chain,
                token_address=test_address,
                status=SignalStatus.OPEN
            )
            print(f"✓ Found {len(pre_signals)} OPEN pre-signals")

        # Test 14: Test to_dict method
        print("\n[14] Testing to_dict method...")
        async with get_db() as session:
            pre_signal = await pre_signal_repo.get_by_id(session, test_pre_signal_id)
            pre_signal_dict = pre_signal.to_dict()
            print(f"✓ PreSignal converted to dict: {len(pre_signal_dict)} fields")
            print(f"  Sample fields: source={pre_signal_dict.get('source')}, "
                  f"status={pre_signal_dict.get('status')}")

        # Clean up: Delete test pre-signals and token
        print("\n[CLEANUP] Deleting test data...")
        async with get_db() as session:
            pre_signals = await pre_signal_repo.get_pre_signals_by_token(
                session,
                chain=test_chain,
                token_address=test_address
            )

            for ps in pre_signals:
                await pre_signal_repo.delete_by_id(session, ps.id)
            print(f"✓ Deleted {len(pre_signals)} test pre-signals")

            if test_token:
                await token_repo.delete_by_id(session, test_token.id)
                print(f"✓ Deleted test token")

            await session.commit()

        print("\n" + "="*60)
        print("✓ All PreSignal tests passed!")
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
    success = asyncio.run(test_pre_signal_operations())
    sys.exit(0 if success else 1)
