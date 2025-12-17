# Prisma Web3 Utils

Utility modules for the prisma-web3-py package.

## Modules

### 1. TokenImporter

Import tokens from CoinGecko JSON format into the database.

**Features**:
- Automatic primary chain detection
- Batch import with configurable commit size
- Update existing tokens
- Statistics tracking
- Error handling and logging

**Usage**:

```python
from prisma_web3_py import get_db
from prisma_web3_py.utils import TokenImporter

importer = TokenImporter()

async with get_db() as session:
    # Import from JSON file
    stats = await importer.import_from_json(
        session,
        "tokens.json",
        update_existing=True,
        batch_size=50
    )

    print(f"Created: {stats['created']}")
    print(f"Updated: {stats['updated']}")
    print(f"Errors: {stats['errors']}")
```

**CLI Tool**:

```bash
python scripts/import_tokens.py data/tokens.json
python scripts/import_tokens.py data/tokens.json --no-update
python scripts/import_tokens.py data/tokens.json --batch-size 100
```

**Expected JSON Format**:

```json
[
  {
    "coingecko_id": "uniswap",
    "symbol": "UNI",
    "name": "Uniswap",
    "description": "UNI is the governance token for Uniswap",
    "logo": "https://...",
    "market_cap_rank": 20,
    "platforms": {
      "ethereum": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
      "polygon": "0xb33eaad8d922b1083446dc23f610c2567fb5180f",
      "arbitrum": "0xfa7f8980b0f1e64a2062791cc3b0871572f1f7f0"
    },
    "categories": ["DeFi", "DEX"],
    "aliases": ["UNI-V2"],
    "social_links": {
      "website": "https://uniswap.org",
      "twitter": "@Uniswap",
      "telegram": "https://t.me/uniswap",
      "github": "uniswap",
      "discord": "https://discord.gg/uniswap"
    }
  }
]
```

**Primary Chain Priority**:
1. ethereum
2. binance-smart-chain
3. polygon-pos
4. solana
5. arbitrum-one
6. optimistic-ethereum
7. avalanche
8. (fallback to first chain in platforms)

**Mainnet Tokens**:
For tokens like BTC, ETH that don't have a specific chain:
```json
{
  "coingecko_id": "bitcoin",
  "symbol": "BTC",
  "name": "Bitcoin",
  "platforms": {}  // Empty platforms
}
```
These will be stored with `chain=""` and `token_address=""`.

---

## Testing

Run tests for the utils modules:

```bash
# Test TokenImporter (via token tests)
python scripts/test_token.py

# Test TokenRecognition
python scripts/test_token_recognition.py

# Run all tests
python scripts/run_all_tests.py
```

## Examples

See example usage in:
- `prisma_web3_py/utils/token_importer.py` (bottom of file)
- `prisma_web3_py/utils/token_recognition.py` (bottom of file)
- `scripts/import_tokens.py` (CLI tool)
- `scripts/test_token_recognition.py` (comprehensive tests)

## Dependencies

- `sqlalchemy` - Database ORM
- `asyncpg` - Async PostgreSQL driver
- `python-dotenv` - Environment configuration

All dependencies are included in the main package requirements.
