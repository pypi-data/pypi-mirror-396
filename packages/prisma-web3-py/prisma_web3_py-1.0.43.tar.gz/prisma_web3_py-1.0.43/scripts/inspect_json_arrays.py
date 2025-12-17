"""
Inspect JSON/JSONB columns that are expected to be arrays but may contain
legacy scalar/object values.

Targets:
  - AIAnalysisResult.tokens
  - CryptoNews.matched_currencies
  - CryptoNews.entity_list

Usage (from repo root):
  poetry run python prisma-web3/python/scripts/inspect_json_arrays.py

The script only reads data and prints:
  - type distribution per column (jsonb_typeof)
  - a small sample of non-array rows for manual inspection
"""

from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy import text
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv

load_dotenv()


from prisma_web3_py.database import session_scope


async def _inspect_ai_tokens(limit: int = 20) -> None:
    print("\n=== AIAnalysisResult.tokens type distribution ===")
    async with session_scope(readonly=True) as session:
        summary_sql = text(
            """
            SELECT
                jsonb_typeof(tokens::jsonb) AS kind,
                COUNT(*) AS cnt
            FROM "AIAnalysisResult"
            WHERE tokens IS NOT NULL
            GROUP BY kind
            ORDER BY cnt DESC;
            """
        )
        result = await session.execute(summary_sql)
        rows = result.fetchall()
        if not rows:
            print("  (no non-NULL tokens rows)")
        else:
            for kind, cnt in rows:
                print(f"  {kind or 'NULL'}: {cnt}")

        print(f"\n=== AIAnalysisResult.tokens non-array samples (limit {limit}) ===")
        samples_sql = text(
            """
            SELECT id, source_type, source_id, tokens
            FROM "AIAnalysisResult"
            WHERE tokens IS NOT NULL
              AND jsonb_typeof(tokens::jsonb) <> 'array'
            ORDER BY id DESC
            LIMIT :limit;
            """
        )
        result = await session.execute(samples_sql, {"limit": limit})
        samples = result.fetchall()
        if not samples:
            print("  (no non-array tokens rows)")
        else:
            for row in samples:
                print(f"  id={row.id}, source_type={row.source_type}, source_id={row.source_id}, tokens={row.tokens}")


async def _fix_ai_tokens() -> None:
    """
    Normalize AIAnalysisResult.tokens so that they are always arrays (or NULL at SQL level).

    - JSON 'null' -> '[]'
    - SQL NULL    -> '[]'
    """
    print("\n=== Fixing AIAnalysisResult.tokens JSON null / SQL NULL ===")
    async with session_scope() as session:
        # JSON null -> []
        update_json_null = text(
            """
            UPDATE "AIAnalysisResult"
            SET tokens = '[]'::jsonb
            WHERE tokens IS NOT NULL
              AND jsonb_typeof(tokens::jsonb) = 'null';
            """
        )
        res1 = await session.execute(update_json_null)
        print(f"  JSON null -> [] rows affected: {res1.rowcount}")

        # SQL NULL -> []
        update_sql_null = text(
            """
            UPDATE "AIAnalysisResult"
            SET tokens = '[]'::jsonb
            WHERE tokens IS NULL;
            """
        )
        res2 = await session.execute(update_sql_null)
        print(f"  SQL NULL -> [] rows affected: {res2.rowcount}")


async def _inspect_crypto_news(limit: int = 20) -> None:
    async with session_scope(readonly=True) as session:
        print("\n=== CryptoNews.matched_currencies type distribution ===")
        mc_summary = text(
            """
            SELECT
                jsonb_typeof(matched_currencies::jsonb) AS kind,
                COUNT(*) AS cnt
            FROM "CryptoNews"
            WHERE matched_currencies IS NOT NULL
            GROUP BY kind
            ORDER BY cnt DESC;
            """
        )
        result = await session.execute(mc_summary)
        for kind, cnt in result.fetchall() or []:
            print(f"  {kind or 'NULL'}: {cnt}")

        print(f"\n=== CryptoNews.matched_currencies non-array samples (limit {limit}) ===")
        mc_samples = text(
            """
            SELECT id, source, source_link, matched_currencies
            FROM "CryptoNews"
            WHERE matched_currencies IS NOT NULL
              AND jsonb_typeof(matched_currencies::jsonb) <> 'array'
            ORDER BY id DESC
            LIMIT :limit;
            """
        )
        result = await session.execute(mc_samples, {"limit": limit})
        samples = result.fetchall()
        if not samples:
            print("  (no non-array matched_currencies rows)")
        else:
            for row in samples:
                print(
                    f"  id={row.id}, source={row.source}, "
                    f"source_link={row.source_link}, matched_currencies={row.matched_currencies}"
                )

        print("\n=== CryptoNews.entity_list type distribution ===")
        el_summary = text(
            """
            SELECT
                jsonb_typeof(entity_list::jsonb) AS kind,
                COUNT(*) AS cnt
            FROM "CryptoNews"
            WHERE entity_list IS NOT NULL
            GROUP BY kind
            ORDER BY cnt DESC;
            """
        )
        result = await session.execute(el_summary)
        for kind, cnt in result.fetchall() or []:
            print(f"  {kind or 'NULL'}: {cnt}")

        print(f"\n=== CryptoNews.entity_list non-array samples (limit {limit}) ===")
        el_samples = text(
            """
            SELECT id, source, source_link, entity_list
            FROM "CryptoNews"
            WHERE entity_list IS NOT NULL
              AND jsonb_typeof(entity_list::jsonb) <> 'array'
            ORDER BY id DESC
            LIMIT :limit;
            """
        )
        result = await session.execute(el_samples, {"limit": limit})
        samples = result.fetchall()
        if not samples:
            print("  (no non-array entity_list rows)")
        else:
            for row in samples:
                print(
                    f"  id={row.id}, source={row.source}, "
                    f"source_link={row.source_link}, entity_list={row.entity_list}"
                )


async def _fix_crypto_news() -> None:
    """
    Normalize CryptoNews.matched_currencies/entity_list so they are arrays (or NULL at SQL level).

    - JSON 'null' -> '[]'
    - SQL NULL    -> '[]'
    """
    print("\n=== Fixing CryptoNews JSON null / SQL NULL ===")
    async with session_scope() as session:
        # matched_currencies
        update_mc_json_null = text(
            """
            UPDATE "CryptoNews"
            SET matched_currencies = '[]'::jsonb
            WHERE matched_currencies IS NOT NULL
              AND jsonb_typeof(matched_currencies::jsonb) = 'null';
            """
        )
        res1 = await session.execute(update_mc_json_null)
        print(f"  matched_currencies JSON null -> [] rows affected: {res1.rowcount}")

        update_mc_sql_null = text(
            """
            UPDATE "CryptoNews"
            SET matched_currencies = '[]'::jsonb
            WHERE matched_currencies IS NULL;
            """
        )
        res2 = await session.execute(update_mc_sql_null)
        print(f"  matched_currencies SQL NULL -> [] rows affected: {res2.rowcount}")

        # entity_list
        update_el_json_null = text(
            """
            UPDATE "CryptoNews"
            SET entity_list = '[]'::jsonb
            WHERE entity_list IS NOT NULL
              AND jsonb_typeof(entity_list::jsonb) = 'null';
            """
        )
        res3 = await session.execute(update_el_json_null)
        print(f"  entity_list JSON null -> [] rows affected: {res3.rowcount}")

        update_el_sql_null = text(
            """
            UPDATE "CryptoNews"
            SET entity_list = '[]'::jsonb
            WHERE entity_list IS NULL;
            """
        )
        res4 = await session.execute(update_el_sql_null)
        print(f"  entity_list SQL NULL -> [] rows affected: {res4.rowcount}")


async def main() -> None:
    # Fix first, then re-inspect so the output reflects the cleaned state.
    await _fix_ai_tokens()
    await _fix_crypto_news()
    await _inspect_ai_tokens()
    await _inspect_crypto_news()


if __name__ == "__main__":
    asyncio.run(main())
