#!/usr/bin/env python3
"""
Test script to validate token data import logic without database writes.

This performs a dry-run of the import process to catch any data issues.
"""

import json
import sys
from pathlib import Path
from collections import Counter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def validate_token_data(token: dict, index: int) -> list:
    """
    Validate a single token record.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check required fields
    if not token.get('coingecko_id'):
        errors.append(f"[{index}] Missing coingecko_id")

    if not token.get('symbol'):
        errors.append(f"[{index}] Missing symbol")

    if not token.get('name'):
        errors.append(f"[{index}] Missing name")

    # Check platforms format
    platforms = token.get('platforms', {})
    if not isinstance(platforms, dict):
        errors.append(f"[{index}] platforms must be a dict, got {type(platforms)}")

    # Check categories format
    categories = token.get('categories', [])
    if not isinstance(categories, list):
        errors.append(f"[{index}] categories must be a list, got {type(categories)}")

    return errors


def analyze_data(tokens_file: str, aliases_file: str):
    """Analyze token and alias data."""

    print("\n" + "="*70)
    print(" "*20 + "TOKEN DATA VALIDATION")
    print("="*70)

    # Load tokens
    print(f"\nLoading tokens from {tokens_file}...")
    with open(tokens_file, 'r', encoding='utf-8') as f:
        tokens = json.load(f)
    print(f"✓ Loaded {len(tokens)} tokens")

    # Load aliases
    print(f"\nLoading aliases from {aliases_file}...")
    with open(aliases_file, 'r', encoding='utf-8') as f:
        aliases_data = json.load(f)
    print(f"✓ Loaded {len(aliases_data)} alias mappings")

    # Validate token data
    print("\n" + "-"*70)
    print("Validating token data...")
    print("-"*70)

    all_errors = []
    for i, token in enumerate(tokens):
        errors = validate_token_data(token, i)
        all_errors.extend(errors)

    if all_errors:
        print(f"\n✗ Found {len(all_errors)} validation errors:")
        for error in all_errors[:10]:  # Show first 10
            print(f"  {error}")
        if len(all_errors) > 10:
            print(f"  ... and {len(all_errors) - 10} more errors")
        return False
    else:
        print("✓ All tokens have valid structure")

    # Analyze platforms
    print("\n" + "-"*70)
    print("Analyzing platforms...")
    print("-"*70)

    mainnet_tokens = 0
    multichain_tokens = 0
    chain_counter = Counter()

    for token in tokens:
        platforms = token.get('platforms', {})

        # Clean empty keys
        clean_platforms = {k: v for k, v in platforms.items()
                          if k and k.strip() and v and v.strip()}

        if not clean_platforms:
            mainnet_tokens += 1
        elif len(clean_platforms) > 1:
            multichain_tokens += 1

        for chain in clean_platforms.keys():
            chain_counter[chain] += 1

    print(f"  Mainnet tokens (no specific chain): {mainnet_tokens}")
    print(f"  Multi-chain tokens: {multichain_tokens}")
    print(f"  Single-chain tokens: {len(tokens) - mainnet_tokens - multichain_tokens}")
    print(f"\nTop 10 chains by token count:")
    for chain, count in chain_counter.most_common(10):
        print(f"    {chain}: {count}")

    # Analyze aliases
    print("\n" + "-"*70)
    print("Analyzing aliases...")
    print("-"*70)

    # Create alias map
    alias_map = {}
    total_aliases = 0
    for item in aliases_data:
        canonical = item.get('canonical', '').upper()
        aliases = item.get('aliases', [])
        if canonical:
            alias_map[canonical] = [a.upper() for a in aliases if a]
            total_aliases += len(alias_map[canonical])

    # Find how many tokens will get aliases
    tokens_with_aliases = 0
    tokens_without_match = []

    for token in tokens:
        symbol = token.get('symbol', '').upper()
        if symbol in alias_map:
            tokens_with_aliases += 1
        elif symbol:  # Has symbol but no aliases
            tokens_without_match.append(symbol)

    print(f"  Total alias entries: {len(alias_map)}")
    print(f"  Total aliases: {total_aliases}")
    print(f"  Tokens that will get aliases: {tokens_with_aliases}")
    print(f"  Tokens without alias match: {len(tokens_without_match)}")

    if tokens_without_match[:5]:
        print(f"  Sample tokens without aliases: {tokens_without_match[:5]}")

    # Check for missing canonical symbols
    canonical_symbols = set(alias_map.keys())
    token_symbols = set(t.get('symbol', '').upper() for t in tokens if t.get('symbol'))
    missing_in_tokens = canonical_symbols - token_symbols

    if missing_in_tokens:
        print(f"\n  ⚠ Warning: {len(missing_in_tokens)} canonical symbols not found in tokens")
        print(f"    Sample: {list(missing_in_tokens)[:5]}")

    # Analyze social links
    print("\n" + "-"*70)
    print("Analyzing social links...")
    print("-"*70)

    social_stats = {
        'website': 0,
        'twitter': 0,
        'telegram': 0,
        'github': 0,
        'discord': 0
    }

    for token in tokens:
        social_links = token.get('social_links', {})
        for key in social_stats.keys():
            if social_links.get(key):
                social_stats[key] += 1

    for key, count in social_stats.items():
        percentage = (count / len(tokens)) * 100
        print(f"  {key}: {count} ({percentage:.1f}%)")

    # Analyze market cap ranks
    print("\n" + "-"*70)
    print("Analyzing market cap ranks...")
    print("-"*70)

    without_rank = len(tokens) - with_rank


    if with_rank > 0:
        print(f"  Rank range: {min(ranks)} - {max(ranks)}")

    # Summary
    print("\n" + "="*70)
    print(" "*25 + "SUMMARY")
    print("="*70)
    print(f"✓ Total tokens to import: {len(tokens)}")
    print(f"✓ Tokens with aliases: {tokens_with_aliases}")
    print(f"✓ Mainnet tokens: {mainnet_tokens}")
    print(f"✓ Multi-chain tokens: {multichain_tokens}")
    print(f"✓ All data validation passed!")
    print("="*70)

    print("\n✓ Ready to import! Run:")
    print("  python scripts/import_token_recognition_data.py")
    print()

    return True


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    tokens_path = project_root / "python/token_recognition/data/tokens.json"
    aliases_path = project_root / "python/token_recognition/data/aliases.json"

    if not tokens_path.exists():
        print(f"✗ Tokens file not found: {tokens_path}")
        sys.exit(1)

    if not aliases_path.exists():
        print(f"✗ Aliases file not found: {aliases_path}")
        sys.exit(1)

    success = analyze_data(str(tokens_path), str(aliases_path))
    sys.exit(0 if success else 1)
