# TashanRAG 示例和测试脚本

本目录包含了用于测试和演示 TashanRAG 系统功能的脚本。

## 文件说明

### MCP 客户端示例
- **client.py** - FastMCP 客户端示例，展示如何调用 TashanRAG MCP 服务
- **test_mcp_client.py** - 使用 FastMCP 客户端测试 HTTP 模式
- **test_mcp_http.py** - 测试 MCP HTTP API（需要正确配置 Accept 头）
- **test_mcp_sse.py** - 测试 MCP Server-Sent Events API

### 功能演示脚本
- **demo_answer_pipeline.py** - 演示完整的 RAG 管道（搜索→访问→回答）
- **demo_search.py** - 演示论文搜索功能
- **demo_visit.py** - 演示单篇论文的信息提取功能
- **demo_findpdf.py** - 演示 PDF 文件查找功能
- **demo_pdf_tools.py** - 综合演示 PDF 处理工具链

## 使用方法

### 1. 运行 STDIO 模式示例
```bash
# 启动服务器（STDIO 模式，默认）
uv run python src/ts_rag/tashanrag_server.py

# 在另一个终端运行客户端
uv run python examples/client.py
```

### 2. 运行 HTTP 模式示例
```bash
# 启动服务器（HTTP 模式）
FASTMCP_TRANSPORT=streamable-http FASTMCP_HOST=0.0.0.0 FASTMCP_PORT=8080 \
  uv run python src/ts_rag/tashanrag_server.py

# 在另一个终端测试 HTTP API
uv run python examples/test_mcp_client.py
```

### 3. 演示各个功能模块
```bash
# 演示 PDF 查找
uv run python examples/demo_findpdf.py

# 演示 PDF 转换和索引构建
uv run python examples/demo_pdf_tools.py

# 演示论文搜索
uv run python examples/demo_search.py

# 演示信息提取
uv run python examples/demo_visit.py

# 演示完整 RAG 流程
uv run python examples/demo_answer_pipeline.py
```

### 4. 环境变量配置
某些演示脚本支持通过环境变量进行配置：
```bash
# 设置论文目录
export TASHANRAG_PAPER_ROOT="01-文献"

# 设置测试问题
export TEST_QUESTION="细胞迁移的机制是什么？"

# 设置搜索目录（用于 demo_findpdf.py）
export SEARCH_DIR="01-文献"
```

## 注意事项

1. 这些是**示例和测试脚本**，不是核心库代码的一部分
2. 脚本主要用于：
   - 验证 MCP 服务器功能
   - 演示如何集成 TashanRAG
   - 调试和性能测试
3. 实际使用时，请参考这些示例编写您自己的客户端代码

## 依赖要求

示例脚本需要额外的依赖：
```bash
# 安装 FastMCP（用于 client.py 和 test_mcp_client.py）
pip install fastmcp

# 安装 aiohttp（用于 HTTP API 测试）
pip install aiohttp
```
