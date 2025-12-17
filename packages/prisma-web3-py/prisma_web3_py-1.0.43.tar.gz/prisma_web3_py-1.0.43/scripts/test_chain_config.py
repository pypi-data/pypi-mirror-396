"""
Test script for ChainConfig functionality.

Tests abbreviation conversions, priority ordering, and Token model integration.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prisma_web3_py.utils.chain_config import ChainConfig, Chain, abbr, standard, display


def test_abbreviation_conversions():
    """Test chain abbreviation conversions."""
    print("\n" + "="*60)
    print("TEST 1: Abbreviation Conversions")
    print("="*60)

    tests = [
        ("ethereum", "eth"),
        ("binance-smart-chain", "bsc"),
        ("solana", "sol"),
        ("base", "base"),
        ("arbitrum-one", "arb"),
        ("polygon-pos", "poly"),
        ("avalanche", "avax"),
        ("optimistic-ethereum", "op"),
    ]

    passed = 0
    failed = 0

    for standard_name, expected_abbr in tests:
        result = ChainConfig.get_abbreviation(standard_name)
        if result == expected_abbr:
            print(f"  ✅ {standard_name:25} -> {result}")
            passed += 1
        else:
            print(f"  ❌ {standard_name:25} -> {result} (expected {expected_abbr})")
            failed += 1

    print(f"\nResult: {passed}/{passed+failed} tests passed")
    return failed == 0


def test_reverse_conversion():
    """Test abbreviation -> standard name conversion."""
    print("\n" + "="*60)
    print("TEST 2: Reverse Conversion (Abbreviation -> Standard)")
    print("="*60)

    tests = [
        ("eth", "ethereum"),
        ("bsc", "binance-smart-chain"),
        ("sol", "solana"),
        ("arb", "arbitrum-one"),
        ("poly", "polygon-pos"),
        ("op", "optimistic-ethereum"),
    ]

    passed = 0
    failed = 0

    for abbr_input, expected_standard in tests:
        result = ChainConfig.get_standard_name(abbr_input)
        if result == expected_standard:
            print(f"  ✅ {abbr_input:6} -> {result}")
            passed += 1
        else:
            print(f"  ❌ {abbr_input:6} -> {result} (expected {expected_standard})")
            failed += 1

    print(f"\nResult: {passed}/{passed+failed} tests passed")
    return failed == 0


def test_idempotent_conversion():
    """Test that standard name -> standard name works (idempotent)."""
    print("\n" + "="*60)
    print("TEST 3: Idempotent Conversion (Standard -> Standard)")
    print("="*60)

    tests = ["ethereum", "binance-smart-chain", "solana", "arbitrum-one"]

    passed = 0
    failed = 0

    for standard_name in tests:
        result = ChainConfig.get_standard_name(standard_name)
        if result == standard_name:
            print(f"  ✅ {standard_name:25} -> {result}")
            passed += 1
        else:
            print(f"  ❌ {standard_name:25} -> {result} (should be unchanged)")
            failed += 1

    print(f"\nResult: {passed}/{passed+failed} tests passed")
    return failed == 0


def test_display_names():
    """Test display name retrieval."""
    print("\n" + "="*60)
    print("TEST 4: Display Names")
    print("="*60)

    tests = [
        ("ethereum", "Ethereum"),
        ("eth", "Ethereum"),  # Should work with abbreviation too
        ("binance-smart-chain", "BNB Chain"),
        ("bsc", "BNB Chain"),
        ("solana", "Solana"),
        ("sol", "Solana"),
    ]

    passed = 0
    failed = 0

    for input_chain, expected_display in tests:
        result = ChainConfig.get_display_name(input_chain)
        if result == expected_display:
            print(f"  ✅ {input_chain:25} -> {result}")
            passed += 1
        else:
            print(f"  ❌ {input_chain:25} -> {result} (expected {expected_display})")
            failed += 1

    print(f"\nResult: {passed}/{passed+failed} tests passed")
    return failed == 0


def test_priority_ordering():
    """Test chain priority ordering."""
    print("\n" + "="*60)
    print("TEST 5: Priority Ordering")
    print("="*60)

    chains = ["solana", "ethereum", "polygon-pos", "arbitrum-one", "binance-smart-chain"]

    print("  Input chains:", chains)

    sorted_chains = sorted(chains, key=ChainConfig.get_priority)

    print("  Sorted by priority:")
    for i, chain in enumerate(sorted_chains, 1):
        priority = ChainConfig.get_priority(chain)
        print(f"    {i}. {chain:25} (priority: {priority})")

    # Ethereum should be first (highest priority)
    if sorted_chains[0] == "ethereum":
        print("\n  ✅ Ethereum has highest priority")
        return True
    else:
        print(f"\n  ❌ Expected ethereum first, got {sorted_chains[0]}")
        return False


def test_convenience_functions():
    """Test convenience functions."""
    print("\n" + "="*60)
    print("TEST 6: Convenience Functions (abbr, standard, display)")
    print("="*60)

    tests = [
        (abbr("ethereum"), "eth"),
        (standard("eth"), "ethereum"),
        (display("eth"), "Ethereum"),
        (display("bsc"), "BNB Chain"),
    ]

    passed = 0
    failed = 0

    for result, expected in tests:
        if result == expected:
            print(f"  ✅ Result: {result}")
            passed += 1
        else:
            print(f"  ❌ Result: {result} (expected {expected})")
            failed += 1

    print(f"\nResult: {passed}/{passed+failed} tests passed")
    return failed == 0


def test_chain_constants():
    """Test Chain class constants."""
    print("\n" + "="*60)
    print("TEST 7: Chain Class Constants")
    print("="*60)

    tests = [
        ("Chain.ETH", Chain.ETH, "eth"),
        ("Chain.BSC", Chain.BSC, "bsc"),
        ("Chain.SOL", Chain.SOL, "sol"),
        ("Chain.ARB", Chain.ARB, "arb"),
        ("Chain.ETHEREUM", Chain.ETHEREUM, "ethereum"),
        ("Chain.BINANCE_SMART_CHAIN", Chain.BINANCE_SMART_CHAIN, "binance-smart-chain"),
    ]

    passed = 0
    failed = 0

    for name, constant, expected in tests:
        if constant == expected:
            print(f"  ✅ {name:30} = {constant}")
            passed += 1
        else:
            print(f"  ❌ {name:30} = {constant} (expected {expected})")
            failed += 1

    print(f"\nResult: {passed}/{passed+failed} tests passed")
    return failed == 0


def main():
    """Run all tests."""
    print("\n" + "🧪"*30)
    print("CHAIN CONFIGURATION TEST SUITE")
    print("🧪"*30)

    results = []

    results.append(("Abbreviation Conversions", test_abbreviation_conversions()))
    results.append(("Reverse Conversion", test_reverse_conversion()))
    results.append(("Idempotent Conversion", test_idempotent_conversion()))
    results.append(("Display Names", test_display_names()))
    results.append(("Priority Ordering", test_priority_ordering()))
    results.append(("Convenience Functions", test_convenience_functions()))
    results.append(("Chain Constants", test_chain_constants()))

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
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
