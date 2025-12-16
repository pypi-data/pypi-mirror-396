"""
Token data importer from CoinGecko JSON format.
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from ..models.token import Token
from ..repositories.token_repository import TokenRepository
from .chain_config import ChainConfig

logger = logging.getLogger(__name__)


class TokenImporter:
    """Import token data from CoinGecko JSON format into database."""

    def __init__(self):
        self.token_repo = TokenRepository()
        self.stats = {
            'total': 0,
            'created': 0,
            'updated': 0,
            'errors': 0,
            'skipped': 0
        }

    def _determine_primary_chain(self, platforms: Dict[str, str], coingecko_id: str = "") -> tuple[str, str]:
        """
        Determine the primary chain for this token.

        Args:
            platforms: Dictionary of chain -> address mappings
            coingecko_id: CoinGecko ID for mainnet tokens

        Returns:
            Tuple of (chain, token_address)
        """
        # Mainnet token (like BTC, ETH)
        # Use coingecko_id as token_address to maintain uniqueness
        if not platforms:
            return ("", coingecko_id or "")

        # Use ChainConfig priority order
        # Select first available priority chain
        for chain in ChainConfig.CHAIN_PRIORITY:
            if chain in platforms:
                return (chain, platforms[chain])

        # Fallback to first chain in dict
        first_chain = list(platforms.keys())[0]
        return (first_chain, platforms[first_chain])

    def _extract_social_links(self, data: dict) -> Dict[str, str]:
        """Extract social links from CoinGecko data."""
        social_links = data.get("social_links", {})

        result = {}
        if social_links.get("website"):
            result['website'] = social_links['website']
        if social_links.get("twitter"):
            result['twitter'] = social_links['twitter']
        if social_links.get("telegram"):
            result['telegram'] = social_links['telegram']
        if social_links.get("github"):
            result['github'] = social_links['github']
        if social_links.get("discord"):
            result['discord'] = social_links['discord']

        return result

    def _clean_platforms(self, platforms: Dict[str, str]) -> Dict[str, str]:
        """
        Clean platforms dict by removing empty keys/values.

        Args:
            platforms: Raw platforms dict from JSON

        Returns:
            Cleaned platforms dict
        """
        if not platforms:
            return {}

        # Remove empty string keys and values
        cleaned = {}
        for chain, address in platforms.items():
            if chain and chain.strip() and address and address.strip():
                cleaned[chain] = address

        return cleaned

    async def import_token(
        self,
        session: AsyncSession,
        coin_data: dict,
        update_existing: bool = True
    ) -> Optional[Token]:
        """
        Import a single token from CoinGecko data.

        Args:
            session: Database session
            coin_data: CoinGecko token data
            update_existing: Whether to update existing tokens

        Returns:
            Token instance or None if failed
        """
        # Initialize variables for error logging
        chain = None
        token_address = None
        other_platforms = {}

        try:
            coingecko_id = coin_data.get("coingecko_id")
            if not coingecko_id:
                logger.warning(f"Skipping token without coingecko_id: {coin_data.get('symbol')}")
                self.stats['skipped'] += 1
                return None

            # Check if token already exists
            existing = await session.execute(
                select(Token).where(Token.coingecko_id == coingecko_id)
            )
            existing_token = existing.scalar_one_or_none()

            # Determine primary chain and platforms
            platforms = coin_data.get("platforms", {})
            # Clean platforms first (remove empty strings)
            platforms = self._clean_platforms(platforms)
            chain, token_address = self._determine_primary_chain(platforms, coingecko_id)

            # Other platforms (excluding primary chain)
            other_platforms = {k: v for k, v in platforms.items() if k != chain and k != ""}

            # Extract social links
            social_links = self._extract_social_links(coin_data)

            if existing_token:
                if not update_existing:
                    logger.debug(f"Token {existing_token.symbol} already exists, skipping")
                    self.stats['skipped'] += 1
                    return existing_token

                # Update existing token
                existing_token.symbol = coin_data.get("symbol", "").upper()
                existing_token.name = coin_data.get("name")
                existing_token.description = coin_data.get("description")
                existing_token.logo = coin_data.get("logo")
          
                existing_token.categories = coin_data.get("categories", [])
                existing_token.aliases = coin_data.get("aliases", [])
                existing_token.platforms = other_platforms
                existing_token.website = social_links.get("website")
                existing_token.twitter = social_links.get("twitter")
                existing_token.telegram = social_links.get("telegram")
                existing_token.github = social_links.get("github")
                existing_token.discord = social_links.get("discord")
                existing_token.market_cap_rank = coin_data.get("market_cap_rank")


                await session.flush()
                logger.info(f"Updated token: {existing_token.symbol}")
                self.stats['updated'] += 1
                return existing_token

            else:
                # Create new token
                token = Token(
                    chain=chain,
                    token_address=token_address,
                    symbol=coin_data.get("symbol", "").upper(),
                    name=coin_data.get("name"),
                    coingecko_id=coingecko_id,
                    platforms=other_platforms,
                    description=coin_data.get("description"),
                    logo=coin_data.get("logo"),
                    categories=coin_data.get("categories", []),
                    aliases=coin_data.get("aliases", []),
                    website=social_links.get("website"),
                    twitter=social_links.get("twitter"),
                    telegram=social_links.get("telegram"),
                    github=social_links.get("github"),
                    discord=social_links.get("discord"),
                    market_cap_rank=coin_data.get("market_cap_rank"),
                )

                session.add(token)
                await session.flush()
                logger.info(f"Created token: {token.symbol} on {token.chain or 'mainnet'}")
                self.stats['created'] += 1
                return token

        except SQLAlchemyError as e:
            symbol = coin_data.get('symbol', 'UNKNOWN')
            coingecko_id = coin_data.get('coingecko_id', 'UNKNOWN')
            logger.error(
                f"Database error importing token {symbol} (coingecko_id: {coingecko_id}): {e}\n"
                f"Token data: chain={chain}, token_address={token_address}, "
                f"platforms={other_platforms}"
            )
            # Log the full exception for debugging
            import traceback
            logger.debug(f"Full traceback:\n{traceback.format_exc()}")

            self.stats['errors'] += 1
            # Rollback the transaction to recover from the error
            await session.rollback()
            return None

        except Exception as e:
            symbol = coin_data.get('symbol', 'UNKNOWN')
            coingecko_id = coin_data.get('coingecko_id', 'UNKNOWN')
            logger.error(
                f"Unexpected error importing token {symbol} (coingecko_id: {coingecko_id}): {e}"
            )
            # Log the full exception for debugging
            import traceback
            logger.debug(f"Full traceback:\n{traceback.format_exc()}")

            self.stats['errors'] += 1
            # Try to rollback in case transaction is active
            try:
                await session.rollback()
            except:
                pass
            return None

    async def import_from_json(
        self,
        session: AsyncSession,
        json_file: str,
        update_existing: bool = True,
        batch_size: int = 50
    ):
        """
        Import tokens from a JSON file.

        Args:
            session: Database session
            json_file: Path to JSON file with token data
            update_existing: Whether to update existing tokens
            batch_size: Commit every N tokens

        Returns:
            Import statistics
        """
        json_path = Path(json_file)
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_file}")

        logger.info(f"Loading tokens from {json_file}...")

        with open(json_path, 'r', encoding='utf-8') as f:
            coins_data = json.load(f)

        if not isinstance(coins_data, list):
            raise ValueError("JSON file must contain an array of tokens")

        self.stats['total'] = len(coins_data)
        logger.info(f"Found {self.stats['total']} tokens to import")

        for i, coin_data in enumerate(coins_data, 1):
            await self.import_token(session, coin_data, update_existing)

            # Commit in batches
            if i % batch_size == 0:
                try:
                    await session.commit()
                    logger.info(f"Progress: {i}/{self.stats['total']} tokens processed")
                except SQLAlchemyError as e:
                    logger.error(f"Error committing batch at {i}: {e}")
                    await session.rollback()

        # Final commit
        try:
            await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error in final commit: {e}")
            await session.rollback()

        logger.info(f"Import complete: {self.stats}")
        return self.stats

    async def import_from_dict_list(
        self,
        session: AsyncSession,
        coins_data: List[dict],
        update_existing: bool = True,
        batch_size: int = 50
    ):
        """
        Import tokens from a list of dictionaries.

        Args:
            session: Database session
            coins_data: List of token data dictionaries
            update_existing: Whether to update existing tokens
            batch_size: Commit every N tokens

        Returns:
            Import statistics
        """
        self.stats['total'] = len(coins_data)
        logger.info(f"Importing {self.stats['total']} tokens...")

        for i, coin_data in enumerate(coins_data, 1):
            await self.import_token(session, coin_data, update_existing)

            # Commit in batches
            if i % batch_size == 0:
                try:
                    await session.commit()
                    logger.info(f"Progress: {i}/{self.stats['total']} tokens processed")
                except SQLAlchemyError as e:
                    logger.error(f"Error committing batch at {i}: {e}")
                    await session.rollback()

        # Final commit
        try:
            await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error in final commit: {e}")
            await session.rollback()

        logger.info(f"Import complete: {self.stats}")
        return self.stats

    def get_stats(self) -> Dict[str, int]:
        """Get import statistics."""
        return self.stats.copy()


# Example usage
async def example_import():
    """Example of importing tokens."""
    from prisma_web3_py import get_db, init_db, close_db

    await init_db()

    importer = TokenImporter()

    async with get_db() as session:
        # Import from JSON file
        stats = await importer.import_from_json(
            session,
            "path/to/tokens.json",
            update_existing=True
        )

        print(f"Import stats: {stats}")

    await close_db()


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_import())
