import json
import os
import sys
from pathlib import Path

import tashan_core as cg

# 导入统一配置
from config import config
from litellm import completion
from llm_config import DEFAULT_MAX_PARAGRAPHS_PER_CALL_VISIT, register_qwen_models


def setup_environment():
    """配置必要的环境变量"""
    # 设置 LiteLLM 环境变量
    os.environ["OPENAI_API_KEY"] = config.openai_api_key
    os.environ["OPENAI_BASE_URL"] = config.openai_base_url

    # 注册 qwen-flash 模型信息（消除 warning）
    register_qwen_models()


def classify_question(question_text, model_name):
    """
    使用 LLM 判断问题类型：是需要在回答中列出多个条目（LIST），还是单一的回答（SINGLE）。
    """
    prompt = f"""
    Analyze the following question and determine if the expected answer should be a LIST of
    items/steps/entities, or a SINGLE text block/summary.

    Question: "{question_text}"

    Return strictly valid JSON format: {{"type": "LIST"}} or {{"type": "SINGLE"}}.
    Do not output anything else.
    """

    try:
        response = completion(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        content = response.choices[0].message.content
        if not content:
            print("[Warning] Classification returned empty content, defaulting to SINGLE.")
            return "SINGLE"

        # 清理可能存在的 Markdown 代码块标记
        content = content.strip().replace("```json", "").replace("```", "")
        result = json.loads(content)
        return result.get("type", "SINGLE")
    except Exception as e:
        print(f"[Warning] Classification failed, defaulting to SINGLE. Error: {e}")
        return "SINGLE"


def extract_info(question: str, file_path: str) -> dict:
    """
    核心功能函数：输入问题和文件路径，输出结构化的提取结果。

    Args:
        question (str): 用户的问题
        file_path (str): 本地文件的路径

    Returns:
        dict: 符合要求的 JSON 数据结构
    """
    setup_environment()

    # 默认返回结构
    response = {
        "status": "error",
        "message": "",
        "question": question,
        "source_document": {
            "file_path": (os.path.abspath(file_path) if os.path.exists(file_path) else file_path),
            "extracted_knowledge": [],
        },
    }

    # 1. 检查和读取文件
    if not os.path.exists(file_path):
        response["message"] = f"File not found: {file_path}"
        return response

    try:
        with open(file_path, encoding="utf-8") as f:
            paper_text = f.read()
    except Exception as e:
        response["message"] = f"Failed to read file: {str(e)}"
        return response

    # 2. 预分类问题类型 (LIST vs SINGLE)
    q_type = classify_question(question, config.model_name)

    # 3. 构建 ContextGem 文档和提取任务 Concept
    doc = cg.Document(raw_text=paper_text)

    # 构造增强的描述，强制要求相关性解释
    # 这段提示词会被注入到 Concept 的 System Prompt 中
    enhanced_description = f"""
    [Task]: Extract information to answer the specific question: "{question}"

    [Strict Constraints]:
    1. ONLY extract sentences/sections that provide DIRECT evidence or answers to the question.
    2. If the text contains keywords but does not establish a clear relationship or answer, DO NOT extract it.
    3. Ignore general background info unless it directly answers the specific "How/Why/What" of the question.
    4. It is better to return NOTHING than to return irrelevant information.
    5. In the 'justification' field, you MUST explicitly explain WHY this excerpt is directly relevant.
    """

    if q_type == "LIST":
        concept = cg.ListConcept(
            name="target_info",
            description=enhanced_description,  # 使用增强版 Prompt
            add_references=True,
            add_justifications=True,
        )
    else:
        concept = cg.StringConcept(
            name="target_info",
            description=enhanced_description,  # 使用增强版 Prompt
            add_references=True,
            add_justifications=True,
        )

    doc.concepts = [concept]

    # 4. 初始化 ContextGem LLM 引擎
    llm = cg.DocumentLLM(
        model=config.model_name,
        api_key=config.openai_api_key,
        api_base=config.openai_base_url,
    )

    # 5. 执行提取（带分批机制，防止长文档超出上下文限制）
    try:
        result_doc = llm.extract_all(
            doc,
            max_paragraphs_to_analyze_per_call=DEFAULT_MAX_PARAGRAPHS_PER_CALL_VISIT,
        )
    except Exception as e:
        response["message"] = f"Extraction process failed: {str(e)}"
        return response

    # 6. 组装输出数据结构
    extracted_knowledge = []
    extracted_concept = result_doc.get_concept_by_name("target_info")

    if extracted_concept and extracted_concept.extracted_items:
        items_data = []
        for item in extracted_concept.extracted_items:
            # 提取原文片段
            evidence_snippets = []
            if hasattr(item, "reference_paragraphs") and item.reference_paragraphs:
                # 这里假设 reference_paragraphs 是 Paragraph 对象列表，有 raw_text 属性
                evidence_snippets = [p.raw_text for p in item.reference_paragraphs]

            # 构建单个知识点对象
            item_dict = {
                "content": item.value,  # 提取出的核心回答（文本或列表）
                "reason": item.justification,  # 提取理由
                "evidence_snippets": evidence_snippets,  # 原文证据片段
            }
            items_data.append(item_dict)

        extracted_knowledge.append({"type": q_type, "items": items_data})

    # 7. 更新并返回结果
    response["status"] = "success"
    response["message"] = "Extraction completed successfully."
    response["source_document"]["extracted_knowledge"] = extracted_knowledge

    return response


if __name__ == "__main__":
    # Simple test
    import sys

    if len(sys.argv) > 2:
        question = sys.argv[1]
        file_path = sys.argv[2]
    else:
        # Default test file
        papers_dir = Path("01-文献/.indexonly/papers")
        if papers_dir.exists():
            md_files = list(papers_dir.glob("*.md"))
            if md_files:
                file_path = str(md_files[0])
            else:
                print("No markdown files found")
                sys.exit(1)
        else:
            print("Papers directory not found")
            sys.exit(1)
        question = "这篇文章的主要发现是什么？"

    result = extract_info(question, file_path)
    print(f"Status: {result['status']}")
    print(f"Extracted {len(result['source_document']['extracted_knowledge'])} knowledge items")
