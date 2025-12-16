# Quick Start Guide

快速开始使用 `prisma-web3-py` 包。

## 5 分钟快速上手

### 1. 安装包（选择一种方式）

**方式 A: 本地开发安装**
```bash
cd /Users/qinghuan/Documents/code/prisma-web3/python
pip install -e .
```

**方式 B: 在你的项目中引用**
```bash
# 在你的项目中创建 requirements.txt
echo "prisma-web3-py @ file:///Users/qinghuan/Documents/code/prisma-web3/python" > requirements.txt
pip install -r requirements.txt
```

### 2. 配置数据库

创建 `.env` 文件：
```bash
echo "DATABASE_URL=postgresql://user:password@localhost:5432/prisma_web3" > .env
```

### 3. 编写代码

创建 `test.py`：
```python
import asyncio
from prisma_web3_py import get_db
from prisma_web3_py.repositories import TokenRepository

async def main():
    repo = TokenRepository()

    async with get_db() as session:
        tokens = await repo.get_verified_tokens(session, chain="ethereum", limit=5)
        print(f"Found {len(tokens)} tokens:")
        for token in tokens:
            print(f"  - {token.symbol}: {token.name}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. 运行

```bash
python test.py
```

---

## 常用代码片段

### 查询 Token

```python
from prisma_web3_py import get_db
from prisma_web3_py.repositories import TokenRepository

async def get_token_info(chain: str, address: str):
    repo = TokenRepository()
    async with get_db() as session:
        token = await repo.get_by_address(session, chain, address)
        return token.to_dict() if token else None
```

### 添加/更新 Token

```python
async def upsert_token_data(token_data: dict):
    repo = TokenRepository()
    async with get_db() as session:
        token_id = await repo.upsert_token(session, token_data)
        return token_id
```

### 查询最近信号

```python
from prisma_web3_py.repositories import SignalRepository

async def get_recent_buy_signals():
    repo = SignalRepository()
    async with get_db() as session:
        signals = await repo.get_recent_signals(
            session,
            signal_type="buy",
            hours=24
        )
        return [s.to_dict() for s in signals]
```

### 获取热门 Token

```python
async def get_trending_tokens():
    repo = SignalRepository()
    async with get_db() as session:
        trending = await repo.get_trending_tokens_by_signals(
            session,
            hours=24,
            limit=20
        )
        return [(t.to_dict(), count) for t, count in trending]
```

---

## FastAPI 快速集成

```python
from fastapi import FastAPI, Depends
from prisma_web3_py import get_db, init_db
from prisma_web3_py.repositories import TokenRepository

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/tokens/{chain}")
async def list_tokens(chain: str, session = Depends(get_db)):
    repo = TokenRepository()
    tokens = await repo.get_verified_tokens(session, chain=chain)
    return [t.to_dict() for t in tokens]

# 运行: uvicorn main:app --reload
```

---

## 完整示例项目

查看 `examples/async_usage.py` 获取完整示例。

---

## 需要帮助？

- 📖 [完整文档](README.md)
- 🔧 [安装指南](INSTALLATION.md)
- 🚀 [集成指南](INTEGRATION_GUIDE.md)
- 💡 [示例代码](examples/)
