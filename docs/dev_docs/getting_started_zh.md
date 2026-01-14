# 智能记忆系统 - 快速开始指南

本指南将帮助您快速设置和启动智能记忆系统项目。

## 📋 目录

- [环境要求](#环境要求)
- [安装依赖](#安装依赖)
- [环境配置](#环境配置)
- [启动服务](#启动服务)
- [运行测试脚本](#运行测试脚本)
- [常见问题](#常见问题)

## 🔧 环境要求

### 系统要求
- **操作系统**: macOS, Linux, Windows
- **Python版本**: 3.10+
- **包管理器**: uv (推荐)

### 必需的外部服务
- **MongoDB**: 用于存储记忆数据
- **Redis**: 用于缓存和任务队列
- **Elasticsearch**: 用于全文搜索
- **Milvus**: 用于向量检索

## 📦 安装依赖

### 1. 安装 uv

uv 是一个快速的 Python 包管理器，推荐使用。

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 验证安装
uv --version
```

### 2. 克隆项目

```bash
# 克隆项目到本地
git clone <项目地址>
cd memsys_opensource

# 查看项目结构
ls -la
```

### 3. 安装项目依赖

```bash
# 使用 uv 同步依赖（推荐）
# uv 会自动创建虚拟环境并安装所有依赖
uv sync

# 验证安装
uv run python --version
```

## ⚙️ 环境配置

### 1. 创建环境配置文件

```bash
# 复制环境变量模板
cp env.template .env

# 使用编辑器打开 .env 文件
vim .env  # 或使用你喜欢的编辑器
```

### 2. 配置必要的环境变量

编辑 `.env` 文件，填入实际的配置值：

#### LLM 配置
```bash
# LLM 配置
LLM_PROVIDER=openai
LLM_MODEL=google/gemini-2.5-flash
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=sk-or-v1-你的API密钥
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=16384
```

#### DeepInfra 配置（用于 Embedding 和 Rerank）
```bash
# DeepInfra Embedding / 嵌入向量
VECTORIZE_API_KEY=你的DeepInfra密钥
VECTORIZE_BASE_URL=https://api.deepinfra.com/v1/openai
VECTORIZE_MODEL=Qwen/Qwen3-Embedding-4B
VECTORIZE_TIMEOUT=30
VECTORIZE_MAX_RETRIES=3
VECTORIZE_BATCH_SIZE=10
VECTORIZE_MAX_CONCURRENT=5
VECTORIZE_ENCODING_FORMAT=float
VECTORIZE_DIMENSIONS=1024

# DeepInfra Rerank / 重排序
RERANK_BASE_URL=https://api.deepinfra.com/v1/inference
RERANK_MODEL=Qwen/Qwen3-Reranker-4B
RERANK_TIMEOUT=30
RERANK_MAX_RETRIES=3
RERANK_BATCH_SIZE=10
RERANK_MAX_CONCURRENT=5
```

#### 数据库配置
```bash
# Redis配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=8
REDIS_SSL=false

# MongoDB配置
MONGODB_HOST=your-mongodb-host
MONGODB_PORT=27017
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_DATABASE=your_database_name
MONGODB_URI_PARAMS="socketTimeoutMS=15000&authSource=admin"

# Elasticsearch配置
ES_HOSTS=https://your-elasticsearch-host:9200
ES_USERNAME=elastic
ES_PASSWORD=your_password
ES_VERIFY_CERTS=true
SELF_ES_INDEX_NS=your-namespace

# Milvus向量数据库配置
MILVUS_HOST=your-milvus-host
MILVUS_PORT=19530
SELF_MILVUS_COLLECTION_NS=your_namespace
```

#### 环境与日志配置
```bash
LOG_LEVEL=DEBUG
ENV=dev
PYTHONASYNCIODEBUG=1
```

### 3. API 密钥获取

#### OpenRouter API 密钥
1. 访问 [OpenRouter](https://openrouter.ai/)
2. 注册账号并创建 API 密钥
3. 将密钥填入 `.env` 文件的 `LLM_API_KEY`

#### DeepInfra API 密钥
1. 访问 [DeepInfra](https://deepinfra.com/)
2. 注册账号并创建 API 密钥
3. 将密钥填入 `.env` 文件的 `VECTORIZE_API_KEY`

## 🚀 启动服务

### 1. 启动 Web 服务（REST API）

启动主应用服务，提供 REST API 接口：

```bash
# 基本启动（使用默认端口 1995）
uv run python src/run.py

# 指定日志级别启动
LOG_LEVEL=DEBUG uv run python src/run.py

# 指定端口启动
uv run python src/run.py --port 8080

# 指定主机和端口
uv run python src/run.py --host 0.0.0.0 --port 8080

# 使用自定义环境文件
uv run python src/run.py --env-file .env.production
```

#### 启动参数说明
- `--host`: 服务器监听地址（默认: 0.0.0.0）
- `--port`: 服务器端口（默认: 1995）
- `--env-file`: 环境变量文件路径（默认: .env）
- `--mock`: 启用 Mock 模式（用于测试和开发）

#### 启动成功输出示例
```
🚀 启动 Memory System v1.0.0
📝 记忆系统主应用
🌟 启动参数:
  📡 Host: 0.0.0.0
  🔌 Port: 1995
  📄 Env File: .env
  🎭 Mock Mode: False
  🔧 LongJob Mode: Disabled
🚀 正在初始化依赖注入容器...
✅ 依赖注入设置完成
🔄 正在注册异步任务...
✅ 异步任务注册完成
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:1995 (Press CTRL+C to quit)
```

### 2. 验证服务启动

服务启动后，可以通过以下方式验证：

```bash
# 访问 API 文档
curl http://localhost:1995/docs

# 或在浏览器中打开
open http://localhost:1995/docs
```

### 3. 启动长任务消费者（可选）

如果需要启动异步任务处理器（如 Kafka 消费者）：

```bash
# 启动 Kafka 消费者
uv run python src/run.py --longjob kafka_consumer

# 关停任务（在另一个终端）
pkill -9 -f 'src/run.py'
```

## 🧪 运行测试脚本

### Bootstrap 脚本介绍

`bootstrap.py` 是一个通用的脚本运行器，它会自动处理：
- Python 路径设置
- 环境变量加载
- 依赖注入容器初始化
- 应用上下文管理

使用 Bootstrap 可以让你**无认知负担**地运行任何测试脚本。

### 基本用法

```bash
# 基本语法
uv run python src/bootstrap.py [脚本路径] [脚本参数...]

# 运行测试脚本
uv run python src/bootstrap.py tests/test_convert_rest.py

# 运行带参数的脚本
uv run python src/bootstrap.py tests/my_test.py --verbose

# 使用 Mock 模式运行
uv run python src/bootstrap.py tests/my_test.py --mock

# 使用自定义环境文件
uv run python src/bootstrap.py tests/my_test.py --env-file .env.test
```

### 实际示例

#### 1. 运行评估脚本
```bash
# 运行 LoCoMo 评估第一阶段
uv run python src/bootstrap.py evaluation/locomo_evaluation/stage1_memcells_extraction.py

# 运行其他评估阶段
uv run python src/bootstrap.py evaluation/locomo_evaluation/stage2_index_building.py
uv run python src/bootstrap.py evaluation/locomo_evaluation/stage3_memory_retrivel.py
```

#### 2. 运行 Demo 脚本
```bash
# 运行记忆提取演示
uv run python src/bootstrap.py demo/extract_memory.py

# 运行记忆对话演示
uv run python src/bootstrap.py demo/chat_with_memory.py
```

#### 3. 运行单元测试
```bash
# 运行测试模板（学习如何使用 DI 和 MongoDB）
uv run python src/bootstrap.py tests/bootstrap_test_template.py

# 运行自定义测试
uv run python src/bootstrap.py unit_test/my_unit_test.py
```

### Bootstrap 命令行选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `--env-file` | 指定环境变量文件 | `--env-file .env.test` |
| `--mock` | 启用 Mock 模式 | `--mock` |

### Bootstrap 工作原理

1. **自动设置环境**：加载 `.env` 文件，设置 Python 路径
2. **初始化依赖注入**：启动 DI 容器，注册所有组件
3. **启动应用上下文**：初始化数据库连接、缓存等
4. **执行目标脚本**：在完整的应用上下文中运行你的脚本
5. **清理资源**：脚本执行完毕后自动清理

## 🐛 开发调试

### 1. Mock 模式

在开发和测试时，可以启用 Mock 模式来模拟外部依赖：

```bash
# 方式1: 使用命令行参数
uv run python src/run.py --mock

# 方式2: 设置环境变量
export MOCK_MODE=true
uv run python src/run.py

# 方式3: 在 .env 文件中配置
# MOCK_MODE=true
```

### 2. 调试日志

```bash
# 设置详细日志级别
export LOG_LEVEL=DEBUG
uv run python src/run.py

# 或直接在命令行指定
LOG_LEVEL=DEBUG uv run python src/run.py
```

### 3. 开发环境配置

创建开发专用的环境配置：

```bash
# 创建开发环境配置
cp .env .env.dev

# 编辑开发配置
vim .env.dev
```

在 `.env.dev` 中设置开发相关配置：
```bash
# 开发模式
ENV=dev
DEBUG=true
LOG_LEVEL=DEBUG
MOCK_MODE=true

# 本地服务
MONGODB_HOST=localhost
REDIS_HOST=localhost
ES_HOSTS=http://localhost:9200
MILVUS_HOST=localhost
```

使用开发配置启动：
```bash
uv run python src/run.py --env-file .env.dev
```

## ❓ 常见问题

### 1. uv 相关问题

#### 问题：uv sync 失败
```bash
# 解决方案：清理缓存后重试
uv cache clean
uv sync

# 或使用 pip 作为备选
pip install -e .
```

#### 问题：找不到 uv 命令
```bash
# 确保 uv 已安装
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载 shell 配置
source ~/.bashrc  # 或 source ~/.zshrc
```

### 2. 环境配置问题

#### 问题：找不到 .env 文件
```bash
# 确保 .env 文件存在
ls -la .env

# 如果不存在，复制模板
cp env.template .env
```

#### 问题：环境变量未生效
```bash
# 检查 .env 文件格式
cat .env | grep -v "^#" | grep -v "^$"

# 确保没有多余的空格和引号
```

### 3. 数据库连接问题

#### 问题：MongoDB 连接失败
```bash
# 检查 MongoDB 是否运行
# macOS
brew services list | grep mongodb

# Linux
systemctl status mongod

# 检查连接配置
echo $MONGODB_HOST
echo $MONGODB_PORT
```

#### 问题：Redis 连接失败
```bash
# 检查 Redis 是否运行
redis-cli ping

# 如果未运行，启动 Redis
# macOS
brew services start redis

# Linux
sudo systemctl start redis
```

### 4. 启动失败问题

#### 问题：端口被占用
```bash
# 检查端口占用
lsof -i :1995

# 使用其他端口启动
uv run python src/run.py --port 8080
```

#### 问题：模块导入错误
```bash
# 确保在项目根目录执行
pwd

# 重新安装依赖
uv sync --reinstall
```

### 5. Bootstrap 运行问题

#### 问题：脚本路径找不到
```bash
# 确保使用正确的相对路径
ls -la evaluation/locomo_evaluation/stage1_memcells_extraction.py

# 或使用绝对路径
uv run python src/bootstrap.py /path/to/your/script.py
```

#### 问题：脚本执行出错
```bash
# 查看详细错误信息
LOG_LEVEL=DEBUG uv run python src/bootstrap.py your_script.py

# 使用 Mock 模式测试
uv run python src/bootstrap.py your_script.py --mock
```

## 🎯 下一步

现在你已经成功设置并启动了智能记忆系统！接下来可以：

1. **阅读开发指南**: 查看 [development_guide.md](development_guide.md) 了解项目架构和最佳实践
2. **探索 Bootstrap**: 查看 [bootstrap_usage.md](bootstrap_usage.md) 深入了解脚本运行器
3. **查看 API 文档**: 访问 http://localhost:1995/docs 了解可用的 API 接口
4. **运行示例代码**: 尝试运行 `demo/` 目录下的示例脚本

## 📞 获取帮助

如果遇到问题，可以通过以下方式获取帮助：

1. **查看日志**: 使用 `LOG_LEVEL=DEBUG` 查看详细日志
2. **检查配置**: 确认 `.env` 文件配置正确
3. **查看文档**: 阅读相关技术文档
4. **提交 Issue**: 在项目仓库中报告问题

---

**祝你使用愉快！** 🎉
