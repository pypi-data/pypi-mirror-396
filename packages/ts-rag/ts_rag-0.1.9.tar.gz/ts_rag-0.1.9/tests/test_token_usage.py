import os
from pathlib import Path

from litellm import completion

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
    from dotenv import load_dotenv

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

# Config - 从环境变量读取
MODEL_NAME = os.environ.get("MODEL_NAME", "openai/qwen-flash")


def test_usage():
    print(f"Testing token usage for {MODEL_NAME}...")
    try:
        # 对于阿里云的 Qwen 模型，需要使用 openai/ 前缀
        model_name = f"openai/{MODEL_NAME}" if not MODEL_NAME.startswith("openai/") else MODEL_NAME
        print(f"Using model: {model_name}")

        response = completion(
            model=model_name,
            messages=[{"role": "user", "content": "Hello, how are you?"}],
            temperature=0.0,
        )
        print("\nRaw Response Usage:")
        print(response.usage)
        print(f"Prompt Tokens: {response.usage.prompt_tokens}")
        print(f"Completion Tokens: {response.usage.completion_tokens}")
        print(f"Total Tokens: {response.usage.total_tokens}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_usage()
