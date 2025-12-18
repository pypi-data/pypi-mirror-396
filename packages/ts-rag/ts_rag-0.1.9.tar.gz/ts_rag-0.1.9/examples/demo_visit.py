#!/usr/bin/env python3
"""
测试 TashanRAG 信息提取功能的示例脚本

此脚本演示如何使用 visit.py 中的 extract_info 功能，
从单个论文文件中提取相关信息。
"""

import json
import os
import sys
import traceback
from pathlib import Path

# 添加 src 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "ts_rag"))

from visit import extract_info


def test_visit():
    """测试信息提取功能"""

    # ================= 配置区域 =================
    # 修改以下参数来测试不同的文件和问题
    test_question = "宽通道和窄通道中，细胞迁移的速度和形态有什么区别？"

    # 自动检测可用的论文文件
    papers_dir = Path("01-文献/.indexonly/papers")
    if papers_dir.exists():
        # 获取第一个 .md 文件作为测试文件
        md_files = list(papers_dir.glob("*.md"))
        if md_files:
            test_file = str(md_files[0])
            print(f"自动找到文件: {Path(test_file).name}")
        else:
            print("错误: 未找到转换后的 Markdown 文件")
            print("请先运行 indexer.py 或 paperindexg.py 来转换 PDF 文件")
            return
    else:
        # 手动指定文件路径（如果自动检测失败）
        test_file = "01-文献/.indexonly/papers/示例论文.md"
        print(f"使用手动指定的文件: {test_file}")
    # ===========================================

    print("=" * 60)
    print("TashanRAG 信息提取测试")
    print("=" * 60)
    print(f"问题: {test_question}")
    print(f"文件: {test_file}")
    print()

    # 确保文件存在
    if not os.path.exists(test_file):
        print(f"❌ 错误: 文件不存在: {test_file}")
        print("\n请确认:")
        print("1. 论文目录是否正确")
        print("2. PDF 文件是否已转换为 Markdown")
        print("3. 文件路径是否正确")
        return

    try:
        # 执行信息提取
        result = extract_info(test_question, test_file)

        # 显示结果
        print("\n" + "=" * 60)
        print("提取结果")
        print("=" * 60)
        print(f"状态: {result['status']}")
        print(f"消息: {result['message']}")
        print()

        if result["status"] == "success":
            # 显示文件路径
            file_info = result["source_document"]
            print(f"处理文件: {file_info['file_path']}")
            print()

            # 显示提取的知识
            knowledge_list = file_info.get("extracted_knowledge", [])
            print(f"提取的知识项数: {len(knowledge_list)}")
            print()

            for i, knowledge in enumerate(knowledge_list, 1):
                print(f"知识项 {i}:")
                print(f"  类型: {knowledge.get('type', 'unknown')}")

                items = knowledge.get("items", [])
                print(f"  包含内容数: {len(items)}")

                for j, item in enumerate(items, 1):
                    print(f"\n  内容 {j}:")
                    if isinstance(item.get("content"), list):
                        print(f"    内容列表: {item['content'][:3]}...")  # 只显示前3个
                    else:
                        content_preview = str(item.get("content", ""))[:200]
                        print(f"    内容: {content_preview}...")

                    reason = item.get("reason", "")
                    if reason:
                        reason_preview = reason[:100]
                        print(f"    理由: {reason_preview}...")

                    # 显示证据片段
                    evidence = item.get("evidence_snippets", [])
                    if evidence:
                        print(f"    证据片段数: {len(evidence)}")
                        if evidence:
                            first_evidence = evidence[0][:100]
                            print(f"    第一个证据: {first_evidence}...")

                print("-" * 40)

        # 显示完整的 JSON 输出
        print("\n" + "=" * 60)
        print("完整响应（JSON 格式）")
        print("=" * 60)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"\n❌ 提取失败: {str(e)}")
        traceback.print_exc()

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # 提示信息
    print("提示:")
    print("1. 确保已有转换后的 Markdown 文件")
    print("2. 修改脚本顶部的配置来测试不同的问题和文件")
    print("3. 可以使用不同的文件来测试不同的主题")
    print("4. 提取结果包含内容、理由和原文证据片段")
    print()

    test_visit()
