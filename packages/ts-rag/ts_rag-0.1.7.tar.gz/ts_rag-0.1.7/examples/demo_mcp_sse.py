#!/usr/bin/env python3
"""测试 MCP SSE (Server-Sent Events) API 的脚本"""

import asyncio
import json
import sys
from datetime import datetime


async def test_mcp_sse():
    """测试 MCP SSE API"""
    import aiohttp

    base_url = "http://localhost:8080/mcp"
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

    print("=" * 60)
    print("TashanRAG MCP SSE API 测试")
    print("=" * 60)
    print(f"服务器地址: {base_url}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # MCP JSON-RPC 请求
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "tashanrag_ask_paper_db",
            "arguments": {
                "question": "细胞增殖如何影响集体行为？",
                "top_k": 3,
                "max_concurrent_visits": 5,
            },
        },
    }

    async with aiohttp.ClientSession() as session:
        print("发送请求...")
        print(f"问题: {mcp_request['params']['arguments']['question']}")
        print()

        start_time = datetime.now()

        try:
            async with session.post(base_url, json=mcp_request, headers=headers, timeout=300) as resp:
                print(f"响应状态: {resp.status}")
                print(f"响应头: {dict(resp.headers)}")
                print()

                if resp.status == 200:
                    print("接收数据流...")
                    print("-" * 40)

                    buffer = ""
                    full_response = None

                    async for line in resp.content:
                        line_str = line.decode("utf-8").strip()

                        if line_str:
                            buffer += line_str

                            # SSE 格式以 "data: " 开头
                            if line_str.startswith("data: "):
                                data_part = line_str[6:]  # 去掉 "data: "

                                # 尝试解析 JSON
                                try:
                                    chunk_data = json.loads(data_part)

                                    # 检查是否是完整的响应
                                    if "result" in chunk_data:
                                        full_response = chunk_data
                                        break
                                    elif "error" in chunk_data:
                                        full_response = chunk_data
                                        break
                                    elif "progress" in chunk_data:
                                        # 进度更新
                                        progress = chunk_data["progress"]
                                        current = progress.get("current", 0)
                                        total = progress.get("total", 100)
                                        message = progress.get("message", "")
                                        print(
                                            f"\r进度: {current}/{total} - {message}",
                                            end="",
                                            flush=True,
                                        )

                                except json.JSONDecodeError:
                                    # 可能是部分数据，继续累积
                                    pass

                    print()  # 换行

                    if full_response:
                        print("\n" + "=" * 60)
                        print("最终响应")
                        print("=" * 60)

                        if "error" in full_response:
                            error = full_response["error"]
                            print(f"❌ 错误: {error.get('message', 'Unknown error')}")
                            print(f"错误代码: {error.get('code', 'Unknown')}")
                        else:
                            result = full_response.get("result", {})
                            content = result.get("content", [])

                            if content and len(content) > 0:
                                # 处理内容
                                first_content = content[0]

                                if isinstance(first_content, dict) and "text" in first_content:
                                    response_text = first_content["text"]

                                    # 尝试解析为 JSON
                                    try:
                                        if isinstance(response_text, str):
                                            data = json.loads(response_text)
                                        else:
                                            data = response_text
                                    except (json.JSONDecodeError, Exception):
                                        data = {"raw_response": response_text}

                                    print("\n✅ 请求成功!")
                                    elapsed = (datetime.now() - start_time).total_seconds()
                                    print(f"处理时间: {elapsed:.1f}秒")

                                    if data.get("status") == "error":
                                        print("\n❌ 状态: 错误")
                                        print(f"错误信息: {data.get('error_message', 'Unknown error')}")
                                    else:
                                        # 显示最终回答
                                        if data.get("final_answer"):
                                            print("\n📢 最终回答:")
                                            answer = data["final_answer"]
                                            print(answer[:1000] + "..." if len(answer) > 1000 else answer)

                                        # 显示引用
                                        citations = data.get("citations_map", {})
                                        if citations:
                                            print(f"\n📚 引用来源 ({len(citations)} 个):")
                                            for cid, item in list(citations.items())[:5]:
                                                paper_id = item.get("paper_id", "Unknown")
                                                text = item.get("text", "")
                                                preview = text[:150] + "..." if len(text) > 150 else text
                                                print(f"   [^{cid}] {paper_id}")
                                                print(f"      {preview}\n")

                                        # 显示指标
                                        metrics = data.get("metrics", {})
                                        if metrics:
                                            print("📊 处理指标:")
                                            print(f"   - 论文处理数: {metrics.get('papers_processed', 0)}")
                                            print(f"   - 片段提取数: {metrics.get('snippets_count', 0)}")
                                            print(f"   - 总耗时: {metrics.get('total_time', 0)}秒")
                                            print(f"   - 内存峰值: {metrics.get('memory_peak_mb', 0)}MB")
                            else:
                                print("\n⚠️ 返回内容为空")
                    else:
                        print("\n⚠️ 未收到完整响应")
                        print(f"缓冲区内容: {buffer[:500]}...")
                else:
                    print(f"❌ 请求失败: {resp.status}")
                    error_text = await resp.text()
                    print(f"错误信息: {error_text[:500]}")

        except TimeoutError:
            print("\n❌ 请求超时")
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")
            import traceback

            traceback.print_exc()

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
    asyncio.run(test_mcp_sse())
