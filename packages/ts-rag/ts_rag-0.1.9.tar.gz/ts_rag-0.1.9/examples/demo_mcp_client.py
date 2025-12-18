#!/usr/bin/env python3
"""使用 FastMCP 客户端测试 HTTP 模式"""

import asyncio
import json
import sys
from datetime import datetime


async def test_with_fastmcp_client():
    """使用 FastMCP 客户端测试"""
    print("=" * 60)
    print("FastMCP 客户端 HTTP 模式测试")
    print("=" * 60)

    try:
        from fastmcp import Client
    except ImportError:
        print("错误: fastmcp 包未安装")
        return

    # 服务器脚本路径
    server_script = "src/ts_rag/tashanrag_server.py"

    print(f"服务器脚本: {server_script}")
    print("连接到 HTTP 模式服务器...")
    print()

    try:
        # FastMCP 客户端会自动检测服务器运行模式
        async with Client(server_script) as client:
            # 列出工具
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            print(f"✅ 成功连接，发现工具: {tool_names}")

            if "tashanrag_ask_paper_db" not in tool_names:
                print("❌ 错误: 未找到目标工具")
                return

            print("\n调用工具 tashanrag_ask_paper_db...")
            print("问题: 细胞增殖如何影响集体行为？")
            print("(处理时间较长，请耐心等待)")
            print()

            start_time = datetime.now()

            # 调用工具
            response = await client.call_tool(
                "tashanrag_ask_paper_db",
                {
                    "question": "细胞增殖如何影响集体行为？",
                    "top_k": 3,
                    "max_concurrent_visits": 5,
                },
            )

            elapsed = (datetime.now() - start_time).total_seconds()

            print("\n" + "=" * 60)
            print("响应结果")
            print("=" * 60)
            print(f"处理时间: {elapsed:.1f}秒")

            if response and response.content:
                content = response.content[0]

                if hasattr(content, "text"):
                    # FastMCP 2.x 可能已经解析了 JSON
                    if isinstance(content.text, dict):
                        data = content.text
                    else:
                        try:
                            data = json.loads(content.text)
                        except json.JSONDecodeError:
                            data = {"raw_response": content.text}
                        except Exception:
                            data = {"raw_response": content.text}

                    print("\n✅ 请求成功!")

                    if data.get("status") == "error":
                        print("\n❌ 状态: 错误")
                        print(f"错误信息: {data.get('error_message')}")
                    else:
                        # 显示最终回答
                        if data.get("final_answer"):
                            print("\n📢 最终回答:")
                            answer = data["final_answer"]
                            print(answer[:1200] + "..." if len(answer) > 1200 else answer)

                        # 显示引用
                        citations = data.get("citations_map", {})
                        if citations:
                            print(f"\n📚 引用来源 ({len(citations)} 个):")
                            for cid, item in list(citations.items())[:5]:
                                paper_id = item.get("paper_id", "Unknown")
                                text = item.get("text", "")
                                preview = text[:150] + "..." if len(text) > 150 else text
                                print(f"\n   [^{cid}] {paper_id}")
                                print(f"      {preview}")

                        # 显示指标
                        metrics = data.get("metrics", {})
                        if metrics:
                            print("\n📊 处理指标:")
                            print(f"   - 论文处理数: {metrics.get('papers_processed', 0)}")
                            print(f"   - 片段提取数: {metrics.get('snippets_count', 0)}")
                            print(f"   - 总耗时: {metrics.get('total_time', 0)}秒")
                            print(f"   - 搜索耗时: {metrics.get('search_time', 0)}秒")
                            print(f"   - 访问耗时: {metrics.get('visit_time', 0)}秒")
                            print(f"   - 内存峰值: {metrics.get('memory_peak_mb', 0)}MB")
                else:
                    print("\n⚠️ 响应内容格式异常")
            else:
                print("\n❌ 未收到响应")

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    # 首先确认 HTTP 服务器是否运行
    print("检查 HTTP 服务器状态...")
    try:
        import aiohttp
    except ImportError:
        print("提示: 安装 aiohttp 可以更好地检查服务器状态")
        aiohttp = None

    if aiohttp:

        async def check_server():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "http://localhost:8080/mcp",
                        headers={"Accept": "text/event-stream, application/json"},
                    ) as resp:
                        return resp.status != 0
            except Exception:
                return False

        is_running = asyncio.run(check_server())

        if not is_running:
            print("❌ HTTP 服务器未运行或无法访问")
            print("请先运行以下命令启动服务器:")
            print(
                "  FASTMCP_TRANSPORT=streamable-http FASTMCP_HOST=0.0.0.0 "
                "FASTMCP_PORT=8080 uv run python src/ts_rag/tashanrag_server.py"
            )
            sys.exit(1)

        print("✅ HTTP 服务器正在运行")
        print()

    # 运行测试
    asyncio.run(test_with_fastmcp_client())
