#!/usr/bin/env python3
"""
测试 TashanRAG PDF 查找功能的示例脚本

此脚本演示如何使用 findpdf.py 中的 find_pdfs 函数来查找 PDF 文件。
"""

import os
import sys
import traceback
from pathlib import Path

# 添加 src 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "ts_rag"))

from findpdf import find_pdfs


def test_findpdf():
    """测试 PDF 查找功能"""

    # ================= 配置区域 =================
    # 修改以下参数来测试不同的目录
    search_directory = "01-文献"  # 要搜索的目录
    output_file = None  # 输出文件（None 表示使用默认位置）
    # ===========================================

    print("=" * 60)
    print("TashanRAG PDF 查找测试")
    print("=" * 60)
    print(f"搜索目录: {search_directory}")
    print(f"输出文件: {output_file or '默认'}")
    print()

    search_path = Path(search_directory)

    # 确保目录存在
    if not search_path.exists():
        print(f"❌ 错误: 目录不存在: {search_path}")
        print("\n请确认:")
        print("1. 搜索目录是否正确")
        print("2. 路径是否存在")
        return

    try:
        # 执行 PDF 查找
        pdf_files = find_pdfs(search_path, output_file)

        print("\n" + "=" * 60)
        print("查找结果")
        print("=" * 60)

        if pdf_files:
            print(f"✅ 成功找到 {len(pdf_files)} 个 PDF 文件")
            print()

            # 显示前几个文件
            print("前几个文件:")
            for i, pdf_file in enumerate(pdf_files[:10], 1):
                file_size = Path(pdf_file).stat().st_size / (1024 * 1024)  # MB
                print(f"  [{i}] {pdf_file}")
                print(f"      大小: {file_size:.2f} MB")

            if len(pdf_files) > 10:
                print(f"  ... 还有 {len(pdf_files) - 10} 个文件")

            # 显示总大小统计
            total_size = sum(Path(pdf).stat().st_size for pdf in pdf_files) / (1024 * 1024)
            print(f"\n总大小: {total_size:.2f} MB")

            # 检查输出文件
            if output_file is None:
                output_file = search_path / "pdf_paths.txt"

            if Path(output_file).exists():
                print(f"\n✅ 路径列表已保存到: {output_file}")
            else:
                print("\n⚠️ 警告: 输出文件未创建")

        else:
            print("❌ 未找到 PDF 文件")
            print("\n可能的原因:")
            print("1. 目录中没有 PDF 文件")
            print("2. PDF 文件扩展名不是 .pdf")
            print("3. 文件权限问题")

    except Exception as e:
        print(f"\n❌ 查找失败: {str(e)}")
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("下一步:")
    print("1. 使用 paperindexg.py 转换 PDF 为 Markdown")
    print("2. 使用 indexer.py 构建搜索索引")
    print("3. 使用 test_search.py 测试搜索功能")
    print("=" * 60)


if __name__ == "__main__":
    # 提示信息
    print("提示:")
    print("1. 确保搜索目录中有 PDF 文件")
    print("2. 修改脚本顶部的 search_directory 来指定不同目录")
    print("3. 查找结果会保存到 pdf_paths.txt 文件")
    print()

    # 检查默认目录是否存在
    if not Path("01-文献").exists():
        print("⚠️ 警告: 默认搜索目录 '01-文献' 不存在")
        print("请创建目录并添加 PDF 文件，或修改脚本配置")
        print()

    test_findpdf()
