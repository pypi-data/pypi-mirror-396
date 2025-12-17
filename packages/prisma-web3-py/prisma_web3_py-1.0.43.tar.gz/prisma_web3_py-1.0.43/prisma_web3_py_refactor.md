# Prisma Web3 Python & HawkFi 集成重构说明

## 目标概述

- 对 `prisma_web3_py` Python 包完成 SQLAlchemy 2.x 风格的异步会话与仓储重构：
  - 统一使用 `session_scope/get_db` 管理事务（`async with session.begin()`）。
  - CRUD 和查询全部使用 2.0 API（`select().scalars()`、ORM identity 更新）。
  - 错误处理从 “吞掉异常 + 返回默认值” 收紧为 “记录日志 + 抛出异常”，由调用方决定容错策略。
- 补全/修复 HawkFi 主项目中对该包的调用（特别是 `TokenRepository` 在 pricing 服务中的使用）。
- 增强测试与 CI：
  - 为 Python 包增加单元测试与集成测试，覆盖 JSONB 查询、统计、公共工具函数。
  - 在 GitHub Actions `publish.yml` 中加入测试步骤，通过 GitHub Secrets 注入 `DATABASE_URL` / `RUN_DB_TESTS`。

---

## 主要代码改动

### 1. 会话与配置层

文件：`prisma_web3_py/database.py`

- 新增/重构：
  - `configure_engine(database_url: Optional[str] = None, **engine_kwargs)`: 工厂式创建 engine + `async_sessionmaker`，支持测试/本地覆盖。
  - `session_scope(readonly: bool = False)`: SQLAlchemy 2.x 单元工作模式，统一 `begin()` / rollback / close。
  - `get_db = session_scope`：对外兼容旧接口。
  - `dispose_engine`, `init_db`, `close_db`：用于测试与应用关闭。
- 影响：
  - HawkFi 中所有 `async with get_db() as session:` 的位置，事务语义统一变为 “成功自动 commit，异常 rollback 并抛出”。

文件：`prisma_web3_py/config.py`

- 新增 `_normalize_url()`，并在：
  - `database_url` 属性读取 env 时；
  - `set_database_url()` 手动设置时；
 统一将 `postgres://` / `postgresql://` 正规化为 `postgresql+asyncpg://`。

### 2. BaseRepository 重构

文件：`prisma_web3_py/repositories/base_repository.py`

- 变更：
  - `create()`：
    - 不再 `try/except` 吞掉 `SQLAlchemyError`，而是直接 `session.add/flush/refresh`，异常由调用方处理。
  - `get_by_id/get_all/filter_by/count()`：
    - 使用 2.0 风格 `select(self.model)` / `select(func.count())` + `session.execute()` + `.scalars()`。
    - 删除了内部异常捕获，异常将往上冒。
  - `update_by_id` / `delete_by_id`：
    - 从 `update/delete + rowcount` 改为 “先查实体，再在 ORM 层更新/删除 + flush”，返回 `True/False`。
  - `_prepare_kwargs` 保留，用于自动规范化 `chain` 字段。
- 风险/收益：
  - 原来少数地方依赖 “失败返回 False/0” 的行为，现在 DB 异常会抛出，需要上层在关键路径作 `try/except`。
  - 更新/删除不再依赖 driver 的 `rowcount`，在有触发器/批量操作的情况下更可靠。

### 3. 各 Repository 的具体调整

#### 3.1 CryptoNewsRepository

文件：`prisma_web3_py/repositories/crypto_news_repository.py`

- 修复：
  - `create_news` 原本调用不存在的 `_to_utc(news_created_at)`，导致运行时 `NameError`。
  - 现在统一使用 `to_naive_utc` / `utc_now_naive`（从 `utils.datetime` 引入）处理所有时间字段。
- 错误处理：
  - `create_news`, `upsert_news`, 以及各种统计/查询方法:
    - 捕获 `SQLAlchemyError` 后不再返回 `None`/`[]`，而是 `logger.error(...)` 后 `raise`。
  - `upsert_twitter` 保留“软失败”行为：捕获 `Exception`，记录日志，返回 `None`。
    - 原因：Twitter 消息入库属于增强功能，失败不一定要中断整个 Handler。
- 测试增强：
  - `tests/test_repositories.py:test_crypto_news_constraint_and_upsert` 增加了 JSONB tag 搜索的覆盖：
    - 新增一条带 `tags=["unit","tests"]` 的记录；
    - 验证 `search_by_tag("tests")` 能命中。

#### 3.2 EventImpactRepository

文件：`prisma_web3_py/repositories/event_impact_repository.py`

- 修复：
  - `price_t0` 判定从 `if price_t0 and price_t0 > 0` 改为 `if price_t0 is not None and price_t0 > 0`，避免误把 0 当作“无价格”。
- 错误处理：
  - `create_snapshot`, `update_snapshot`, `update_meta` 不再吞掉异常，而是让 `SQLAlchemyError` 向上抛，只有“找不到记录”返回 `None/False`。
- 测试：
  - `tests/test_repositories.py` 中新增：
    - `test_event_impact_snapshot_and_update` / `test_event_impact_snapshot` 覆盖：
      - t0/30m/4h/24h 的变化率计算；
      - meta 合并逻辑；
      - `get_by_id` 再次读取校验。

#### 3.3 EventLabelsRepository

文件：`prisma_web3_py/repositories/event_labels_repository.py`

- 变化：
  - `create_label`：仍在 label 非法时返回 `None`（业务校验），DB 异常不再被捕获。
  - 所有查询和统计方法（`get_by_id`, `get_labels_for_event`, `get_by_label_type`, `get_by_reviewer`, `get_unlabeled_events`, `get_label_stats`, `get_reviewer_stats`, `get_events_by_label`, `get_recent_labels`, `delete_label`）：
    - 删除 `SQLAlchemyError` 捕获，异常直接抛出。
  - `has_label` 保留布尔返回语义，但不再把 DB 异常当作 `False`。
  - 仅 `get_accuracy_rate` 保留宽松的 `except Exception`，返回 `None`。

#### 3.4 PreSignalRepository & SignalRepository

文件：`pre_signal_repository.py`, `signal_repository.py`

- 变化：
  - 删除对 `SQLAlchemyError` 的捕获，所有查询/统计异常统一抛出。
  - 创建和更新接口（`create_pre_signal`, `upsert_signal`, `update_pre_signal_status`）同样不再吞错。
- 行为：
  - 正常无数据时仍返回 `None` / `[]` / `{}`；
  - DB 异常由调用方决定是否降级（例如某些 handler 使用统一 `try/except` 的外层包装）。

#### 3.5 TokenRepository

文件：`prisma_web3_py/repositories/token_repository.py`

- `__init__`：
  - 改为 `__init__(self, *args, **kwargs)`，忽略任何多余参数（用于兼容旧代码/测试中 `TokenRepository(session)` 这种调用）。
- 查询方法：
  - `get_by_address`, `get_recent_tokens`, `search_tokens`, `get_recently_updated_tokens`, `batch_get_by_addresses`, `batch_search_by_symbols`：
    - 删除 `SQLAlchemyError` 捕获，异常抛出。
  - JSONB / pg_trgm 相关方法（`search_by_alias`, `fuzzy_search`）保留 `Exception` 捕获，用于在未安装扩展时软降级。
- 写入方法：
  - `upsert_token`：
    - 对缺少 `token_address` 的数据返回 `None`（业务校验），其他 DB 异常抛出。
  - `batch_upsert_tokens`：
    - 准备阶段错误计入 `failed`；
    - `execute` 阶段若抛 `SQLAlchemyError`，仍会返回统计结构，表示批量操作失败。
    - 这一点保留原有“尽量不崩”的语义。

#### 3.6 AIAnalysisRepository

文件：`prisma_web3_py/repositories/ai_analysis_repository.py`

- 所有依赖 SQL 的方法（创建 Twitter/News 分析、查询、统计等）统一改为：
  - `logger.error(...)` 后 `raise SQLAlchemyError`，不再返回默认空结构。
- 纯 Python 归一化逻辑（`_normalize_analysis_payload` 等）保持不变。

---

## HawkFi 调用修复与影响

### 1. PricingService 与 TokenRepository

文件：`hawkfi_trader/infrastructure/pricing/service.py`

- 修复调用：
  - `get_price_by_contract`：
    - 原：`token_repo = TokenRepository(session); token = await token_repo.get_by_chain_and_address(...)`（真实 `TokenRepository` 中不存在该方法，且构造签名不匹配）。
    - 现：  
      ```python
      token_repo = TokenRepository()
      token = await token_repo.get_by_address(session, chain_lower, address_lower)
      ```
  - `get_multiple_prices`：
    - 原：`token_repo = TokenRepository(session); tokens = await token_repo.get_by_symbols(uncached_symbols)`
    - 现：
      ```python
      token_repo = TokenRepository()
      tokens = await token_repo.batch_search_by_symbols(session, uncached_symbols, exact=True)
      ```
- 影响：
  - 在真实运行环境中不再依赖不存在的 `get_by_chain_and_address/get_by_symbols`。
  - 对于 pricing 层调用者（策略、事件任务）来说，行为保持不变：找不到 token → 空 dict 或 `ValueError`，DB 异常会抛出，通过上层的 `try/except` 转为降级或失败。

### 2. News Consumer & Twitter Handler & Narrative Context

文件：
- `application/tasks/news_consumer.py`（AIAnalysis + EventImpacts）
- `application/processors/twitter_ai_analysis_handler.py`（Twitter → CryptoNews + AIAnalysis）
- `application/agents/news/narrative_context.py`（叙事上下文）

主要行为：
- AIAnalysis/News 写入路径：
  - 关键路径出错会向外抛异常，由 task handler 捕获并写入 dead-letter / metrics。
  - 保证「分析入库失败」是可观测的，而不是静默忽略。
- 叙事上下文：
  - 保持软失败：任意异常（包括 SQL）都只会记日志，并在 state 中写入 `error` 字段，agent 流程继续。

### 3. Telegram Handlers 与 PreSignal/Token

文件：
- `application/processors/jin_vip_message_handler.py`
- `application/processors/lianzhi_evm_handler.py`
- `application/processors/lianzhi_gaobei_handler.py`
- `application/processors/dca_watcher_handler.py`

行为总结：
- JinVip / 链智 Handler：
  - 外层 `_store_token_and_signal` 有统一 `try/except`，记录“写库失败”并 re-raise；
  - 这里是**关键链路**，DB 失败应直接暴露。
- DCA Watcher：
  - `_store_dca_signal` 捕获所有异常，记录 log，但不 re-raise；
  - 属于次要监控链路，系统可以容忍单条写入失败。
- 由于 repo 不再吞错，这些 handler 的行为会更清晰：
  - 关键路径：遇到 DB 错误立即被上层捕获；
  - 次要路径：仍由 handler 自己吞错并打日志。

---

## 测试与 CI

### 1. Prisma Web3 Python 测试

位置：`prisma-web3/python/tests/`

- 单元测试（无 DB）：
  - `test_config_and_datetime.py`：配置与时间工具。
  - `test_ai_analysis_utils.py`：AIAnalysis 归一化函数。
  - `test_base_repository_unit.py`：BaseRepository 行为。
- 集成测试（需 Postgres + `RUN_DB_TESTS=1`）：
  - `test_repositories.py`：习惯用法 + JSONB 查询/统计 + 约束/去重等。
  - `test_database_session.py`：`session_scope` 行为。

### 2. HawkFi Pricing 单元测试

位置：`tests/infrastructure/pricing/test_service_unit.py`

- 使用 `StubTokenRepository` + `StubCoinGecko` 等进行隔离：
  - 验证 `get_price`、`get_spot_snapshot`、`get_price_by_contract`、`get_multiple_prices` 等逻辑。
  - 通过 monkeypatch 将 `TokenRepository` 替换为 stub。
- 在本次修复中同步调整 stub：
  - 实现 `get_by_address(session, chain, address)` 与 `batch_search_by_symbols(session, symbols, exact=True)`，
  - 与新的 service 调用方式一致。

### 3. GitHub Actions publish 流程

文件：`prisma-web3/.github/workflows/publish.yml`

- 在 build + twine 之前新增：
  - 安装 dev 依赖：`pip install -e python[dev]`
  - 运行 `pytest`（总是跑单元；若配置 Secrets，则顺带跑集成测试）。
- 环境变量由 GitHub Secrets/Vars 注入：
  - `PRISMA_DATABASE_URL` → `DATABASE_URL`
  - `PRISMA_RUN_DB_TESTS` → `RUN_DB_TESTS`
- 推荐配置：
  - 在仓库 Settings → Secrets and variables → Actions 中设置：
    - `PRISMA_DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/prisma_web3_test`
    - `PRISMA_RUN_DB_TESTS=1`

---

## 总结：优化目标回顾

1. **SQLAlchemy 2.x 规范化**  
   - 全面采用 async engine + `async_sessionmaker` + `session.begin()`。
   - CRUD 与查询统一使用 ORM identity 模式，避免对 `rowcount` 的依赖。

2. **错误处理透明化**  
   - 底层 repo 不再把 SQL 异常伪装成“返回空结果”，关键逻辑可以更早发现 DB 问题。
   - 容错策略统一上移到 HawkFi 的业务层/任务/handler 中，根据场景决定是否 swallow。

3. **调用点修复与一致性**  
   - 修正了 pricing service 对 `TokenRepository` 的错误使用，确保真实运行环境和测试 stub 一致。
   - 所有关键业务路径（news_consumer、Twitter handler、链智/JinVip handler）在 DB 出错时都有明确的日志与错误传播路径。

4. **测试与 CI 集成**  
   - Python 包与 HawkFi 的关键集成点都有对应的测试覆盖（单元 + 集成）。
   - 发布流程增加测试 gate，配合 GitHub Secrets 实现标准的开源项目 CI 模式。

这份文档可作为后续维护和审查 prisma-web3 与 HawkFi 集成的设计基线。***

