import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# 添加 src/ts_rag 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "ts_rag"))

import litellm

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

# 加载 .env 文件并强制使用其中的变量
env_path = Path(__file__).parent.parent / ".env"
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


def test_litellm_registration():
    model_name = "openai/qwen-flash"

    print(f"Before registration: {model_name in litellm.model_cost}")

    # Register the model
    litellm.model_cost[model_name] = {
        "max_input_tokens": 1000000,
        "max_output_tokens": 8192,
        "input_cost_per_token": 0,
        "output_cost_per_token": 0,
        "litellm_provider": "openai",
        "mode": "chat",
    }

    print(f"After registration: {model_name in litellm.model_cost}")

    # Check if DocumentLLM picks it up (via litellm.get_model_info)
    try:
        info = litellm.get_model_info(model_name)
        print(f"Model Info Max Input Tokens: {info.get('max_input_tokens')}")
    except Exception as e:
        print(f"Error getting model info: {e}")


if __name__ == "__main__":
    test_litellm_registration()
