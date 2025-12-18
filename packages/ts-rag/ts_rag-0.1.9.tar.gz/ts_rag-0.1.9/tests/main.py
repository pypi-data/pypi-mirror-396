import json
import os
import sys
import threading
import time
from pathlib import Path

import psutil
from dotenv import load_dotenv
from litellm import completion

# 添加 src/ts_rag 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "ts_rag"))

import tashan_core as cg

# 清除代理环境变量
proxy_vars = [
    "http_proxy",
    "https_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "no_proxy",
    "NO_PROXY",
]

for var in proxy_vars:
    if var in os.environ:
        del os.environ[var]
        print(f"已清除代理环境变量: {var}")

# 加载 .env 文件并强制使用其中的变量
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    # 先加载 .env
    load_dotenv(dotenv_path=env_path)
    print(f"已加载环境配置文件: {env_path}")

    # 读取 .env 文件内容并强制设置环境变量
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()
                print(f"设置环境变量: {key.strip()}={value.strip()[:20]}{'...' if len(value) > 20 else ''}")

# 配置 - 从环境变量读取
MODEL_NAME = os.environ.get("MODEL_NAME", "openai/qwen-flash")


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


def classify_question(question_text):
    """
    使用 LLM 判断问题类型：是需要在回答中列出多个条目（LIST），还是单一的回答（SINGLE）。
    """
    print("正在分析问题类型...")
    prompt = f"""
    Analyze the following question and determine if the expected answer should be a LIST of
    items/steps/entities, or a SINGLE text block/summary.

    Question: "{question_text}"

    Return strictly valid JSON format: {{"type": "LIST"}} or {{"type": "SINGLE"}}.
    Do not output anything else.
    """

    try:
        response = completion(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        content = response.choices[0].message.content
        # 清理可能存在的 Markdown 代码块标记
        content = content.strip().replace("```json", "").replace("```", "")
        result = json.loads(content)
        return result.get("type", "SINGLE")
    except Exception as e:
        print(f"分类失败，默认使用 SINGLE. Error: {e}")
        return "SINGLE"


def main():
    total_start_time = time.time()
    memory_monitor = MemoryMonitor()
    memory_monitor.start()
    memory_stats: dict[str, float] | None = None

    # 1. 读取论文
    paper_file = (
        r"G:\deepresearch\contextgem-main\MyNewProject2\paper1\Vedula 等 - 2012 - "
        r"Emerging modes of collective cell migration induced by geometrical constraints_cleaned.md"
    )
    # paper_file = (
    #     r"G:\deepresearch\contextgem-main\Zhao_等_-_AstroInsight_Leveraging_Large_"
    #     r"Language_Models_to_Spark_Idea_Draft_Generation_in_Astronomy.md"
    # )
    print(f"正在读取论文文件: {paper_file}")

    if not os.path.exists(paper_file):
        print(f"错误：文件不存在 {paper_file}")
        return

    with open(paper_file, encoding="utf-8") as f:
        paper_text = f.read()

    # 2. 定义问题
    user_question = "宽通道和窄通道中，细胞迁移的速度和形态有什么区别？"
    # user_question = "这篇论文提出的框架包含哪些步骤，每个步骤是什么？"

    print(f"\n当前问题: {user_question}")

    # 3. 预分类 (Pre-classification)
    q_type = classify_question(user_question)
    print(f"判定类型: {q_type}")

    # 4. 动态构建 Concept
    print("正在初始化文档和提取任务...")
    doc = cg.Document(raw_text=paper_text)

    if q_type == "LIST":
        concept = cg.ListConcept(
            name="target_info",
            description=user_question,
            add_references=True,
            add_justifications=True,
        )
    else:
        concept = cg.StringConcept(
            name="target_info",
            description=user_question,
            add_references=True,
            add_justifications=True,
        )

    doc.concepts = [concept]

    # 5. 初始化 ContextGem LLM
    llm = cg.DocumentLLM(
        model=MODEL_NAME,
        api_key=os.environ.get("OPENAI_API_KEY"),
        api_base=os.environ.get("OPENAI_BASE_URL"),
    )

    # 6. 执行提取
    print("开始提取内容 (ContextGem)...")
    extract_start_time = time.time()

    try:
        result_doc = llm.extract_all(doc)

        # 7. 输出结果
        print("\n" + "=" * 60)
        print("提取结果报告")
        print("=" * 60)

        extracted_concept = result_doc.get_concept_by_name("target_info")

        if extracted_concept and extracted_concept.extracted_items:
            items = extracted_concept.extracted_items

            if q_type == "LIST":
                print(f"找到 {len(items)} 个相关条目:\n")
                for idx, item in enumerate(items, 1):
                    val = item.value
                    if isinstance(val, list):
                        print(f"--- 提取项 {idx} (包含 {len(val)} 个子项) ---")
                        for sub_idx, sub_item in enumerate(val, 1):
                            print(f"  {sub_idx}. {sub_item}")
                    else:
                        print(f"--- 提取项 {idx} ---")
                        print(val)

                    if item.justification:
                        print(f"  [理由]: {item.justification}")

                    if hasattr(item, "reference_paragraphs") and item.reference_paragraphs:
                        print(f"  [参考段落]: {len(item.reference_paragraphs)} 个")
                        for i, ref_para in enumerate(item.reference_paragraphs, 1):
                            print(f"   > [段落 {i}]: {ref_para.raw_text}")
                    print("")

            else:  # SINGLE
                print("找到答案:\n")
                item = items[0]
                print(f"{item.value}")
                if item.justification:
                    print(f"\n[理由]: {item.justification}")
                if hasattr(item, "reference_paragraphs") and item.reference_paragraphs:
                    print("\n[参考段落]:")
                    for p in item.reference_paragraphs:
                        print(f"> {p.raw_text}\n")

        else:
            print("未找到相关信息。")

        # 8. 统计 Token 消耗
        print("\n" + "=" * 60)
        print("资源消耗统计")
        print("=" * 60)
        usage_list = llm.get_usage()
        total_input = 0
        total_output = 0

        # 使用字典去重，因为 usage_list 可能包含相同 model+role 的重复条目
        unique_usage = {}
        for u in usage_list:
            key = f"{u.model}_{u.role}"
            unique_usage[key] = u

        for u in unique_usage.values():
            # u is _LLMUsageOutputContainer
            print(f"Model: {u.model}")
            print(f"  Input Tokens: {u.usage.input}")
            print(f"  Output Tokens: {u.usage.output}")
            print(f"  Total Tokens: {u.usage.input + u.usage.output}")
            total_input += u.usage.input
            total_output += u.usage.output

        print("-" * 30)
        print(f"Total Input: {total_input}")
        print(f"Total Output: {total_output}")
        print(f"Grand Total: {total_input + total_output}")

    except Exception as e:
        print(f"提取过程中发生错误: {e}")
        import traceback

        traceback.print_exc()
    finally:
        memory_stats = memory_monitor.stop()

    total_end_time = time.time()
    print("\n" + "=" * 60)
    print(f"分类耗时: {extract_start_time - total_start_time:.2f}s")
    print(f"提取耗时: {total_end_time - extract_start_time:.2f}s")
    print(f"总耗时: {total_end_time - total_start_time:.2f}s")

    if memory_stats:
        print("=" * 60)
        print("内存统计 (MB)")
        print("=" * 60)
        print(f"平均 RSS: {memory_stats['avg']:.2f} MB")
        print(f"峰值 RSS: {memory_stats['peak']:.2f} MB")


if __name__ == "__main__":
    main()
