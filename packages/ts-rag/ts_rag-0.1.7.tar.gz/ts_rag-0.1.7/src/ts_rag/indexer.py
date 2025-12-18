import json
import os
import re
from pathlib import Path

# ==========================================
# 1. 文本清洗与提取逻辑 (Core Extraction Logic)
# ==========================================


def clean_text(text: str) -> str:
    return text.strip()


def is_garbage_line(line: str) -> bool:
    """判断是否为无意义的元数据行"""
    line_lower = line.lower()
    stripped = line.strip()
    words = stripped.split()

    # 长度过短通常不是摘要
    if len(words) < 10:
        return True

    # 关键词过滤
    garbage_keywords = [
        "university",
        "department",
        "institute",
        "school of",
        "faculty of",
        "laboratory",
        "email",
        "e-mail",
        "correspondence",
        "@",
        "arxiv",
        "doi:",
        "https://",
        "vol.",
        "issn",
        "no.",
        "pp.",
        "submitted to",
        "accepted by",
        "received",
        "published",
        "copyright",
    ]
    for kw in garbage_keywords:
        if kw in line_lower:
            return True

    # 符号密度过滤
    clean_chars = re.sub(r"[0-9\s\.,;:\-\(\)\[\]]", "", line)
    if len(clean_chars) < 2:
        return True

    # 大写字母比例过滤 (过滤全大写的作者名/机构名)
    capitalized_words = 0
    total_valid_words = 0
    for w in words:
        if w[0].isalpha():
            total_valid_words += 1
            if w[0].isupper() and not w.isupper():
                capitalized_words += 1

    if total_valid_words > 0:
        ratio = capitalized_words / total_valid_words
        if ratio > 0.5:
            return True

    return False


def is_abstract_header(line: str) -> bool:
    """判断是否为 Abstract 标题"""
    line_lower = line.lower().strip()
    if len(line_lower) > 40:
        return False
    keywords = ["abstract", "summary", "a b s t r a c t", "摘要", "内容摘要"]
    for kw in keywords:
        if kw in line_lower:
            clean = re.sub(r"[^a-z\u4e00-\u9fa5]", "", line_lower)
            if clean == kw.replace(" ", ""):
                return True
    return False


def is_intro_header(line: str) -> bool:
    """判断是否为 Introduction 标题 (作为摘要结束的标志)"""
    line_lower = line.lower().strip()
    target_words_en = [
        "introduction",
        "background",
        "overview",
        "preface",
        "motivation",
        "related work",
        "context",
        "methods",
        "methodology",
    ]
    target_words_cn = [
        "介绍",
        "背景",
        "引言",
        "绪论",
        "导言",
        "概述",
        "前言",
        "方法",
        "研究背景",
    ]
    all_keywords = target_words_en + target_words_cn

    if not any(k in line_lower for k in all_keywords):
        return False
    if len(line_lower) > 80:
        return False

    if line_lower.startswith("#"):
        return True
    if re.match(r"^(\d+|[ivx]+)[\.\,\、\s]", line_lower):
        return True

    clean_content = re.sub(r"[^a-z\u4e00-\u9fa5]", "", line_lower)
    for kw in all_keywords:
        if clean_content == kw:
            return True
        if line.isupper() and kw in clean_content:
            return True
    return False


def extract_paper_info(file_path: Path) -> tuple[str, str]:
    """读取 MD 文件并提取标题和摘要"""
    try:
        with open(file_path, encoding="utf-8") as f:
            raw_lines = [line.rstrip() for line in f.readlines()]
            lines = [line for line in raw_lines if line.strip()]
    except Exception as e:
        return file_path.stem, f"[Error reading file: {e}]"

    if not lines:
        return file_path.stem, "[Empty File]"

    # --- 提取标题 ---
    title = ""
    title_search_limit = min(20, len(lines))
    header_found = False
    for i in range(title_search_limit):
        line = lines[i].strip()
        if line.startswith("# ") or line.startswith("## "):
            title = line.lstrip("#").strip()
            header_found = True
            break
    if not header_found:
        fallback_limit = min(5, len(lines))
        title_candidates = []
        for i in range(fallback_limit):
            clean = lines[i].strip()
            if len(clean) > 2:
                title_candidates.append(clean)
        title = " ".join(title_candidates)

    # --- 提取摘要范围 ---
    abstract_start_index = 0
    scan_limit = min(50, len(lines))
    for i in range(scan_limit):
        if is_abstract_header(lines[i]):
            abstract_start_index = i + 1
            break

    abstract_end_index = len(lines)
    intro_found = False
    for i in range(abstract_start_index, len(lines)):
        if is_intro_header(lines[i]):
            abstract_end_index = i
            intro_found = True
            break

    # --- 清洗摘要内容 ---
    candidate_lines = lines[abstract_start_index:abstract_end_index]
    valid_parts = []
    for line in candidate_lines:
        clean_line = line.strip()
        if is_abstract_header(clean_line):
            continue
        if is_garbage_line(clean_line):
            continue
        valid_parts.append(clean_line)

    if not valid_parts:
        longest_para = ""
        for line in candidate_lines:
            if len(line) > len(longest_para):
                longest_para = line
        if len(longest_para) > 50:
            abstract = longest_para
        else:
            abstract = "[Abstract extraction failed: No valid content found]"
    else:
        full_text = "\n".join(valid_parts)
        if not intro_found:
            words = full_text.split()
            if len(words) > 350:
                truncated = " ".join(words[:350])
                abstract = truncated + "... [Truncated at 350 words]"
            else:
                abstract = full_text
        else:
            abstract = full_text

    return title, abstract


# ==========================================
# 2. 增量更新核心逻辑 (Incremental Logic)
# ==========================================


def parse_existing_pool(pool_path: Path) -> dict[str, str]:
    """
    解析已存在的 summary_pool.txt，利用 ID 标记还原内容
    返回: {paper_id: 完整文本块(包含Start/End标记)}
    """
    if not pool_path.exists():
        return {}

    pool_dict = {}
    current_id = None
    buffer = []

    try:
        with open(pool_path, encoding="utf-8") as f:
            for line in f:
                # 关键：从文本行中提取 ID，与 JSON 的 Key 进行对齐
                start_match = re.match(r"^=== PAPER START: (.+) ===$", line.strip())
                if start_match:
                    current_id = start_match.group(1)
                    buffer = [line]
                    continue

                if line.strip() == "=== PAPER END ===":
                    if current_id:
                        buffer.append(line)
                        pool_dict[current_id] = "".join(buffer)
                    current_id = None
                    buffer = []
                    continue

                if current_id:
                    buffer.append(line)

    except Exception as e:
        print(f"[Warning] Failed to parse existing pool: {e}")
        return {}

    return pool_dict


def load_existing_index(map_path: Path, pool_path: Path) -> tuple[dict, dict]:
    """加载磁盘上的旧索引数据"""
    existing_map = {}
    existing_pool = {}

    if map_path.exists():
        try:
            with open(map_path, encoding="utf-8") as f:
                existing_map = json.load(f)
        except Exception:
            pass  # 文件损坏或空，忽略

    if pool_path.exists():
        existing_pool = parse_existing_pool(pool_path)

    return existing_map, existing_pool


def build_index():
    """
    构建索引

    基于固定的 hidden_dir (${cwd}/.tashan/deepsearch) 工作：
    - 从 papers/ 目录扫描 MD 文件
    - 从 paperfind.txt 读取 PDF 路径用于匹配
    """
    # 使用固定的 hidden_dir，实现多用户自适应
    hidden_dir = Path.cwd() / ".tashan" / "deepsearch"
    paperfind_txt = hidden_dir / "paperfind.txt"
    papers_mirror_root = hidden_dir / "papers"
    index_output_dir = hidden_dir / "index_data"

    map_output_path = index_output_dir / "id_map.json"
    pool_output_path = index_output_dir / "summary_pool.txt"

    # 先创建索引输出目录（即使文件不存在也要创建）
    os.makedirs(index_output_dir, exist_ok=True)

    if not paperfind_txt.exists():
        print(f"【错误】找不到地址列表文件: {paperfind_txt}")
        print("请先运行 run_pdf_sync_pipeline() 生成 paperfind.txt")
        return

    # --- Step A: 加载旧状态 ---
    print(">>> 正在检查现有索引...")
    old_map, old_pool_dict = load_existing_index(map_output_path, pool_output_path)
    existing_ids_set = set(old_map.keys())
    print(f"    - 已有记录: {len(old_map)} 条")

    # --- Step B: 扫描 papers/ 目录获取所有 MD 文件 ---
    print(">>> 正在扫描 MD 文件...")
    md_files_map = {}  # {相对路径key: md_file_path}
    if papers_mirror_root.exists():
        for md_file in papers_mirror_root.rglob("*.md"):
            # 计算相对于 papers_mirror_root 的相对路径
            try:
                rel_path = md_file.relative_to(papers_mirror_root)
                # 生成 ID (与之前逻辑一致)
                rel_path_no_suffix = rel_path.with_suffix("")
                paper_id = str(rel_path_no_suffix).replace(os.sep, "_").replace(".", "_")
                md_files_map[paper_id] = md_file
            except ValueError:
                continue
    print(f"    - 找到 MD 文件: {len(md_files_map)} 个")

    # --- Step C: 读取 PDF 路径列表，建立 PDF 路径映射 ---
    print(f">>> 正在读取文件列表: {paperfind_txt.name}")
    pdf_paths_map = {}  # {paper_id: pdf_abs_path}
    with open(paperfind_txt, encoding="utf-8") as f:
        for line in f:
            pdf_abs_path = line.strip()
            if not pdf_abs_path:
                continue
            pdf_path_obj = Path(pdf_abs_path)
            # 通过文件名匹配找到对应的 MD 文件
            pdf_name_no_ext = pdf_path_obj.stem
            # 尝试匹配：查找 MD 文件中文件名相同的
            for paper_id, md_file in md_files_map.items():
                if md_file.stem == pdf_name_no_ext:
                    pdf_paths_map[paper_id] = pdf_path_obj
                    break

    print(f"    - 读取到 PDF 路径: {len(pdf_paths_map)} 条（已匹配到 MD）")

    # --- Step D: 计算 ID 并分类 (Keep / Add / Remove) ---
    ids_to_process = []  # 需要读取 MD 的 (新增/数据缺失)
    ids_to_keep = []  # 直接复用的 (旧数据完整)
    current_ids_set = set(md_files_map.keys())

    for paper_id, md_file_path in md_files_map.items():
        pdf_path_obj = pdf_paths_map.get(paper_id)  # 可能为 None（如果 PDF 已删除但 MD 还在）

        current_ids_set.add(paper_id)

        # 判定：如果 ID 在旧 Map 里 AND 在旧 Pool 里 -> Keep
        if paper_id in existing_ids_set and paper_id in old_pool_dict:
            ids_to_keep.append((paper_id, old_map[paper_id], old_pool_dict[paper_id]))
        else:
            ids_to_process.append((paper_id, pdf_path_obj, md_file_path))

    print(f"    - 总 MD 文件: {len(md_files_map)} 个")

    ids_to_remove = existing_ids_set - current_ids_set

    print("\n=== 增量分析报告 ===")
    print(f"  - 保持不变 (Skip): {len(ids_to_keep)}")
    print(f"  - 新增/更新 (Task): {len(ids_to_process)}")
    print(f"  - 过期删除 (Drop): {len(ids_to_remove)}")
    print("====================\n")

    # --- Step D: 执行处理 ---
    new_summary_pool = []
    new_id_map = {}

    # 1. 处理保持不变的 (直接内存复制)
    for pid, map_data, pool_text in ids_to_keep:
        new_id_map[pid] = map_data
        new_summary_pool.append(pool_text.strip() + "\n")

    # 2. 处理新增的 (IO 操作)
    if ids_to_process:
        print(f">>> 开始处理 {len(ids_to_process)} 个新文件...")

    processed_count = 0
    missing_md_count = 0

    for paper_id, pdf_path_obj, md_file_path in ids_to_process:
        if not md_file_path.exists():
            missing_md_count += 1
            # print(f"Warning: MD not found for {paper_id}")
            continue

        try:
            # 提取内容 (这是最耗时的步骤)
            title, abstract = extract_paper_info(md_file_path)

            # 生成 Text Block
            entry = f"=== PAPER START: {paper_id} ===\n"
            entry += f"TITLE: {title}\n"
            entry += f"ABSTRACT: {abstract}\n"
            entry += "=== PAPER END ===\n"
            new_summary_pool.append(entry)

            # 生成 Map Entry
            new_id_map[paper_id] = {
                "pdf_path": str(pdf_path_obj) if pdf_path_obj else "",
                "md_path": str(md_file_path),
                "original_filename": pdf_path_obj.name if pdf_path_obj else md_file_path.stem,
                "title": title,
                "abstract_preview": abstract[:200] + "...",
            }

            processed_count += 1
            if processed_count % 10 == 0:
                print(f"    已处理: {processed_count}/{len(ids_to_process)}")

        except Exception as e:
            print(f"Error processing {md_file_path.name}: {e}")

    # --- Step E: 写入磁盘 ---
    print("\n>>> 正在保存索引...")

    with open(pool_output_path, "w", encoding="utf-8") as f:
        f.write("".join(new_summary_pool))

    with open(map_output_path, "w", encoding="utf-8") as f:
        json.dump(new_id_map, f, indent=2, ensure_ascii=False)

    print("-" * 30)
    print("索引构建完成！")
    print(f"  - 总索引量: {len(new_id_map)}")
    print(f"  - 本次新增: {processed_count}")
    print(f"  - 缺失 MD : {missing_md_count}")
    print(f"  - 输出目录: {index_output_dir}")


def main():
    """主函数：直接调用 build_index，基于固定的 hidden_dir 工作"""
    build_index()


if __name__ == "__main__":
    main()
