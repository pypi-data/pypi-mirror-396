#!/usr/bin/env python3
"""
测试 TashanRAG 搜索功能的示例脚本

此脚本演示如何使用 search.py 中的搜索功能，
从论文库中检索相关的论文。
"""

import json
import os
import sys
import traceback

# 添加 src 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "ts_rag"))

from search import search_papers


def test_search():
    """测试论文搜索功能"""

    # ================= 配置区域 =================
    # 修改以下参数来测试不同的搜索场景
    test_question = "宽通道和窄通道中，细胞迁移的速度和形态有什么区别？"
    papers_dir = "01-文献"  # 论文目录
    top_k = 3  # 最大返回论文数
    index_dir = None  # 索引目录（None 表示自动检测）
    # ===========================================

    print("=" * 60)
    print("TashanRAG 论文搜索测试")
    print("=" * 60)
    print(f"搜索问题: {test_question}")
    print(f"论文目录: {papers_dir}")
    print(f"返回数量: {top_k}")
    print()

    try:
        # 执行搜索
        result = search_papers(
            question=test_question,
            top_k=top_k,
            papers_dir=papers_dir,
            index_dir=index_dir,
        )

        # 显示结果
        print("\n" + "=" * 60)
        print("搜索结果")
        print("=" * 60)
        print(f"状态: {result['status']}")
        print(f"找到论文数: {result['total_found']}")
        print()

        if result["status"] == "error":
            print(f"错误信息: {result['message']}")
        else:
            papers = result.get("found_papers", [])
            if papers:
                print(f"找到 {len(papers)} 篇相关论文:\n")
                for i, paper in enumerate(papers, 1):
                    print(f"[{i}] 论文 ID: {paper['paper_id']}")
                    print(f"    文件路径: {paper['file_path']}")
                    print(f"    检索理由: {paper['reason'][:200]}...")
                    print()
            else:
                print("未找到相关论文")

        # 显示用于验证的输出格式
        print("=" * 60)
        print("完整响应（JSON 格式）")
        print("=" * 60)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"\n❌ 搜索失败: {str(e)}")
        traceback.print_exc()

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # 提示信息
    print("提示:")
    print("1. 确保论文目录中有 PDF 文件")
    print("2. 确保索引已构建（首次运行时会自动构建）")
    print("3. 修改脚本顶部的配置来测试不同的问题")
    print("4. 可以使用不同的 top_k 值来控制返回的论文数量")
    print()

    test_search()
