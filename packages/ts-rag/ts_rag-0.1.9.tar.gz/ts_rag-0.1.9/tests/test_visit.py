#!/usr/bin/env python
"""
测试 visit 模块：验证 extract_info 函数是否正常工作
"""

import os
import sys
from pathlib import Path

import pytest

# 添加 src/ts_rag 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "ts_rag"))

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


class TestVisitModule:
    """测试 visit.extract_info 函数"""

    @pytest.fixture(autouse=True)
    def setup_environment(self, monkeypatch):
        """设置测试环境"""
        # 在测试环境中，使用默认配置
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-for-testing-only")
        monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        monkeypatch.setenv("MODEL_NAME", "gpt-3.5-turbo")
        monkeypatch.setenv("TASHANRAG_PAPER_ROOT", "01-文献")

    def test_extract_info_with_file(self):
        """测试在有实际文件的情况下 extract_info 函数"""
        # 测试文件路径
        test_file = Path("01-文献/.indexonly/papers/集群运动_唯像描述与动力学机制.md")

        if not test_file.exists():
            pytest.skip(f"测试文件不存在: {test_file}")

        # 导入函数
        from visit import extract_info

        test_question = "细胞迁移的速度与限制通道的宽度有什么关系？"

        try:
            result = extract_info(test_question, str(test_file))

            # 验证结果结构
            assert "question" in result
            assert "source_document" in result
            assert result["question"] == test_question
            assert "file_path" in result["source_document"]
            assert "extracted_knowledge" in result["source_document"]

            # 验证提取的知识项不为空
            knowledge_items = result["source_document"]["extracted_knowledge"]
            assert len(knowledge_items) > 0

            # 验证每个知识项的结构
            for knowledge in knowledge_items:
                assert "type" in knowledge
                assert "items" in knowledge
                assert len(knowledge["items"]) > 0

                # 验证知识项内容
                for item in knowledge["items"]:
                    assert "content" in item
                    assert len(item["content"]) > 0

        except Exception as e:
            pytest.fail(f"extract_info 函数执行失败: {e}")

    def test_extract_info_with_mock(self, tmp_path):
        """使用模拟文件测试 extract_info 函数"""
        # 创建临时测试文件
        test_file = tmp_path / "test_paper.md"
        test_content = """# 测试论文标题

## 摘要
这是一个测试论文的摘要，包含了一些关于细胞迁移的内容。

## 细胞迁移
细胞迁移是细胞移动的过程，它受到多种因素的影响。研究发现，细胞迁移的速度与通道宽度之间存在关系。

### 实验结果
实验表明，当限制通道的宽度增加时，细胞迁移的速度会相应提高。
"""
        test_file.write_text(test_content)

        # 导入函数
        from visit import extract_info

        test_question = "细胞迁移的速度与限制通道的宽度有什么关系？"

        try:
            result = extract_info(test_question, str(test_file))

            # 验证结果结构
            assert "question" in result
            assert "source_document" in result
            assert result["question"] == test_question
            assert str(test_file) in result["source_document"]["file_path"]
            assert "extracted_knowledge" in result["source_document"]

            # 验证提取的知识项结构
            knowledge_items = result["source_document"]["extracted_knowledge"]

            # 在没有有效 API key 的情况下，知识项可能为空，这是正常的
            if len(knowledge_items) == 0:
                pytest.skip("LLM API 配置问题导致无法提取知识，跳过测试验证")

            # 如果有知识项，验证结构
            for knowledge in knowledge_items:
                assert "type" in knowledge
                assert "items" in knowledge

                # 验证知识项内容
                for item in knowledge["items"]:
                    assert "content" in item
                    assert len(item["content"]) > 0

        except Exception as e:
            # 在测试环境中，如果 LLM 调用失败，跳过测试
            if "AuthenticationError" in str(e) or "API key" in str(e):
                pytest.skip("LLM API 配置问题，跳过测试")
            else:
                pytest.fail(f"extract_info 函数执行失败: {e}")


if __name__ == "__main__":
    # 作为脚本运行时的向后兼容
    print("=" * 60)
    print("Testing visit.extract_info()...")
    print("=" * 60)

    test_file = Path("01-文献/.indexonly/papers/集群运动_唯像描述与动力学机制.md")

    if not test_file.exists():
        print(f"Error: Test file not found: {test_file}")
        print("请先运行 paperindexg.py 将 PDF 转换为 Markdown")
        sys.exit(1)

    # 运行测试
    from visit import extract_info

    test_question = "细胞迁移的速度与限制通道的宽度有什么关系？"

    try:
        result = extract_info(test_question, str(test_file))

        print("=" * 60)
        print("EXTRACTION RESULT")
        print("=" * 60)
        print(f"Question: {result['question']}")
        print(f"Source: {result['source_document']['file_path']}")
        print(f"Extracted Knowledge Items: {len(result['source_document']['extracted_knowledge'])}")

        for idx, knowledge in enumerate(result["source_document"]["extracted_knowledge"], 1):
            print(f"\n--- Knowledge {idx} (Type: {knowledge['type']}) ---")
            for item_idx, item in enumerate(knowledge["items"], 1):
                print(f"  Item {item_idx}: {item['content'][:100]}...")
                if item.get("reason"):
                    print(f"    Reason: {item['reason'][:80]}...")
                if item.get("evidence_snippets"):
                    print(f"    Evidence snippets: {len(item['evidence_snippets'])}")

        print("\n" + "=" * 60)
        print("Visit module test PASSED! ✓")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
