"""
Test Token model integration with ChainConfig.

Tests Token model helper methods that use ChainConfig.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prisma_web3_py.models.token import Token


def test_token_chain_abbr():
    """Test Token.get_chain_abbr() method."""
    print("\n" + "="*60)
    print("TEST 1: Token.get_chain_abbr()")
    print("="*60)

    tests = [
        ("ethereum", "eth"),
        ("binance-smart-chain", "bsc"),
        ("solana", "sol"),
        ("arbitrum-one", "arb"),
        ("polygon-pos", "poly"),
        ("", ""),  # Mainnet token
    ]

    passed = 0
    failed = 0

    for chain, expected_abbr in tests:
        token = Token(
            id=1,
            chain=chain,
            token_address="0xtest",
            symbol="TEST",
            name="Test Token"
        )
        result = token.get_chain_abbr()

        if result == expected_abbr:
            display_chain = chain if chain else "(mainnet)"
            print(f"  ✅ {display_chain:25} -> {result}")
            passed += 1
        else:
            print(f"  ❌ {chain:25} -> {result} (expected {expected_abbr})")
            failed += 1

    print(f"\nResult: {passed}/{passed+failed} tests passed")
    return failed == 0


def test_token_chain_display_name():
    """Test Token.get_chain_display_name() method."""
    print("\n" + "="*60)
    print("TEST 2: Token.get_chain_display_name()")
    print("="*60)

    tests = [
        ("ethereum", "Ethereum"),
        ("binance-smart-chain", "BNB Chain"),
        ("solana", "Solana"),
        ("", "Mainnet"),  # Mainnet token
    ]

    passed = 0
    failed = 0

    for chain, expected_display in tests:
        token = Token(
            id=1,
            chain=chain,
            token_address="0xtest",
            symbol="TEST",
            name="Test Token"
        )
        result = token.get_chain_display_name()

        if result == expected_display:
            display_chain = chain if chain else "(mainnet)"
            print(f"  ✅ {display_chain:25} -> {result}")
            passed += 1
        else:
            print(f"  ❌ {chain:25} -> {result} (expected {expected_display})")
            failed += 1

    print(f"\nResult: {passed}/{passed+failed} tests passed")
    return failed == 0


def test_get_address_on_chain_abbr():
    """Test Token.get_address_on_chain_abbr() method."""
    print("\n" + "="*60)
    print("TEST 3: Token.get_address_on_chain_abbr()")
    print("="*60)

    # Create a cross-chain token
    token = Token(
        id=1,
        chain="ethereum",
        token_address="0xeth123",
        symbol="UNI",
        name="Uniswap",
        platforms={
            "polygon-pos": "0xpoly456",
            "arbitrum-one": "0xarb789",
        }
    )

    tests = [
        ("eth", "0xeth123"),  # Primary chain via abbreviation
        ("ethereum", "0xeth123"),  # Primary chain via standard name
        ("poly", "0xpoly456"),  # Other chain via abbreviation
        ("polygon-pos", "0xpoly456"),  # Other chain via standard name
        ("arb", "0xarb789"),
        ("bsc", None),  # Chain not available
    ]

    passed = 0
    failed = 0

    for chain_input, expected_address in tests:
        result = token.get_address_on_chain_abbr(chain_input)

        if result == expected_address:
            display_result = result if result else "(not available)"
            print(f"  ✅ {chain_input:15} -> {display_result}")
            passed += 1
        else:
            print(f"  ❌ {chain_input:15} -> {result} (expected {expected_address})")
            failed += 1

    print(f"\nResult: {passed}/{passed+failed} tests passed")
    return failed == 0


def test_get_all_chains_with_abbr():
    """Test Token.get_all_chains_with_abbr() method."""
    print("\n" + "="*60)
    print("TEST 4: Token.get_all_chains_with_abbr()")
    print("="*60)

    # Test 1: Cross-chain token
    print("  Test 4.1: Cross-chain token")
    token = Token(
        id=1,
        chain="ethereum",
        token_address="0xeth123",
        symbol="UNI",
        name="Uniswap",
        platforms={
            "polygon-pos": "0xpoly456",
            "arbitrum-one": "0xarb789",
        }
    )

    chains = token.get_all_chains_with_abbr()

    if len(chains) == 3:  # ethereum + polygon-pos + arbitrum-one
        print(f"    ✅ Found {len(chains)} chains")
        for chain_info in chains:
            print(f"       - {chain_info['standard']:20} ({chain_info['abbr']:5}) - {chain_info['display']}")
        test1_pass = True
    else:
        print(f"    ❌ Expected 3 chains, got {len(chains)}")
        test1_pass = False

    # Test 2: Mainnet token
    print("\n  Test 4.2: Mainnet token (should return empty list)")
    mainnet_token = Token(
        id=2,
        chain="",
        token_address="bitcoin",
        symbol="BTC",
        name="Bitcoin",
        platforms={}
    )

    mainnet_chains = mainnet_token.get_all_chains_with_abbr()

    if len(mainnet_chains) == 0:
        print(f"    ✅ Mainnet token returns empty list")
        test2_pass = True
    else:
        print(f"    ❌ Expected empty list, got {len(mainnet_chains)} chains")
        test2_pass = False

    return test1_pass and test2_pass


def test_mainnet_token_detection():
    """Test Token.is_mainnet_token() method."""
    print("\n" + "="*60)
    print("TEST 5: Token.is_mainnet_token()")
    print("="*60)

    tests = [
        # (chain, platforms, expected_is_mainnet)
        ("", {}, True),  # Mainnet token
        ("", None, True),  # Mainnet token (platforms=None)
        ("ethereum", {}, False),  # Chain-specific token
        ("ethereum", {"polygon-pos": "0x..."}, False),  # Cross-chain token
    ]

    passed = 0
    failed = 0

    for chain, platforms, expected in tests:
        token = Token(
            id=1,
            chain=chain,
            token_address="0xtest",
            symbol="TEST",
            name="Test Token",
            platforms=platforms
        )
        result = token.is_mainnet_token()

        chain_display = f"chain='{chain}', platforms={platforms}"
        if result == expected:
            status = "mainnet" if result else "chain-specific"
            print(f"  ✅ {chain_display:40} -> {status}")
            passed += 1
        else:
            print(f"  ❌ {chain_display:40} -> {result} (expected {expected})")
            failed += 1

    print(f"\nResult: {passed}/{passed+failed} tests passed")
    return failed == 0


def main():
    """Run all tests."""
    print("\n" + "🧪"*30)
    print("TOKEN + CHAIN CONFIG INTEGRATION TEST SUITE")
    print("🧪"*30)

    results = []

    results.append(("Token.get_chain_abbr()", test_token_chain_abbr()))
    results.append(("Token.get_chain_display_name()", test_token_chain_display_name()))
    results.append(("Token.get_address_on_chain_abbr()", test_get_address_on_chain_abbr()))
    results.append(("Token.get_all_chains_with_abbr()", test_get_all_chains_with_abbr()))
    results.append(("Token.is_mainnet_token()", test_mainnet_token_detection()))

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")

    print(f"\nTotal: {passed}/{total} test suites passed")

    if passed == total:
        print("\n🎉 All integration tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
