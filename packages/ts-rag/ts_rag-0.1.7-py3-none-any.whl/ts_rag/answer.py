import asyncio
import os
import re
import threading
import time
from typing import Any

import psutil
import tashan_core as cg

# 简化导入：所有模块都在当前目录下
# 导入统一配置
from config import config
from llm_config import register_qwen_models
from pydantic import BaseModel, Field
from search import search_papers
from visit import extract_info


class MemoryMonitor:
    """
    轻量级内存监控器：后台线程采样当前进程的 RSS，统计平均值和峰值。
    """

    def __init__(self, interval: float = 0.5):
        self.interval = interval
        self._samples: list[float] = []
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._process = psutil.Process(os.getpid())

    def _sample_loop(self):
        while not self._stop_event.is_set():
            rss_mb = self._process.memory_info().rss / (1024 * 1024)
            self._samples.append(rss_mb)
            time.sleep(self.interval)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()

    def stop(self) -> dict[str, float]:
        if self._thread:
            self._stop_event.set()
            self._thread.join()
        if not self._samples:
            return {"avg": 0.0, "peak": 0.0}
        avg = sum(self._samples) / len(self._samples)
        peak = max(self._samples)
        return {"avg": avg, "peak": peak}


# Pydantic Models for Response Structure
class AnswerMetrics(BaseModel):
    total_time: float = 0.0
    search_time: float = 0.0
    visit_time: float = 0.0
    answer_time: float = 0.0
    papers_processed: int = 0
    snippets_count: int = 0
    answer_tokens_input: int = 0
    answer_tokens_output: int = 0
    answer_tokens_total: int = 0
    memory_avg_mb: float = 0.0
    memory_peak_mb: float = 0.0


class AnswerResponse(BaseModel):
    status: str = Field(..., description="success or error")
    user_question: str
    final_answer: str
    thinking: str | None = None  # 新增 thinking 字段
    citations_map: dict[str, Any] = Field(default_factory=dict)
    metrics: AnswerMetrics = Field(default_factory=AnswerMetrics)
    error_message: str | None = None


# 初始化环境配置（确保 LiteLLM 使用正确的配置）
def setup_litellm_environment():
    """配置 LiteLLM 环境变量"""
    os.environ["OPENAI_API_KEY"] = config.openai_api_key
    os.environ["OPENAI_BASE_URL"] = config.openai_base_url

    # 注册模型配置
    register_qwen_models()


# 初始化环境配置
setup_litellm_environment()


def load_answer_system_prompt() -> str:
    """
    从模板文件加载 answer 阶段的 system prompt。
    """
    from tashan_core.internal.utils import _get_template

    return str(_get_template("answer_generation_v3", template_extension="txt"))


async def process_single_paper(question: str, paper_info: dict, semaphore: asyncio.Semaphore):
    """
    异步处理单篇论文的提取任务（带并发限制）。
    """
    file_path = paper_info["file_path"]
    paper_id = paper_info.get("paper_id", "Unknown")

    # 使用 semaphore 限制并发
    async with semaphore:
        print(f"  -> Visiting: {paper_id}...")

        # extract_info 目前是同步函数，使用 run_in_executor 模拟异步并发
        loop = asyncio.get_event_loop()
        try:
            # 使用默认 executor (ThreadPoolExecutor)
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


async def run_pipeline(
    question: str,
    top_k: int = None,
    max_concurrent_visits: int = None,
    papers_dir: str | None = None,
) -> dict[str, Any]:
    """运行完整的 RAG 管道"""
    if top_k is None:
        top_k = config.top_k_default
    if max_concurrent_visits is None:
        max_concurrent_visits = config.max_concurrent_visits
    """
    RAG Pipeline 主入口 (Async)
    """
    pipeline_start = time.time()
    search_start = pipeline_start
    visit_start = pipeline_start
    answer_start = pipeline_start

    memory_monitor = MemoryMonitor()
    memory_monitor.start()
    memory_stats: dict[str, float] | None = None

    # 初始化默认 metrics
    current_metrics = AnswerMetrics()

    try:
        # 0. Determine paths
        from pathlib import Path

        # 所有路径都固定为 Path.cwd() / ".tashan" / "deepsearch"
        # papers_dir 参数已废弃，现在使用固定路径
        papers_dir_path = Path.cwd() / ".tashan" / "deepsearch" / "papers"
        # index_dir_path 固定为 ${cwd}/.tashan/deepsearch/index_data/
        index_dir_path = Path.cwd() / ".tashan" / "deepsearch" / "index_data"

        # 0.1 Always Update Index
        # [修改] 不再检查是否存在，始终调用 indexer，依赖 indexer 内部的增量检测逻辑
        print(f"[Auto-Index] Syncing index in {index_dir_path}...")
        try:
            from indexer import build_index

            loop = asyncio.get_event_loop()
            # build_index 现在基于固定的 hidden_dir (${cwd}/.tashan/deepsearch) 工作
            await loop.run_in_executor(None, build_index)
            print("[Auto-Index] Index sync complete.")
        except Exception as e:
            memory_stats = memory_monitor.stop()
            return AnswerResponse(
                status="error",
                user_question=question,
                final_answer="系统错误：索引更新失败。",
                error_message=f"Failed to update index: {e}",
                metrics=current_metrics,
            ).model_dump()

        # 1. Search Phase
        print(f"\n[Phase 1] Searching papers for: {question}...")
        search_start = time.time()

        search_result = search_papers(
            question,
            top_k=top_k,
            papers_dir=str(papers_dir_path),
            index_dir=str(index_dir_path),
        )

        if search_result["status"] == "error":
            memory_stats = memory_monitor.stop()
            return AnswerResponse(
                status="error",
                user_question=question,
                final_answer="系统错误：论文搜索失败。",
                error_message=f"Search failed: {search_result['message']}",
                metrics=current_metrics,
            ).model_dump()

        found_papers = search_result.get("found_papers", [])
        search_duration = time.time() - search_start
        print(f"  -> Found {len(found_papers)} relevant papers in {search_duration:.2f}s")

        current_metrics.search_time = round(time.time() - search_start, 2)

        # 2. Visit Phase (Parallel with concurrency limit)
        visit_info = (
            f"\n[Phase 2] Visiting {len(found_papers)} papers in parallel (max {max_concurrent_visits} concurrent)..."
        )
        print(visit_info)
        visit_start = time.time()

        if found_papers:
            semaphore = asyncio.Semaphore(max_concurrent_visits)
            tasks = [process_single_paper(question, p, semaphore) for p in found_papers]
            visit_results = await asyncio.gather(*tasks)

            valid_results = [
                r for r in visit_results if r is not None and r.get("result", {}).get("status") == "success"
            ]
        else:
            valid_results = []

        visit_duration = time.time() - visit_start
        print(
            f"  -> Finished visiting. Valid results: {len(valid_results)}/{len(found_papers)} "
            f"in {visit_duration:.2f}s"
        )

        current_metrics.visit_time = round(time.time() - visit_start, 2)
        current_metrics.papers_processed = len(valid_results)

        # 3. Aggregation Phase
        print("\n[Phase 3] Aggregating evidence...")
        answer_start = time.time()

        citation_map = {}  # Global Map
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

        current_metrics.snippets_count = len(citation_map)

        # 4. Answer Phase
        print("\n[Phase 4] Generating answer...")

        final_answer = ""
        thinking_content = ""
        answer_token_input = 0
        answer_token_output = 0

        if not snippets_text_block:
            print("  -> No snippets found. Returning 'No info' response.")
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

            try:
                raw_response = await answer_llm.chat_async(prompt=user_prompt)

                # 分离 thinking 和 final_answer
                thinking_match = re.search(r"<thinking>(.*?)</thinking>", raw_response, re.DOTALL)
                if thinking_match:
                    thinking_content = thinking_match.group(1).strip()
                    # 移除 thinking 标签及内容，保留剩下的作为回答
                    final_answer = re.sub(r"<thinking>.*?</thinking>", "", raw_response, flags=re.DOTALL).strip()
                else:
                    final_answer = raw_response

                # 收集 token 统计
                try:
                    answer_usage_list = answer_llm.get_usage()
                    unique_usage = {}
                    for u in answer_usage_list:
                        key = f"{u.model}_{u.role}"
                        unique_usage[key] = u
                    for u in unique_usage.values():
                        answer_token_input += u.usage.input
                        answer_token_output += u.usage.output
                except Exception:
                    pass

            except Exception as e:
                memory_stats = memory_monitor.stop()
                return AnswerResponse(
                    status="error",
                    user_question=question,
                    final_answer="系统错误：生成回答失败。",
                    error_message=f"LLM generation failed: {e}",
                    metrics=current_metrics,
                ).model_dump()

        pipeline_end = time.time()
        memory_stats = memory_monitor.stop()

        current_metrics.total_time = round(pipeline_end - pipeline_start, 2)
        current_metrics.answer_time = round(pipeline_end - answer_start, 2)
        current_metrics.answer_tokens_input = answer_token_input
        current_metrics.answer_tokens_output = answer_token_output
        current_metrics.answer_tokens_total = answer_token_input + answer_token_output

        if memory_stats:
            current_metrics.memory_avg_mb = round(memory_stats["avg"], 2)
            current_metrics.memory_peak_mb = round(memory_stats["peak"], 2)

        # === [NEW] 核心修改：过滤掉未在 final_answer 中引用的 citation ===
        # 1. 扫描答案中出现的所有 [^数字]
        used_citation_ids = set(re.findall(r"\[\^(\d+)\]", final_answer))

        # 2. 构造新的过滤后的 map
        filtered_citation_map = {}
        for cid, content in citation_map.items():
            if cid in used_citation_ids:
                filtered_citation_map[cid] = content
        # ==============================================================

        return AnswerResponse(
            status="success",
            user_question=question,
            final_answer=final_answer,
            thinking=thinking_content,
            citations_map=filtered_citation_map,  # 使用过滤后的 map
            metrics=current_metrics,
        ).model_dump()

    except Exception as e:
        memory_stats = memory_monitor.stop()
        return AnswerResponse(
            status="error",
            user_question=question,
            final_answer="系统发生了未预期的错误。",
            error_message=f"Unexpected pipeline error: {str(e)}",
            metrics=current_metrics,
        ).model_dump()

    finally:
        if memory_stats is None:
            memory_monitor.stop()


def generate_answer(
    question: str,
    top_k: int = 3,
    max_concurrent_visits: int = 5,
    papers_dir: str | None = None,
):
    """
    同步入口封装
    """
    return asyncio.run(
        run_pipeline(
            question,
            top_k=top_k,
            max_concurrent_visits=max_concurrent_visits,
            papers_dir=papers_dir,
        )
    )
