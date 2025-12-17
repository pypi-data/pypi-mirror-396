"""
Basic usage examples for prisma-web3-py package.
"""

import os
from prisma_web3_py import get_session
from prisma_web3_py.models import Token, Signal, SmartWallet


def example_query_tokens():
    """Query tokens from the database."""
    session = get_session()

    try:
        # Query all verified tokens on Ethereum
        tokens = session.query(Token).filter(
            Token.chain == 'ethereum',
            Token.verification_status == 'verified'
        ).limit(10).all()

        print(f"Found {len(tokens)} verified Ethereum tokens:")
        for token in tokens:
            print(f"  - {token.symbol} ({token.name}): {token.token_address}")

    finally:
        session.close()


def example_query_signals():
    """Query recent trading signals."""
    session = get_session()

    try:
        # Query recent buy signals
        signals = session.query(Signal).filter(
            Signal.signal_type == 'buy'
        ).order_by(
            Signal.last_occurrence.desc()
        ).limit(10).all()

        print(f"\nFound {len(signals)} recent buy signals:")
        for signal in signals:
            print(f"  - {signal.source}: {signal.token_address} on {signal.chain}")
            print(f"    Last seen: {signal.last_occurrence}")
            print(f"    Occurrence count: {signal.occurrence_count}")

    finally:
        session.close()


def example_query_smart_wallets():
    """Query top smart wallets by score."""
    session = get_session()

    try:
        # Query smart wallets with high scores
        wallets = session.query(SmartWallet).filter(
            SmartWallet.score > 80
        ).order_by(
            SmartWallet.score.desc()
        ).limit(10).all()

        print(f"\nFound {len(wallets)} high-score smart wallets:")
        for wallet in wallets:
            print(f"  - {wallet.wallet_address} (Score: {wallet.score})")
            print(f"    Chain: {wallet.chain}")
            print(f"    Realized Profit: {wallet.realized_profit}")
            print(f"    Winrate (7d): {wallet.winrate_7d}")

    finally:
        session.close()


def example_complex_query():
    """Example of a more complex query with joins."""
    session = get_session()

    try:
        # Query tokens that have recent signals
        results = session.query(Token, Signal).join(
            Signal,
            (Token.chain == Signal.chain) & (Token.token_address == Signal.token_address)
        ).filter(
            Token.verification_status == 'verified',
            Signal.signal_type == 'buy',
        ).limit(10).all()

        print(f"\nFound {len(results)} verified tokens with recent buy signals:")
        for token, signal in results:
            print(f"  - {token.symbol} on {token.chain}")
            print(f"    Signal from: {signal.source}")
            print(f"    Last occurrence: {signal.last_occurrence}")

    finally:
        session.close()


if __name__ == "__main__":
    # Set your database URL
    # os.environ['DATABASE_URL'] = 'postgresql://user:password@localhost:5432/dbname'

    print("=== Prisma Web3 Python Package Examples ===\n")

    # Run examples
    example_query_tokens()
    example_query_signals()
    example_query_smart_wallets()
    example_complex_query()

    print("\n=== Examples completed ===")
