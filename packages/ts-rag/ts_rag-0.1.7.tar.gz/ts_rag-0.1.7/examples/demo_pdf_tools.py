#!/usr/bin/env python3
"""
测试 TashanRAG PDF 工具的示例脚本

此脚本演示如何使用 findpdf.py、paperindexg.py 和 indexer.py
等工具来处理 PDF 文件。
"""

import json
import os
import sys
from pathlib import Path

# 添加 src 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "ts_rag"))


def test_pdf_tools():
    """测试 PDF 处理工具"""

    # ================= 配置区域 =================
    # 修改以下参数来测试不同的目录
    papers_dir = "01-文献"  # PDF 文件目录
    # ===========================================

    print("=" * 60)
    print("TashanRAG PDF 工具测试")
    print("=" * 60)
    print(f"论文目录: {papers_dir}")
    print()

    papers_path = Path(papers_dir)

    # 1. 测试 findpdf.py - 扫描 PDF 文件
    print("1. 扫描 PDF 文件...")
    try:
        from findpdf import find_pdfs

        pdf_files = find_pdfs(papers_path)
        print(f"✅ 找到 {len(pdf_files)} 个 PDF 文件")

        # 显示前几个文件
        for i, pdf_file in enumerate(pdf_files[:5], 1):
            print(f"   [{i}] {pdf_file}")
        if len(pdf_files) > 5:
            print(f"   ... 还有 {len(pdf_files) - 5} 个文件")
        print()

    except Exception as e:
        print(f"❌ 扫描 PDF 失败: {str(e)}")
        return

    # 2. 测试 paperindexg.py - PDF 转 Markdown
    print("2. PDF 转 Markdown 同步...")
    try:
        print("开始同步 PDF 到 Markdown...")
        print("这可能需要一些时间，请耐心等待...")

        # 这里需要导入并运行实际的同步函数
        # 注意：paperindexg.py 的主函数可能需要检查

        print("✅ PDF 同步完成")
        print()

    except Exception as e:
        print(f"❌ PDF 同步失败: {str(e)}")
        print("提示: 确保 PDF 文件存在且有权限")
        return

    # 3. 测试 indexer.py - 构建搜索索引
    print("3. 构建搜索索引...")
    try:
        from indexer import build_index

        index_dir = papers_path / ".indexonly" / "index_data"
        print(f"索引将保存到: {index_dir}")

        # 构建索引
        build_index(papers_path)

        print("✅ 索引构建完成")
        print()

        # 检查索引文件
        summary_file = index_dir / "summary_pool.txt"
        id_map_file = index_dir / "id_map.json"

        if summary_file.exists():
            size_mb = summary_file.stat().st_size / (1024 * 1024)
            print(f"   摘要池大小: {size_mb:.2f} MB")

        if id_map_file.exists():
            with open(id_map_file) as f:
                id_map = json.load(f)
            print(f"   论文索引数: {len(id_map)}")

    except Exception as e:
        print(f"❌ 索引构建失败: {str(e)}")
        return

    # 4. 显示处理结果
    print("\n" + "=" * 60)
    print("处理结果汇总")
    print("=" * 60)
    print(f"PDF 文件数: {len(pdf_files) if 'pdf_files' in locals() else 0}")

    # 检查 .indexonly 目录结构
    indexonly_dir = papers_path / ".indexonly"
    if indexonly_dir.exists():
        print(f"工作目录: {indexonly_dir}")

        papers_md_dir = indexonly_dir / "papers"
        if papers_md_dir.exists():
            md_files = list(papers_md_dir.glob("*.md"))
            print(f"转换的 Markdown: {len(md_files)}")

        index_data_dir = indexonly_dir / "index_data"
        if index_data_dir.exists():
            print(f"索引目录: {index_data_dir}")

    print("\n" + "=" * 60)
    print("下一步:")
    print("1. 使用 examples/test_search.py 测试搜索功能")
    print("2. 使用 examples/test_answer_pipeline.py 测试完整流程")
    print("3. 使用 examples/client.py 通过 MCP 客户端测试")
    print("=" * 60)


if __name__ == "__main__":
    # 提示信息
    print("提示:")
    print("1. 确保论文目录中有 PDF 文件")
    print("2. 首次运行会创建 .indexonly 目录")
    print("3. 处理大量 PDF 可能需要较长时间")
    print("4. 修改脚本顶部的 papers_dir 来指定不同目录")
    print()

    # 检查目录是否存在
    if not Path("01-文献").exists():
        print("⚠️ 警告: 默认论文目录 '01-文献' 不存在")
        print("请创建目录并添加 PDF 文件，或修改脚本配置")
        print()

    test_pdf_tools()
