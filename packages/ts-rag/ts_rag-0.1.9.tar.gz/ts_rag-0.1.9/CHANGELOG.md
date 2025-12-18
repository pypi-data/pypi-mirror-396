# 更新日志

所有重要的项目更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 初始版本开发中

## [0.1.9] - 2024-12-15

## [0.1.7] - 2024-12-15

### 变更
- 优化配置加载逻辑：优先使用环境变量 `OPENAI_API_KEY`。
- 增强兼容性：`/root/bailiankey.txt` 读取失败时不再阻塞启动，避免在无权限环境下 Crash。
- 恢复 `.env` 文件加载支持。

## [0.1.6] - 2024-12-15

## [0.1.4] - 2024-12-10

### 新增
- 实现基于检索增强生成（RAG）的科研论文问答系统 ts-rag
- PDF 到 Markdown 的增量转换功能
- 倒排索引构建和搜索功能
- 异步并行的论文访问和信息提取
- 支持多种 LLM 提供商（通过 LiteLLM）
- MCP (Model Context Protocol) 服务器支持
- 拆分为两个独立工具：
  - `ts_rag_sync_papers`: PDF 转换和索引构建
  - `ts_rag_search_and_analyze`: 论文搜索和分析
- 完整的测试套件（TDD 开发）
- HTTP 和 STDIO 两种传输模式支持
- 进度报告和日志记录功能

### 技术栈
- Python 3.11+
- FastAPI（HTTP 模式）
- PyMuPDF（PDF 处理）
- NLTK（文本处理）
- LiteLLM（LLM 接口）

### 配置
- 环境变量配置支持
- 灵活的论文目录配置
- 可配置的并发数量和检索参数

[未发布]: https://github.com/yourusername/TashanRAG/compare/v0.1.9...HEAD
[0.1.9]: https://github.com/yourusername/TashanRAG/releases/tag/v0.1.9
[0.1.7]: https://github.com/yourusername/TashanRAG/releases/tag/v0.1.7
[0.1.6]: https://github.com/yourusername/TashanRAG/releases/tag/v0.1.6
[0.1.4]: https://github.com/yourusername/TashanRAG/releases/tag/v0.1.4
