import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ================= 配置区域 =================
# 服务器脚本在 src/ts_rag/ 目录下
DEFAULT_QUESTION = "自动化科研有什么进展？"
# ===========================================


async def run_agent_client():
    # 1. 确定服务器脚本的绝对路径
    # 从 tests/ 目录找到 src/ts_rag/tashanrag_server.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # 项目根目录
    server_path = os.path.join(project_root, "src", "ts_rag", "tashanrag_server.py")

    if not os.path.exists(server_path):
        print(f"❌ 错误: 找不到服务器脚本: {server_path}")
        return

    print(f"🤖 [Agent] 正在启动 MCP 服务器: {server_path} ...")
    print(f"📝 [Agent] 准备提问: {DEFAULT_QUESTION}\n")

    # 2. 配置服务器启动参数 (Stdio模式)
    server_params = StdioServerParameters(
        command=sys.executable,  # 使用当前的 python 解释器
        args=[server_path],  # 启动服务器脚本
        env=os.environ.copy(),  # 传递环境变量 (API Key等)
    )

    # 3. 建立连接
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()

            # 列出可用工具 (调试用，确认连接成功)
            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            print(f"🔗 [Agent] 连接成功，发现工具: {tool_names}")

            # 检查可用工具
            if "tashanrag_sync_papers" not in tool_names:
                print("❌ 错误: 未找到工具 'tashanrag_sync_papers'")
                return
            if "tashanrag_search_and_analyze" not in tool_names:
                print("❌ 错误: 未找到工具 'tashanrag_search_and_analyze'")
                return

            # 4. 先同步论文（如果需要）
            print("⏳ [Agent] 步骤 1: 同步论文和构建索引...")
            sync_result = await session.call_tool(
                "tashanrag_sync_papers",
                arguments={
                    "force_rebuild": False  # 使用增量更新
                },
            )

            if sync_result.content:
                sync_data = json.loads(sync_result.content[0].text)
                if sync_data.get("status") == "error":
                    print(f"⚠️ 同步警告: {sync_data.get('error_message')}")
                else:
                    print(f"✅ 同步完成: {sync_data.get('message', 'Success')}")

            # 5. 搜索和分析论文
            print(f"\n⏳ [Agent] 步骤 2: 搜索和分析论文 (问题: {DEFAULT_QUESTION})...")
            result = await session.call_tool(
                "tashanrag_search_and_analyze",
                arguments={"question": DEFAULT_QUESTION, "top_k": 3, "max_concurrent_visits": 5},
            )

            # 6. 处理结果
            # MCP 返回的结果是一个 list，通常第一个元素包含文本内容
            if not result.content:
                print("❌ 错误: 工具未返回任何内容")
                return

            # 获取服务器返回的原始文本 (这是一个 JSON 字符串)
            raw_json_str = result.content[0].text

            try:
                # 解析 JSON
                response_data = json.loads(raw_json_str)

                print("\n" + "=" * 50)
                print("✅ [Agent] 收到回答")
                print("=" * 50)

                # 打印状态
                if response_data.get("status") == "error":
                    print("⚠️ 状态: Error")
                    print(f"❌ 错误信息: {response_data.get('error_message')}")
                    # 即使出错也可能有一部分回答
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
                        # 简单的按键排序
                        keys = sorted(citations.keys(), key=lambda x: int(x) if x.isdigit() else x)
                        for k in keys:
                            item = citations[k]
                            # 截取前 100 个字符用于展示
                            preview = item.get("text", "")[:100].replace("\n", " ")
                            file_name = os.path.basename(item.get("file_path", "Unknown"))
                            print(f"  [^{k}] {file_name}: {preview}...")

            except json.JSONDecodeError:
                print("❌ 错误: 无法解析服务器返回的 JSON。原始输出如下:")
                print(raw_json_str)


if __name__ == "__main__":
    # Windows 下通常需要这个策略来避免 EventLoop 冲突
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(run_agent_client())
