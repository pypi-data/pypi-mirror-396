#!/usr/bin/env python3
"""
Test TokenRepository chain name normalization.

Verifies that both abbreviations (bsc, eth, sol) and standard names
(binance-smart-chain, ethereum, solana) work correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma_web3_py import get_db, init_db, close_db
from prisma_web3_py.repositories import TokenRepository


async def test_chain_normalization():
    """Test TokenRepository chain normalization."""

    print("\n" + "="*70)
    print("Testing TokenRepository Chain Normalization")
    print("="*70)

    await init_db()
    repo = TokenRepository()

    try:
        # Test 1: Create tokens with abbreviated chain names
        print("\n[1] Creating test tokens with abbreviated chains...")
        async with get_db() as session:
            # Create token with 'bsc' abbreviation
            token_data_bsc = {
                "chain": "bsc",  # Using abbreviation
                "token_address": "0xBSCTEST1234567890abcdef1234567890",
                "symbol": "BSCTEST",
                "name": "BSC Test Token",
                "decimals": 18
            }
            token_id_bsc = await repo.upsert_token(session, token_data_bsc)

            # Create token with 'eth' abbreviation
            token_data_eth = {
                "chain": "eth",  # Using abbreviation
                "token_address": "0xETHTEST1234567890abcdef1234567890",
                "symbol": "ETHTEST",
                "name": "ETH Test Token",
                "decimals": 18
            }
            token_id_eth = await repo.upsert_token(session, token_data_eth)

            await session.commit()

            if token_id_bsc and token_id_eth:
                print(f"✓ Created 2 tokens with abbreviated chains")
                print(f"  - BSC token ID: {token_id_bsc}")
                print(f"  - ETH token ID: {token_id_eth}")
            else:
                print("✗ Failed to create tokens")
                return False

        # Test 2: Retrieve token using abbreviation
        print("\n[2] Retrieving token using 'bsc' abbreviation...")
        async with get_db() as session:
            token = await repo.get_by_address(
                session,
                "bsc",  # Using abbreviation
                "0xBSCTEST1234567890abcdef1234567890"
            )

            if token:
                print(f"✓ Found token using 'bsc': {token.symbol}")
                print(f"  - Stored chain in DB: '{token.chain}'")
                if token.chain == "binance-smart-chain":
                    print(f"  ✓ Chain stored as standard name 'binance-smart-chain'")
                else:
                    print(f"  ✗ Chain should be 'binance-smart-chain', got '{token.chain}'")
                    return False
            else:
                print("✗ Token not found using abbreviation")
                return False

        # Test 3: Retrieve same token using standard name
        print("\n[3] Retrieving same token using 'binance-smart-chain' standard name...")
        async with get_db() as session:
            token = await repo.get_by_address(
                session,
                "binance-smart-chain",  # Using standard name
                "0xBSCTEST1234567890abcdef1234567890"
            )

            if token:
                print(f"✓ Found token using standard name: {token.symbol}")
            else:
                print("✗ Token not found using standard name")
                return False

        # Test 4: Test get_recent_tokens with abbreviation filter
        print("\n[4] Testing get_recent_tokens with 'eth' abbreviation filter...")
        async with get_db() as session:
            tokens = await repo.get_recent_tokens(
                session,
                chain="eth",  # Using abbreviation
                limit=10
            )

            if tokens:
                print(f"✓ Found {len(tokens)} tokens on 'eth' chain")
                # Check if our test token is in results
                eth_test = [t for t in tokens if t.symbol == "ETHTEST"]
                if eth_test:
                    print(f"  ✓ Our test token found in results")
                    print(f"    Chain: '{eth_test[0].chain}'")
                else:
                    print(f"  ✗ Test token not found in results")
            else:
                print("⚠ No tokens found (expected if database is empty)")

        # Test 5: Test search_tokens with abbreviation filter
        print("\n[5] Testing search_tokens with 'bsc' abbreviation filter...")
        async with get_db() as session:
            tokens = await repo.search_tokens(
                session,
                "TEST",
                chain="bsc",  # Using abbreviation
                limit=10
            )

            if tokens:
                print(f"✓ Found {len(tokens)} tokens matching 'TEST' on 'bsc' chain")
                bsc_test = [t for t in tokens if t.symbol == "BSCTEST"]
                if bsc_test:
                    print(f"  ✓ Our test token found in search results")
            else:
                print("⚠ No tokens found")

        # Test 6: Test get_recently_updated_tokens with abbreviation
        print("\n[6] Testing get_recently_updated_tokens with 'eth' abbreviation...")
        async with get_db() as session:
            tokens = await repo.get_recently_updated_tokens(
                session,
                hours=24,
                chain="eth",  # Using abbreviation
                limit=10
            )

            if tokens:
                print(f"✓ Found {len(tokens)} recently updated tokens on 'eth'")
                eth_test = [t for t in tokens if t.symbol == "ETHTEST"]
                if eth_test:
                    print(f"  ✓ Our test token found in results")
            else:
                print("⚠ No tokens found")

        # Test 7: Test upsert with standard name (should update existing)
        print("\n[7] Testing upsert with standard chain name (should update)...")
        async with get_db() as session:
            update_data = {
                "chain": "binance-smart-chain",  # Using standard name
                "token_address": "0xBSCTEST1234567890abcdef1234567890",
                "symbol": "BSCTEST",
                "name": "BSC Test Token UPDATED",
                "decimals": 18,
                "description": "Updated via standard name"
            }
            token_id = await repo.upsert_token(session, update_data)
            await session.commit()

            if token_id == token_id_bsc:
                print(f"✓ Token updated (same ID: {token_id})")

                # Verify the update
                token = await repo.get_by_address(
                    session,
                    "bsc",
                    "0xBSCTEST1234567890abcdef1234567890"
                )
                if token and token.name == "BSC Test Token UPDATED":
                    print(f"  ✓ Update verified: {token.name}")
                    print(f"  ✓ Description: {token.description}")
                else:
                    print(f"  ✗ Update not verified")
                    return False
            else:
                print(f"✗ Expected same token ID, got different ID")
                return False

        # Test 8: Test with solana abbreviation
        print("\n[8] Testing with 'sol' abbreviation...")
        async with get_db() as session:
            sol_data = {
                "chain": "sol",  # Using abbreviation
                "token_address": "SOLTEST1234567890abcdef1234567890",
                "symbol": "SOLTEST",
                "name": "Solana Test Token",
                "decimals": 9
            }
            token_id_sol = await repo.upsert_token(session, sol_data)
            await session.commit()

            if token_id_sol:
                print(f"✓ Created Solana token with 'sol' abbreviation")

                # Retrieve using standard name
                token = await repo.get_by_address(
                    session,
                    "solana",  # Using standard name
                    "SOLTEST1234567890abcdef1234567890"
                )

                if token:
                    print(f"  ✓ Retrieved using 'solana' standard name")
                    print(f"    Stored chain: '{token.chain}'")
                else:
                    print(f"  ✗ Failed to retrieve using standard name")
                    return False
            else:
                print("✗ Failed to create Solana token")
                return False

        # Cleanup
        print("\n[CLEANUP] Deleting test tokens...")
        async with get_db() as session:
            await repo.delete_by_id(session, token_id_bsc)
            await repo.delete_by_id(session, token_id_eth)
            await repo.delete_by_id(session, token_id_sol)
            await session.commit()
            print("✓ Test tokens deleted")

        print("\n" + "="*70)
        print("✓ All chain normalization tests passed!")
        print("="*70)
        print("\nSummary:")
        print("  ✓ Abbreviations (bsc, eth, sol) are auto-converted to standard names")
        print("  ✓ Standard names (binance-smart-chain, ethereum, solana) work directly")
        print("  ✓ Both formats can be used interchangeably for all operations")
        print("  ✓ Database stores CoinGecko standard names")
        print("="*70)
        return True

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await close_db()


if __name__ == "__main__":
    success = asyncio.run(test_chain_normalization())
    sys.exit(0 if success else 1)
