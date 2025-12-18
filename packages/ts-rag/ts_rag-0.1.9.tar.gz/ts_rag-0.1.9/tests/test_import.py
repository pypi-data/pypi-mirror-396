#!/usr/bin/env python
"""
快速测试脚本：验证 tashan_core 重命名后所有导入是否正常
"""

import os
import sys

# 添加 src/ts_rag 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "ts_rag"))

print("=" * 60)
print("Testing tashan_core imports...")
print("=" * 60)

try:
    import tashan_core as cg

    print("✓ tashan_core imported successfully")

    # 测试核心类
    assert hasattr(cg, "Document"), "Document not found"
    print("✓ Document class available")

    assert hasattr(cg, "ListConcept"), "ListConcept not found"
    print("✓ ListConcept class available")

    assert hasattr(cg, "StringConcept"), "StringConcept not found"
    print("✓ StringConcept class available")

    assert hasattr(cg, "DocumentLLM"), "DocumentLLM not found"
    print("✓ DocumentLLM class available")

    # 测试创建实例（不调用 LLM）
    print("\n" + "=" * 60)
    print("Testing basic instantiation (no LLM calls)...")
    print("=" * 60)

    doc = cg.Document(raw_text="This is a test document.")
    print("✓ Document created successfully")

    concept = cg.ListConcept(
        name="test",
        description="Test concept",
        add_references=False,
        add_justifications=False,
    )
    print("✓ ListConcept created successfully")

    print("\n" + "=" * 60)
    print("All basic tests passed! ✓")
    print("=" * 60)

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
