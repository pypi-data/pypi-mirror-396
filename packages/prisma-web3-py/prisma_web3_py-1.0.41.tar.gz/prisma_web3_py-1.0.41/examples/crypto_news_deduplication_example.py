"""
CryptoNews deduplication examples.

Demonstrates how to handle duplicate news using unique constraints and content hashing.
"""

import asyncio
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from prisma_web3_py import init_db, close_db, get_db, CryptoNewsRepository, CryptoNews


async def example_unique_constraint():
    """Example: Unique constraint prevents duplicate imports by source+link."""

    repo = CryptoNewsRepository()

    api_data = {
        "title": "OKX 将上线 SEI (Sei)，2Z (DoubleZero)现货交易",
        "category": 1,
        "source": "TechFlow",
        "sourceLink": "https://www.techflowpost.com/newsletter/detail_105321.html",
        "content": "11 月 14 日，据官方公告...",
        "matchedCurrencies": [{"name": "SEI"}, {"name": "2Z"}],
        "entityList": ["OKX", "SEI", "2Z"],
        "createTime": "1763089364248"
    }

    async with get_db() as session:
        news_time = datetime.fromtimestamp(int(api_data["createTime"]) / 1000)

        print("=" * 60)
        print("Example 1: Unique Constraint (source + source_link)")
        print("=" * 60)

        # First import - should succeed
        print("\n1. First import attempt...")
        try:
            news1 = await repo.create_news(
                session,
                title=api_data["title"],
                category=api_data["category"],
                source=api_data["source"],
                content=api_data["content"],
                source_link=api_data.get("sourceLink"),
                matched_currencies=api_data.get("matchedCurrencies", []),
                entity_list=api_data.get("entityList", []),
                news_created_at=news_time
            )
            await session.commit()
            print(f"   ✅ Success! Created news ID: {news1.id}")
            print(f"   Content hash: {news1.content_hash[:16]}...")
        except IntegrityError as e:
            await session.rollback()
            print(f"   ❌ Duplicate detected: {e}")

        # Second import - should fail due to unique constraint
        print("\n2. Second import attempt (same source + link)...")
        try:
            news2 = await repo.create_news(
                session,
                title=api_data["title"],
                category=api_data["category"],
                source=api_data["source"],
                content=api_data["content"],
                source_link=api_data.get("sourceLink"),
                matched_currencies=api_data.get("matchedCurrencies", []),
                entity_list=api_data.get("entityList", []),
                news_created_at=news_time
            )
            await session.commit()
            print(f"   ✅ Created news ID: {news2.id}")
        except IntegrityError:
            await session.rollback()
            print(f"   ❌ Duplicate detected! Unique constraint (source, source_link) violated.")
            print(f"   This is expected - preventing duplicate imports.")


async def example_upsert():
    """Example: Use upsert to handle duplicates gracefully."""

    repo = CryptoNewsRepository()

    api_data = {
        "title": "Bitfarms 宣布将在未来两年内逐步关停比特币挖矿业务",
        "category": 1,
        "source": "ChainCatcher",
        "sourceLink": "https://www.chaincatcher.com/article/2220067",
        "content": "据 Cointelegraph 报道...",
        "matchedCurrencies": [{"name": "BTC"}],
        "entityList": ["Bitfarms", "Bitcoin"],
        "createTime": "1763089232302"
    }

    async with get_db() as session:
        news_time = datetime.fromtimestamp(int(api_data["createTime"]) / 1000)

        print("\n" + "=" * 60)
        print("Example 2: UPSERT (Insert or Update)")
        print("=" * 60)

        # First upsert - will insert
        print("\n1. First upsert (will INSERT)...")
        news1 = await repo.upsert_news(
            session,
            title=api_data["title"],
            category=api_data["category"],
            source=api_data["source"],
            content=api_data["content"],
            source_link=api_data.get("sourceLink"),
            matched_currencies=api_data.get("matchedCurrencies", []),
            entity_list=api_data.get("entityList", []),
            news_created_at=news_time
        )
        await session.commit()
        print(f"   ✅ Upserted news ID: {news1.id}")
        print(f"   Title: {news1.title[:60]}...")

        # Second upsert - will update
        print("\n2. Second upsert (will UPDATE)...")
        updated_data = api_data.copy()
        updated_data["title"] = "【更新】" + updated_data["title"]

        news2 = await repo.upsert_news(
            session,
            title=updated_data["title"],  # Updated title
            category=updated_data["category"],
            source=updated_data["source"],
            content=updated_data["content"],
            source_link=updated_data.get("sourceLink"),
            matched_currencies=updated_data.get("matchedCurrencies", []),
            entity_list=updated_data.get("entityList", []),
            tags=["updated"],  # Added tag
            news_created_at=news_time
        )
        await session.commit()
        print(f"   ✅ Upserted news ID: {news2.id}")
        print(f"   Same ID? {news1.id == news2.id} (should be True)")
        print(f"   Updated title: {news2.title[:60]}...")
        print(f"   Tags: {news2.tags}")


async def example_content_hash():
    """Example: Detect duplicate content using content_hash."""

    repo = CryptoNewsRepository()

    async with get_db() as session:
        print("\n" + "=" * 60)
        print("Example 3: Content Hash Deduplication")
        print("=" * 60)

        # Same content, different source links
        content = "This is the same news content that appears on multiple sites."

        data1 = {
            "title": "News from Site 1",
            "category": 1,
            "source": "Site1",
            "sourceLink": "https://site1.com/news/123",
            "content": content,
            "createTime": str(int(datetime.utcnow().timestamp() * 1000))
        }

        data2 = {
            "title": "News from Site 2",
            "category": 1,
            "source": "Site2",
            "sourceLink": "https://site2.com/article/456",  # Different link!
            "content": content,  # Same content!
            "createTime": str(int(datetime.utcnow().timestamp() * 1000))
        }

        # Generate content hash
        content_hash = CryptoNews.generate_content_hash(content)
        print(f"\n1. Content hash: {content_hash}")

        # Import from site 1
        print("\n2. Importing from Site1...")
        news1 = await repo.upsert_news(
            session,
            title=data1["title"],
            category=data1["category"],
            source=data1["source"],
            content=data1["content"],
            source_link=data1.get("sourceLink"),
            news_created_at=datetime.fromtimestamp(int(data1["createTime"]) / 1000)
        )
        await session.commit()
        print(f"   ✅ Created news ID: {news1.id}")

        # Check for duplicate before importing from site 2
        print("\n3. Checking for duplicate content before importing from Site2...")
        duplicate = await repo.check_duplicate_by_hash(session, content_hash)
        if duplicate:
            print(f"   ⚠️  Duplicate content detected!")
            print(f"   Existing news ID: {duplicate.id}")
            print(f"   Existing source: {duplicate.source}")
            print(f"   Existing link: {duplicate.source_link}")
            print(f"   Decision: Skip import or link as duplicate")
        else:
            print(f"   ✅ No duplicate found, safe to import")


async def example_batch_import_with_deduplication():
    """Example: Batch import with automatic deduplication."""

    repo = CryptoNewsRepository()

    # Simulated API response with some duplicates
    api_response = {
        "list": [
            {
                "title": "News 1",
                "category": 1,
                "source": "Source1",
                "sourceLink": "https://source1.com/1",
                "content": "Content 1...",
                "createTime": str(int(datetime.utcnow().timestamp() * 1000))
            },
            {
                "title": "News 2",
                "category": 1,
                "source": "Source1",
                "sourceLink": "https://source1.com/2",
                "content": "Content 2...",
                "createTime": str(int(datetime.utcnow().timestamp() * 1000))
            },
            {
                "title": "News 1 (Duplicate)",
                "category": 1,
                "source": "Source1",
                "sourceLink": "https://source1.com/1",  # Duplicate!
                "content": "Content 1...",
                "createTime": str(int(datetime.utcnow().timestamp() * 1000))
            },
        ]
    }

    async with get_db() as session:
        print("\n" + "=" * 60)
        print("Example 4: Batch Import with Deduplication")
        print("=" * 60)

        created = 0
        updated = 0
        skipped = 0

        for idx, item in enumerate(api_response["list"], 1):
            print(f"\n{idx}. Importing: {item['title']}")

            try:
                news = await repo.upsert_news(
                    session,
                    title=item["title"],
                    category=item["category"],
                    source=item["source"],
                    content=item["content"],
                    source_link=item.get("sourceLink"),
                    news_created_at=datetime.fromtimestamp(int(item["createTime"]) / 1000)
                )

                # Check if it was an insert or update
                # (In real scenario, you'd compare created_at and updated_at)
                if news:
                    created += 1
                    print(f"   ✅ Processed (ID: {news.id})")

            except Exception as e:
                skipped += 1
                print(f"   ⚠️  Skipped: {e}")

        await session.commit()

        print(f"\n📊 Import Summary:")
        print(f"   Created/Updated: {created}")
        print(f"   Skipped: {skipped}")
        print(f"   Total: {len(api_response['list'])}")


async def main():
    """Run all examples."""
    await init_db()

    try:
        # Run examples
        await example_unique_constraint()
        await example_upsert()
        await example_content_hash()
        await example_batch_import_with_deduplication()

        print("\n" + "=" * 60)
        print("✅ All deduplication examples completed!")
        print("=" * 60)

    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
