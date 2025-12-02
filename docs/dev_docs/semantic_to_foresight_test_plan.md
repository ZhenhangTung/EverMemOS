# Semantic → Foresight 重命名合并测试方案

> **文档日期**: 2025-12-02  
> **相关分支**: `refactor/semantic-to-foresight`  
> **关联文档**: [semantic_to_foresight_refactor.md](./semantic_to_foresight_refactor.md)

---

## 一、测试背景

本测试方案用于验证 `semantic_memory` → `foresight` 重命名重构与 `refactor/memory-layer-queue` 分支合并后的代码正确性。

### 核心变更点

| 变更类型 | 原名称 | 新名称 |
|---------|-------|-------|
| 枚举值 | `MemoryType.SEMANTIC_MEMORY` | `MemoryType.FORESIGHT` |
| 枚举值 | `MemoryType.PERSONAL_SEMANTIC_MEMORY` | `MemoryType.PERSONAL_FORESIGHT` |
| API 参数 | `data_source=semantic_memory` | `data_source=foresight` |
| 配置参数 | `enable_semantic_extraction` | `enable_foresight_extraction` |
| MongoDB 集合 | `semantic_memories` | `foresights` |
| MongoDB 集合 | `semantic_memory_records` | `foresight_records` |
| Milvus 集合 | `semantic_memory` | `foresight` |

---

## 二、测试阶段

### 第一阶段：静态检查

#### 1.1 语法检查

```bash
cd /Users/admin/Applications/cursor_project/openv2/memsys-opensource

# 核心业务层
python -m py_compile src/biz_layer/*.py

# API 层
python -m py_compile src/agentic_layer/*.py

# 记忆层
python -m py_compile src/memory_layer/*.py src/memory_layer/memory_extractor/*.py

# API 规范
python -m py_compile src/api_specs/*.py src/api_specs/dtos/*.py

# 基础设施层
python -m py_compile src/infra_layer/adapters/out/persistence/repository/*.py
```

**预期结果**: 全部通过，无语法错误

#### 1.2 旧名称残留检查

```bash
# 检查 src/ 目录
grep -rn "semantic_memory\|SemanticMemory\|SEMANTIC_MEMORY" src/ --include="*.py" \
  | grep -v "__pycache__" \
  | grep -v "# 原\|原 \|兼容\|别名"

# 检查 demo/ 目录
grep -rn "semantic_memory\|SemanticMemory" demo/ --include="*.py" \
  | grep -v "__pycache__"

# 检查 evaluation/ 目录
grep -rn "semantic_memory\|SemanticMemory" evaluation/ --include="*.py" \
  | grep -v "__pycache__"
```

**预期结果**: 
- `src/` 目录无遗漏的旧名称
- `demo/` 和 `evaluation/` 目录无遗漏

#### 1.3 导入验证

```bash
python -c "
from api_specs.memory_types import ForesightItem, Foresight, MemoryType
from api_specs.memory_models import ForesightModel, ForesightRecordModel
print('✅ 类型导入成功')
print(f'   MemoryType.FORESIGHT = {MemoryType.FORESIGHT.value}')
print(f'   MemoryType.PERSONAL_FORESIGHT = {MemoryType.PERSONAL_FORESIGHT.value}')
"
```

**预期结果**: 
```
✅ 类型导入成功
   MemoryType.FORESIGHT = foresight
   MemoryType.PERSONAL_FORESIGHT = personal_foresight
```

---

### 第二阶段：单元测试

#### 2.1 核心单元测试

```bash
# Fetch 服务测试
pytest tests/test_fetch_mem_service.py -v

# Memory Controller 测试
pytest tests/test_memory_controller.py -v

# Memory Models 测试（如果存在）
pytest tests/test_memory_models.py -v 2>/dev/null || echo "test_memory_models.py 已删除（预期行为）"
```

**关键测试用例**:
- `test_find_by_user_id_personal_foresight` - 验证 PERSONAL_FORESIGHT 类型查询
- `test_fetch_personal_foresight` - 验证 personal_foresight API 参数

#### 2.2 迁移验证测试

```bash
pytest tests/test_foresight_integration.py -v
```

**验证点**:
- ✅ 旧的 MongoDB 集合 `semantic_memories` 不存在
- ✅ 新的 MongoDB 集合 `foresight_records` 存在
- ✅ API 拒绝 `data_source=semantic_memory` 参数
- ✅ `MemoryType.SEMANTIC_MEMORY` 枚举值不存在

#### 2.3 相关功能测试

```bash
# 离线记忆化测试
pytest tests/test_memorize_offline.py -v

# 记忆层重构测试
pytest tests/test_memory_layer_refactored.py -v

# Dispatcher 测试
pytest tests/test_dispatcher.py -v
```

---

### 第三阶段：集成测试

#### 3.1 服务启动

```bash
# 确保依赖服务运行
docker-compose up -d mongodb milvus elasticsearch redis

# 启动应用
python -m src.run
```

#### 3.2 Memorize API 测试

```bash
# 测试新参数名 enable_foresight_extraction
curl -X POST http://localhost:8001/api/v3/agentic/memorize \
  -H "Content-Type: application/json" \
  -d '{
    "new_raw_data_list": [
      {
        "role": "user",
        "content": "我明天要去北京出差",
        "timestamp": "2024-01-15T10:00:00Z"
      }
    ],
    "raw_data_type": "Conversation",
    "user_id_list": ["test_user_001"],
    "group_id": "test_group",
    "group_name": "测试群组",
    "enable_foresight_extraction": true,
    "enable_event_log_extraction": true
  }'
```

**预期结果**: 返回 `status: ok`，记忆提取成功

#### 3.3 Retrieve API 测试

**测试 1: 有效的 foresight 数据源**

```bash
curl -X POST http://localhost:8001/api/v3/agentic/retrieve_lightweight \
  -H "Content-Type: application/json" \
  -d '{
    "query": "用户的出差计划",
    "user_id": "test_user_001",
    "data_source": "foresight",
    "retrieval_mode": "rrf",
    "top_k": 5
  }'
```

**预期结果**: 返回前瞻记忆列表

**测试 2: 无效的 semantic_memory 数据源（应被拒绝）**

```bash
curl -X POST http://localhost:8001/api/v3/agentic/retrieve_lightweight \
  -H "Content-Type: application/json" \
  -d '{
    "query": "测试查询",
    "user_id": "test_user_001",
    "data_source": "semantic_memory"
  }'
```

**预期结果**: 返回错误，提示无效的 data_source

**测试 3: Episode 数据源（验证其他功能正常）**

```bash
curl -X POST http://localhost:8001/api/v3/agentic/retrieve_lightweight \
  -H "Content-Type: application/json" \
  -d '{
    "query": "出差",
    "user_id": "test_user_001",
    "data_source": "episode",
    "retrieval_mode": "rrf"
  }'
```

**预期结果**: 返回情景记忆列表

---

### 第四阶段：数据库验证

#### 4.1 MongoDB 集合检查

```bash
# 连接 MongoDB
mongosh

# 检查新集合
use memsys
db.foresight_records.countDocuments({})
db.foresights.countDocuments({})

# 确认旧集合不存在或为空
db.semantic_memories.countDocuments({})
db.semantic_memory_records.countDocuments({})
```

**预期结果**:
- `foresight_records` 和 `foresights` 集合存在
- `semantic_memories` 和 `semantic_memory_records` 不存在或为空

#### 4.2 Milvus 集合检查

```python
from pymilvus import connections, utility

connections.connect(host="localhost", port="19530")
collections = utility.list_collections()
print(f"Collections: {collections}")

# 验证
assert "foresight" in collections, "foresight 集合应存在"
assert "semantic_memory" not in collections, "semantic_memory 集合不应存在"
```

#### 4.3 Elasticsearch 索引检查

```bash
# 检查索引列表
curl http://localhost:9200/_cat/indices?v | grep -E "foresight|semantic"
```

**预期结果**: 存在 `foresight` 索引，不存在 `semantic-memory` 索引

---

### 第五阶段：回归测试

#### 5.1 完整测试套件

```bash
# 运行所有测试（排除稳定性和 Redis 测试）
pytest tests/ -v \
  --ignore=tests/test_stability* \
  --ignore=tests/test_redis* \
  --ignore=tests/test_rate_limiter* \
  -x  # 遇到第一个失败就停止
```

#### 5.2 关键路径测试

```bash
pytest tests/test_fetch_mem_service.py \
       tests/test_memory_controller.py \
       tests/test_foresight_integration.py \
       tests/test_memorize_offline.py \
       -v
```

---

## 三、快速验证脚本

### 一键验证命令

```bash
#!/bin/bash
# 文件: scripts/verify_foresight_migration.sh

set -e

echo "=== 1. 语法检查 ==="
python -m py_compile src/biz_layer/mem_memorize.py \
                     src/agentic_layer/fetch_mem_service.py \
                     src/api_specs/dtos/memory_command.py
echo "✅ 语法检查通过"

echo ""
echo "=== 2. 旧名称检查 ==="
count=$(grep -rn "semantic_memory\|SemanticMemory\|SEMANTIC_MEMORY" src/ --include="*.py" \
        | grep -v "__pycache__\|兼容\|别名\|# 原" | wc -l)
if [ "$count" -eq 0 ]; then
    echo "✅ 无遗漏的旧名称"
else
    echo "❌ 发现 $count 处可能的遗漏"
    exit 1
fi

echo ""
echo "=== 3. 参数名检查 ==="
if grep -q "enable_foresight_extraction" src/api_specs/dtos/memory_command.py; then
    echo "✅ enable_foresight_extraction 参数正确"
else
    echo "❌ enable_foresight_extraction 参数缺失"
    exit 1
fi

echo ""
echo "=== 4. 单元测试 ==="
pytest tests/test_fetch_mem_service.py tests/test_foresight_integration.py -v --tb=short

echo ""
echo "✅ 所有验证通过！"
```

### 使用方法

```bash
chmod +x scripts/verify_foresight_migration.sh
./scripts/verify_foresight_migration.sh
```

---

## 四、测试通过标准

| 检查项 | 通过标准 |
|-------|---------|
| 语法检查 | 所有 .py 文件编译无错误 |
| 旧名称检查 | 仅存在兼容性别名和文档说明 |
| 单元测试 | 100% 通过 |
| 集成测试 | API 响应正确，数据存储正确 |
| 数据库验证 | 新集合存在，旧集合不存在 |
| 回归测试 | 无新增失败用例 |

---

## 五、问题排查

### 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| ImportError: ForesightItem | 导入路径错误 | 使用 `from api_specs.memory_types import ForesightItem` |
| KeyError: SEMANTIC_MEMORY | 代码使用旧枚举值 | 替换为 `MemoryType.FORESIGHT` |
| 数据库集合不存在 | 未初始化新集合 | 重启服务或手动创建索引 |
| API 返回 500 | 导入或类型错误 | 检查日志，修复相关代码 |

### 日志检查

```bash
# 查看应用日志
tail -f logs/app.log | grep -E "foresight|semantic|error"

# 查看 Worker 日志
tail -f logs/worker.log | grep -E "foresight|FORESIGHT"
```

---

## 六、相关文档

- [重构详情文档](./semantic_to_foresight_refactor.md)
- [API 文档 (中文)](../api_docs/agentic_v3_api_zh.md)
- [API 文档 (英文)](../api_docs/agentic_v3_api.md)

