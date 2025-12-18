import os
import re
import statistics
from pathlib import Path

import fitz  # PyMuPDF


class PDFToMarkdownParser:
    def __init__(self, filepath, output_dir):
        self.filepath = Path(filepath)
        self.output_dir = Path(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

        self.doc = fitz.open(self.filepath)
        self.body_fontsize = self._analyze_global_body_fontsize()

        # === 关键词分级 ===

        # 1. 锚点关键词 (Anchor Keywords)
        # 作用：如果矢量框包含这些词，说明该框是“正文容器”（如摘要框、页面边框），框内所有内容保留。
        self.anchor_keywords = {
            "abstract",
            "introduction",
            "background",
            "related work",
            "preface",
            "acknowledgments",
            "author contributions",
            "declaration",
            "conflict of interest",
            "data availability",
            "references",
            "bibliography",
            "摘要",
            "前言",
            "引言",
            "绪论",
            "致谢",
            "参考文献",
        }

        # 2. 豁免关键词 (Immune Keywords)
        # 作用：包含锚点词 + 图表常用词。
        # 如果Block包含这些词，它自己会被保留（作为标题），但不会让整个矢量框变安全。
        self.immune_keywords = self.anchor_keywords.union(
            {
                "results",
                "analysis",
                "discussion",
                "conclusion",
                "summary",
                "method",
                "methodology",
                "experiments",
                "evaluation",
                "findings",
                "outcomes",
                "implementation",
                "figure",
                "fig.",
                "table",
                "chart",
                "scheme",
                "结果",
                "分析",
                "讨论",
                "结论",
                "总结",
                "方法",
                "实验",
                "图",
                "表",
            }
        )

        # 3. 基础保留关键词 (用于 Title/Body 判定)
        self.keep_keywords = self.immune_keywords.union(
            {
                "overview",
                "prologue",
                "materials and methods",
                "experimental procedures",
                "interpretation",
                "concluding remarks",
                "future work",
                "works cited",
                "literature cited",
                "appendix",
                "appendices",
                "supplementary",
                "supplementary information",
                "supporting information",
                "funding",
                "abbreviations",
                "内容摘要",
                "研究方法",
                "材料与方法",
                "实验设计",
                "研究结果",
                "实验结果",
                "局限性",
                "结语",
                "未来展望",
                "参考书目",
                "附录",
                "附件",
                "鸣谢",
                "利益冲突",
                "目录",
                "图表索引",
            }
        )

    # ================= 矢量图检测相关方法 =================
    def _is_background_or_full_page(self, rect, page_width, page_height):
        if rect.width > page_width * 0.95 and rect.height > page_height * 0.95:
            return True
        if rect.get_area() < 1.0:
            return True
        return False

    def _merge_nearby_rects(self, rects, distance_threshold=15):
        if not rects:
            return []
        rects.sort(key=lambda r: r.y0)
        merged = []
        curr = rects[0]
        for i in range(1, len(rects)):
            next_rect = rects[i]
            v_gap = max(0, next_rect.y0 - curr.y1)
            min(curr.x1, next_rect.x1) - max(curr.x0, next_rect.x0)
            if curr.x1 < next_rect.x0:
                h_gap = next_rect.x0 - curr.x1
            elif next_rect.x1 < curr.x0:
                h_gap = curr.x0 - next_rect.x1
            else:
                h_gap = 0
            if v_gap < distance_threshold and h_gap < distance_threshold:
                curr.x0 = min(curr.x0, next_rect.x0)
                curr.y0 = min(curr.y0, next_rect.y0)
                curr.x1 = max(curr.x1, next_rect.x1)
                curr.y1 = max(curr.y1, next_rect.y1)
            else:
                merged.append(curr)
                curr = next_rect
        merged.append(curr)
        if len(merged) < len(rects):
            return self._merge_nearby_rects(merged, distance_threshold)
        return merged

    def _get_page_vector_rects(self, page):
        W, H = page.rect.width, page.rect.height
        drawings = page.get_drawings()
        raw_rects = []
        for d in drawings:
            r = d["rect"]
            if self._is_background_or_full_page(r, W, H):
                continue
            raw_rects.append(r)
        vector_regions = self._merge_nearby_rects(raw_rects, distance_threshold=15.0)
        final_regions = [r for r in vector_regions if not self._is_background_or_full_page(r, W, H)]
        return final_regions

    def _analyze_global_body_fontsize(self):
        sizes = []
        for page in self.doc[:3]:
            try:
                blocks = page.get_text("dict")["blocks"]
                for b in blocks:
                    if "lines" not in b:
                        continue
                    for line in b["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if len(text) > 3 and re.search(r"[a-zA-Z\u4e00-\u9fa5]", text):
                                sizes.append(round(span["size"]))
            except Exception:
                pass
        return statistics.mode(sizes) if sizes else 10.0

    def _get_block_style_from_cache(self, page_spans, bbox):
        size_counts = {}
        total_text_len = 0
        bold_text_len = 0
        bx0, by0, bx1, by1 = bbox
        for s in page_spans:
            sx = (s["bbox"][0] + s["bbox"][2]) / 2
            sy = (s["bbox"][1] + s["bbox"][3]) / 2
            if bx0 <= sx <= bx1 and by0 <= sy <= by1:
                text = s["text"].strip()
                if not text:
                    continue
                text_len = len(text)
                sz = round(s["size"])
                size_counts[sz] = size_counts.get(sz, 0) + text_len
                font_name = s["font"].lower()
                is_span_bold = (
                    "bold" in font_name
                    or "black" in font_name
                    or "medi" in font_name
                    or "semi" in font_name
                    or (s["flags"] & 16)
                )
                total_text_len += text_len
                if is_span_bold:
                    bold_text_len += text_len
        if not size_counts or total_text_len == 0:
            return 0, False
        repr_size = max(size_counts, key=size_counts.get)
        bold_ratio = bold_text_len / total_text_len
        is_majority_bold = bold_ratio > 0.6
        return repr_size, is_majority_bold

    def _is_header_footer(self, bbox, page_height, text):
        y_center = (bbox[1] + bbox[3]) / 2
        is_edge = (y_center < page_height * 0.08) or (y_center > page_height * 0.92)
        text_lower = text.lower()
        if is_edge:
            noise_kws = [
                "arxiv",
                "doi:",
                "vol.",
                "issn",
                "downloaded",
                "manuscript",
                "submitted",
                "index",
            ]
            if any(k in text_lower for k in noise_kws):
                return True
            if re.match(r"^\s*-?\s*\d+(\s?/\s?\d+)?\s*-?\s*$", text):
                return True
            if len(text) < 30:
                return True
        if ("doi:" in text_lower or "https://" in text_lower) and len(text) < 100:
            return True
        return False

    def _apply_spatial_cut(self, raw_blocks, page_spans, page_num):
        if not raw_blocks:
            return []
        work_list = []
        for i, b in enumerate(raw_blocks):
            bbox = fitz.Rect(b[:4])
            text_preview = b[4].strip().replace("\n", "")[:10]
            work_list.append(
                {
                    "id": i,
                    "bbox": bbox,
                    "area": bbox.get_area(),
                    "text": b[4],
                    "short": text_preview,
                    "origin_data": b,
                    "is_deleted": False,
                }
            )
        work_list.sort(key=lambda x: x["area"])
        new_generated_blocks = []
        for i in range(len(work_list)):
            knife = work_list[i]
            if knife["is_deleted"]:
                continue
            for j in range(len(work_list)):
                if i == j:
                    continue
                victim = work_list[j]
                if victim["is_deleted"]:
                    continue
                if victim["area"] < knife["area"]:
                    continue
                intersection = knife["bbox"] & victim["bbox"]
                if intersection.is_empty:
                    continue
                overlap_ratio = intersection.get_area() / knife["area"]
                if overlap_ratio > 0.90:
                    knife_y0, knife_y1 = knife["bbox"].y0, knife["bbox"].y1
                    victim_rect = victim["bbox"]
                    victim_spans = []
                    for s in page_spans:
                        sx, sy = (s["bbox"][0] + s["bbox"][2]) / 2, (s["bbox"][1] + s["bbox"][3]) / 2
                        if victim_rect.contains(fitz.Point(sx, sy)):
                            victim_spans.append(s)
                    if not victim_spans:
                        continue
                    top_spans, bottom_spans = [], []
                    tolerance = 1.0
                    for s in victim_spans:
                        sy = (s["bbox"][1] + s["bbox"][3]) / 2
                        if sy < knife_y0 + tolerance:
                            top_spans.append(s)
                        elif sy > knife_y1 - tolerance:
                            bottom_spans.append(s)
                    if top_spans:
                        top_bbox = fitz.Rect(
                            min(s["bbox"][0] for s in top_spans),
                            min(s["bbox"][1] for s in top_spans),
                            max(s["bbox"][2] for s in top_spans),
                            max(s["bbox"][3] for s in top_spans),
                        )
                        sorted_top = sorted(top_spans, key=lambda x: (x["bbox"][1], x["bbox"][0]))
                        top_text = "".join([s["text"] for s in sorted_top])
                        new_generated_blocks.append(
                            (
                                top_bbox.x0,
                                top_bbox.y0,
                                top_bbox.x1,
                                top_bbox.y1,
                                top_text,
                                0,
                                0,
                            )
                        )
                    if bottom_spans:
                        bot_bbox = fitz.Rect(
                            min(s["bbox"][0] for s in bottom_spans),
                            min(s["bbox"][1] for s in bottom_spans),
                            max(s["bbox"][2] for s in bottom_spans),
                            max(s["bbox"][3] for s in bottom_spans),
                        )
                        sorted_bot = sorted(bottom_spans, key=lambda x: (x["bbox"][1], x["bbox"][0]))
                        bot_text = "".join([s["text"] for s in sorted_bot])
                        new_generated_blocks.append(
                            (
                                bot_bbox.x0,
                                bot_bbox.y0,
                                bot_bbox.x1,
                                bot_bbox.y1,
                                bot_text,
                                0,
                                0,
                            )
                        )
                    victim["is_deleted"] = True
        final_result = []
        for item in work_list:
            if not item["is_deleted"]:
                final_result.append(item["origin_data"])
        final_result.extend(new_generated_blocks)
        final_result.sort(key=lambda b: b[1])
        return final_result

    def _sort_blocks(self, blocks, page_width):
        mid_x = page_width / 2
        primary_flow = []
        secondary_flow = []
        for b in blocks:
            if b["bbox"][0] < mid_x:
                primary_flow.append(b)
            else:
                secondary_flow.append(b)
        primary_flow.sort(key=lambda b: b["bbox"][1])
        secondary_flow.sort(key=lambda b: b["bbox"][1])
        return primary_flow + secondary_flow

    def _semantic_merge(self, blocks):
        if not blocks:
            return []
        merged = []
        current = blocks[0]
        for next_b in blocks[1:]:
            gap = next_b["bbox"][1] - current["bbox"][3]
            ref_font_size = current.get("font_size", 10.0)
            if ref_font_size < 5:
                ref_font_size = 10.0
            same_role = current["role"] == next_b["role"]
            aligned_left = abs(current["bbox"][0] - next_b["bbox"][0]) < 20

            if current["role"] == "HEADER" or next_b["role"] == "HEADER":
                is_close = False
            elif current["role"] == "TITLE":
                is_close = gap < 10
            elif current["role"] == "FIGURE":
                is_close = gap < 10
            else:
                is_close = gap < (ref_font_size * 2.0)

            if same_role and aligned_left and is_close:
                txt_curr = current["text"].strip()
                txt_next = next_b["text"].strip()
                if txt_curr.endswith("-"):
                    new_text = txt_curr[:-1] + txt_next
                else:
                    new_text = txt_curr + " " + txt_next
                current["text"] = new_text
                current["bbox"] = (
                    min(current["bbox"][0], next_b["bbox"][0]),
                    min(current["bbox"][1], next_b["bbox"][1]),
                    max(current["bbox"][2], next_b["bbox"][2]),
                    max(current["bbox"][3], next_b["bbox"][3]),
                )
                current["font_size"] = max(current["font_size"], next_b["font_size"])
            else:
                merged.append(current)
                current = next_b
        merged.append(current)
        return merged

    def _clean_text(self, text):
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _check_title_features(self, text):
        clean_line = text.strip()
        if len(clean_line) > 150:
            return False, "Too long"
        unit_blacklist = [
            "Pa",
            "kPa",
            "MPa",
            "GPa",
            "m",
            "cm",
            "mm",
            "nm",
            "um",
            "km",
            "g",
            "kg",
            "mg",
            "s",
            "ms",
            "min",
            "h",
            "Hz",
            "kHz",
            "MHz",
            "V",
            "mV",
            "A",
            "mA",
            "deg",
            "°",
            "°C",
            "K",
            "%",
            "mol",
            "M",
        ]
        num_match = re.match(r"^(\d+)", clean_line)
        if num_match:
            rest_of_string = clean_line[len(num_match.group(1)) :]
            words = rest_of_string.strip().split()
            if words:
                first_word = words[0].strip(".,;)]}")
                if first_word in unit_blacklist:
                    return False, f"Unit detected: {first_word}"
        hierarchy_match = re.match(r"^([\d\.]+)\s+[A-Z]", clean_line)
        if hierarchy_match:
            numbering_part = hierarchy_match.group(1)
            parts = [p for p in numbering_part.split(".") if p.strip()]
            is_valid_numbering = True
            if not parts:
                is_valid_numbering = False
            for p in parts:
                if p.isdigit():
                    if int(p) > 100:
                        is_valid_numbering = False
                        break
            if is_valid_numbering:
                return True, "Regex match"
            else:
                return False, "Number too large"
        return False, "No match"

    def _is_strong_header(self, line):
        line = line.strip()
        if len(line) > 100:
            return False
        if re.search(r"^\d+\s+.*et\s+al", line, re.IGNORECASE):
            return True
        if re.search(r".*et\s+al.*\s+\d+\s*$", line, re.IGNORECASE):
            return True
        header_keywords = [
            "Proceedings of",
            "International",
            "Conference",
            "Astronomical Union",
            "Symposium",
            "Physical Review",
            "PRL",
            "Letters",
            "Week ending",
            "Manuscript",
            "Accepted",
            "Vol.",
            "No.",
            "pp.",
            "doi:",
            "ISSN",
            "ISBN",
        ]
        line_lower = line.lower()
        if any(k.lower() in line_lower for k in header_keywords):
            return True
        if re.search(r"第\s*\d+\s*[卷期]", line):
            return True
        if re.match(r"^\s*-?\s*\d+(\s?/\s?\d+)?\s*-?\s*$", line):
            return True
        return False

    def _split_compound_block(self, bbox, text):
        lines = text.split("\n")
        if not lines:
            return None
        total_lines = len(lines)
        block_h = bbox[3] - bbox[1]
        line_h = block_h / total_lines
        sub_blocks = []
        header_end_idx = 0
        if bbox[1] < 72:
            if self._is_strong_header(lines[0]):
                header_end_idx = 1
                for i in range(1, min(5, len(lines))):
                    next_line = lines[i].strip()
                    next_line_lower = next_line.lower()
                    next_line_clean = re.sub(r"^(\d+(\.\d+)*\.?)\s*", "", next_line_lower).strip()
                    if next_line_clean in self.immune_keywords:
                        break
                    is_all_caps = next_line.isupper() and len(next_line) < 100
                    has_date = re.search(
                        r"(January|February|March|April|May|June|July|August|September|October|November|December)",
                        next_line,
                        re.IGNORECASE,
                    )
                    is_week_ending = "week ending" in next_line.lower()
                    is_very_short = len(next_line) < 20
                    if is_all_caps or has_date or is_week_ending or is_very_short:
                        header_end_idx = i + 1
                    else:
                        break
        if header_end_idx > 0:
            header_text = "\n".join(lines[:header_end_idx])
            header_bbox = (
                bbox[0],
                bbox[1],
                bbox[2],
                bbox[1] + header_end_idx * line_h * 1.3,
            )
            sub_blocks.append({"bbox": header_bbox, "text": header_text, "force_role": "HEADER"})
        split_indices = []
        if header_end_idx > 0 and header_end_idx < len(lines):
            post_header_line = lines[header_end_idx].strip()
            if len(post_header_line) < 200 and not post_header_line.islower():
                split_indices.append(header_end_idx)
        terminators = (
            ".",
            "?",
            "!",
            ":",
            ";",
            "]",
            ")",
            "”",
            '"',
            "…",
            "。",
            "？",
            "！",
            "：",
            "；",
            "”",
            "’",
        )
        start_scan = header_end_idx
        if header_end_idx in split_indices:
            start_scan = header_end_idx + 1
        for i in range(start_scan, len(lines)):
            curr_line = lines[i].strip()
            if i > 0:
                prev_line = lines[i - 1].strip()
                if len(prev_line) > 5 and not prev_line.endswith(terminators):
                    continue

            is_regex, _ = self._check_title_features(curr_line)
            clean_kwd = re.sub(r"^(\d+(\.\d+)*\.?)\s*", "", curr_line.lower()).strip()
            if is_regex or (clean_kwd in self.immune_keywords):
                split_indices.append(i)

        split_indices = sorted(set(split_indices))
        if not sub_blocks and not split_indices:
            return None
        current_y = bbox[1] + (header_end_idx * line_h * 1.3) if header_end_idx > 0 else bbox[1]
        curr_line_pointer = header_end_idx
        for split_idx in split_indices:
            if split_idx > curr_line_pointer:
                body_text = "\n".join(lines[curr_line_pointer:split_idx])
                body_h = (split_idx - curr_line_pointer) * line_h
                body_bbox = (bbox[0], current_y, bbox[2], current_y + body_h)
                sub_blocks.append({"bbox": body_bbox, "text": body_text, "force_role": "BODY"})
                current_y += body_h
            title_text = lines[split_idx]
            title_h = line_h * 1.2
            title_bbox = (bbox[0], current_y, bbox[2], current_y + title_h)
            sub_blocks.append({"bbox": title_bbox, "text": title_text, "force_role": "TITLE"})
            current_y += title_h
            curr_line_pointer = split_idx + 1
        if curr_line_pointer < len(lines):
            tail_text = "\n".join(lines[curr_line_pointer:])
            tail_bbox = (bbox[0], current_y, bbox[2], bbox[3])
            sub_blocks.append({"bbox": tail_bbox, "text": tail_text, "force_role": "BODY"})
        return sub_blocks

    def _reconstruct_paragraphs_v2(self, block_text, block_bbox, page_spans):
        if not block_text or not page_spans:
            return block_text
        bx0, by0, bx1, by1 = block_bbox
        relevant_spans = []
        for s in page_spans:
            sx = (s["bbox"][0] + s["bbox"][2]) / 2
            sy = (s["bbox"][1] + s["bbox"][3]) / 2
            if bx0 <= sx <= bx1 and by0 <= sy <= by1:
                relevant_spans.append(s)
        if not relevant_spans:
            return block_text
        relevant_spans.sort(key=lambda s: (round(s["origin"][1], 1), s["bbox"][0]))
        lines = []
        current_line_spans = []
        last_y = -9999
        for s in relevant_spans:
            y = s["origin"][1]
            if abs(y - last_y) > 3:
                if current_line_spans:
                    l_x0 = min(sp["bbox"][0] for sp in current_line_spans)
                    l_x1 = max(sp["bbox"][2] for sp in current_line_spans)
                    l_text = "".join([sp["text"] for sp in current_line_spans])
                    lines.append({"x0": l_x0, "x1": l_x1, "text": l_text})
                current_line_spans = [s]
                last_y = y
            else:
                current_line_spans.append(s)
        if current_line_spans:
            l_x0 = min(sp["bbox"][0] for sp in current_line_spans)
            l_x1 = max(sp["bbox"][2] for sp in current_line_spans)
            l_text = "".join([sp["text"] for sp in current_line_spans])
            lines.append({"x0": l_x0, "x1": l_x1, "text": l_text})
        if not lines:
            return block_text
        all_x1 = [line["x1"] for line in lines]
        block_right_edge = max(all_x1)
        paragraphs = []
        current_para = []
        for i, line in enumerate(lines):
            text = line["text"].strip()
            if not text:
                continue
            is_new_para = False
            if i > 0:
                prev_line = lines[i - 1]
                gap_to_right = block_right_edge - prev_line["x1"]
                if gap_to_right > 15.0:
                    is_new_para = True
            if i > 0 and not is_new_para:
                prev_line = lines[i - 1]
                if line["x0"] - prev_line["x0"] > 10.0:
                    is_new_para = True
            if is_new_para and current_para:
                paragraphs.append(" ".join(current_para))
                current_para = [text]
            else:
                current_para.append(text)
        if current_para:
            paragraphs.append(" ".join(current_para))
        return "\n\n".join(paragraphs)

    def _smart_bridge(self, all_global_blocks):
        final_output = []
        pending_text = ""
        for block in all_global_blocks:
            role = block["role"]
            text = block["text"]
            if role == "FIGURE":
                continue
            if role == "TITLE":
                if pending_text:
                    final_output.append(pending_text)
                    pending_text = ""
                final_output.append(f"\n\n## {text}\n\n")
                continue
            if not pending_text:
                pending_text = text
                continue
            should_merge = False
            if len(pending_text) > 100:
                stripped_prev = pending_text.strip()
                if stripped_prev.endswith("-"):
                    pending_text = stripped_prev[:-1] + text
                    should_merge = True
                elif not stripped_prev.endswith((".", "!", "?", ":", ";", '"', "”")):
                    pending_text = stripped_prev + " " + text
                    should_merge = True
            if not should_merge:
                final_output.append(pending_text)
                pending_text = text
        if pending_text:
            final_output.append(pending_text)
        return "\n\n".join(final_output)

    def _is_valid_content(self, text):
        if not text:
            return False
        clean_lower = text.strip().lower()
        clean_lower_no_num = re.sub(r"^(\d+(\.\d+)*\.?)\s*", "", clean_lower).strip()
        if clean_lower_no_num in self.immune_keywords:
            return True
        if re.search(r"[\u4e00-\u9fa5]", text):
            return True
        clean_txt = re.sub(r"[\x00-\x1f\x7f]", "", text)
        letters = re.findall(r"[a-zA-Z]", clean_txt)
        words = clean_txt.strip().split()
        if len(letters) >= 6 and len(words) >= 2:
            return True
        return False

    def _is_valid_start_line(self, text):
        if re.search(r"[\u4e00-\u9fa5]", text):
            return True
        clean_text = re.sub(r"^#+\s*", "", text)
        words = re.findall(r"\b[a-zA-Z]{2,}\b", clean_text)
        if len(words) >= 3:
            return True
        return False

    def _final_content_cleaning(self, full_text):
        lines = full_text.split("\n")
        valid_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                valid_lines.append(line)
                continue
            if not stripped:
                valid_lines.append("")
                continue
            if self._is_valid_content(stripped):
                valid_lines.append(line)
        start_index = 0
        found_start = False
        for i, line in enumerate(valid_lines):
            if not line.strip():
                continue
            if self._is_valid_start_line(line):
                start_index = i
                found_start = True
                break
        if found_start:
            final_content_lines = valid_lines[start_index:]
        else:
            final_content_lines = valid_lines
        result = "\n".join(final_content_lines)
        result = re.sub(r"\n{3,}", "\n\n", result)
        return result

    def _merge_scattered_short_lines(self, text):
        lines = text.split("\n")
        processed_lines = []
        buffer = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if buffer:
                    if len(buffer) >= 4:
                        processed_lines.append(" ".join(buffer))
                    else:
                        processed_lines.extend(buffer)
                    buffer = []
                processed_lines.append(line)
                continue
            is_hash_header = stripped.startswith("#")
            is_num_header = re.match(r"^\d", stripped) is not None
            clean_lower = re.sub(r"^[\d\.\s#]+", "", stripped.lower()).strip()
            is_keyword_header = False
            for kw in self.keep_keywords:
                if clean_lower.startswith(kw):
                    is_keyword_header = True
                    break
            should_protect = is_hash_header or is_num_header or is_keyword_header
            word_count = len(stripped.split())
            if should_protect:
                if buffer:
                    if len(buffer) >= 4:
                        processed_lines.append(" ".join(buffer))
                    else:
                        processed_lines.extend(buffer)
                    buffer = []
                processed_lines.append(line)
            elif word_count <= 8:
                buffer.append(stripped)
            else:
                if buffer:
                    if len(buffer) >= 4:
                        processed_lines.append(" ".join(buffer))
                    else:
                        processed_lines.extend(buffer)
                    buffer = []
                processed_lines.append(line)
        if buffer:
            if len(buffer) >= 4:
                processed_lines.append(" ".join(buffer))
            else:
                processed_lines.extend(buffer)
        return "\n".join(processed_lines)

    def run(self):
        all_global_blocks = []

        for i, page in enumerate(self.doc):
            W = page.rect.width
            H = page.rect.height
            mid_x = W / 2

            # 1. 提取位图
            valid_image_rects = []
            try:
                images = page.get_images()
                for img in images:
                    img_rects = page.get_image_rects(img[0])
                    for r in img_rects:
                        if r.get_area() < (W * H * 0.8):
                            valid_image_rects.append(r)
            except Exception:
                pass

            # 2. 提取矢量图
            vector_rects = self._get_page_vector_rects(page)

            page_spans = []
            try:
                full_dict = page.get_text("dict")
                for b in full_dict["blocks"]:
                    if "lines" not in b:
                        continue
                    for line in b["lines"]:
                        page_spans.extend(line["spans"])
            except Exception:
                pass

            raw_blocks = page.get_text("blocks")
            clean_blocks = self._apply_spatial_cut(raw_blocks, page_spans, i + 1)

            # === Phase 1: 确定安全区 (Anchoring) ===
            safe_vector_indices = set()
            if i <= 1:
                # 前两页豁免
                for idx in range(len(vector_rects)):
                    safe_vector_indices.add(idx)
            else:
                for b in clean_blocks:
                    text = b[4].strip()
                    if not text:
                        continue
                    bbox = b[:4]
                    block_rect = fitz.Rect(bbox)
                    text_lower = text.lower()

                    # 使用【锚点关键词】来判定区域安全
                    is_anchor = False
                    for kw in self.anchor_keywords:
                        if kw in text_lower:
                            is_anchor = True
                            break

                    if is_anchor:
                        for idx, v_rect in enumerate(vector_rects):
                            if v_rect.intersects(block_rect) or v_rect.contains(
                                fitz.Point((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
                            ):
                                safe_vector_indices.add(idx)

            # Layout Analysis
            right_side_blocks_count = 0
            has_tall_right_block = False
            for _, b in enumerate(clean_blocks):
                bx0, by0, bx1, by1 = b[:4]
                b_height = by1 - by0
                is_on_right = bx0 > mid_x - 20
                if is_on_right:
                    right_side_blocks_count += 1
                    if b_height > H * 0.1:
                        has_tall_right_block = True
            is_single_column_layout = not (right_side_blocks_count >= 1 and has_tall_right_block)
            if is_single_column_layout:
                single_column_blocks = []
            else:
                top_blocks = []
                left_blocks = []
                right_blocks = []
                bottom_blocks = []

            # === Phase 2: 过滤垃圾 ===
            for b in clean_blocks:
                if b[6] != 0:
                    continue
                text = b[4].strip()
                if not text:
                    continue
                bbox = b[:4]
                block_rect = fitz.Rect(bbox)

                is_figure_block = False

                # A. 位图检查
                for img_rect in valid_image_rects:
                    if img_rect.intersects(block_rect):
                        if (img_rect & block_rect).get_area() / block_rect.get_area() > 0.90:
                            is_figure_block = True
                            break

                # B. 矢量图检查 (使用安全区逻辑)
                if not is_figure_block:
                    in_safe_zone = False
                    in_unsafe_zone = False

                    for idx, vec_rect in enumerate(vector_rects):
                        if vec_rect.intersects(block_rect):
                            if idx in safe_vector_indices:
                                in_safe_zone = True
                            else:
                                in_unsafe_zone = True

                    # 只有落在【不安全区】且没沾到【安全区】边的，才会被审判
                    if in_unsafe_zone and not in_safe_zone:
                        # 最后的豁免权：长句子 或 【豁免关键词】(自身是标题)
                        is_immune_self = False
                        word_count = len(text.split())
                        if word_count > 10:
                            is_immune_self = True
                        else:
                            for kw in self.immune_keywords:
                                if kw in text.lower():
                                    is_immune_self = True
                                    break

                        if not is_immune_self:
                            is_figure_block = True

                if self._is_header_footer(bbox, H, text):
                    continue

                if is_figure_block:
                    items_to_process = [{"bbox": bbox, "text": text, "force_role": "FIGURE"}]
                else:
                    sub_blocks_data = self._split_compound_block(bbox, text)
                    items_to_process = (
                        sub_blocks_data if sub_blocks_data else [{"bbox": bbox, "text": text, "force_role": None}]
                    )

                for item in items_to_process:
                    t_text = item["text"]
                    t_bbox = item["bbox"]
                    forced_role = item["force_role"]

                    role = "BODY"
                    font_size = self.body_fontsize

                    if forced_role == "FIGURE":
                        role = "FIGURE"
                        font_size = 0
                    elif forced_role == "HEADER":
                        role = "HEADER"
                        font_size = 8.0
                    elif forced_role == "TITLE":
                        role = "TITLE"
                        font_size = self.body_fontsize + 2.0
                    elif forced_role == "BODY":
                        role = "BODY"
                    else:
                        clean_kwd = re.sub(r"^(\d+(\.\d+)*\.?)\s*", "", t_text.lower()).strip()
                        if clean_kwd in self.immune_keywords:
                            role = "TITLE"
                            font_size = self.body_fontsize + 2.0
                        elif len(t_text) < 150:
                            is_regex_title, _ = self._check_title_features(t_text)
                            if is_regex_title:
                                role = "TITLE"
                                font_size = self.body_fontsize + 2.0
                            else:
                                real_fs, is_majority_bold = self._get_block_style_from_cache(page_spans, t_bbox)
                                font_size = real_fs
                                is_big = real_fs > (self.body_fontsize + 1.0)
                                is_bold_title = (
                                    is_majority_bold
                                    and len(t_text) < 100
                                    and real_fs >= self.body_fontsize
                                    and "doi" not in t_text.lower()
                                )
                                if is_big or is_bold_title:
                                    role = "TITLE"

                    final_block = {
                        "bbox": t_bbox,
                        "text": t_text,
                        "role": role,
                        "font_size": font_size,
                    }

                    if is_single_column_layout:
                        single_column_blocks.append(final_block)
                    else:
                        bx0, bx1 = t_bbox[0], t_bbox[2]
                        b_width = bx1 - bx0
                        b_center = (bx0 + bx1) / 2
                        if b_width > W * 0.6:
                            is_true_bottom = False
                            if t_bbox[1] > H * 0.85:
                                has_block_below = False
                                current_bottom = t_bbox[3]
                                for check_b in clean_blocks:
                                    if check_b[1] > current_bottom + 5:
                                        has_block_below = True
                                        break
                                if not has_block_below:
                                    is_true_bottom = True
                            if is_true_bottom:
                                bottom_blocks.append(final_block)
                            else:
                                top_blocks.append(final_block)
                        elif b_center < mid_x:
                            left_blocks.append(final_block)
                        else:
                            right_blocks.append(final_block)

            if is_single_column_layout:
                single_column_blocks.sort(key=lambda b: b["bbox"][1])
                final_blocks = self._semantic_merge(single_column_blocks)
            else:
                top_blocks.sort(key=lambda b: b["bbox"][1])
                left_blocks.sort(key=lambda b: b["bbox"][1])
                right_blocks.sort(key=lambda b: b["bbox"][1])
                bottom_blocks.sort(key=lambda b: b["bbox"][1])
                merged_top = self._semantic_merge(top_blocks)
                merged_left = self._semantic_merge(left_blocks)
                merged_right = self._semantic_merge(right_blocks)
                merged_bottom = self._semantic_merge(bottom_blocks)
                if not merged_right:
                    main_flow = merged_top + merged_left
                    main_flow.sort(key=lambda b: b["bbox"][1])
                else:
                    main_flow = merged_top + merged_left + merged_right
                final_blocks = main_flow + merged_bottom

            for block in final_blocks:
                if block["role"] == "HEADER":
                    continue
                clean_txt = block["text"]
                if block["role"] == "BODY":
                    clean_txt = self._reconstruct_paragraphs_v2(clean_txt, block["bbox"], page_spans)
                    clean_txt = re.sub(r"[ \t]+", " ", clean_txt).replace(" \n\n ", "\n\n")
                else:
                    clean_txt = self._clean_text(clean_txt)
                all_global_blocks.append({"role": block["role"], "text": clean_txt})

        full_md_text = self._smart_bridge(all_global_blocks)
        final_clean_md = self._final_content_cleaning(full_md_text)
        final_clean_md = self._merge_scattered_short_lines(final_clean_md)

        md_out = self.output_dir / f"{self.filepath.stem}.md"

        with open(md_out, "w", encoding="utf-8") as f:
            f.write(final_clean_md)

        print(f"✅ 处理完成: {md_out}")


if __name__ == "__main__":
    BASE_DIR = Path("G:/deepresearch/contextgem-main/TashanRAG/01-文献")
    OUTPUT_DIR = BASE_DIR / "debug_output"
    files = [Path(r"G:\deepresearch\contextgem-main\TashanRAG\paperfindtest\folder_2_1\folder_3_1\2511.00147v1.pdf")]
    if files[0].exists():
        parser = PDFToMarkdownParser(files[0], OUTPUT_DIR)
        parser.run()
    else:
        print("File not found.")
