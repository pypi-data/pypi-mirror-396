# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

TashanRAG 是一个基于检索增强生成（RAG）的科研论文问答系统，能够从本地 PDF 论文库中自动提取内容、构建索引、检索相关论文片段，并生成带有精确引用的综合答案。

## 核心架构

系统采用模块化设计，主要包含以下模块：

- **`paperindexg.py`**: PDF 到 Markdown 转换和增量同步
- **`indexer.py`**: 搜索索引构建（倒排索引）
- **`search.py`**: 基于 LLM 的论文检索
- **`visit.py`**: 并行信息提取
- **`answer.py`**: 主入口，协调搜索、访问和回答流程
- **`tashanrag_server.py`**: MCP 服务器实现

数据流向：
```
PDF 文件库 → .indexonly/papers (Markdown) → .indexonly/index_data (搜索索引)
```

## 常用命令

### 安装依赖
```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 运行方式

1. **直接运行 Python 脚本**
```bash
python src/ts_rag/answer.py
# 需要修改 answer.py 底部的 papers_dir 为你的论文目录
```

2. **作为 MCP Server 运行（推荐）**
```bash
python src/ts_rag/tashanrag_server.py
```

3. **测试 MCP Client**
```bash
python src/ts_rag/client.py
```

### 环境变量配置

```bash
# API 配置
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"

# 或在代码中修改（answer.py 第81-82行）
API_KEY = "your-key"
BASE_URL = "your-url"
```

## 开发指南

### 代码结构

- `/src/ts_rag/`: 核心源代码目录
  - `/tashan_core/`: 核心文档处理和 LLM 交互框架
  - `paperindexg.py`, `answer.py`, `search.py`, `visit.py`, `indexer.py`: RAG 流程核心模块
- `/archive/`: 历史版本和测试代码
- `/01-文献/`: 示例论文存储目录

### 重要文件说明

- `requirements.txt`: 包含所有 Python 依赖
- `llm_config.py`: LLM 模型配置
- `pdf2md.py`: PDF 到 Markdown 转换器
- `findpdf.py`: PDF 文件扫描工具

### 关键功能实现

1. **增量索引机制**：系统会在论文目录下创建 `.indexonly` 文件夹存储转换后的 Markdown 和索引数据，只处理新增或修改的文件。

2. **并行处理**：`visit.py` 使用异步并行处理多篇论文，提高信息提取效率。

3. **引用追踪**：生成的答案包含 `[^ID]` 格式的引用，每个引用对应原始段落和论文路径。

### 测试

测试文件位于 `/archive/tests/` 目录，包含：
- `test_visit.py`: 访问模块测试
- `test_concurrent_visits.py`: 并发访问测试
- `test_litellm.py`: LLM 调用测试

## 注意事项

1. 首次运行需要时间进行 PDF 转换和索引构建
2. 删除 `.indexonly` 文件夹可触发全量重建索引
3. 确保 Python 版本 >= 3.11
4. 建议使用 SSD 硬盘以提高 PDF 处理速度
