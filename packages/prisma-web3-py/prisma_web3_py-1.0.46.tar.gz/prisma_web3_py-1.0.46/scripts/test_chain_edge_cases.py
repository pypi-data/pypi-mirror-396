#!/usr/bin/env python3
"""
Test edge cases for chain normalization in TokenRepository.

Tests scenarios like:
1. Querying tokens on chains where they don't exist
2. Invalid chain names
3. Empty chain values
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma_web3_py import get_db, init_db, close_db
from prisma_web3_py.repositories import TokenRepository


async def test_edge_cases():
    """Test edge cases for chain normalization."""

    print("\n" + "="*70)
    print("Testing Chain Normalization Edge Cases")
    print("="*70)

    await init_db()
    repo = TokenRepository()

    try:
        # Setup: Create a UNI token on Ethereum only
        print("\n[SETUP] Creating UNI token on Ethereum...")
        async with get_db() as session:
            uni_data = {
                "chain": "ethereum",
                "token_address": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
                "symbol": "UNI",
                "name": "Uniswap",
                "coingecko_id": "uniswap",
                "decimals": 18,
                "platforms": {
                    "ethereum": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
                    "polygon-pos": "0xb33eaad8d922b1083446dc23f610c2567fb5180f",
                    "arbitrum-one": "0xfa7f8980b0f1e64a2062791cc3b0871572f1f7f0"
                }
            }
            uni_id = await repo.upsert_token(session, uni_data)
            await session.commit()
            print(f"✓ Created UNI token (ID: {uni_id}) on Ethereum")
            print(f"  Platforms: {list(uni_data['platforms'].keys())}")

        # Test 1: Query UNI on Solana (doesn't exist)
        print("\n[1] Query UNI on Solana (chain where it doesn't exist)...")
        async with get_db() as session:
            # 使用search_tokens查找sol链上的UNI
            tokens = await repo.search_tokens(
                session,
                "UNI",
                chain="sol",  # UNI doesn't exist on Solana
                limit=10
            )

            if len(tokens) == 0:
                print(f"✓ Correctly returned empty list (no UNI on Solana)")
                print(f"  Result: {tokens}")
            else:
                print(f"✗ Unexpectedly found {len(tokens)} tokens")
                return False

        # Test 2: Query UNI on Ethereum (exists)
        print("\n[2] Query UNI on Ethereum (chain where it exists)...")
        async with get_db() as session:
            tokens = await repo.search_tokens(
                session,
                "UNI",
                chain="eth",  # Using abbreviation, should find it
                limit=10
            )

            if len(tokens) > 0:
                print(f"✓ Found {len(tokens)} UNI token(s) on Ethereum")
                print(f"  Token: {tokens[0].symbol} - {tokens[0].name}")
                print(f"  Chain: {tokens[0].chain}")
            else:
                print(f"✗ Should have found UNI on Ethereum")
                return False

        # Test 3: Get by address on wrong chain
        print("\n[3] Get by address on wrong chain...")
        async with get_db() as session:
            # Try to get Ethereum address but specify Solana chain
            token = await repo.get_by_address(
                session,
                "sol",  # Wrong chain
                "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"  # Ethereum address
            )

            if token is None:
                print(f"✓ Correctly returned None (address not on Solana)")
            else:
                print(f"✗ Unexpectedly found token")
                return False

        # Test 4: Get by address on correct chain (using abbreviation)
        print("\n[4] Get by address on correct chain (using 'eth' abbreviation)...")
        async with get_db() as session:
            token = await repo.get_by_address(
                session,
                "eth",  # Correct chain (abbreviation)
                "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"
            )

            if token:
                print(f"✓ Found token: {token.symbol}")
                print(f"  Chain stored: {token.chain}")
            else:
                print(f"✗ Should have found UNI on Ethereum")
                return False

        # Test 5: Invalid chain name (not in mapping)
        print("\n[5] Query with invalid/unknown chain name...")
        async with get_db() as session:
            tokens = await repo.search_tokens(
                session,
                "UNI",
                chain="invalid-chain-xyz",  # Not in ChainConfig
                limit=10
            )

            print(f"✓ Query executed without error")
            print(f"  Result: {len(tokens)} tokens found")
            print(f"  Note: Returns empty or matches literal 'invalid-chain-xyz' in DB")

        # Test 6: Empty chain filter (should return all chains)
        print("\n[6] Query with None/empty chain filter...")
        async with get_db() as session:
            tokens = await repo.search_tokens(
                session,
                "UNI",
                chain=None,  # No chain filter
                limit=10
            )

            if len(tokens) > 0:
                print(f"✓ Found {len(tokens)} UNI token(s) across all chains")
                for token in tokens:
                    print(f"  - {token.symbol} on {token.chain}")
            else:
                print(f"⚠ No UNI tokens found")

        # Test 7: Recent tokens with non-existent chain
        print("\n[7] Get recent tokens on Solana (no tokens exist)...")
        async with get_db() as session:
            tokens = await repo.get_recent_tokens(
                session,
                chain="sol",
                limit=10
            )

            print(f"✓ Query executed without error")
            print(f"  Result: {len(tokens)} tokens found on Solana")

        # Test 8: Verify normalization with platforms data
        print("\n[8] Verify UNI platforms data (cross-chain addresses)...")
        async with get_db() as session:
            token = await repo.get_by_address(
                session,
                "eth",
                "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"
            )

            if token:
                print(f"✓ UNI token found")
                print(f"  Primary chain: {token.chain}")
                print(f"  Platforms data: {token.platforms}")

                # Check if we can get addresses on other chains
                if token.platforms:
                    print(f"\n  Cross-chain addresses:")
                    for chain, address in token.platforms.items():
                        print(f"    - {chain}: {address[:20]}...")

        # Test 9: Explain the behavior
        print("\n" + "="*70)
        print("EXPLANATION: How Chain Normalization Works")
        print("="*70)
        print("""
1. 输入层 - 用户使用缩写:
   repo.search_tokens(session, "UNI", chain="sol")

2. 规范化层 - Repository自动转换:
   "sol" → "solana" (通过ChainConfig.get_standard_name())

3. 数据库查询:
   SELECT * FROM tokens
   WHERE symbol LIKE '%UNI%' AND chain = 'solana'

4. 结果:
   - 如果数据库中存在 chain='solana' 的UNI，返回结果
   - 如果不存在，返回空列表 []
   - 不会抛出错误，只是查询条件不匹配

关键点:
✓ 不会导致错误 - 只是查询条件更严格
✓ 如果token不在该链上，正常返回空结果
✓ platforms字段存储所有链的地址映射
✓ chain字段存储主链（按优先级选择）
        """)

        # Cleanup
        print("\n[CLEANUP] Deleting test token...")
        async with get_db() as session:
            await repo.delete_by_id(session, uni_id)
            await session.commit()
            print("✓ Test token deleted")

        print("\n" + "="*70)
        print("✓ All edge case tests passed!")
        print("="*70)
        print("\n结论:")
        print("  ✓ 查询不存在的链不会报错，只返回空结果")
        print("  ✓ chain字段存储主链，platforms字段存储跨链地址")
        print("  ✓ 规范化是透明的，不影响查询逻辑")
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
    success = asyncio.run(test_edge_cases())
    sys.exit(0 if success else 1)
