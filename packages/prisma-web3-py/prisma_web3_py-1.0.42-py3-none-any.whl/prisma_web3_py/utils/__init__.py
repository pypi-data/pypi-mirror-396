"""
Utility modules for prisma-web3-py.

We avoid eagerly importing heavy utilities (e.g., TokenImporter) to prevent
circular imports when repositories pull lightweight helpers. TokenImporter is
exposed via lazy import.
"""

from .chain_config import ChainConfig, Chain, abbr, standard, display

__all__ = [
    'ChainConfig',
    'Chain',
    'abbr',
    'standard',
    'display',
    'TokenImporter',
]


def __getattr__(name):
    if name == "TokenImporter":
        from .token_importer import TokenImporter  # lazy import to avoid cycles
        return TokenImporter
    raise AttributeError(name)
