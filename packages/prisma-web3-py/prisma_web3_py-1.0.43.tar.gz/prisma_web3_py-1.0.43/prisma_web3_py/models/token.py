"""
Token model - represents cryptocurrency token information.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict
from sqlalchemy import (
    BigInteger, Boolean, DateTime, Integer, Numeric, String, Text,
    UniqueConstraint, Index, func, text, and_
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign

from ..base import Base
from .token_alias import TokenAlias


class Token(Base):
    """
    Token model representing cryptocurrency token information and metadata.

    This model stores one record per token, recording its primary chain.
    Other chain addresses are stored in the platforms JSON field.

    Corresponds to Prisma model: Token
    Table: Token
    """

    __tablename__ = "Token"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # === Core identification ===
    chain: Mapped[str] = mapped_column(String(255), nullable=False, comment="Primary chain")
    token_address: Mapped[str] = mapped_column(String(255), nullable=False, comment="Primary chain address")
    symbol: Mapped[Optional[str]] = mapped_column(String(255))
    name: Mapped[Optional[str]] = mapped_column(String(255))
    coingecko_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    market_cap_rank: Mapped[Optional[int]] = mapped_column(Integer, index=True)

    # === Cross-chain support ===
    platforms: Mapped[Optional[dict]] = mapped_column(
        JSON,
        server_default=text("'{}'::json"),
        comment="Other chain addresses: {polygon: 0x..., arbitrum: 0x...}"
    )

    # === Description and display ===
    description: Mapped[Optional[str]] = mapped_column(Text)
    logo: Mapped[Optional[str]] = mapped_column(Text)

    # === Categories and aliases ===
    categories: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json")
    )
    aliases: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json")
    )

    # === Social links ===
    website: Mapped[Optional[str]] = mapped_column(Text)
    twitter: Mapped[Optional[str]] = mapped_column(String(255))
    telegram: Mapped[Optional[str]] = mapped_column(Text)
    github: Mapped[Optional[str]] = mapped_column(String(255))
    discord: Mapped[Optional[str]] = mapped_column(String(255))

    # === On-chain data ===
    decimals: Mapped[Optional[int]] = mapped_column(Integer)
    total_supply: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    deploy_time: Mapped[Optional[int]] = mapped_column(BigInteger)
    creator_address: Mapped[Optional[str]] = mapped_column(String(255))
    can_mint: Mapped[Optional[bool]] = mapped_column(Boolean)
    pool_creation_timestamp: Mapped[Optional[int]] = mapped_column(BigInteger)
    top_pools: Mapped[Optional[str]] = mapped_column(Text)

    # === Metadata ===
    raw_metadata: Mapped[Optional[dict]] = mapped_column(JSON)

    # === Timestamps ===
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now()
    )
    signal_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # === Relationships (lazy loading for async) ===
    signals: Mapped[List["Signal"]] = relationship(
        "Signal",
        back_populates="token",
        lazy="selectin",
        viewonly=True
    )
    pre_signals: Mapped[List["PreSignal"]] = relationship(
        "PreSignal",
        back_populates="token",
        lazy="selectin",
        viewonly=True
    )
    token_metrics: Mapped[Optional["TokenMetrics"]] = relationship(
        "TokenMetrics",
        back_populates="token",
        uselist=False,
        lazy="selectin",
        viewonly=True
    )
    token_analysis_reports: Mapped[List["TokenAnalysisReport"]] = relationship(
        "TokenAnalysisReport",
        back_populates="token",
        lazy="selectin",
        viewonly=True
    )
    aliases_rel: Mapped[List[TokenAlias]] = relationship(
        TokenAlias,
        back_populates="token",
        lazy="selectin",
        viewonly=True,
    )

    # === Table constraints ===
    __table_args__ = (
        UniqueConstraint('chain', 'token_address', name='Token_chain_token_address_key'),
        Index('Token_chain_idx', 'chain'),
        Index('Token_token_address_idx', 'token_address'),
        Index('Token_symbol_idx', 'symbol'),
        Index('Token_coingecko_id_idx', 'coingecko_id'),
        Index('idx_token_chain_address_optimized', 'chain', 'token_address', 'symbol', 'name'),
        Index('idx_token_aliases_gin', 'aliases', postgresql_using='gin'),
        Index('idx_token_categories_gin', 'categories', postgresql_using='gin'),
        Index('idx_token_platforms_gin', 'platforms', postgresql_using='gin'),
        {'schema': 'public'}
    )

    def __repr__(self):
        return f"<Token(id={self.id}, symbol={self.symbol}, chain={self.chain}, address={self.token_address})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "chain": self.chain,
            "token_address": self.token_address,
            "symbol": self.symbol,
            "name": self.name,
            "coingecko_id": self.coingecko_id,
            "platforms": self.platforms or {},
            "description": self.description,
            "logo": self.logo,
            "categories": self.categories or [],
            "aliases": self.aliases or [],
            "website": self.website,
            "twitter": self.twitter,
            "telegram": self.telegram,
            "github": self.github,
            "discord": self.discord,
            "decimals": self.decimals,
            "total_supply": str(self.total_supply) if self.total_supply else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_address_on_chain(self, chain: str) -> Optional[str]:
        """
        Get the token address on a specific chain.

        Args:
            chain: Chain name (e.g., "polygon", "arbitrum")

        Returns:
            Token address on that chain, or None if not available
        """
        # Mainnet tokens don't have chain-specific addresses
        if self.is_mainnet_token():
            return None

        if chain == self.chain:
            return self.token_address  # Primary chain address

        if self.platforms:
            return self.platforms.get(chain)

        return None

    def get_all_chains(self) -> List[str]:
        """
        Get all chains where this token is available.

        Returns:
            List of chain names (empty for mainnet tokens)
        """
        # Mainnet tokens don't have specific chains
        if self.is_mainnet_token():
            return []

        chains = []

        if self.chain:
            chains.append(self.chain)

        if self.platforms:
            chains.extend(self.platforms.keys())

        return chains

    def get_social_links(self) -> Dict[str, str]:
        """
        Get all social links as a dictionary.

        Returns:
            Dictionary of social links
        """
        links = {}

        if self.website:
            links['website'] = self.website
        if self.twitter:
            links['twitter'] = self.twitter
        if self.telegram:
            links['telegram'] = self.telegram
        if self.github:
            links['github'] = self.github
        if self.discord:
            links['discord'] = self.discord

        return links

    def is_mainnet_token(self) -> bool:
        """
        Check if this is a mainnet token (no specific chain).

        For mainnet tokens, chain is empty and token_address is the coingecko_id.

        Returns:
            True if mainnet token (like BTC, ETH)
        """
        return (self.chain == "" or self.chain is None) and not self.platforms

    def get_chain_abbr(self) -> str:
        """
        Get the abbreviation of the primary chain.

        Returns:
            Chain abbreviation (e.g., 'eth', 'bsc', 'sol')

        Example:
            >>> token.chain = "ethereum"
            >>> token.get_chain_abbr()
            'eth'
        """
        from ..utils.chain_config import ChainConfig
        if not self.chain:
            return ""
        return ChainConfig.get_abbreviation(self.chain)

    def get_chain_display_name(self) -> str:
        """
        Get the display name of the primary chain.

        Returns:
            Chain display name (e.g., 'Ethereum', 'BNB Chain')

        Example:
            >>> token.chain = "binance-smart-chain"
            >>> token.get_chain_display_name()
            'BNB Chain'
        """
        from ..utils.chain_config import ChainConfig
        if not self.chain:
            return "Mainnet"
        return ChainConfig.get_display_name(self.chain)

    def get_address_on_chain_abbr(self, chain_abbr: str) -> Optional[str]:
        """
        Get token address using chain abbreviation.

        Args:
            chain_abbr: Chain abbreviation (e.g., 'eth', 'bsc', 'poly')

        Returns:
            Token address on that chain, or None if not available

        Example:
            >>> token.get_address_on_chain_abbr('eth')
            '0x...'
            >>> token.get_address_on_chain_abbr('poly')
            '0x...'
        """
        from ..utils.chain_config import ChainConfig
        standard_chain = ChainConfig.get_standard_name(chain_abbr)
        return self.get_address_on_chain(standard_chain)

    def get_all_chains_with_abbr(self) -> List[Dict[str, str]]:
        """
        Get all chains where this token is available with their abbreviations.

        Returns:
            List of dicts with 'standard', 'abbr', and 'display' keys

        Example:
            >>> token.get_all_chains_with_abbr()
            [
                {'standard': 'ethereum', 'abbr': 'eth', 'display': 'Ethereum'},
                {'standard': 'polygon-pos', 'abbr': 'poly', 'display': 'Polygon'}
            ]
        """
        from ..utils.chain_config import ChainConfig

        chains = []

        # Mainnet tokens don't have chains
        if self.is_mainnet_token():
            return chains

        # Add primary chain
        if self.chain:
            chains.append({
                'standard': self.chain,
                'abbr': ChainConfig.get_abbreviation(self.chain),
                'display': ChainConfig.get_display_name(self.chain)
            })

        # Add other chains from platforms
        if self.platforms:
            for chain in self.platforms.keys():
                chains.append({
                    'standard': chain,
                    'abbr': ChainConfig.get_abbreviation(chain),
                    'display': ChainConfig.get_display_name(chain)
                })

        return chains
