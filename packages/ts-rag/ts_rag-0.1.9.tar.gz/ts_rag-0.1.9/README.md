# TashanRAG - 多论文 RAG 问答系统

## 项目简介

TashanRAG 是一个基于检索增强生成（RAG）的科研论文问答系统。系统能够从本地论文库（PDF）中自动提取内容、构建索引、检索相关论文片段，并生成带有精确引用的综合答案。

## 核心特性

- **PDF 自动处理**：自动扫描目录下的 PDF 文件，转换为 Markdown 并构建索引（增量同步）。
- **多论文检索**：基于 LLM 的智能论文搜索，从论文库中筛选相关论文。
- **并行信息提取**：异步并行处理多篇论文，提高效率。
- **引用溯源**：生成的答案包含 `[^ID]` 格式的引用，每个引用对应原始段落和论文路径。
- **MCP 支持**：内置 Model Context Protocol (MCP) Server，可作为工具集成到 Claude Desktop 或其他 Agent 系统中。

## 系统架构

流程概览：

```
PDF 文件库
    ↓ (paperindexg.py)
Markdown 镜像库 (.indexonly/papers)
    ↓ (indexer.py)
搜索索引 (.indexonly/index_data)
    ↓ (search.py)
检索阶段 (Search Phase)
    ↓ (visit.py)
并行提取 (Visit Phase)
    ↓ (answer.py)
答案生成 (Answer Phase) → 最终答案 + 引用
```

## 快速开始

### 1. 环境配置

```bash
# 安装依赖（推荐使用 uv）
# 方式1: 使用 uv（快速、现代的 Python 包管理器）
uv sync

# 方式2: 使用传统 pip
pip install -e .

# 方式3: 从 PyPI 安装（发布版本）
pip install ts-rag

# 配置 API Key（推荐使用 .env 文件）
# 方式1：使用 .env 文件
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key 和配置

# 方式2：使用环境变量
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export MODEL_NAME="openai/qwen-flash"
```

#### 环境变量说明

项目支持以下环境变量配置：

**必需配置：**
- `OPENAI_API_KEY` - API 密钥（必需）
- `OPENAI_BASE_URL` - API 基础 URL（必需）

**可选配置：**
- `MODEL_NAME` - 使用的模型名称（默认：`openai/qwen-flash`）
- `TASHANRAG_PAPER_ROOT` 或 `DEFAULT_PAPER_ROOT` - 论文根目录路径（默认：`01-文献`）
- `MAX_CONCURRENT_VISITS` - 最大并发处理数（默认：`5`）
- `TOP_K_DEFAULT` - 默认检索论文数量（默认：`3`）
- `DEBUG` - 调试模式开关（默认：`false`）
- `VERBOSE` - 详细输出开关（默认：`false`）
- `ENABLE_CACHE` - 缓存开关（默认：`true`）

**完整配置示例（.env 文件）：**
```bash
# API 配置
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 模型配置
MODEL_NAME=openai/qwen-flash

# 论文目录配置
TASHANRAG_PAPER_ROOT=/path/to/your/papers

# 性能配置
MAX_CONCURRENT_VISITS=5
TOP_K_DEFAULT=3

# 调试配置
DEBUG=false
VERBOSE=true
ENABLE_CACHE=true
```

### 2. 准备论文库

将你的 PDF 论文放入任意文件夹，例如：

```
G:\papers\
├── paper1.pdf
├── subfolder\
│   └── paper2.pdf
└── ...
```

### 3. 运行问答系统

#### 方式一：使用 Python 脚本直接运行

你可以直接运行 `src/ts_rag/answer.py`，它封装了完整流程（注意：需要先修改代码底部的 `papers_dir` 为你的论文目录）：

```bash
uv run python src/ts_rag/answer.py
```

在 `src/ts_rag/answer.py` 的 `if __name__ == "__main__":` 块中：

```python
if __name__ == "__main__":
    test_question = "自动化科研有什么进展？"
    # 指定你的论文根目录
    papers_dir = r"G:\path\to\your\papers"

    # 这一步会自动触发 PDF -> MD 转换和索引构建
    # 注意：首次运行可能需要一些时间进行 PDF 转换
    result = generate_answer(
        test_question,
        max_concurrent_visits=5,
        papers_dir=papers_dir
    )
    # ...
```

#### 方式二：作为 MCP Server 运行（推荐）

TashanRAG 提供了符合 Model Context Protocol 标准的服务器，支持多种运行模式。

**1. 使用 uvx 运行（推荐）**

从 PyPI 安装并运行：
```bash
# STDIO 模式（默认）
uvx ts-rag

# HTTP 模式
uvx --env FASTMCP_TRANSPORT=streamable-http ts-rag

# 带自定义配置
uvx --env OPENAI_API_KEY="your-key" \
    --env OPENAI_BASE_URL="your-url" \
    --env TASHANRAG_PAPER_ROOT="/path/to/papers" \
    ts-rag
```

**2. 从源码运行**

**本地模式（stdio，默认）**：
```bash
# 标准模式，通过标准输入输出通信，适合 Claude Desktop 等本地集成
uv run python src/ts_rag/tashanrag_server.py
```

**HTTP 模式（支持远程访问）**：
```bash
# 使用默认配置（0.0.0.0:8080）
FASTMCP_TRANSPORT=streamable-http uv run python src/ts_rag/tashanrag_server.py

# 自定义配置
FASTMCP_TRANSPORT=streamable-http FASTMCP_HOST=127.0.0.1 FASTMCP_PORT=9000 uv run python src/ts_rag/tashanrag_server.py
```

**环境变量配置**：
```bash
# 主机配置
export FASTMCP_HOST=0.0.0.0      # 监听所有接口
export FASTMCP_PORT=8080         # 端口号
export FASTMCP_TRANSPORT=streamable-http  # 传输协议

# API 路径
export FASTMCP_STREAMABLE_HTTP_PATH=/mcp  # 默认路径
```

**配置 Claude Desktop**：

在 Claude Desktop 的配置文件中添加：

**使用 uvx（推荐）**：
```json
{
  "mcpServers": {
    "TashanRAG": {
      "command": "uvx",
      "args": ["ts-rag"],
      "env": {
        "OPENAI_API_KEY": "your-api-key",
        "OPENAI_BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1"
      }
    }
  }
}
```

**从源码运行**：
```json
{
  "mcpServers": {
    "TashanRAG": {
      "command": "uv",
      "args": ["run", "python", "/absolute/path/to/TashanRAG/src/ts_rag/tashanrag_server.py"],
      "env": {
        "OPENAI_API_KEY": "your-api-key",
        "OPENAI_BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "MODEL_NAME": "openai/qwen-flash",
        "TASHANRAG_PAPER_ROOT": "/path/to/your/papers",
        "MAX_CONCURRENT_VISITS": "5",
        "TOP_K_DEFAULT": "3",
        "DEBUG": "false",
        "VERBOSE": "true",
        "ENABLE_CACHE": "true"
      }
    }
  }
}
```


**HTTP 模式客户端连接**：

使用 FastMCP 客户端：
```python
from fastmcp import Client

async def main():
    # 连接到 HTTP 服务器
    async with Client("http://localhost:8080/mcp") as client:
        # 列出工具
        tools = await client.list_tools()

        # 调用工具
        result = await client.call_tool(
            "tashanrag_ask_paper_db",
            {
                "question": "你的问题",
                "top_k": 3
            }
        )
```

**测试示例**：
项目提供了多个客户端示例，位于 `examples/` 目录：
- `demo_mcp_client.py` - FastMCP 客户端示例
- `demo_mcp_http.py` - HTTP 客户端示例
- `demo_mcp_sse.py` - Server-Sent Events 示例

```bash
# 测试 HTTP 客户端
uv run python examples/demo_mcp_client.py
```

### 4. 项目结构

```
TashanRAG/
├── src/ts_rag/           # 核心源代码
│   ├── answer.py        # 主入口，协调 RAG 流程
│   ├── search.py        # 论文检索模块
│   ├── visit.py         # 信息提取模块
│   ├── indexer.py       # 索引构建模块
│   ├── paperindexg.py   # PDF 转换模块
│   ├── tashanrag_server.py  # MCP 服务器
│   ├── config.py        # 配置管理
│   └── llm_config.py    # LLM 模型配置
├── examples/            # 使用示例
│   ├── demo_*.py        # 各种演示脚本
│   └── client.py        # MCP 客户端示例
├── tests/              # 测试文件
├── archive/            # 历史版本和测试代码
└── 01-文献/            # 示例论文存储
```

## 详细配置

### 模型配置

在 `answer.py` 中可以修改使用的模型：

```python
MODEL_NAME = "openai/qwen-flash"  # 支持 openai 格式的模型
```

如果使用非 OpenAI 官方模型（如阿里云 Qwen），请确保正确配置 `BASE_URL`。

### 索引机制

系统会自动维护索引。当你指向一个新的 `papers_dir` 时：
1. `paperindexg` 会扫描 PDF 并转换为 Markdown (存储在 `.indexonly/papers`)。
2. `indexer` 会基于这些 Markdown 构建倒排索引 (存储在 `.indexonly/index_data`)。
3. 后续运行时，只会处理新增或修改的文件。

## 输出字段说明

JSON 返回值包含：
- `status`: "success" 或 "error"
- `final_answer`: 生成的回答文本
- `citations_map`: 引用详情字典
- `metrics`: 性能指标（耗时、Token消耗等）
- `thinking`: 模型的思考过程（如果模型支持并输出了 `<thinking>` 标签）

## 常见问题

**Q: 首次运行为什么很慢？**
A: 首次运行需要将所有 PDF 转换为 Markdown 并构建索引，这是 CPU 密集型任务。后续运行将只处理增量文件，速度会显著加快。

**Q: 如何重新构建索引？**
A: 删除论文目录下的 `.indexonly` 文件夹即可触发全量重建。

**Q: HTTP 模式和 stdio 模式有什么区别？**
A: stdio 模式通过标准输入输出通信，适合本地集成（如 Claude Desktop）；HTTP 模式通过网络协议通信，支持远程访问和多客户端连接。

**Q: 如何在不同端口运行多个实例？**
A: 设置不同的 `FASTMCP_PORT` 环境变量即可。

## 版本发布

TashanRAG 遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

### 最新版本

- 查看 [PyPI](https://pypi.org/project/ts-rag/) 获取最新稳定版
- 查看 [GitHub Releases](https://github.com/your-username/TashanRAG/releases) 获取所有版本

### 更新日志

详细的版本更新记录请查看 [CHANGELOG.md](CHANGELOG.md)。

### 发布说明

版本发布已自动化，推送版本标签（如 `v0.1.9`）即可自动创建 GitHub Release 并发布到 PyPI。
