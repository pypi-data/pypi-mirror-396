"""
Master test script - runs all database tests for prisma-web3-py.
This script validates that all models and repositories work correctly with the database.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma_web3_py import init_db, close_db
from prisma_web3_py.config import config


async def check_database_connection():
    """Check if database is accessible."""
    print("\n" + "="*60)
    print("Checking Database Connection")
    print("="*60)
    try:
        db_url = config.database_url
        print(f"Database URL: {db_url[:50]}...")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return False

    try:
        await init_db()
        print("✓ Database connection successful!")
        await close_db()
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


async def run_test_module(module_name, test_function_name):
    """Import and run a test module."""
    try:
        # Import the module dynamically
        module = __import__(f"scripts.{module_name}", fromlist=[test_function_name])
        test_function = getattr(module, test_function_name)

        # Run the test
        result = await test_function()
        return result
    except Exception as e:
        print(f"\n✗ Failed to run {module_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""

    print("\n" + "="*70)
    print(" "*15 + "PRISMA-WEB3-PY TEST SUITE")
    print(" "*20 + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)

    # Check database connection first
    if not await check_database_connection():
        print("\n✗ Cannot proceed - database connection failed!")
        print("Please check your .env file and database configuration.")
        return False

    # List of tests to run
    tests = [
        ("test_token", "test_token_operations"),
        ("test_signal", "test_signal_operations"),
        ("test_pre_signal", "test_pre_signal_operations"),
    ]

    results = {}

    # Run all tests
    for module_name, function_name in tests:
        print("\n" + "-"*70)
        try:
            result = await run_test_module(module_name, function_name)
            results[module_name] = result
        except Exception as e:
            print(f"\n✗ Error running {module_name}: {e}")
            results[module_name] = False

    # Print summary
    print("\n" + "="*70)
    print(" "*25 + "TEST SUMMARY")
    print("="*70)

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status:12} | {test_name}")

    print("-"*70)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    print("="*70)

    if failed == 0:
        print("\n🎉 All tests passed! The database integration is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
