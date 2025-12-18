#!/usr/bin/env python3
"""
测试 TashanRAG 完整 RAG 流程的示例脚本

此脚本演示如何使用 answer.py 中的功能进行完整的问答流程，
包括搜索、访问和答案生成。
"""

import asyncio
import os
import sys
import traceback
from pathlib import Path

# 添加 src 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "ts_rag"))

from answer import generate_answer


async def test_answer_pipeline():
    """测试完整的 RAG 流程"""

    # ================= 配置区域 =================
    # 修改以下参数来测试不同的场景
    test_question = "细胞增殖和集体行为的相互作用是什么？"
    papers_dir = "01-文献"  # 论文目录
    top_k = 3  # 检索的论文数量
    max_concurrent_visits = 5  # 最大并发访问数
    # ===========================================

    print("=" * 60)
    print("TashanRAG 完整 RAG 流程测试")
    print("=" * 60)
    print(f"问题: {test_question}")
    print(f"论文目录: {papers_dir}")
    print(f"检索论文数: {top_k}")
    print(f"最大并发: {max_concurrent_visits}")
    print()

    # 确保论文目录存在
    papers_path = Path(papers_dir)
    if not papers_path.exists():
        print(f"❌ 错误: 论文目录不存在: {papers_path}")
        print("请确认路径是否正确，或修改 papers_dir 变量")
        return

    print("开始处理...")
    print("这可能需要一些时间，请耐心等待...")
    print()

    try:
        result = generate_answer(
            question=test_question,
            top_k=top_k,
            max_concurrent_visits=max_concurrent_visits,
            papers_dir=papers_dir,
        )

        print("\n" + "=" * 60)
        print("处理结果")
        print("=" * 60)

        if result["status"] == "error":
            print("❌ 处理失败")
            print(f"错误信息: {result.get('error_message')}")
            if result.get("final_answer"):
                print(f"\n参考回答: {result['final_answer'][:200]}...")
        else:
            print("✅ 处理成功")

            # 显示思考过程（如果有）
            if result.get("thinking"):
                print("\n🧠 思考过程:")
                print(result["thinking"][:500] + "..." if len(result["thinking"]) > 500 else result["thinking"])
                print("-" * 30)

            # 显示最终回答
            if result.get("final_answer"):
                print("\n📢 最终回答:")
                print(result["final_answer"])

            # 显示引用
            citations = result.get("citations_map", {})
            if citations:
                print(f"\n📚 引用来源 ({len(citations)} 个):")
                keys = sorted(citations.keys(), key=lambda x: int(x) if x.isdigit() else x)
                for k in keys[:5]:  # 只显示前5个
                    item = citations[k]
                    preview = item.get("text", "")[:100].replace("\n", " ")
                    file_name = os.path.basename(item.get("file_path", "Unknown"))
                    print(f"  [^{k}] {file_name}")
                    print(f"      {preview}...")

            # 显示处理指标
            metrics = result.get("metrics", {})
            if metrics:
                print("\n📊 处理指标:")
                print(f"  - 总耗时: {metrics.get('total_time', 0)}秒")
                print(f"  - 搜索耗时: {metrics.get('search_time', 0)}秒")
                print(f"  - 访问耗时: {metrics.get('visit_time', 0)}秒")
                print(f"  - 处理论文数: {metrics.get('papers_processed', 0)}")
                print(f"  - 提取片段数: {metrics.get('snippets_count', 0)}")
                print(f"  - 内存峰值: {metrics.get('memory_peak_mb', 0)}MB")

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断了处理")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    # 提示信息
    print("提示:")
    print("1. 确保论文目录中有 PDF 文件")
    print("2. 首次运行会创建索引，需要一些时间")
    print("3. 使用 Ctrl+C 可以中断处理")
    print("4. 修改脚本顶部的配置来测试不同的问题")
    print()

    asyncio.run(test_answer_pipeline())
