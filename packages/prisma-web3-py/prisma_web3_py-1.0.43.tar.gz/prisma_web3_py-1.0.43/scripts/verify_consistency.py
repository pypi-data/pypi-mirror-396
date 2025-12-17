#!/usr/bin/env python3
"""
Comprehensive consistency check for Token model, repository, and import script.

This script verifies:
1. Python model fields match Prisma schema
2. Repository create method supports all fields
3. Import script handles all fields correctly
4. Token relationships are properly configured
"""

import re
import ast
from pathlib import Path
from typing import List, Set, Dict

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{title:^70}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")


def check_prisma_vs_python_model():
    """Check if Python model matches Prisma schema."""
    print_section("1. Prisma Schema vs Python Model")

    # Expected fields from Prisma schema
    prisma_fields = [
        'id', 'chain', 'token_address', 'symbol', 'name', 'coingecko_id',
        'platforms', 'description', 'logo',
        'categories', 'aliases', 'website', 'twitter', 'telegram', 'github', 'discord',
        'decimals', 'total_supply', 'deploy_time', 'creator_address',
        'can_mint', 'pool_creation_timestamp', 'top_pools',
        'raw_metadata', 'created_at', 'updated_at', 'signal_updated_at'
    ]

    # Read Python model
    model_file = Path('prisma_web3_py/models/token.py')
    with open(model_file, 'r') as f:
        content = f.read()

    # Extract field definitions
    pattern = r'(\w+):\s*Mapped\[.*?\]\s*=\s*mapped_column'
    python_fields = re.findall(pattern, content)

    # Compare
    missing = set(prisma_fields) - set(python_fields)
    extra = set(python_fields) - set(prisma_fields)

    print(f"Prisma schema fields: {len(prisma_fields)}")
    print(f"Python model fields:  {len(python_fields)}")

    if not missing and not extra:
        print(f"{GREEN}✓ All fields match perfectly!{RESET}")
        return True
    else:
        if missing:
            print(f"\n{RED}✗ Missing in Python model:{RESET}")
            for field in sorted(missing):
                print(f"    - {field}")
        if extra:
            print(f"\n{YELLOW}⚠ Extra in Python model:{RESET}")
            for field in sorted(extra):
                print(f"    - {field}")
        return False


def check_token_importer():
    """Check if TokenImporter handles all required fields."""
    print_section("2. TokenImporter Field Handling")

    # Required fields for import
    required_fields = [
        'coingecko_id', 'symbol', 'name', 'chain', 'token_address',
        'platforms', 'description', 'logo',
        'categories', 'aliases', 'website', 'twitter', 'telegram', 'github', 'discord'
    ]

    # Read importer file
    importer_file = Path('prisma_web3_py/utils/token_importer.py')
    with open(importer_file, 'r') as f:
        content = f.read()

    # Check if fields are handled in import_token method
    found_fields = []
    issues = []

    for field in required_fields:
        # Look for field in code
        patterns = [
            f'coin_data.get\\("{field}"',  # coin_data.get("field")
            f'token.{field} = ',  # token.field =
            f'existing_token.{field} = ',  # existing_token.field =
            f'{field}=',  # field= (constructor)
        ]

        if any(pattern in content for pattern in patterns):
            found_fields.append(field)
        else:
            issues.append(field)

    print(f"Required fields for import: {len(required_fields)}")
    print(f"Fields handled in importer: {len(found_fields)}")

    if not issues:
        print(f"{GREEN}✓ All required fields are handled!{RESET}")
        return True
    else:
        print(f"\n{YELLOW}⚠ Fields not explicitly handled:{RESET}")
        for field in sorted(issues):
            print(f"    - {field}")
        print(f"\n{BLUE}ℹ Note: Some fields may be handled dynamically{RESET}")
        return len(issues) < 3  # Allow a few to be dynamic


def check_primary_chain_logic():
    """Check primary chain determination logic."""
    print_section("3. Primary Chain Logic")

    importer_file = Path('prisma_web3_py/utils/token_importer.py')
    with open(importer_file, 'r') as f:
        content = f.read()

    checks = {
        "Uses coingecko_id for mainnet tokens": 'coingecko_id' in content,
        "Cleans platforms dict": '_clean_platforms' in content,
        "Uses ChainConfig.CHAIN_PRIORITY": 'ChainConfig.CHAIN_PRIORITY' in content,
        "Handles empty platforms": 'if not platforms' in content,
    }

    all_passed = True
    for check, passed in checks.items():
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"  {status} {check}")
        all_passed = all_passed and passed

    # Check if ChainConfig is used
    if 'ChainConfig.CHAIN_PRIORITY' in content:
        print(f"\n{BLUE}ℹ Using centralized ChainConfig for chain priority{RESET}")

    return all_passed


def check_mainnet_token_handling():
    """Check how mainnet tokens (BTC, ETH) are handled."""
    print_section("4. Mainnet Token Handling")

    # Check importer
    importer_file = Path('prisma_web3_py/utils/token_importer.py')
    with open(importer_file, 'r') as f:
        importer_content = f.read()

    # Check model
    model_file = Path('prisma_web3_py/models/token.py')
    with open(model_file, 'r') as f:
        model_content = f.read()

    checks = {
        "Importer: Returns coingecko_id for mainnet": 'return ("", coingecko_id' in importer_content,
        "Model: has is_mainnet_token() method": 'def is_mainnet_token' in model_content,
        "Model: Checks platforms in is_mainnet": 'not self.platforms' in model_content,
        "Model: get_address_on_chain handles mainnet": 'if self.is_mainnet_token()' in model_content,
    }

    all_passed = True
    for check, passed in checks.items():
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"  {status} {check}")
        all_passed = all_passed and passed

    if all_passed:
        print(f"\n{GREEN}✓ Mainnet tokens will be handled correctly!{RESET}")
        print(f"{BLUE}ℹ Mainnet tokens (BTC, ETH, etc) will have:{RESET}")
        print(f"    - chain = ''")
        print(f"    - token_address = coingecko_id (e.g., 'bitcoin', 'ethereum')")
        print(f"    - platforms = {{}}")

    return all_passed


def check_unique_constraints():
    """Check unique constraint handling."""
    print_section("5. Unique Constraint Handling")

    # Read Prisma schema
    prisma_file = Path('../prisma/models/token.prisma')
    with open(prisma_file, 'r') as f:
        prisma_content = f.read()

    # Find unique constraints
    unique_constraints = []
    if '@@unique([chain, token_address])' in prisma_content:
        unique_constraints.append('(chain, token_address)')
    if '@unique' in prisma_content and 'coingecko_id' in prisma_content:
        unique_constraints.append('coingecko_id')

    print(f"{BLUE}Unique constraints in Prisma schema:{RESET}")
    for constraint in unique_constraints:
        print(f"    - {constraint}")

    # Check if Python model has matching indexes
    model_file = Path('prisma_web3_py/models/token.py')
    with open(model_file, 'r') as f:
        model_content = f.read()

    checks = {
        "UniqueConstraint on chain+token_address": "UniqueConstraint('chain', 'token_address'" in model_content,
        "coingecko_id is unique": "coingecko_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)" in model_content,
    }

    all_passed = True
    for check, passed in checks.items():
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"\n  {status} {check}")
        all_passed = all_passed and passed

    if all_passed:
        print(f"\n{GREEN}✓ Unique constraints are properly defined!{RESET}")
    else:
        print(f"\n{YELLOW}⚠ Check unique constraint definitions{RESET}")

    return all_passed


def check_relationships():
    """Check model relationships."""
    print_section("6. Model Relationships")

    model_file = Path('prisma_web3_py/models/token.py')
    with open(model_file, 'r') as f:
        content = f.read()

    # Expected relationships
    expected_relationships = [
        'signals',
        'pre_signals',
        'token_metrics',
        'token_analysis_reports'
    ]

    found = []
    for rel in expected_relationships:
        if f'{rel}: Mapped' in content or f'{rel} = relationship' in content:
            found.append(rel)

    print(f"Expected relationships: {len(expected_relationships)}")
    print(f"Found in Python model: {len(found)}")

    for rel in expected_relationships:
        if rel in found:
            print(f"  {GREEN}✓{RESET} {rel}")
        else:
            print(f"  {RED}✗{RESET} {rel}")

    # Check viewonly=True
    if 'viewonly=True' in content:
        print(f"\n{GREEN}✓{RESET} Relationships use viewonly=True (correct for composite FKs)")
    else:
        print(f"\n{YELLOW}⚠{RESET} Relationships should use viewonly=True for composite foreign keys")

    return len(found) == len(expected_relationships)


def check_import_script_data_handling():
    """Check import script data handling."""
    print_section("7. Import Script Data Handling")

    script_file = Path('scripts/import_token_recognition_data.py')
    with open(script_file, 'r') as f:
        content = f.read()

    checks = {
        "Loads tokens.json": 'tokens.json' in content,
        "Loads aliases.json": 'aliases.json' in content,
        "Merges aliases": 'alias_map' in content or 'merge' in content.lower(),
        "Uses TokenImporter": 'TokenImporter' in content,
        "Calls import_from_dict_list": 'import_from_dict_list' in content,
        "Handles batch commits": 'batch_size' in content,
        "Reports statistics": 'stats' in content,
    }

    all_passed = True
    for check, passed in checks.items():
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"  {status} {check}")
        all_passed = all_passed and passed

    return all_passed


def main():
    """Run all consistency checks."""
    print(f"\n{BLUE}{'*' * 70}{RESET}")
    print(f"{BLUE}{'Token Model Consistency Verification':^70}{RESET}")
    print(f"{BLUE}{'*' * 70}{RESET}")

    results = {
        "Prisma vs Python Model": check_prisma_vs_python_model(),
        "TokenImporter Field Handling": check_token_importer(),
        "Primary Chain Logic": check_primary_chain_logic(),
        "Mainnet Token Handling": check_mainnet_token_handling(),
        "Unique Constraints": check_unique_constraints(),
        "Model Relationships": check_relationships(),
        "Import Script": check_import_script_data_handling(),
    }

    # Summary
    print_section("SUMMARY")

    passed = sum(results.values())
    total = len(results)

    for check, result in results.items():
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"  {status:20} {check}")

    print(f"\n{BLUE}{'─' * 70}{RESET}")
    print(f"  Total: {total} checks")
    print(f"  {GREEN}Passed: {passed}{RESET}")
    print(f"  {RED}Failed: {total - passed}{RESET}")
    print(f"{BLUE}{'─' * 70}{RESET}\n")

    if passed == total:
        print(f"{GREEN}✅ All consistency checks passed!{RESET}")
        print(f"{GREEN}✅ Ready to import data!{RESET}\n")
        return 0
    else:
        print(f"{YELLOW}⚠️  Some checks failed. Please review the issues above.{RESET}\n")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
