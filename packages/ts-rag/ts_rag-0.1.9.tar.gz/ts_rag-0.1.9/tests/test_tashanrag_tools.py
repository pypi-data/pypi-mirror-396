"""
测试 TashanRAG 的 MCP 工具
测试两个新的拆分工具：tashanrag_sync_papers 和 tashanrag_search_and_analyze
"""

import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

pytestmark = pytest.mark.asyncio

# 确保能找到测试模块
test_dir = Path(__file__).parent
project_root = test_dir.parent
sys.path.insert(0, str(test_dir))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src" / "ts_rag"))

# 测试配置 - 使用临时目录避免影响实际数据
TEST_PAPERS_DIR = "test_papers"


class TestTashanragSyncPapers:
    """测试 tashanrag_sync_papers 工具"""

    @pytest.fixture(autouse=True)
    def setup_test_env(self, monkeypatch):
        """设置测试环境"""
        # 创建临时测试目录
        self.test_dir = Path(tempfile.mkdtemp())
        self.papers_dir = self.test_dir / "papers"
        self.papers_dir.mkdir()

        # 设置环境变量
        monkeypatch.setenv("TASHANRAG_PAPER_ROOT", str(self.papers_dir))

        # 创建测试 PDF 文件
        self.sample_pdf = self.papers_dir / "test.pdf"
        with open(self.sample_pdf, "wb") as f:
            f.write(b"%PDF-1.4\n%mock PDF content")

        # 重定向日志输出以避免测试时的打印
        self.patch_print = patch("builtins.print")

        yield

        # 清理
        shutil.rmtree(self.test_dir)

    @pytest.fixture
    def mock_config(self):
        """Mock 配置对象"""
        from unittest.mock import MagicMock

        config = MagicMock()
        config.paper_root = str(self.papers_dir)
        config.index_data_dir = ".indexonly/index_data"
        return config

    @pytest.fixture
    def mock_ctx(self):
        """Mock MCP Context"""
        from unittest.mock import AsyncMock

        ctx = AsyncMock()
        ctx.info = AsyncMock()
        ctx.error = AsyncMock()
        ctx.warning = AsyncMock()
        ctx.report_progress = AsyncMock()
        return ctx

    async def test_sync_papers_success(self, mock_config, mock_ctx):
        """测试成功的论文同步"""
        # 改为直接测试内部实现函数
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "ts_rag"))

        from tashanrag_server import _tashanrag_sync_papers_impl

        # Mock 相关函数
        with (
            patch("tashanrag_server.run_pdf_sync_pipeline") as mock_sync,
            patch("tashanrag_server.build_index") as mock_index,
            patch("tashanrag_server.config", mock_config),
        ):
            mock_ctx.report_progress = AsyncMock()
            mock_ctx.info = AsyncMock()

            result = await _tashanrag_sync_papers_impl(force_rebuild=False, ctx=mock_ctx)

            # 验证调用
            mock_sync.assert_called_once_with(str(self.papers_dir))
            mock_index.assert_called_once()

            # 验证返回值结构
            assert "status" in result
            assert "message" in result
            assert result["status"] == "success"

    async def test_sync_papers_force_rebuild(self, mock_config, mock_ctx):
        """测试强制重建索引"""

        from tashanrag_server import _tashanrag_sync_papers_impl

        with (
            patch("tashanrag_server.run_pdf_sync_pipeline"),
            patch("tashanrag_server.build_index") as mock_index,
            patch("tashanrag_server.config", mock_config),
            patch("pathlib.Path.exists", return_value=True),
            patch("shutil.rmtree") as mock_rmtree,
            patch("tashanrag_server.os.makedirs"),
        ):
            mock_ctx.report_progress = AsyncMock()

            await _tashanrag_sync_papers_impl(force_rebuild=True, ctx=mock_ctx)

            # 验证重建逻辑
            mock_rmtree.assert_called_once()
            mock_index.assert_called_once()

    async def test_sync_papers_no_papers(self, mock_config, mock_ctx):
        """测试空目录的同步"""
        # 移除测试 PDF
        if self.sample_pdf.exists():
            self.sample_pdf.unlink()

        from tashanrag_server import _tashanrag_sync_papers_impl

        with (
            patch("tashanrag_server.run_pdf_sync_pipeline") as mock_sync,
            patch("tashanrag_server.config", mock_config),
        ):
            mock_sync.return_value = {"new_files": 0, "updated_files": 0, "removed_files": 0}

            result = await _tashanrag_sync_papers_impl(force_rebuild=False, ctx=mock_ctx)

            assert result["status"] == "success"
            # Check for any indication of no papers being processed
            assert "0 new files" in result["message"] or "no papers" in result["message"].lower()


class TestTashanragSearchAndAnalyze:
    """测试 tashanrag_search_and_analyze 工具"""

    @pytest.fixture(autouse=True)
    def setup_test_env(self, monkeypatch):
        """设置测试环境"""
        # 创建临时测试目录
        self.test_dir = Path(tempfile.mkdtemp())
        self.papers_dir = self.test_dir / "papers"
        self.papers_dir.mkdir()
        self.index_dir = self.papers_dir / ".indexonly" / "index_data"
        self.index_dir.mkdir(parents=True)

        # 创建模拟索引文件
        self.id_map_file = self.index_dir / "id_map.json"
        self.pool_file = self.index_dir / "summary_pool.txt"

        # 设置环境变量
        monkeypatch.setenv("TASHANRAG_PAPER_ROOT", str(self.papers_dir))

        # 创建索引文件
        with open(self.id_map_file, "w") as f:
            f.write('{"test_paper": {"path": "/path/to/test.pdf", "title": "Test Paper"}}')

        with open(self.pool_file, "w") as f:
            f.write("Test abstract\nTest title\n")

        yield

        # 清理
        shutil.rmtree(self.test_dir)

    @pytest.fixture
    def mock_config(self):
        """Mock 配置对象"""
        from unittest.mock import MagicMock

        config = MagicMock()
        config.paper_root = str(self.papers_dir)
        config.index_data_dir = ".indexonly/index_data"
        config.top_k_default = 3
        config.max_concurrent_visits = 5
        return config

    @pytest.fixture
    def mock_ctx(self):
        """Mock MCP Context"""
        from unittest.mock import AsyncMock

        ctx = AsyncMock()
        ctx.info = AsyncMock()
        ctx.error = AsyncMock()
        ctx.warning = AsyncMock()
        ctx.report_progress = AsyncMock()
        return ctx

    async def test_search_and_analyze_success(self, mock_config, mock_ctx):
        """测试成功的搜索和分析"""
        from tashanrag_server import _tashanrag_search_and_analyze_impl

        # Mock 相关函数
        mock_search_result = {
            "status": "success",
            "found_papers": [
                {
                    "paper_id": "test_paper",
                    "title": "Test Paper",
                    "path": "/path/to/test.pdf",
                    "reason": "Relevant to question",
                }
            ],
        }

        mock_answer_result = {
            "status": "success",
            "final_answer": "Test answer",
            "citations_map": {"1": {"paper_id": "test_paper", "text": "Test citation"}},
            "user_question": "Test question",
            "thinking": None,
        }

        with (
            patch("tashanrag_server.search_papers", return_value=mock_search_result),
            patch("tashanrag_server._search_and_answer_only", return_value=mock_answer_result),
            patch("tashanrag_server.config", mock_config),
        ):
            mock_ctx.report_progress = AsyncMock()
            mock_ctx.info = AsyncMock()

            result = await _tashanrag_search_and_analyze_impl(
                question="Test question", top_k=3, max_concurrent_visits=5, ctx=mock_ctx
            )

            # 验证结果
            assert result["status"] == "success"
            assert result["final_answer"] == "Test answer"
            assert "citations_map" in result

    async def test_search_and_analyze_no_index(self, mock_config, mock_ctx):
        """测试没有索引时的错误处理"""
        # 删除索引目录
        if self.index_dir.exists():
            shutil.rmtree(self.index_dir)

        from tashanrag_server import _tashanrag_search_and_analyze_impl

        with patch("tashanrag_server.config", mock_config):
            mock_ctx.info = AsyncMock()

            result = await _tashanrag_search_and_analyze_impl(question="Test question", ctx=mock_ctx)

            # 验证错误处理
            assert result["status"] == "error"
            assert "sync_papers" in result["error_message"].lower()

    async def test_search_and_analyze_search_failed(self, mock_config, mock_ctx):
        """测试搜索失败的情况"""
        from tashanrag_server import _tashanrag_search_and_analyze_impl

        mock_search_result = {"status": "error", "message": "Search failed"}

        with (
            patch("tashanrag_server.search_papers", return_value=mock_search_result),
            patch("tashanrag_server.config", mock_config),
        ):
            result = await _tashanrag_search_and_analyze_impl(question="Test question", ctx=mock_ctx)

            assert result["status"] == "error"
            # The error message might be prefixed, so check if it contains the original message
            assert "Search failed" in result["error_message"]

    async def test_search_and_analyze_visit_failed(self, mock_config, mock_ctx):
        """测试访问失败的情况"""
        from tashanrag_server import _tashanrag_search_and_analyze_impl

        mock_search_result = {"status": "success", "found_papers": [{"paper_id": "test", "path": "/path/to/test.pdf"}]}

        mock_answer_result = {"status": "error", "error_message": "Visit failed"}

        with (
            patch("tashanrag_server.search_papers", return_value=mock_search_result),
            patch("tashanrag_server._search_and_answer_only", return_value=mock_answer_result),
            patch("tashanrag_server.config", mock_config),
        ):
            result = await _tashanrag_search_and_analyze_impl(question="Test question", ctx=mock_ctx)

            assert result["status"] == "error"
            assert result["error_message"] == "Visit failed"


class TestBackwardCompatibility:
    """测试向后兼容性"""

    @pytest.fixture(autouse=True)
    def setup_test_env(self, monkeypatch):
        """设置测试环境"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.papers_dir = self.test_dir / "papers"
        self.papers_dir.mkdir()

        monkeypatch.setenv("TASHANRAG_PAPER_ROOT", str(self.papers_dir))

        # 创建测试文件
        (self.papers_dir / "test.pdf").touch()

        yield

        shutil.rmtree(self.test_dir)

    @pytest.fixture
    def mock_config(self):
        """Mock 配置对象"""
        from unittest.mock import MagicMock

        config = MagicMock()
        config.paper_root = str(self.papers_dir)
        return config

    @pytest.fixture
    def mock_ctx(self):
        """Mock MCP Context"""
        from unittest.mock import AsyncMock

        ctx = AsyncMock()
        ctx.info = AsyncMock()
        ctx.error = AsyncMock()
        ctx.warning = AsyncMock()
        ctx.report_progress = AsyncMock()
        return ctx

    async def test_original_tool_still_works(self, mock_config, mock_ctx):
        """测试原有工具仍然工作"""
        # 这个测试在决定保留原工具时需要
        # 从 tashanrag_server 导入现有工具进行测试
        # 如果删除了原工具，这个测试应该被移除
        pass
