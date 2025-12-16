#!/usr/bin/env python3
"""
Import token data from token_recognition JSON files.

This script reads tokens.json and aliases.json, merges them,
and imports into the database.

Usage:
    python scripts/import_token_recognition_data.py [--no-update] [--batch-size 50]

Example:
    python scripts/import_token_recognition_data.py
    python scripts/import_token_recognition_data.py --no-update
    python scripts/import_token_recognition_data.py --batch-size 100
"""

import asyncio
import argparse
import logging
import sys
import json
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma_web3_py import get_db, init_db, close_db
from prisma_web3_py.utils import TokenImporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_and_merge_data(tokens_file: str, aliases_file: str) -> List[dict]:
    """
    Load tokens and aliases, then merge them.

    Args:
        tokens_file: Path to tokens.json
        aliases_file: Path to aliases.json

    Returns:
        List of merged token data
    """
    logger.info(f"Loading tokens from {tokens_file}...")
    with open(tokens_file, 'r', encoding='utf-8') as f:
        tokens = json.load(f)
    logger.info(f"Loaded {len(tokens)} tokens")

    logger.info(f"Loading aliases from {aliases_file}...")
    with open(aliases_file, 'r', encoding='utf-8') as f:
        aliases_data = json.load(f)
    logger.info(f"Loaded {len(aliases_data)} alias mappings")

    # Create alias lookup: canonical symbol -> aliases list
    alias_map: Dict[str, List[str]] = {}
    for item in aliases_data:
        canonical = item.get('canonical', '').upper()
        aliases = item.get('aliases', [])
        if canonical:
            # Convert all aliases to uppercase for consistency
            alias_map[canonical] = [a.upper() for a in aliases if a]

    logger.info(f"Created alias map with {len(alias_map)} entries")

    # Merge aliases into token data
    merged_count = 0
    for token in tokens:
        symbol = token.get('symbol', '').upper()
        if symbol in alias_map:
            # Get existing aliases from token data
            existing_aliases = token.get('aliases', [])
            if not isinstance(existing_aliases, list):
                existing_aliases = []

            # Merge with new aliases (avoid duplicates)
            new_aliases = alias_map[symbol]
            combined_aliases = list(set(existing_aliases + new_aliases))

            # Update token
            token['aliases'] = combined_aliases
            merged_count += 1

    logger.info(f"Merged aliases for {merged_count} tokens")

    return tokens


async def main():
    """Main import function."""
    parser = argparse.ArgumentParser(
        description='Import tokens from token_recognition data files'
    )
    parser.add_argument(
        '--tokens-file',
        type=str,
        default='python/token_recognition/data/tokens.json',
        help='Path to tokens.json file'
    )
    parser.add_argument(
        '--aliases-file',
        type=str,
        default='python/token_recognition/data/aliases.json',
        help='Path to aliases.json file'
    )
    parser.add_argument(
        '--no-update',
        action='store_true',
        help='Skip updating existing tokens'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='Commit every N tokens (default: 50)'
    )

    args = parser.parse_args()

    # Find project root (parent of python directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    tokens_path = project_root / args.tokens_file
    aliases_path = project_root / args.aliases_file

    # Validate files exist
    if not tokens_path.exists():
        logger.error(f"Tokens file not found: {tokens_path}")
        return 1

    if not aliases_path.exists():
        logger.error(f"Aliases file not found: {aliases_path}")
        return 1

    logger.info("=" * 60)
    logger.info("Token Recognition Data Import")
    logger.info("=" * 60)
    logger.info(f"Tokens file: {tokens_path}")
    logger.info(f"Aliases file: {aliases_path}")
    logger.info(f"Update existing: {not args.no_update}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info("=" * 60)

    # Load and merge data
    try:
        merged_data = load_and_merge_data(str(tokens_path), str(aliases_path))
    except Exception as e:
        logger.error(f"Failed to load/merge data: {e}", exc_info=True)
        return 1

    # Initialize database
    try:
        await init_db()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return 1

    # Create importer
    importer = TokenImporter()

    try:
        async with get_db() as session:
            # Import tokens using merged data
            stats = await importer.import_from_dict_list(
                session,
                merged_data,
                update_existing=not args.no_update,
                batch_size=args.batch_size
            )

            # Display results
            logger.info("=" * 60)
            logger.info("Import Complete!")
            logger.info("=" * 60)
            logger.info(f"Total tokens processed: {stats['total']}")
            logger.info(f"Created: {stats['created']}")
            logger.info(f"Updated: {stats['updated']}")
            logger.info(f"Skipped: {stats['skipped']}")
            logger.info(f"Errors: {stats['errors']}")
            logger.info("=" * 60)

            if stats['errors'] > 0:
                logger.warning(f"Import completed with {stats['errors']} errors")
                # Don't return error code if some imports succeeded
                if stats['created'] + stats['updated'] > 0:
                    logger.info("Some tokens were imported successfully despite errors")
                    return 0
                return 1

            return 0

    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        return 1

    finally:
        await close_db()
        logger.info("Database connection closed")


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
