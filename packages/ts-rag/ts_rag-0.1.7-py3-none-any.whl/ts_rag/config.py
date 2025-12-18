"""
TashanRAG 统一配置管理模块

该模块负责：
1. 从 /root/bailiankey.txt 读取 API key
2. 从环境变量读取其他配置（OPENAI_BASE_URL, MODEL_NAME 等）
3. 提供统一的配置访问接口
4. 验证必需的配置项
5. 设置 LiteLLM 相关配置

注意：所有路径现在都固定为 Path.cwd() / ".tashan" / "deepsearch"
"""

import os
import sys
import warnings
from pathlib import Path

# 抑制来自第三方库的弃用警告
warnings.filterwarnings("ignore", category=DeprecationWarning, module="litellm.*")


class TashanRAGConfig:
    """TashanRAG 统一配置管理类

    采用单例模式，确保全项目使用同一份配置。
    API key 从 /root/bailiankey.txt 读取，其他配置从环境变量读取。
    所有路径都固定为 Path.cwd() / ".tashan" / "deepsearch"
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._load_env()
            self._validate_config()
            self._setup_litellm()
            self._initialized = True

    def _load_env(self):
        """加载配置

        现在路径都固定为 Path.cwd() / ".tashan" / "deepsearch"
        优先从环境变量读取配置，其次尝试读取 .env 文件
        为了兼容旧环境，也会尝试从 /root/bailiankey.txt 读取 API key（但不强求）
        """
        # 1. 尝试加载 .env 文件（标准做法）
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass  # 如果没有安装 python-dotenv，就跳过

        # 2. 尝试从 /root/bailiankey.txt 读取 (为了兼容特定环境)
        # 即使读取失败也不报错，依赖后续的 _validate_config 检查环境变量
        try:
            api_key_path = Path("/root/bailiankey.txt")
            if api_key_path.exists():
                with open(api_key_path, encoding="utf-8") as f:
                    api_key = f.read().strip()
                    if api_key:
                        os.environ["OPENAI_API_KEY"] = api_key
        except Exception as e:
            # 仅在调试模式下打印警告，避免干扰正常启动
            if os.environ.get("DEBUG", "false").lower() == "true":
                print(f"[Config] Debug: 尝试读取 {api_key_path} 失败: {e}", file=sys.stderr)

    def _validate_config(self):
        """验证必需的配置项"""
        # 检查 API key
        if not os.environ.get("OPENAI_API_KEY"):
            # 如果是 uvx 环境下，可能没有传递环境变量且无法读取文件
            # 此时不抛出异常，而是打印警告，允许程序启动（方便排查问题）
            # 但在实际调用需要 Key 的功能时会失败
            if os.environ.get("FASTMCP_TRANSPORT"):  # 这是一个简单的判断是否在 MCP 环境下的依据
                print("[Config] 警告: 未找到 OPENAI_API_KEY，部分功能可能不可用。", file=sys.stderr)
            else:
                # 保持原有逻辑，非 MCP 环境下严格检查
                raise ValueError("缺少必需的配置项：OPENAI_API_KEY (API 密钥)")

        # OPENAI_BASE_URL 有默认值，不是必需的

    def _setup_litellm(self):
        """设置 LiteLLM 相关配置"""
        try:
            # 尝试相对导入（支持作为包运行）
            try:
                from .llm_config import register_qwen_models
            except ImportError:
                # 回退到绝对导入（开发模式）
                from llm_config import register_qwen_models

            register_qwen_models()
        except ImportError:
            # 注册失败不是致命错误，只给出警告
            # LiteLLM 仍然可以正常工作，只是可能缺少一些自定义模型
            print(
                "[Config] 警告: 无法导入 llm_config，LiteLLM 模型可能未注册",
                file=sys.stderr,
            )

    # OpenAI API 配置
    @property
    def openai_api_key(self) -> str:
        """OpenAI API 密钥（从 /root/bailiankey.txt 读取）"""
        return os.environ["OPENAI_API_KEY"]

    @property
    def openai_base_url(self) -> str:
        """OpenAI API 基础 URL"""
        return os.environ.get("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

    @property
    def model_name(self) -> str:
        """默认使用的模型名称"""
        return os.environ.get("MODEL_NAME", "openai/qwen-flash")

    # 路径配置（已废弃，现在都使用固定路径）
    # 保留这些属性以保持向后兼容，但返回固定路径
    @property
    def paper_root(self) -> str:
        """论文根目录（已废弃，保留以兼容旧代码）"""
        # 现在路径都固定为 Path.cwd() / ".tashan" / "deepsearch"
        return str(Path.cwd() / ".tashan" / "deepsearch")

    @property
    def index_dir(self) -> str:
        """索引目录（已废弃，保留以兼容旧代码）"""
        return ".tashan/deepsearch"

    @property
    def papers_dir(self) -> str:
        """转换后的论文目录（已废弃，保留以兼容旧代码）"""
        return str(Path.cwd() / ".tashan" / "deepsearch" / "papers")

    @property
    def index_data_dir(self) -> str:
        """索引数据目录（已废弃，保留以兼容旧代码）"""
        return str(Path.cwd() / ".tashan" / "deepsearch" / "index_data")

    # 处理配置
    @property
    def max_concurrent_visits(self) -> int:
        """最大并发访问数"""
        return int(os.environ.get("MAX_CONCURRENT_VISITS", "5"))

    @property
    def max_concurrent_pdf_conversion(self) -> int:
        """PDF 转换的最大并发数（默认 3，适合 2GB 内存环境）"""
        # 优先使用环境变量
        if "MAX_CONCURRENT_PDF_CONVERSION" in os.environ:
            return int(os.environ["MAX_CONCURRENT_PDF_CONVERSION"])

        # 否则基于 CPU 核心数，但设置合理范围（2-6）
        cpu_count = os.cpu_count() or 4
        return max(2, min(cpu_count, 6))

    @property
    def top_k_default(self) -> int:
        """默认检索的论文数量"""
        return int(os.environ.get("TOP_K_DEFAULT", "3"))

    # 路径配置
    @property
    def project_root(self) -> Path:
        """项目根目录"""
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS).parent
        else:
            return Path(__file__).parent.parent.parent

    def get_absolute_path(self, relative_path: str) -> str:
        """获取相对路径的绝对路径"""
        if os.path.isabs(relative_path):
            return relative_path
        return str(self.project_root / relative_path)

    # 调试配置
    @property
    def debug_mode(self) -> bool:
        """是否开启调试模式"""
        return os.environ.get("DEBUG", "false").lower() == "true"

    @property
    def verbose(self) -> bool:
        """是否输出详细信息"""
        return os.environ.get("VERBOSE", "false").lower() == "true"

    # 缓存配置
    @property
    def enable_cache(self) -> bool:
        """是否启用缓存"""
        return os.environ.get("ENABLE_CACHE", "true").lower() == "true"

    def print_config(self):
        """打印当前配置（调试用）"""
        print("\n" + "=" * 60)
        print("TashanRAG 配置信息")
        print("=" * 60)
        print(f"API Base URL: {self.openai_base_url}")
        print(f"Model: {self.model_name}")
        print(f"Data Directory: {Path.cwd() / '.tashan' / 'deepsearch'}")
        print(f"Max Concurrent Visits: {self.max_concurrent_visits}")
        print(f"Top K Default: {self.top_k_default}")
        print(f"Debug Mode: {self.debug_mode}")
        print("=" * 60)


# 创建全局配置实例
config = TashanRAGConfig()

# 为了向后兼容，也可以直接导入常用配置
OPENAI_API_KEY = config.openai_api_key
OPENAI_BASE_URL = config.openai_base_url
MODEL_NAME = config.model_name
PAPER_ROOT = config.paper_root
MAX_CONCURRENT_VISITS = config.max_concurrent_visits
TOP_K_DEFAULT = config.top_k_default
