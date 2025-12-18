import os
import sys
from pathlib import Path

# 导入统一配置


def find_all_pdfs(target_directory, output_txt_path):
    """
    遍历指定目录及其所有子目录，找到所有PDF文件，
    将其绝对路径写入指定的TXT文件中。
    """

    # 确保目标目录存在
    if not os.path.exists(target_directory):
        print(f"错误：找不到目录 '{target_directory}'")
        return

    # 计数器
    count = 0

    # 使用 'w' 模式打开文件，encoding='utf-8' 防止中文路径乱码
    with open(output_txt_path, "w", encoding="utf-8") as f:
        print(f"开始在 '{target_directory}' 中扫描 PDF...")

        # os.walk 会递归遍历所有文件夹
        # root: 当前正在遍历的文件夹路径
        # dirs: 当前文件夹下的子文件夹列表
        # files: 当前文件夹下的文件列表
        for root, _dirs, files in os.walk(target_directory):
            for file in files:
                # 检查后缀名，忽略大小写 (比如 .pdf 和 .PDF 都会被识别)
                if file.lower().endswith(".pdf"):
                    # 组合成完整路径
                    full_path = os.path.join(root, file)
                    # 转换为绝对路径
                    abs_path = os.path.abspath(full_path)

                    # 写入文件并换行
                    f.write(abs_path + "\n")
                    count += 1

    print("-" * 30)
    print("扫描完成！")
    print(f"共找到 {count} 个 PDF 文件。")
    print(f"路径已保存至: {os.path.abspath(output_txt_path)}")


def find_pdfs(directory_path: str | Path, output_file: str | Path | None = None) -> list[str]:
    """
    查找指定目录中的所有 PDF 文件

    Args:
        directory_path: 搜索目录路径
        output_file: 输出文件路径（可选）

    Returns:
        list[str]: 找到的 PDF 文件路径列表
    """
    directory_path = Path(directory_path)

    if not directory_path.exists():
        print(f"错误：找不到目录 '{directory_path}'")
        return []

    # 默认输出文件路径
    if output_file is None:
        output_file = directory_path / "pdf_paths.txt"
    else:
        output_file = Path(output_file)

    pdf_files = []

    print(f"开始在 '{directory_path}' 中扫描 PDF...")

    for root, _dirs, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                abs_path = os.path.abspath(full_path)
                pdf_files.append(abs_path)

    # 保存到文件
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for pdf_path in pdf_files:
            f.write(pdf_path + "\n")

    print("-" * 30)
    print("扫描完成！")
    print(f"共找到 {len(pdf_files)} 个 PDF 文件。")
    print(f"路径已保存至: {os.path.abspath(output_file)}")

    return pdf_files


if __name__ == "__main__":
    # Simple test
    import sys

    if len(sys.argv) > 1:
        search_dir = sys.argv[1]
    else:
        search_dir = "."

    pdf_files = find_pdfs(search_dir)
    print(f"Found {len(pdf_files)} PDF files in {search_dir}")
    for pdf in pdf_files[:3]:
        print(f"  - {pdf}")
