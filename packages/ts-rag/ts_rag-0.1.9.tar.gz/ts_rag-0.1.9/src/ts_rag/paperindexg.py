import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# ================= 导入模块 =================
try:
    import findpdf
except ImportError:
    # 尝试添加当前目录到 sys.path (适配 server 调用场景)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    try:
        import findpdf
    except ImportError:
        print("错误: 找不到 findpdf.py")
        sys.exit(1)

try:
    from pdf2md import PDFToMarkdownParser
except ImportError:
    print("错误: 找不到 pdf2md.py")
    sys.exit(1)

# ================= 辅助函数 =================


def get_relative_key(full_path, root_path):
    try:
        rel = full_path.relative_to(root_path)
        return str(rel.with_suffix("")).replace("\\", "/")
    except ValueError:
        return None


def scan_existing_mds(papers_root):
    md_map = {}
    if not papers_root.exists():
        return md_map
    for md_file in papers_root.rglob("*.md"):
        key = get_relative_key(md_file, papers_root)
        if key:
            md_map[key] = md_file
    return md_map


def convert_single_pdf(pdf_path, target_dir):
    """
    转换单个 PDF 文件（用于并行处理）

    Args:
        pdf_path: PDF 文件路径
        target_dir: 目标输出目录

    Returns:
        dict: {"success": bool, "path": Path, "error": str | None}
    """
    try:
        # 确保目标目录存在
        target_dir.mkdir(parents=True, exist_ok=True)

        # 执行转换
        parser = PDFToMarkdownParser(pdf_path, target_dir)
        parser.run()

        return {"success": True, "path": pdf_path, "error": None}
    except Exception as e:
        return {"success": False, "path": pdf_path, "error": str(e)}


# ================= 核心逻辑封装 =================


def run_pdf_sync_pipeline():
    """
    供外部调用的主入口函数

    PDF 输入目录固定为 Path.cwd() / "01-文献"
    输出目录固定为 Path.cwd() / ".tashan" / "deepsearch"
    """
    # 输入目录固定为当前工作目录下的 "01-文献"
    source_root = Path.cwd() / "01-文献"

    if not source_root.exists():
        print(f"【错误】找不到源文件夹: {source_root}")
        print("请确保在当前工作目录下创建 '01-文献' 文件夹并放入 PDF 文件")
        return {
            "new_files": 0,
            "updated_files": 0,
            "failed_files": 0,
            "total_pdfs": 0,
            "total_mds": 0,
        }
    # 定义隐藏目录结构 (使用当前工作目录，实现多用户自适应)
    # ${cwd} 表示当前工作目录 (current working directory)
    hidden_dir = Path.cwd() / ".tashan" / "deepsearch"
    index_file = hidden_dir / "paperfind.txt"
    papers_output_root = hidden_dir / "papers"

    print("=== [Step 1] PDF->MD 增量同步启动 ===")
    print(f"源目录: {source_root}")
    print(f"MD库目录: {papers_output_root}")

    # 1. 初始化环境
    if not hidden_dir.exists():
        hidden_dir.mkdir(parents=True, exist_ok=True)

    if not papers_output_root.exists():
        papers_output_root.mkdir(parents=True, exist_ok=True)

    # 2. 扫描 PDF (findpdf)
    print("扫描 PDF 列表...")
    findpdf.find_all_pdfs(str(source_root), str(index_file))

    # 3. 构建 Source Map
    source_pdf_map = {}
    if index_file.exists():
        with open(index_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                p = Path(line)
                key = get_relative_key(p, source_root.resolve())
                if key:
                    source_pdf_map[key] = p

    # 4. 扫描现有 MD
    dest_md_map = scan_existing_mds(papers_output_root)

    # 5. 计算差异
    source_keys = set(source_pdf_map.keys())
    dest_keys = set(dest_md_map.keys())
    keys_to_add = source_keys - dest_keys
    keys_to_remove = dest_keys - source_keys

    print(
        f"同步分析: 总PDF {len(source_keys)} | 现有MD {len(dest_keys)} | "
        f"新增 {len(keys_to_add)} | 删除 {len(keys_to_remove)}"
    )

    # 6. 执行删除
    if keys_to_remove:
        for key in keys_to_remove:
            md_path_to_delete = dest_md_map[key]
            try:
                os.remove(md_path_to_delete)
                # 尝试清理空目录
                parent_dir = md_path_to_delete.parent
                if parent_dir != papers_output_root and not any(parent_dir.iterdir()):
                    try:
                        parent_dir.rmdir()
                    except Exception:
                        pass
            except OSError:
                pass

    # 7. 执行转换 (新增，并行处理)
    new_files_count = 0
    updated_files_count = 0
    failed_files_count = 0

    if keys_to_add:
        # 获取并行数配置
        try:
            from config import config

            max_workers = config.max_concurrent_pdf_conversion
        except ImportError:
            # 如果无法导入 config，使用默认值
            max_workers = int(os.environ.get("MAX_CONCURRENT_PDF_CONVERSION", "3"))

        print(f"开始转换 {len(keys_to_add)} 个新文件（并行数: {max_workers}）...")

        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = {}
            for key in keys_to_add:
                pdf_path = source_pdf_map[key]
                relative_parent = Path(key).parent
                target_dir = papers_output_root / relative_parent

                future = executor.submit(convert_single_pdf, pdf_path, target_dir)
                futures[future] = (key, pdf_path)

            # 收集结果（使用 as_completed 以便实时显示进度）
            completed_count = 0
            for future in as_completed(futures):
                completed_count += 1
                key, pdf_path = futures[future]

                try:
                    result = future.result()
                    if result["success"]:
                        new_files_count += 1
                        print(f"[{completed_count}/{len(keys_to_add)}] ✅ 完成: {pdf_path.name}")
                    else:
                        failed_files_count += 1
                        print(f"[{completed_count}/{len(keys_to_add)}] ❌ 失败: {pdf_path.name} - {result['error']}")
                except Exception as e:
                    failed_files_count += 1
                    print(f"[{completed_count}/{len(keys_to_add)}] ❌ 异常: {pdf_path.name} - {str(e)}")
    else:
        print("没有新文件需要转换。")

    print("=== [Step 1] PDF->MD 同步完成 ===\n")

    # 返回同步结果
    return {
        "new_files": new_files_count,
        "updated_files": updated_files_count,
        "failed_files": failed_files_count,
        "total_pdfs": len(source_keys),
        "total_mds": len(dest_keys),
    }


# ================= 脚本入口 (兼容旧用法) =================

if __name__ == "__main__":
    # 直接调用，输入目录固定为 Path.cwd() / "01-文献"
    run_pdf_sync_pipeline()
