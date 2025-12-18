#!/usr/bin/env python3
"""测试 MCP HTTP API 的脚本"""

import asyncio
import json
import sys
from datetime import datetime


# MCP JSON-RPC 请求格式
def create_mcp_request(method, params=None, id=1):
    """创建 MCP JSON-RPC 请求"""
    return {"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}}


async def test_mcp_http():
    """测试 MCP HTTP API"""
    import aiohttp

    base_url = "http://localhost:8080/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    print("=" * 60)
    print("TashanRAG MCP HTTP API 测试")
    print("=" * 60)
    print(f"服务器地址: {base_url}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    async with aiohttp.ClientSession() as session:
        # 1. 初始化连接
        print("1. 初始化连接...")
        init_request = create_mcp_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        )

        async with session.post(base_url, json=init_request, headers=headers) as resp:
            if resp.status == 200:
                init_result = await resp.json()
                print("   ✅ 初始化成功")
                if "result" in init_result:
                    server_info = init_result["result"].get("serverInfo", {})
                    print(f"   服务器: {server_info.get('name', 'Unknown')} {server_info.get('version', '')}")
            else:
                print(f"   ❌ 初始化失败: {resp.status}")
                text = await resp.text()
                print(f"   错误信息: {text}")
                return

        print()

        # 2. 列出可用工具
        print("2. 列出可用工具...")
        tools_request = create_mcp_request("tools/list")

        async with session.post(base_url, json=tools_request, headers=headers) as resp:
            if resp.status == 200:
                tools_result = await resp.json()
                if "result" in tools_result:
                    tools = tools_result["result"].get("tools", [])
                    print(f"   ✅ 找到 {len(tools)} 个工具:")
                    for tool in tools:
                        print(f"   - {tool.get('name', '')}: {tool.get('description', '')[:80]}...")
            else:
                print(f"   ❌ 获取工具列表失败: {resp.status}")
                return

        print()

        # 3. 调用 tashanrag_ask_paper_db 工具
        print("3. 调用 tashanrag_ask_paper_db 工具...")
        print("   问题: '细胞增殖如何影响集体行为？'")
        print("   (这可能需要一些时间来处理 PDF 和索引)")
        print()

        call_request = create_mcp_request(
            "tools/call",
            {
                "name": "tashanrag_ask_paper_db",
                "arguments": {
                    "question": "细胞增殖如何影响集体行为？",
                    "top_k": 3,
                    "max_concurrent_visits": 5,
                },
            },
            id=2,
        )

        # 显示进度
        print("   处理中...", end="", flush=True)

        start_time = datetime.now()

        async with session.post(base_url, json=call_request, headers=headers, timeout=300) as resp:
            elapsed = (datetime.now() - start_time).total_seconds()

            if resp.status == 200:
                print(f"\r   ✅ 请求完成 (耗时: {elapsed:.1f}秒)")
                call_result = await resp.json()

                if "result" in call_result:
                    result_content = call_result["result"].get("content", [])

                    if result_content:
                        # 第一个内容项通常是文本
                        if isinstance(result_content[0], dict) and "text" in result_content[0]:
                            response_data = result_content[0]["text"]

                            if isinstance(response_data, str):
                                try:
                                    # 尝试解析为 JSON
                                    data = json.loads(response_data)
                                except (json.JSONDecodeError, Exception):
                                    data = {"raw_response": response_data}
                            else:
                                data = response_data

                            print("\n4. 回答结果:")
                            print("-" * 40)

                            if data.get("status") == "error":
                                print("❌ 状态: 错误")
                                print(f"错误信息: {data.get('error_message', 'Unknown error')}")
                            else:
                                print("✅ 状态: 成功")

                                # 显示思考过程（如果有）
                                if data.get("thinking"):
                                    print("\n🧠 思考过程:")
                                    print(
                                        data["thinking"][:500] + "..."
                                        if len(data["thinking"]) > 500
                                        else data["thinking"]
                                    )

                                # 显示最终回答
                                if data.get("final_answer"):
                                    print("\n📢 最终回答:")
                                    answer = data["final_answer"]
                                    print(answer[:800] + "..." if len(answer) > 800 else answer)

                                # 显示引用
                                citations = data.get("citations_map", {})
                                if citations:
                                    print(f"\n📚 引用来源 ({len(citations)} 个):")
                                    for cid, item in list(citations.items())[:3]:  # 只显示前3个
                                        paper_id = item.get("paper_id", "Unknown")
                                        text = item.get("text", "")
                                        preview = text[:100] + "..." if len(text) > 100 else text
                                        print(f"   [^{cid}] {paper_id}: {preview}")

                                # 显示指标
                                metrics = data.get("metrics", {})
                                if metrics:
                                    print("\n📊 处理指标:")
                                    print(f"   - 处理论文数: {metrics.get('papers_processed', 0)}")
                                    print(f"   - 提取片段数: {metrics.get('snippets_count', 0)}")
                                    print(f"   - 总耗时: {metrics.get('total_time', 0)}秒")
                                    print(f"   - 内存峰值: {metrics.get('memory_peak_mb', 0)}MB")
                    else:
                        print("\n   ⚠️ 返回结果为空")
                else:
                    print("\n   ⚠️ 返回格式异常")
                    print(json.dumps(call_result, indent=2)[:500])
            else:
                print(f"\r   ❌ 请求失败: {resp.status}")
                error_text = await resp.text()
                print(f"   错误信息: {error_text[:300]}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    # 检查依赖
    try:
        import aiohttp  # noqa: F401
    except ImportError:
        print("请安装 aiohttp: pip install aiohttp")
        sys.exit(1)

    # 运行测试
    asyncio.run(test_mcp_http())
