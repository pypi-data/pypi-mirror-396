# OrcaKit SDK

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**OrcaKit SDK** 是基于 [LangGraph](https://github.com/langchain-ai/langgraph) 构建的 AI Agent 开发框架，提供了一套完整的工具和适配器，用于快速构建、部署和运行生产级 AI Agent 应用。

## ✨ 特性

- 🚀 **快速开发**：基于 LangGraph 的声明式 Agent 开发，简化复杂工作流
- 🔌 **多通道支持**：内置 LangGraph、OpenAI 兼容、A2A 协议等多种通道
- 🛠️ **MCP 集成**：完整支持 Model Context Protocol，轻松接入外部工具和数据源
- 💾 **持久化支持**：内置 SQLite 和 PostgreSQL checkpoint 存储
- 📊 **可观测性**：集成 Langfuse，提供完整的 Agent 运行追踪和分析
- 🔄 **流式输出**：支持流式响应，提升用户体验
- 🎯 **类型安全**：完整的类型注解，提供更好的 IDE 支持

## 📦 安装

### 使用 pip

```bash
pip install orcakit-sdk
```

### 使用 uv（推荐）

```bash
uv pip install orcakit-sdk
```

### 开发模式安装

```bash
git clone https://github.com/yourusername/orcakit-sdk.git
cd orcakit-sdk
pip install -e ".[dev]"
```

## 🚀 快速开始

### 1. 创建一个简单的 Agent

```python
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from orcakit_sdk.runner.agent_executor import LangGraphAgentExecutor
from orcakit_sdk.runner.runner import SimpleRunner

# 定义状态
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# 创建 LLM 节点
def chatbot(state: State) -> State:
    llm = ChatOpenAI(model="gpt-4")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 构建图
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

# 创建执行器和运行器
executor = LangGraphAgentExecutor(graph=graph)
runner = SimpleRunner(executor)

# 启动服务器
runner.start(port=8080)
```

### 2. 调用 Agent

```bash
# 同步调用
curl -X POST http://localhost:8080/langgraph/call \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, how are you?"}'

# 流式调用
curl -X POST http://localhost:8080/langgraph/stream \
  -H "Content-Type: application/json" \
  -d '{"content": "Tell me a story"}' \
  --no-buffer
```

## 📚 核心组件

### Agent Executor

`LangGraphAgentExecutor` 是 Agent 的执行引擎，负责管理 LangGraph 的执行、状态持久化和观测。

```python
from orcakit_sdk.runner.agent_executor import LangGraphAgentExecutor

executor = LangGraphAgentExecutor(
    graph=graph,
    checkpointer="sqlite",  # 或 "postgres"
    enable_langfuse=True,   # 启用 Langfuse 追踪
)
```

### Runner

提供多种运行模式：

#### SimpleRunner - 单一通道服务器

```python
from orcakit_sdk.runner.runner import SimpleRunner
from orcakit_sdk.runner.channels.langgraph_channel import LangGraphChannel

runner = SimpleRunner(
    executor=executor,
    channel=LangGraphChannel(),
    port=8080
)
runner.start()
```

#### 多通道服务器

```python
from fastapi import FastAPI
from orcakit_sdk.runner.channels.langgraph_channel import LangGraphChannel
from orcakit_sdk.runner.channels.openai_channel import OpenAIChannel
from orcakit_sdk.runner.channels.a2a_channel import A2AChannel

app = FastAPI()

# LangGraph 通道
langgraph_channel = LangGraphChannel()
langgraph_channel.create_router(app, executor, url_prefix="/langgraph")

# OpenAI 兼容通道
openai_channel = OpenAIChannel()
openai_channel.create_router(app, executor, url_prefix="/v1")

# A2A 协议通道
a2a_channel = A2AChannel()
a2a_channel.create_router(app, executor, url_prefix="/a2a")

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8080)
```

### MCP 适配器

集成 Model Context Protocol，轻松接入外部工具：

```python
from orcakit_sdk.mcp_adapter import MCPManager

# 初始化 MCP 管理器
mcp_manager = MCPManager()

# 添加 MCP 服务器
await mcp_manager.add_servers({
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/data"],
        "env": {}
    }
})

# 获取工具
tools = await mcp_manager.get_tools()

# 在 LangGraph 中使用
from langgraph.prebuilt import ToolNode
tool_node = ToolNode(tools)
```

## 🔧 通道说明

### LangGraph Channel

原生 LangGraph 协议，支持完整的状态管理和检查点功能。

**端点：**
- `POST /langgraph/call` - 同步调用
- `POST /langgraph/stream` - 流式调用
- `POST /langgraph/invoke` - 带配置的调用

### OpenAI Channel

完全兼容 OpenAI Chat Completions API，可直接替换 OpenAI SDK 使用。

**端点：**
- `POST /v1/chat/completions` - 聊天完成（支持流式）
- `GET /v1/models` - 模型列表

### A2A Channel

支持 Agent-to-Agent (A2A) 协议，用于 Agent 之间的互操作。

**端点：**
- 完整的 A2A 协议端点（任务创建、查询、流式订阅等）

### 企业微信 Channel

支持企业微信机器人集成。

```python
from orcakit_sdk.runner.channels.wework_channel import WeWorkChannel

wework_channel = WeWorkChannel(
    corp_id="your_corp_id",
    agent_id="your_agent_id",
    secret="your_secret"
)
```

## 🔍 可观测性

### Langfuse 集成

```python
import os

# 设置环境变量
os.environ["LANGFUSE_PUBLIC_KEY"] = "your-public-key"
os.environ["LANGFUSE_SECRET_KEY"] = "your-secret-key"
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"

# 启用 Langfuse
executor = LangGraphAgentExecutor(
    graph=graph,
    enable_langfuse=True
)
```

## 💾 状态持久化

### SQLite (默认)

```python
executor = LangGraphAgentExecutor(
    graph=graph,
    checkpointer="sqlite"
)
```

### PostgreSQL

```python
import os

os.environ["POSTGRES_URI"] = "postgresql://user:pass@localhost:5432/dbname"

executor = LangGraphAgentExecutor(
    graph=graph,
    checkpointer="postgres"
)
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行集成测试
pytest tests/integration_tests/

# 运行单元测试
pytest tests/unit_tests/

# 带覆盖率
pytest tests/ --cov=orcakit_sdk
```

### 手动测试

```bash
# 启动测试服务器
python tests/manual_test_agent.py

# 选择运行模式
# 1: SimpleRunner (LangGraph channel)
# 2: 多通道服务器
# 3: OpenAI 兼容服务器
```

## 📖 示例

更多示例请查看 [tests/manual_test_agent.py](tests/manual_test_agent.py)

## 🛠️ 开发

### 代码规范

项目使用 `ruff` 进行代码检查和格式化：

```bash
# 检查代码
ruff check .

# 自动修复
ruff check --fix .

# 格式化代码
ruff format .
```

### 类型检查

```bash
mypy src/
```

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🤝 贡献

欢迎贡献！请查看贡献指南了解更多信息。

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系方式

- 作者：Jubao Liang
- 邮箱：jubaoliang@gmail.com

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - 强大的 Agent 编排框架
- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用开发框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Web 框架
- [Langfuse](https://langfuse.com/) - LLM 应用可观测平台

---

**OrcaKit SDK** - 让 AI Agent 开发更简单 🐋
