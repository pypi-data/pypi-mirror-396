"""
Simple database connection test.
Verifies that the database configuration is correct and accessible.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma_web3_py import get_db, init_db, close_db
from prisma_web3_py.config import config
from sqlalchemy import text


async def test_connection():
    """Test basic database connection and query."""

    print("\n" + "="*60)
    print("Database Connection Test")
    print("="*60)

    # Show configuration (masked)
    try:
        db_url = config.database_url
    except ValueError as e:
        print(f"\n✗ {e}")
        return False
    if db_url:
        # Mask password in URL
        parts = db_url.split('@')
        if len(parts) > 1:
            user_pass = parts[0].split('://')[-1]
            if ':' in user_pass:
                user = user_pass.split(':')[0]
                masked_url = db_url.replace(user_pass, f"{user}:****")
            else:
                masked_url = db_url
        else:
            masked_url = db_url[:50] + "..."

        print(f"\nDatabase URL: {masked_url}")
    else:
        print("\n✗ DATABASE_URL not configured!")
        return False

    try:
        # Test 1: Initialize database
        print("\n[1] Initializing database connection...")
        await init_db()
        print("✓ Database engine created")

        # Test 2: Execute simple query
        print("\n[2] Testing query execution...")
        async with get_db() as session:
            result = await session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✓ Query executed successfully")
            else:
                print("✗ Query returned unexpected result")
                return False

        # Test 3: Check if Token table exists
        print("\n[3] Checking if Token table exists...")
        async with get_db() as session:
            result = await session.execute(
                text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'Token'
                    )
                """)
            )
            exists = result.scalar()
            if exists:
                print("✓ Token table found")
            else:
                print("⚠ Token table not found - database may need migration")

        # Test 4: Count tokens (if table exists)
        if exists:
            print("\n[4] Counting tokens in database...")
            async with get_db() as session:
                result = await session.execute(
                    text('SELECT COUNT(*) FROM "Token"')
                )
                count = result.scalar()
                print(f"✓ Found {count} tokens in database")

        # Test 5: Check other tables
        print("\n[5] Checking other tables...")
        tables_to_check = ['Signal', 'PreSignal', 'TokenMetrics', 'TokenAnalysisReport']
        async with get_db() as session:
            for table_name in tables_to_check:
                result = await session.execute(
                    text(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_schema = 'public'
                            AND table_name = '{table_name}'
                        )
                    """)
                )
                exists = result.scalar()
                status = "✓" if exists else "✗"
                print(f"  {status} {table_name}")

        print("\n" + "="*60)
        print("✓ Database connection test completed successfully!")
        print("="*60)
        return True

    except Exception as e:
        print(f"\n✗ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await close_db()


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
