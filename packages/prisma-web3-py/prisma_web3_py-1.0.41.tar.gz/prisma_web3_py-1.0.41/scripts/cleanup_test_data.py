"""
Cleanup script to remove test data from the database.
Use this to clean up data from failed test runs.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma_web3_py import close_db, session_scope
from sqlalchemy import text


async def cleanup_test_data():
    """Remove all test data from database."""

    print("\n" + "="*60)
    print("Cleanup Test Data")
    print("="*60)

    try:
        async with session_scope() as session:
            # Delete test signals
            print("\n[1] Deleting test signals...")
            result = await session.execute(
                text("""
                    DELETE FROM "Signal"
                    WHERE token_address LIKE '0xTEST%'
                    OR token_address LIKE '0xtest%'
                """)
            )
            signal_count = result.rowcount
            print(f"✓ Deleted {signal_count} test signals")

            # Delete test pre-signals
            print("\n[2] Deleting test pre-signals...")
            result = await session.execute(
                text("""
                    DELETE FROM "PreSignal"
                    WHERE token_address LIKE '0xTEST%'
                    OR token_address LIKE '0xtest%'
                """)
            )
            pre_signal_count = result.rowcount
            print(f"✓ Deleted {pre_signal_count} test pre-signals")

            # Delete test tokens
            print("\n[3] Deleting test tokens...")
            result = await session.execute(
                text("""
                    DELETE FROM "Token"
                    WHERE token_address LIKE '0xTEST%'
                    OR token_address LIKE '0xtest%'
                    OR symbol IN ('TEST', 'TSIG', 'TPRE', 'ABC')
                """)
            )
            token_count = result.rowcount
            print(f"✓ Deleted {token_count} test tokens")

            # Delete AIAnalysisResult rows created by e2e tests
            print("\n[4] Deleting AIAnalysisResult test data...")
            result = await session.execute(
                text("""
                    DELETE FROM "AIAnalysisResult"
                    WHERE model_name = 'fake-llm'
                       OR analysis_version LIKE 'e2e%'
                       OR source_link LIKE 'https://example.com/%'
                """)
            )
            ai_count = result.rowcount
            print(f"✓ Deleted {ai_count} AIAnalysisResult rows")

            # Delete EventImpacts tied to removed analyses
            print("\n[5] Deleting EventImpacts linked to test analyses...")
            result = await session.execute(
                text("""
                    DELETE FROM "EventImpacts"
                    WHERE meta->>'analysis_id' IS NOT NULL
                      AND (
                        meta->>'analysis_id' NOT IN (
                          SELECT id::text FROM "AIAnalysisResult"
                        )
                        OR meta->>'analysis_id' IN (
                          SELECT id::text FROM "AIAnalysisResult"
                          WHERE model_name = 'fake-llm' OR analysis_version LIKE 'e2e%'
                        )
                      )
                """)
            )
            impacts_count = result.rowcount
            print(f"✓ Deleted {impacts_count} EventImpacts rows")

            # Delete EventLabels referencing removed events
            print("\n[6] Deleting EventLabels linked to test analyses...")
            result = await session.execute(
                text("""
                    DELETE FROM "EventLabels"
                    WHERE event_id NOT IN (SELECT id FROM "AIAnalysisResult")
                """)
            )
            labels_count = result.rowcount
            print(f"✓ Deleted {labels_count} EventLabels rows")

            print("\n" + "="*60)
            print("✓ Cleanup completed successfully!")
            total_removed = (
                signal_count
                + pre_signal_count
                + token_count
                + ai_count
                + impacts_count
                + labels_count
            )
            print(f"  Total items removed: {total_removed}")
            print("="*60)
            return True

    except Exception as e:
        print(f"\n✗ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await close_db()


if __name__ == "__main__":
    success = asyncio.run(cleanup_test_data())
    sys.exit(0 if success else 1)
