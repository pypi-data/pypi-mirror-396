# Scripts Directory

测试和工具脚本集合。

---

## 🚀 导入脚本

### `import_token_recognition_data.py` ⭐ 主导入工具
导入 token_recognition 数据（自动合并 aliases）

```bash
python scripts/import_token_recognition_data.py
```

**可选参数**:
- `--no-update` - 跳过已存在的代币
- `--batch-size N` - 批次大小（默认50）

---

## 🧪 测试脚本

| 脚本 | 测试内容 | 测试数 |
|------|---------|--------|
| `test_token.py` | Token 模型和 Repository | 10 |
| `test_signal.py` | Signal 模型和 Repository | 11 |
| `test_pre_signal.py` | PreSignal 模型和 Repository | 14 ✅ |
| `test_chain_config.py` | ChainConfig 链配置 | 7 ✅ |
| `test_token_chain_integration.py` | Token + ChainConfig 集成 | 5 ✅ |
| `run_all_tests.py` | **运行所有测试** | - |

### 运行测试

```bash
# 单个测试
python scripts/test_token.py

# 运行所有测试
python scripts/run_all_tests.py
```

---

## ✅ 验证脚本

### `verify_consistency.py` ⭐ 一致性检查
全面检查模型、schema 和导入脚本的一致性（7项检查）

```bash
python scripts/verify_consistency.py
```

**检查项**: 
- Prisma ↔ Python 模型
- 字段处理
- 主链逻辑
- 唯一约束
- 模型关系
- 导入脚本

**结果**: ✅ 全部通过 (7/7)

### `test_import_data.py` - 数据验证
验证 JSON 数据有效性（导入前运行）

```bash
python scripts/test_import_data.py
```

### `test_connection.py` - 连接测试
快速数据库连接测试

```bash
python scripts/test_connection.py
```

---

## 🧹 工具脚本

### `cleanup_test_data.py`
清理测试数据（地址以 0xTEST 开头）

```bash
python scripts/cleanup_test_data.py
```

---

## 📊 推荐工作流程

### 首次导入

```bash
# 1. 验证系统
python scripts/verify_consistency.py  # 7/7 通过

# 2. 验证数据
python scripts/test_import_data.py    # 1000 tokens 有效

# 3. 执行导入
python scripts/import_token_recognition_data.py

# 4. 测试功能
```

### 日常开发

```bash
# 快速测试
python scripts/test_connection.py

# 完整测试
python scripts/run_all_tests.py
```

---

## 📁 文件列表

| 文件 | 类型 | 说明 |
|------|------|------|
| `import_token_recognition_data.py` | 导入 | 主导入脚本（含 aliases） |
| `verify_consistency.py` | 验证 | 一致性检查（7项） |
| `test_import_data.py` | 验证 | 数据验证 |
| `test_connection.py` | 测试 | 数据库连接 |
| `test_token.py` | 测试 | Token 模型 |
| `test_signal.py` | 测试 | Signal 模型 |
| `test_pre_signal.py` | 测试 | PreSignal 模型 |
| `test_chain_config.py` | 测试 | ChainConfig 链配置 |
| `test_token_chain_integration.py` | 测试 | Token + ChainConfig 集成 |
| `run_all_tests.py` | 测试 | 完整测试套件 |
| `cleanup_test_data.py` | 工具 | 清理测试数据 |

---

查看详细文档: `../IMPORT_GUIDE.md`
