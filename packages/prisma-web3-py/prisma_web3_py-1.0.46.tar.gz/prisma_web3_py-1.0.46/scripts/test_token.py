"""
Test script for Token model and TokenRepository.
Tests actual database read/write operations.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma_web3_py import get_db, init_db, close_db
from prisma_web3_py.models import Token
from prisma_web3_py.repositories import TokenRepository


async def test_token_operations():
    """Test Token CRUD operations."""

    print("\n" + "="*60)
    print("Testing Token Model and Repository")
    print("="*60)

    # Initialize database
    await init_db()

    repo = TokenRepository()
    test_chain = "ethereum"
    test_address = "0xTEST1234567890abcdef1234567890abcdef1234"

    try:
        # Test 1: Create a new token
        print("\n[1] Creating a new token...")
        async with get_db() as session:
            token = await repo.create(
                session,
                chain=test_chain,
                token_address=test_address,
                symbol="TEST",
                name="Test Token",
                decimals=18,
                description="A test token for validation",
                coingecko_id="test-token",
                platforms={"polygon": "0xPOLYGON123", "arbitrum": "0xARBITRUM123"},
                categories=["DeFi", "Testing"],
                github="https://github.com/test/token",
                discord="https://discord.gg/test"
            )
            await session.commit()

            if token:
                print(f"✓ Token created successfully: ID={token.id}, Symbol={token.symbol}")
                token_id = token.id
            else:
                print("✗ Failed to create token")
                return False

        # Test 2: Get token by ID
        print("\n[2] Getting token by ID...")
        async with get_db() as session:
            token = await repo.get_by_id(session, token_id)
            if token:
                print(f"✓ Token retrieved: {token.symbol} ({token.name})")
                print(f"  Chain: {token.chain}, Address: {token.token_address}")
            else:
                print("✗ Failed to retrieve token")
                return False

        # Test 3: Get token by chain and address (using specialized method)
        print("\n[3] Getting token by chain and address...")
        async with get_db() as session:
            token = await repo.get_by_address(
                session,
                test_chain,
                test_address
            )
            if token:
                print(f"✓ Token found: {token.symbol}")
            else:
                print("✗ Failed to find token by chain and address")
                return False

        # Test 4: Update token
        print("\n[4] Updating token...")
        async with get_db() as session:
            success = await repo.update_by_id(
                session,
                token_id,
                description="Updated test token description",
                twitter="@testtoken"
            )
            await session.commit()

            if success:
                print("✓ Token updated successfully")

                # Verify update
                token = await repo.get_by_id(session, token_id)
                print(f"  New description: {token.description}")
                print(f"  Twitter: {token.twitter}")
            else:
                print("✗ Failed to update token")
                return False

        # Test 5: Get all tokens (with limit)
        print("\n[5] Getting all tokens (limited to 5)...")
        async with get_db() as session:
            tokens = await repo.get_all(session, limit=5)
            print(f"✓ Retrieved {len(tokens)} tokens")
            for t in tokens[:3]:
                print(f"  - {t.symbol or 'N/A'} on {t.chain}")

        # Test 6: Filter tokens
        print("\n[6] Filtering tokens by chain...")
        async with get_db() as session:
            tokens = await repo.filter_by(session, chain=test_chain, limit=5)
            print(f"✓ Found {len(tokens)} tokens on {test_chain}")

        # Test 7: Count tokens
        print("\n[7] Counting tokens...")
        async with get_db() as session:
            count = await repo.count(session, chain=test_chain)
            print(f"✓ Total tokens on {test_chain}: {count}")

        # Test 8: Search tokens (if method exists)
        print("\n[8] Searching tokens by symbol...")
        async with get_db() as session:
            tokens = await repo.search_tokens(session, "TEST", limit=5)
            print(f"✓ Found {len(tokens)} tokens matching 'TEST'")
            for t in tokens[:3]:
                print(f"  - {t.symbol} ({t.name})")

        # Test 9: Get recently updated tokens
        print("\n[9] Getting recently updated tokens...")
        async with get_db() as session:
            tokens = await repo.get_recently_updated_tokens(session, hours=24, limit=5)
            print(f"✓ Found {len(tokens)} recently updated tokens")

        # Test 10: Test to_dict and helper methods
        print("\n[10] Testing to_dict and helper methods...")
        async with get_db() as session:
            token = await repo.get_by_id(session, token_id)
            token_dict = token.to_dict()
            print(f"✓ Token converted to dict: {len(token_dict)} fields")
            print(f"  Sample fields: symbol={token_dict.get('symbol')}, "
                  f"name={token_dict.get('name')}")

            # Test helper methods
            print(f"  All chains: {token.get_all_chains()}")
            print(f"  Address on polygon: {token.get_address_on_chain('polygon')}")
            print(f"  Social links: {list(token.get_social_links().keys())}")
            print(f"  Is mainnet token: {token.is_mainnet_token()}")

        # Clean up: Delete test token
        print("\n[CLEANUP] Deleting test token...")
        async with get_db() as session:
            success = await repo.delete_by_id(session, token_id)
            await session.commit()

            if success:
                print("✓ Test token deleted successfully")
            else:
                print("⚠ Failed to delete test token (may need manual cleanup)")

        print("\n" + "="*60)
        print("✓ All Token tests passed!")
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
    success = asyncio.run(test_token_operations())
    sys.exit(0 if success else 1)
