import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 添加 src/ts_rag 到路径以导入配置
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "ts_rag"))

import litellm
from llm_config import DEFAULT_MAX_PARAGRAPHS_PER_CALL_SEARCH, register_qwen_models
from tashan_core import Document

# 注册 qwen-flash 模型信息
litellm.model_cost["openai/qwen-flash"] = {
    "max_input_tokens": 1_000_000,
    "max_output_tokens": 32768,
    "input_cost_per_token": 0,
    "output_cost_per_token": 0,
    "litellm_provider": "openai",
    "mode": "chat",
}

# 注册模型配置
register_qwen_models()


def count_tokens_for_text(model: str, text: str) -> int:
    """估算文本的 token 数"""
    try:
        messages = [{"role": "user", "content": text}]
        count = litellm.token_counter(model=model, messages=messages)
        return count
    except Exception as e:
        print(f"Token counting failed: {e}")
        # Fallback: 粗略估算（英文约 4 字符 = 1 token，中文约 1.5 字符 = 1 token）
        return len(text) // 3


def analyze_search_phase():
    """分析 Search 阶段的 token 使用"""
    print("=" * 60)
    print("Search Phase Token Analysis")
    print("=" * 60)

    # 读取 summary_pool.txt
    index_dir = Path(__file__).parent / "index_data"
    pool_path = index_dir / "summary_pool.txt"

    if not pool_path.exists():
        print(f"Error: {pool_path} not found")
        return

    with open(pool_path, encoding="utf-8") as f:
        summary_pool_text = f.read()

    # 估算 token 数
    model = "openai/qwen-flash"
    token_count = count_tokens_for_text(model, summary_pool_text)

    print(f"Summary Pool Text Length: {len(summary_pool_text)} chars")
    print(f"Estimated Token Count: {token_count}")
    print("Max Input Tokens (qwen-flash): 1,000,000")
    print(f"Usage: {token_count / 1_000_000 * 100:.2f}%")
    # 计算如果使用默认分批的情况

    # 估算摘要池的段落数（粗略：按 "===" 分隔符计算）
    num_papers = summary_pool_text.count("=== PAPER START")
    # 假设每篇论文在 summary_pool 中占约 10-20 个段落（TITLE + ABSTRACT + 分隔符等）
    estimated_paragraphs = num_papers * 15
    batches_needed = (
        (estimated_paragraphs + DEFAULT_MAX_PARAGRAPHS_PER_CALL_SEARCH - 1) // DEFAULT_MAX_PARAGRAPHS_PER_CALL_SEARCH
        if estimated_paragraphs > 0
        else 1
    )

    print("\n结论: 当前 Search 阶段已启用分批机制")
    print(f"      默认批次大小: {DEFAULT_MAX_PARAGRAPHS_PER_CALL_SEARCH} 段落/批次")
    print(f"      当前摘要池 ({num_papers} 篇论文) 将分为 {batches_needed} 个批次")
    print(f"      每批次约 {token_count // batches_needed if batches_needed > 0 else token_count} tokens（平均）")


def analyze_visit_phase():
    """分析 Visit 阶段的 token 使用（单篇论文）"""
    print("\n" + "=" * 60)
    print("Visit Phase Token Analysis (Single Paper)")
    print("=" * 60)

    # 读取一篇论文
    papers_dir = Path(__file__).parent / "papers_converted"
    paper_files = list(papers_dir.glob("*.md"))

    if not paper_files:
        print(f"Error: No papers found in {papers_dir}")
        return

    # 分析第一篇论文
    paper_path = paper_files[0]
    print(f"Analyzing: {paper_path.name}")

    with open(paper_path, encoding="utf-8") as f:
        paper_text = f.read()

    # 创建 Document 对象，看看它会被分成多少段落
    doc = Document(raw_text=paper_text)
    num_paragraphs = len(doc.paragraphs)

    # 估算 token 数
    model = "openai/qwen-flash"
    token_count = count_tokens_for_text(model, paper_text)

    print(f"Paper Text Length: {len(paper_text)} chars")
    print(f"Number of Paragraphs: {num_paragraphs}")
    print(f"Estimated Token Count: {token_count}")
    print("Max Input Tokens (qwen-flash): 1,000,000")
    print(f"Usage: {token_count / 1_000_000 * 100:.2f}%")
    # 计算如果使用默认分批（3000 段落/批次）的情况

    batches_needed = (
        num_paragraphs + DEFAULT_MAX_PARAGRAPHS_PER_CALL_SEARCH - 1
    ) // DEFAULT_MAX_PARAGRAPHS_PER_CALL_SEARCH
    tokens_per_batch = token_count // batches_needed if batches_needed > 0 else token_count

    print("\n结论: 当前 Visit 阶段已启用分批机制")
    print(f"      默认批次大小: {DEFAULT_MAX_PARAGRAPHS_PER_CALL_SEARCH} 段落/批次")
    print(f"      这篇论文 ({num_paragraphs} 段落) 将分为 {batches_needed} 个批次")
    print(f"      每批次约 {tokens_per_batch} tokens（平均）")
    print(
        f"      对于博士论文（假设 5000 段落），将分为 "
        f"{(5000 + DEFAULT_MAX_PARAGRAPHS_PER_CALL_SEARCH - 1) // DEFAULT_MAX_PARAGRAPHS_PER_CALL_SEARCH} 个批次"
    )


if __name__ == "__main__":
    analyze_search_phase()
    analyze_visit_phase()
