import json
import os
import sys
from pathlib import Path

import tashan_core as cg

# 导入统一配置
from config import config
from llm_config import DEFAULT_MAX_PARAGRAPHS_PER_CALL_SEARCH, register_qwen_models


def load_index_data(index_dir: Path | str | None = None):
    """
    读取构建好的索引数据：摘要池和ID映射

    Args:
        index_dir: 索引目录路径，如果为 None 则使用项目根目录的 index_data/

    Returns:
        tuple: (summary_pool_text, id_map)
    """
    if index_dir is None:
        base_dir = Path(__file__).parent
        index_dir = base_dir / "index_data"
    else:
        index_dir = Path(index_dir)

    pool_path = index_dir / "summary_pool.txt"
    map_path = index_dir / "id_map.json"

    if not pool_path.exists() or not map_path.exists():
        raise FileNotFoundError(f"Index data not found in {index_dir}. Please run indexer.py first.")

    with open(pool_path, encoding="utf-8") as f:
        summary_pool_text = f.read()

    with open(map_path, encoding="utf-8") as f:
        id_map = json.load(f)

    return summary_pool_text, id_map


def search_papers(
    question: str,
    top_k: int = 3,
    papers_dir: Path | str | None = None,
    index_dir: Path | str | None = None,
):
    """
    核心搜索函数：使用 tashan_core 从摘要池中筛选最相关的论文。

    Args:
        question (str): 用户问题
        top_k (int): 最大返回篇数
        papers_dir: 论文库目录路径，如果为 None 则使用项目根目录的 papers/
        index_dir: 索引目录路径。如果为 None：
                   1. 若提供了 papers_dir，则默认为 papers_dir/index_data
                   2. 否则默认为项目根目录的 index_data/

    Returns:
        dict: 包含问题、筛选结果（带路径和理由）。格式始终统一，不返回 {"error": ...}。
              失败时 found_papers 为空列表。
    """
    # 设置 LiteLLM 环境变量
    os.environ["OPENAI_API_KEY"] = config.openai_api_key
    os.environ["OPENAI_BASE_URL"] = config.openai_base_url

    # 注册模型
    register_qwen_models()

    # 0. 路径推导
    base_dir = Path(__file__).parent
    if index_dir is None:
        if papers_dir:
            index_dir = Path(papers_dir) / "index_data"
        else:
            index_dir = base_dir / "index_data"

    # 默认返回结构
    response = {
        "status": "error",  # 默认为 error，成功后改为 success
        "question": question,
        "found_papers": [],
        "total_found": 0,
        "message": "",
    }

    # 1. 加载数据
    try:
        summary_pool_text, id_map = load_index_data(index_dir=index_dir)
    except Exception as e:
        response["message"] = f"Failed to load index data: {str(e)}"
        return response

    print(f"Searching for: {question}...")

    # 2. 使用 tashan_core 进行提取
    try:
        # 创建 Document
        doc = cg.Document(raw_text=summary_pool_text)

        # 创建 PaperSelectionConcept
        selection_concept = cg.PaperSelectionConcept(
            name="Relevant Papers",
            description=f"""
            Papers that discuss topics related to: {question}

            [Instructions]:
            1. Analyze the title, abstract, AND selected figure captions (if available) of each paper.
            2. Select papers that might contain RELEVANT information. It is recommended to
               prioritize approximately {top_k} papers, but you should include ALL papers that
               are potentially relevant, even if this exceeds {top_k}.
            3. EXCLUDE papers that are clearly irrelevant (e.g., wrong scientific field,
               completely different topic).
            4. It is better to include a paper if you are unsure, but do not include papers
               you are certain are irrelevant.
            5. If a paper mentions key concepts from the question (e.g., "speed", "width",
               "geometry", "migration") in its abstract or captions, include it.
            6. Provide a brief reason for each selection based on specific keywords or findings mentioned.
            """,
            singular_occurrence=False,
        )

        doc.concepts = [selection_concept]

        # 初始化 DocumentLLM
        llm = cg.DocumentLLM(
            model=config.model_name,
            api_key=config.openai_api_key,
            api_base=config.openai_base_url,
        )

        # 执行提取（带分批机制，防止摘要池过大时超出上下文限制）
        result_doc = llm.extract_all(
            doc,
            max_paragraphs_to_analyze_per_call=DEFAULT_MAX_PARAGRAPHS_PER_CALL_SEARCH,
        )

        # 3. 提取结果
        extracted_concept = result_doc.get_concept_by_name("Relevant Papers")

        if not extracted_concept or not extracted_concept.extracted_items:
            response["status"] = "success"
            response["message"] = "No papers selected by LLM."
            return response

        # 4. 结果映射回文件路径
        selected_files = []
        seen_ids = set()

        for item in extracted_concept.extracted_items:
            # item.value is a dict: {paper_id, title, reason}
            data = item.value
            pid = data.get("paper_id")
            reason = data.get("reason", "")

            # 后处理：双重检查，如果 reason 里包含 "irrelevant" 或 "not relevant"，则跳过
            if "not relevant" in reason.lower() or "irrelevant" in reason.lower():
                continue

            if pid and pid in id_map and pid not in seen_ids:
                paper_info = id_map[pid]
                paper_path = Path(paper_info["md_path"])

                # 如果路径是相对路径（不以 / 开头），且不是绝对路径
                if not paper_path.is_absolute():
                    # 如果 md_path 已经包含了 papers_dir 前缀，直接使用
                    if str(paper_path).startswith(str(papers_dir) if papers_dir else ""):
                        paper_path = Path.cwd() / paper_path
                    # 否则，将 papers_dir 作为基准路径
                    elif papers_dir:
                        paper_path = Path(papers_dir) / paper_path
                    else:
                        paper_path = Path.cwd() / paper_path
                else:
                    # 已经是绝对路径，直接使用
                    pass

                selected_files.append(
                    {
                        "paper_id": pid,
                        "file_path": str(paper_path.resolve()),  # 转换为绝对路径
                        "reason": reason,
                    }
                )
                seen_ids.add(pid)

        response["status"] = "success"
        response["found_papers"] = selected_files
        response["total_found"] = len(selected_files)
        response["message"] = "Search completed successfully."

    except Exception as e:
        response["message"] = f"LLM extraction failed: {str(e)}"
        return response

    # 5. 返回最终结构
    return response


if __name__ == "__main__":
    # Simple test
    import sys

    if len(sys.argv) > 1:
        question = sys.argv[1]
    else:
        question = "细胞迁移"

    result = search_papers(question)
    print(f"Status: {result['status']}")
    print(f"Found {result['total_found']} papers")
    for paper in result["found_papers"][:3]:
        print(f"  - {paper['paper_id']}: {paper['reason'][:50]}...")
