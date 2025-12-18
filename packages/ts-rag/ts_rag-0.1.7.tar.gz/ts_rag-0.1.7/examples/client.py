import asyncio
import json
import os
import sys

from fastmcp import Client

# ================= 配置区域 =================
SERVER_SCRIPT = "tashanrag_server.py"  # 服务器脚本文件名
DEFAULT_QUESTION = "细胞增殖和集体行为的相互作用是什么？"
# ===========================================


async def run_agent_client():
    """运行 FastMCP 客户端示例"""
    # 1. 确定服务器脚本的绝对路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    server_path = os.path.join(project_root, "src", "ts_rag", SERVER_SCRIPT)

    if not os.path.exists(server_path):
        print(f"❌ 错误: 找不到服务器脚本: {server_path}")
        return

    print(f"🤖 [Client] 正在启动 MCP 服务器: {SERVER_SCRIPT} ...")
    print(f"📝 [Client] 准备提问: {DEFAULT_QUESTION}\n")

    # 2. 使用 FastMCP Client 连接
    try:
        async with Client(server_path) as client:
            # 列出可用工具
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            print(f"🔗 [Client] 连接成功，发现工具: {tool_names}")

            if "tashanrag_ask_paper_db" not in tool_names:
                print("❌ 错误: 未找到目标工具 'tashanrag_ask_paper_db'")
                return

            print("⏳ [Client] 正在调用工具 (这可能需要一些时间来处理 PDF 和索引)...")

            # 3. 调用工具 - FastMCP 自动处理参数和返回值
            response = await client.call_tool(
                "tashanrag_ask_paper_db",
                {"question": DEFAULT_QUESTION, "top_k": 3, "max_concurrent_visits": 5},
            )

            # 4. 处理响应 - FastMCP 返回 CallToolResult
            if not response or not response.content:
                print("❌ 错误: 工具未返回任何内容")
                return

            # 获取第一个内容项（通常是 TextContent）
            content = response.content[0]
            if not hasattr(content, "text"):
                print("❌ 错误: 响应内容格式不正确")
                return

            # FastMCP 2.x 已经自动解析了 JSON
            response_data = content.text if isinstance(content.text, dict) else json.loads(content.text)

            print("\n" + "=" * 50)
            print("✅ [Client] 收到回答")
            print("=" * 50)

            # 打印状态
            if isinstance(response_data, dict) and response_data.get("status") == "error":
                print("⚠️ 状态: Error")
                print(f"❌ 错误信息: {response_data.get('error_message')}")
                if response_data.get("final_answer"):
                    print(f"\n参考回答: {response_data.get('final_answer')}")
            else:
                # 打印思考过程 (如果有)
                thinking = response_data.get("thinking")
                if thinking:
                    print("\n🧠 [思考过程]:")
                    print(thinking)
                    print("-" * 30)

                # 打印最终回答
                final_answer = response_data.get("final_answer")
                print("\n📢 [最终回答]:")
                print(final_answer)

                # 打印引用 (如果有)
                citations = response_data.get("citations_map")
                if citations:
                    print("\n📚 [引用来源]:")
                    keys = sorted(citations.keys(), key=lambda x: int(x) if x.isdigit() else x)
                    for k in keys:
                        item = citations[k]
                        preview = item.get("text", "")[:100].replace("\n", " ")
                        file_name = os.path.basename(item.get("file_path", "Unknown"))
                        print(f"  [^{k}] {file_name}: {preview}...")

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Windows 下通常需要这个策略来避免 EventLoop 冲突
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(run_agent_client())
