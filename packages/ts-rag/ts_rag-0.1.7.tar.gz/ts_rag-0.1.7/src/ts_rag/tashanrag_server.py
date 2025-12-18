import asyncio
import os
import shutil
import sys
from pathlib import Path
from typing import Any

# 导入统一配置
try:
    from .config import config
except ImportError:
    from config import config
from fastmcp import Context, FastMCP

# 导入项目版本
try:
    from . import __version__
except ImportError:
    # 如果相对导入失败，尝试直接导入
    try:
        import ts_rag

        __version__ = ts_rag.__version__
    except ImportError:
        __version__ = "unknown"

# 确保能找到同级模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    try:
        from .indexer import build_index  # 导入索引构建函数
    except ImportError:
        from indexer import build_index
    try:
        from .paperindexg import run_pdf_sync_pipeline  # 导入同步函数
    except ImportError:
        from paperindexg import run_pdf_sync_pipeline
    try:
        from .search import search_papers  # 导入搜索函数
    except ImportError:
        from search import search_papers
except ImportError:
    print(
        "Fatal Error: Could not import required modules (paperindexg.py, indexer.py, search.py).",
        file=sys.stderr,
    )
    sys.exit(1)

# 初始化 MCP Server
mcp = FastMCP("TashanRAG", version=__version__)


# 定义实际的函数实现（不被装饰器包装）
async def _tashanrag_sync_papers_impl(force_rebuild: bool = False, ctx: Context = None) -> dict[str, Any]:
    """
    Sync papers: Convert PDFs to Markdown and build search index.

    This tool performs two steps:
    1. Scans the paper directory for new PDFs and converts them to Markdown
    2. Updates or rebuilds the search index

    Args:
        force_rebuild: Whether to rebuild the index from scratch (default: False)
        ctx: MCP context for logging and progress reporting
    """
    # 记录请求开始
    # 输入目录固定为 Path.cwd() / "01-文献"
    if ctx:
        await ctx.info(f"Starting paper sync from: {Path.cwd() / '01-文献'}")
        await ctx.report_progress(0, 100, "Starting paper sync...")

    try:
        # Step 1: PDF to Markdown sync
        # run_pdf_sync_pipeline 现在使用固定输入路径 Path.cwd() / "01-文献"
        if ctx:
            await ctx.info("Converting PDFs to Markdown...")
            await ctx.report_progress(20, 100, "Converting PDFs to Markdown...")

        sync_result = run_pdf_sync_pipeline()

        if ctx:
            await ctx.info(
                f"PDF sync complete: {sync_result.get('new_files', 0)} new, "
                f"{sync_result.get('updated_files', 0)} updated"
            )

        # Step 2: Build or rebuild index
        # 索引目录固定为 Path.cwd() / ".tashan" / "deepsearch" / "index_data"
        index_dir = Path.cwd() / ".tashan" / "deepsearch" / "index_data"

        if force_rebuild and index_dir.exists():
            if ctx:
                await ctx.info("Rebuilding index from scratch...")
                await ctx.report_progress(50, 100, "Rebuilding index...")
            shutil.rmtree(index_dir)
            os.makedirs(index_dir, exist_ok=True)

        if ctx:
            await ctx.report_progress(60, 100, "Building search index...")

        # Use run_in_executor to run the synchronous build_index function
        # build_index 现在基于固定的 hidden_dir (${cwd}/.tashan/deepsearch) 工作
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, build_index)

        if ctx:
            await ctx.report_progress(100, 100, "Sync complete!")
            await ctx.info("Paper database synchronized successfully")

        return {
            "status": "success",
            "message": f"Successfully synchronized paper database. "
            f"Processed {sync_result.get('new_files', 0)} new files, "
            f"{sync_result.get('updated_files', 0)} updated files.",
            "sync_result": sync_result,
            "index_path": str(index_dir),
        }

    except Exception as e:
        error_msg = f"Failed to sync papers: {str(e)}"
        if ctx:
            await ctx.error(error_msg)

        return {"status": "error", "error_message": error_msg}


# 定义实际的函数实现（不被装饰器包装）
async def _tashanrag_search_and_analyze_impl(
    question: str, top_k: int = 3, max_concurrent_visits: int = 5, ctx: Context = None
) -> dict[str, Any]:
    """
    Search and analyze papers without rebuilding the index.

    This tool performs two steps:
    1. Searches the existing index for relevant papers
    2. Visits papers in parallel and generates an answer with citations

    Args:
        question: The scientific question to answer
        top_k: Number of papers to retrieve (default: 3)
        max_concurrent_visits: Max concurrency for processing papers (default: 5)
        ctx: MCP context for logging and progress reporting
    """
    # 记录请求开始
    if ctx:
        await ctx.info(f"Processing question: {question}")
        await ctx.report_progress(0, 100, "Starting paper analysis...")

    try:
        # Check if index exists
        # 路径都固定为 Path.cwd() / ".tashan" / "deepsearch"
        papers_dir = Path.cwd() / ".tashan" / "deepsearch" / "papers"
        index_dir = Path.cwd() / ".tashan" / "deepsearch" / "index_data"

        if not index_dir.exists():
            error_msg = "Index not found. Please run tashanrag_sync_papers first."
            if ctx:
                await ctx.error(error_msg)

            return {"status": "error", "error_message": error_msg}

        # Step 1: Search papers
        if ctx:
            await ctx.info("Searching relevant papers...")
            await ctx.report_progress(20, 100, "Searching relevant papers...")

        search_result = search_papers(question, top_k=top_k, papers_dir=str(papers_dir), index_dir=str(index_dir))

        if search_result["status"] == "error":
            error_msg = f"Search failed: {search_result.get('message', 'Unknown error')}"
            if ctx:
                await ctx.error(error_msg)

            return {"status": "error", "error_message": error_msg}

        found_papers = search_result.get("found_papers", [])
        if ctx:
            await ctx.info(f"Found {len(found_papers)} relevant papers")
            await ctx.report_progress(40, 100, f"Found {len(found_papers)} papers")

        # Step 2: Visit papers and generate answer
        if ctx:
            await ctx.info("Analyzing papers and generating answer...")
            await ctx.report_progress(50, 100, "Analyzing papers...")

        # Use a separate function that only does search and answer without index building
        result = await _search_and_answer_only(
            question, found_papers, max_concurrent_visits, papers_dir=str(papers_dir), ctx=ctx
        )

        # Report completion
        if ctx:
            await ctx.report_progress(100, 100, "Analysis complete!")
            if result.get("status") == "success":
                await ctx.info("Successfully generated answer with citations")
            else:
                await ctx.warning(f"Completed with errors: {result.get('error_message', 'Unknown error')}")

        return result

    except Exception as e:
        error_msg = f"Failed to analyze papers: {str(e)}"
        if ctx:
            await ctx.error(error_msg)

        return {"status": "error", "error_message": error_msg}


# 注册为 MCP 工具
@mcp.tool()
async def tashanrag_sync_papers(force_rebuild: bool = False, ctx: Context = None) -> dict[str, Any]:
    """
    Sync papers: Convert PDFs to Markdown and build search index.

    This tool performs two steps:
    1. Scans the paper directory for new PDFs and converts them to Markdown
    2. Updates or rebuilds the search index

    Args:
        force_rebuild: Whether to rebuild the index from scratch (default: False)
        ctx: MCP context for logging and progress reporting
    """
    return await _tashanrag_sync_papers_impl(force_rebuild, ctx)


@mcp.tool()
async def tashanrag_search_and_analyze(
    question: str, top_k: int = 3, max_concurrent_visits: int = 5, ctx: Context = None
) -> dict[str, Any]:
    """
    Search and analyze papers without rebuilding the index.

    This tool performs two steps:
    1. Searches the existing index for relevant papers
    2. Visits papers in parallel and generates an answer with citations

    Args:
        question: The scientific question to answer
        top_k: Number of papers to retrieve (default: 3)
        max_concurrent_visits: Max concurrency for processing papers (default: 5)
        ctx: MCP context for logging and progress reporting
    """
    # Call the implementation function
    return await _tashanrag_search_and_analyze_impl(question, top_k, max_concurrent_visits, ctx)


async def _search_and_answer_only(
    question: str, found_papers: list[dict], max_concurrent_visits: int, papers_dir: str, ctx: Context = None
) -> dict[str, Any]:
    """
    Internal helper function to perform visit and answer phases only.
    Assumes search has already been done.
    """
    import asyncio

    # Visit Phase (Parallel with concurrency limit)
    if ctx:
        await ctx.info(f"Visiting {len(found_papers)} papers in parallel (max {max_concurrent_visits} concurrent)...")

    if found_papers:
        semaphore = asyncio.Semaphore(max_concurrent_visits)
        tasks = [_process_single_paper(question, p, semaphore) for p in found_papers]
        visit_results = await asyncio.gather(*tasks)

        valid_results = [r for r in visit_results if r is not None and r.get("result", {}).get("status") == "success"]
    else:
        valid_results = []

    if ctx:
        await ctx.info(f"Finished visiting. Valid results: {len(valid_results)}/{len(found_papers)}")

    # Generate answer using the visit results
    if ctx:
        await ctx.info("Generating final answer...")

    # Here we would reuse the answer generation logic from answer.py
    # For now, we'll call the existing run_pipeline with a modified approach
    # that skips the index building step
    try:
        # Create a temporary pipeline that only does search and answer
        # This is a simplified approach - in production you might want to refactor
        # the run_pipeline function to accept pre-searched results
        import re

        import tashan_core as cg
        from answer import load_answer_system_prompt

        # Aggregation Phase
        citation_map = {}
        snippets_text_block = ""
        global_id_counter = 1

        for res in valid_results:
            paper_id = res["paper_id"]
            file_path = res["file_path"]
            extract_data = res["result"].get("source_document", {}).get("extracted_knowledge", [])

            local_snippets = set()
            for knowledge_item in extract_data:
                items = knowledge_item.get("items", [])
                for item in items:
                    evidence = item.get("evidence_snippets", [])
                    if evidence:
                        for snip in evidence:
                            local_snippets.add(snip)
                    else:
                        content = item.get("content")
                        if isinstance(content, list):
                            for c in content:
                                local_snippets.add(c)
                        elif isinstance(content, str):
                            local_snippets.add(content)

            if local_snippets:
                snippets_text_block += f"--- Paper: {paper_id} ---\n"
                for snip in local_snippets:
                    cid = str(global_id_counter)
                    cleaned_snip = snip.strip().replace("\n", " ")
                    snippets_text_block += f"片段 [^{cid}]: {cleaned_snip}\n\n"
                    citation_map[cid] = {
                        "id": cid,
                        "paper_id": paper_id,
                        "file_path": file_path,
                        "text": cleaned_snip,
                    }
                    global_id_counter += 1

        # Answer Phase
        final_answer = ""
        thinking_content = ""

        if not snippets_text_block:
            final_answer = (
                "未找到相关资料。基于您提供的问题，在现有的论文库中未检索到相关信息，"
                "或者从相关论文中未能提取到具体支持该问题的片段。"
            )
        else:
            user_prompt = f"""
            [科研问题]:
            {question}

            [参考片段库]:
            {snippets_text_block}

            请根据以上片段回答问题。注意区分不同来源的观点。
            """

            system_prompt = load_answer_system_prompt()
            answer_llm = cg.DocumentLLM(
                model=config.model_name,
                api_key=config.openai_api_key,
                api_base=config.openai_base_url,
                system_message=system_prompt,
                temperature=0.2,
            )

            raw_response = await answer_llm.chat_async(prompt=user_prompt)

            # 分离 thinking 和 final_answer
            thinking_match = re.search(r"<thinking>(.*?)</thinking>", raw_response, re.DOTALL)
            if thinking_match:
                thinking_content = thinking_match.group(1).strip()
                # 移除 thinking 标签及内容，保留剩下的作为回答
                final_answer = re.sub(r"<thinking>.*?</thinking>", "", raw_response, flags=re.DOTALL).strip()
            else:
                final_answer = raw_response

        # 过滤未使用的引用
        used_citation_ids = set(re.findall(r"\[\^(\d+)\]", final_answer))
        filtered_citation_map = {}
        for cid, content in citation_map.items():
            if cid in used_citation_ids:
                filtered_citation_map[cid] = content

        return {
            "status": "success",
            "user_question": question,
            "final_answer": final_answer,
            "thinking": thinking_content,
            "citations_map": filtered_citation_map,
            "found_papers": found_papers,
        }

    except Exception as e:
        error_msg = f"Failed to generate answer: {str(e)}"
        if ctx:
            await ctx.error(error_msg)

        return {"status": "error", "error_message": error_msg, "user_question": question}


async def _process_single_paper(question: str, paper_info: dict, semaphore: asyncio.Semaphore):
    """
    异步处理单篇论文的提取任务（带并发限制）。
    """
    import asyncio

    file_path = paper_info["file_path"]
    paper_id = paper_info.get("paper_id", "Unknown")

    # 使用 semaphore 限制并发
    async with semaphore:
        if semaphore._value == 0:  # 只在有限制时打印
            print(f"  -> Visiting: {paper_id}...")

        # extract_info 目前是同步函数，使用 run_in_executor 模拟异步并发
        loop = asyncio.get_event_loop()
        try:
            # 使用默认 executor (ThreadPoolExecutor)
            from visit import extract_info

            result = await loop.run_in_executor(None, extract_info, question, file_path)
            return {"paper_id": paper_id, "file_path": file_path, "result": result}
        except Exception as e:
            print(f"  [Error] Failed to visit {paper_id}: {e}")
            return {
                "paper_id": paper_id,
                "file_path": file_path,
                "result": {
                    "status": "error",
                    "message": str(e),
                    "source_document": {"extracted_knowledge": []},
                },
            }


def main():
    """主入口函数，支持命令行调用"""
    import os

    # 检查是否启用 HTTP 模式
    transport = os.environ.get("FASTMCP_TRANSPORT", "stdio")

    if transport == "http" or transport == "streamable-http":
        # HTTP 模式配置
        host = os.environ.get("FASTMCP_HOST", "0.0.0.0")
        port = int(os.environ.get("FASTMCP_PORT", "8080"))
        path = os.environ.get("FASTMCP_STREAMABLE_HTTP_PATH", "/mcp")

        print(f"启动 TashanRAG MCP 服务器 v{__version__} (HTTP 模式)")
        print(f"地址: http://{host}:{port}{path}")
        print("使用 Ctrl+C 停止服务器")

        # 使用环境变量来配置 HTTP 模式
        mcp.run(transport="streamable-http")
    else:
        # 默认 STDIO 模式
        if os.environ.get("DEBUG", "false").lower() == "true":
            print(f"TashanRAG MCP 服务器 v{__version__} (STDIO 模式)", file=sys.stderr)
        mcp.run()


if __name__ == "__main__":
    main()
