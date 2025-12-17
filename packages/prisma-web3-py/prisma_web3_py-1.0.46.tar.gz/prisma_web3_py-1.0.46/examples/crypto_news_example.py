"""
CryptoNews usage examples.

Demonstrates how to store and query cryptocurrency news.
"""

import asyncio
from datetime import datetime
from prisma_web3_py import init_db, close_db, get_db, CryptoNewsRepository


async def example_create_news():
    """Example: Create crypto news from external API data."""

    # Example data from your API
    api_data = {
        "title": "OKX 将上线 SEI (Sei)，2Z (DoubleZero)现货交易",
        "category": 1,
        "source": "TechFlow",
        "sourceLink": "https://www.techflowpost.com/newsletter/detail_105321.html",
        "content": "11 月 14 日，据官方公告，OKX 即将上线SEI (Sei)，2Z (DoubleZero)...",
        "sector": "Others",
        "matchedCurrencies": [
            {"name": "2Z"},
            {"name": "SEI"},
            {"name": "OKB"}
        ],
        "matchedStocks": [],
        "createTime": "1763089364248",  # Millisecond timestamp
        "entityList": ["OKX", "SEI", "2Z"]
    }

    repo = CryptoNewsRepository()

    async with get_db() as session:
        # Convert createTime from milliseconds to datetime
        news_created_at = datetime.fromtimestamp(int(api_data["createTime"]) / 1000)

        # ✅ Correct: Use repository.create_news()
        news = await repo.create_news(
            session,
            title=api_data["title"],
            category=api_data["category"],
            source=api_data["source"],
            content=api_data["content"],
            source_link=api_data.get("sourceLink"),
            sector=api_data.get("sector"),
            matched_currencies=api_data.get("matchedCurrencies", []),
            matched_stocks=api_data.get("matchedStocks", []),
            entity_list=api_data.get("entityList", []),
            news_created_at=news_created_at
        )

        if news:
            await session.commit()
            print(f"✅ Created news ID: {news.id}")
            print(f"   Title: {news.title}")
            print(f"   Matched currencies: {news.get_currency_names()}")
            return news
        else:
            print("❌ Failed to create news")
            return None


async def example_batch_import():
    """Example: Batch import news from API response."""

    # Example API response with multiple news
    api_response = {
        "status": "success",
        "data": {
            "list": [
                {
                    "title": "OKX 将上线 SEI (Sei)，2Z (DoubleZero)现货交易",
                    "category": 1,
                    "source": "TechFlow",
                    "sourceLink": "https://www.techflowpost.com/newsletter/detail_105321.html",
                    "content": "...",
                    "sector": "Others",
                    "matchedCurrencies": [{"name": "SEI"}, {"name": "2Z"}],
                    "matchedStocks": [],
                    "createTime": "1763089364248",
                    "entityList": ["OKX", "SEI"]
                },
                {
                    "title": "Bitfarms 宣布将在未来两年内逐步关停比特币挖矿业务",
                    "category": 1,
                    "source": "ChainCatcher",
                    "sourceLink": "https://www.chaincatcher.com/article/2220067",
                    "content": "...",
                    "sector": "Bitcoin",
                    "matchedCurrencies": [{"name": "BTC"}],
                    "matchedStocks": [],
                    "createTime": "1763089232302",
                    "entityList": ["Bitfarms", "Bitcoin"]
                }
            ]
        }
    }

    repo = CryptoNewsRepository()

    async with get_db() as session:
        created_count = 0

        for item in api_response["data"]["list"]:
            news_created_at = datetime.fromtimestamp(int(item["createTime"]) / 1000)

            news = await repo.create_news(
                session,
                title=item["title"],
                category=item["category"],
                source=item["source"],
                content=item["content"],
                source_link=item.get("sourceLink"),
                sector=item.get("sector"),
                matched_currencies=item.get("matchedCurrencies", []),
                matched_stocks=item.get("matchedStocks", []),
                entity_list=item.get("entityList", []),
                news_created_at=news_created_at
            )

            if news:
                created_count += 1

        # Commit all at once
        await session.commit()
        print(f"✅ Imported {created_count} news articles")


async def example_query_news():
    """Example: Query news."""

    repo = CryptoNewsRepository()

    async with get_db() as session:
        # 1. Get recent news (last 24 hours)
        recent_news = await repo.get_recent_news(session, hours=24, limit=10)
        print(f"\n📰 Recent news (24h): {len(recent_news)} articles")
        for news in recent_news[:3]:
            print(f"   - {news.title}")

        # 2. Search news about a specific cryptocurrency
        btc_news = await repo.search_by_currency(session, "BTC", hours=72)
        print(f"\n₿ Bitcoin news: {len(btc_news)} articles")

        # 3. Search news by entity
        okx_news = await repo.search_by_entity(session, "OKX", hours=24)
        print(f"\n🏢 OKX mentions: {len(okx_news)} articles")

        # 4. Get news by source
        techflow_news = await repo.get_news_by_source(session, "TechFlow", hours=24)
        print(f"\n📱 TechFlow articles: {len(techflow_news)}")

        # 5. Get trending cryptocurrencies
        trending = await repo.get_trending_currencies(session, hours=24, limit=10)
        print(f"\n🔥 Trending cryptocurrencies:")
        for item in trending[:5]:
            print(f"   - {item['currency']}: {item['mentions']} mentions")

        # 6. Get trending entities
        trending_entities = await repo.get_trending_entities(session, hours=24, limit=10)
        print(f"\n🔥 Trending entities:")
        for item in trending_entities[:5]:
            print(f"   - {item['entity']}: {item['mentions']} mentions")

        # 7. Search by tag
        defi_news = await repo.search_by_tag(session, "defi", hours=24)
        print(f"\n🏷️  DeFi tagged news: {len(defi_news)}")

        # 8. Get statistics
        stats = await repo.get_news_statistics(session, hours=24)
        print(f"\n📊 News statistics (24h):")
        print(f"   Total: {stats['total']}")
        print(f"   By source: {stats['by_source']}")
        print(f"   By sector: {stats['by_sector']}")


async def example_search_news():
    """Example: Search news by keyword."""

    repo = CryptoNewsRepository()

    async with get_db() as session:
        # Search in title
        results = await repo.search_news(
            session,
            search_term="Bitcoin",
            search_in_content=False,
            limit=10
        )
        print(f"\n🔍 Search results for 'Bitcoin' in title: {len(results)}")

        # Search in both title and content
        results_full = await repo.search_news(
            session,
            search_term="DeFi",
            search_in_content=True,
            limit=20
        )
        print(f"🔍 Search results for 'DeFi' in title+content: {len(results_full)}")


async def main():
    """Run all examples."""
    await init_db()

    try:
        print("=" * 60)
        print("CryptoNews Examples")
        print("=" * 60)

        # Uncomment to run specific examples:

        # await example_create_news()
        # await example_batch_import()
        await example_query_news()
        # await example_search_news()

    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
