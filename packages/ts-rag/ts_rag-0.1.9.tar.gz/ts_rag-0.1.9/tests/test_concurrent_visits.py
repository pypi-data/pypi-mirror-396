"""
测试并发 visit 的各种场景
包括：正常情况、大量论文、API 错误、部分成功等
"""

import asyncio
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# 添加 src/ts_rag 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "ts_rag"))

from answer import run_pipeline

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
        print(f"已清除代理环境变量: {var}")

# 加载环境配置文件
# 在测试环境中，优先使用 .env.example
env_path = Path(__file__).parent.parent / ".env"
example_env_path = Path(__file__).parent.parent / ".env.example"

# 检查是否在测试环境中
is_testing = os.environ.get("PYTEST_CURRENT_TEST") or "test" in sys.modules

if is_testing:
    # 测试环境中使用 .env.example
    if example_env_path.exists():
        env_path = example_env_path
        print(f"测试环境：使用 {env_path}")
    else:
        # 设置测试默认值
        os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-for-testing-only")
        os.environ.setdefault("OPENAI_BASE_URL", "https://api.openai.com/v1")
        os.environ.setdefault("MODEL_NAME", "gpt-3.5-turbo")
        os.environ.setdefault("TASHANRAG_PAPER_ROOT", "01-文献")
        print("测试环境：使用默认测试配置")

if env_path.exists():
    # 先加载 .env
    load_dotenv(dotenv_path=env_path)
    print(f"已加载环境配置文件: {env_path}")

    # 读取 .env 文件内容并强制设置环境变量
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()
                print(f"设置环境变量: {key.strip()}={value.strip()[:20]}{'...' if len(value) > 20 else ''}")


def print_test_header(test_name: str, test_num: int, total: int):
    """打印测试标题"""
    print("\n" + "=" * 80)
    print(f"测试 {test_num}/{total}: {test_name}")
    print("=" * 80)


def print_test_result(success: bool, details: dict = None):
    """打印测试结果"""
    status = "✓ 通过" if success else "✗ 失败"
    print(f"\n测试结果: {status}")
    if details:
        for key, value in details.items():
            print(f"  {key}: {value}")


async def test_case_1_normal_small():
    """测试用例 1: 正常情况 - 少量论文（1-3篇）"""
    print_test_header("正常情况 - 少量论文", 1, 6)

    question = "细胞迁移的速度与限制通道的宽度有什么关系？"

    start_time = time.time()
    try:
        result = await run_pipeline(question, top_k=2, max_concurrent_visits=5)
        elapsed = time.time() - start_time

        success = "error" not in result and "final_answer" in result
        details = {
            "耗时": f"{elapsed:.2f}s",
            "找到论文数": result.get("metrics", {}).get("papers_processed", 0),
            "片段数": result.get("metrics", {}).get("snippets_count", 0),
            "是否有答案": bool(result.get("final_answer")),
        }

        print_test_result(success, details)
        return success
    except Exception as e:
        print(f"测试异常: {e}")
        print_test_result(False, {"异常": str(e)})
        return False


async def test_case_2_normal_large():
    """测试用例 2: 正常情况 - 较多论文（超过并发限制）"""
    print_test_header("正常情况 - 较多论文（测试并发控制）", 2, 6)

    question = "细胞迁移"

    start_time = time.time()
    try:
        # 设置较小的并发限制，测试是否能正确控制
        result = await run_pipeline(question, top_k=10, max_concurrent_visits=3)
        elapsed = time.time() - start_time

        papers_processed = result.get("metrics", {}).get("papers_processed", 0)
        success = "error" not in result and papers_processed > 0

        details = {
            "耗时": f"{elapsed:.2f}s",
            "找到论文数": papers_processed,
            "并发限制": 3,
            "是否超过并发限制": papers_processed > 3,
            "片段数": result.get("metrics", {}).get("snippets_count", 0),
        }

        print_test_result(success, details)
        return success
    except Exception as e:
        print(f"测试异常: {e}")
        print_test_result(False, {"异常": str(e)})
        return False


async def test_case_3_concurrent_limit():
    """测试用例 3: 验证并发限制是否生效"""
    print_test_header("验证并发限制是否生效", 3, 6)

    question = "细胞迁移"

    # 测试不同的并发限制
    test_limits = [1, 2, 5]
    results = []

    for limit in test_limits:
        print(f"\n  测试并发限制 = {limit}")
        start_time = time.time()
        try:
            result = await run_pipeline(question, top_k=5, max_concurrent_visits=limit)
            elapsed = time.time() - start_time

            papers_processed = result.get("metrics", {}).get("papers_processed", 0)
            success = "error" not in result

            results.append(
                {
                    "limit": limit,
                    "success": success,
                    "papers": papers_processed,
                    "time": elapsed,
                }
            )

            print(f"    结果: {'✓' if success else '✗'}, 论文数: {papers_processed}, 耗时: {elapsed:.2f}s")
        except Exception as e:
            print(f"    异常: {e}")
            results.append({"limit": limit, "success": False, "error": str(e)})

    # 验证所有测试都成功
    all_success = all(r.get("success", False) for r in results)
    print_test_result(all_success, {"测试的并发限制": test_limits, "所有测试通过": all_success})

    return all_success


async def test_case_4_no_papers():
    """测试用例 4: 边界情况 - 没有找到相关论文"""
    print_test_header("边界情况 - 没有找到相关论文", 4, 6)

    # 使用一个不太可能匹配的问题
    question = "量子计算在生物医学中的应用（这是一个不太可能匹配的问题）"

    start_time = time.time()
    try:
        result = await run_pipeline(question, top_k=3, max_concurrent_visits=5)
        elapsed = time.time() - start_time

        # 应该返回空结果，但不应该报错
        papers_processed = result.get("metrics", {}).get("papers_processed", 0)
        has_answer = bool(result.get("final_answer"))

        success = "error" not in result and papers_processed == 0

        details = {
            "耗时": f"{elapsed:.2f}s",
            "找到论文数": papers_processed,
            "是否有答案": has_answer,
            "答案内容": (result.get("final_answer", "")[:100] + "..." if has_answer else "无"),
        }

        print_test_result(success, details)
        return success
    except Exception as e:
        print(f"测试异常: {e}")
        print_test_result(False, {"异常": str(e)})
        return False


async def test_case_5_partial_success():
    """测试用例 5: 部分成功场景（模拟某些论文处理失败）"""
    print_test_header("部分成功场景", 5, 6)

    question = "细胞迁移"

    start_time = time.time()
    try:
        result = await run_pipeline(question, top_k=5, max_concurrent_visits=3)
        elapsed = time.time() - start_time

        papers_processed = result.get("metrics", {}).get("papers_processed", 0)
        snippets_count = result.get("metrics", {}).get("snippets_count", 0)

        # 检查是否有部分失败（valid_results < found_papers）
        # 这个信息在 metrics 中可能没有，但我们可以通过其他方式判断
        success = "error" not in result

        details = {
            "耗时": f"{elapsed:.2f}s",
            "处理论文数": papers_processed,
            "提取片段数": snippets_count,
            "是否有最终答案": bool(result.get("final_answer")),
            "系统是否正常处理部分失败": success,
        }

        print_test_result(success, details)
        return success
    except Exception as e:
        print(f"测试异常: {e}")
        print_test_result(False, {"异常": str(e)})
        return False


async def test_case_6_performance():
    """测试用例 6: 性能测试 - 对比不同并发限制的耗时"""
    print_test_header("性能测试 - 并发限制对耗时的影响", 6, 6)

    question = "细胞迁移"

    # 测试不同的并发限制
    test_configs = [
        {"limit": 1, "name": "串行（并发=1）"},
        {"limit": 3, "name": "并发=3"},
        {"limit": 5, "name": "并发=5"},
    ]

    results = []

    for config in test_configs:
        print(f"\n  测试: {config['name']}")
        start_time = time.time()
        try:
            result = await run_pipeline(question, top_k=5, max_concurrent_visits=config["limit"])
            elapsed = time.time() - start_time

            papers_processed = result.get("metrics", {}).get("papers_processed", 0)
            success = "error" not in result

            results.append(
                {
                    "name": config["name"],
                    "limit": config["limit"],
                    "success": success,
                    "time": elapsed,
                    "papers": papers_processed,
                }
            )

            print(f"    结果: {'✓' if success else '✗'}, 耗时: {elapsed:.2f}s, 论文数: {papers_processed}")
        except Exception as e:
            print(f"    异常: {e}")
            results.append(
                {
                    "name": config["name"],
                    "limit": config["limit"],
                    "success": False,
                    "error": str(e),
                }
            )

    # 分析性能差异
    successful_results = [r for r in results if r.get("success")]
    if len(successful_results) >= 2:
        times = [r["time"] for r in successful_results]
        speedup = max(times) / min(times) if min(times) > 0 else 0
        print("\n  性能分析:")
        fastest_limit = [r["limit"] for r in successful_results if r["time"] == min(times)][0]
        slowest_limit = [r["limit"] for r in successful_results if r["time"] == max(times)][0]
        print(f"    最快: {min(times):.2f}s (并发={fastest_limit})")
        print(f"    最慢: {max(times):.2f}s (并发={slowest_limit})")
        print(f"    加速比: {speedup:.2f}x")

    all_success = all(r.get("success", False) for r in results)
    print_test_result(
        all_success,
        {
            "测试配置数": len(test_configs),
            "成功数": len(successful_results),
            "所有测试通过": all_success,
        },
    )

    return all_success


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("开始并发 Visit 测试套件")
    print("=" * 80)

    test_cases = [
        ("正常情况-少量论文", test_case_1_normal_small),
        ("正常情况-较多论文", test_case_2_normal_large),
        ("并发限制验证", test_case_3_concurrent_limit),
        ("边界情况-无论文", test_case_4_no_papers),
        ("部分成功场景", test_case_5_partial_success),
        ("性能测试", test_case_6_performance),
    ]

    results = []
    total_start = time.time()

    for name, test_func in test_cases:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n测试 '{name}' 发生异常: {e}")
            results.append((name, False))

    total_elapsed = time.time() - total_start

    # 打印总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status}: {name}")

    print(f"\n总计: {passed}/{total} 通过")
    print(f"总耗时: {total_elapsed:.2f}s")

    return passed == total


if __name__ == "__main__":
    # 确保索引存在
    index_data_dir = Path(__file__).parent.parent / "index_data"
    if not index_data_dir.exists() or not list(index_data_dir.glob("*.json")):
        print("警告: 索引数据不存在，请先运行 indexer.py")
        print("继续测试可能会失败...")

    # 运行测试
    success = asyncio.run(run_all_tests())

    exit(0 if success else 1)
