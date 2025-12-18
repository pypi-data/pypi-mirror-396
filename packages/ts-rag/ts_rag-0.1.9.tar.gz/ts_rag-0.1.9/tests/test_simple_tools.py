"""
简单的工具测试，直接测试内部实现函数
"""

# 确保能找到模块
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

test_dir = Path(__file__).parent
project_root = test_dir.parent
sys.path.insert(0, str(project_root / "src" / "ts_rag"))

pytestmark = pytest.mark.asyncio


class TestSimpleTools:
    """简化的工具测试"""

    @pytest.fixture
    def mock_config(self):
        """Mock 配置对象"""
        from unittest.mock import MagicMock

        config = MagicMock()
        config.paper_root = "/test/papers"
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

    async def test_sync_papers_impl(self, mock_config, mock_ctx):
        """测试同步工具实现"""
        from tashanrag_server import _tashanrag_sync_papers_impl

        # Mock 外部函数
        with (
            patch("tashanrag_server.config", mock_config),
            patch("tashanrag_server.run_pdf_sync_pipeline") as mock_sync,
            patch("tashanrag_server.build_index") as mock_index,
            patch("pathlib.Path.exists", return_value=True),
        ):
            mock_sync.return_value = {"new_files": 1, "updated_files": 0}

            result = await _tashanrag_sync_papers_impl(force_rebuild=False, ctx=mock_ctx)

            # 验证结果
            assert result["status"] == "success"
            assert "message" in result
            assert "Successfully synchronized" in result["message"]
            assert result["sync_result"]["new_files"] == 1

            # 验证调用
            mock_sync.assert_called_once_with("/test/papers")
            mock_index.assert_called_once()

    async def test_sync_papers_impl_force_rebuild(self, mock_config, mock_ctx):
        """测试强制重建"""
        from tashanrag_server import _tashanrag_sync_papers_impl

        with (
            patch("tashanrag_server.config", mock_config),
            patch("tashanrag_server.run_pdf_sync_pipeline") as mock_sync,
            patch("tashanrag_server.build_index") as mock_index,
            patch("pathlib.Path.exists", return_value=True),
            patch("tashanrag_server.shutil.rmtree") as mock_rmtree,
            patch("tashanrag_server.os.makedirs") as mock_makedirs,
        ):
            mock_sync.return_value = {"new_files": 0, "updated_files": 0}

            await _tashanrag_sync_papers_impl(force_rebuild=True, ctx=mock_ctx)

            # 验证重建逻辑
            mock_rmtree.assert_called_once()
            mock_makedirs.assert_called_once()
            mock_index.assert_called_once()

    async def test_search_and_analyze_impl(self, mock_config, mock_ctx):
        """测试搜索分析工具实现"""
        from tashanrag_server import _tashanrag_search_and_analyze_impl

        # Mock 搜索结果
        mock_search_result = {"status": "success", "found_papers": [{"paper_id": "test", "path": "/test/paper.pdf"}]}

        # Mock 答案结果
        mock_answer_result = {
            "status": "success",
            "user_question": "Test question",
            "final_answer": "Test answer",
            "thinking": None,
            "citations_map": {"1": {"paper_id": "test", "text": "Test citation"}},
            "found_papers": [{"paper_id": "test", "path": "/test/paper.pdf"}],
        }

        with (
            patch("tashanrag_server.config", mock_config),
            patch("tashanrag_server.search_papers", return_value=mock_search_result),
            patch("tashanrag_server._search_and_answer_only", return_value=mock_answer_result),
            patch("pathlib.Path.exists", return_value=True),
        ):
            result = await _tashanrag_search_and_analyze_impl(
                question="Test question", top_k=3, max_concurrent_visits=5, ctx=mock_ctx
            )

            # 验证结果
            assert result["status"] == "success"
            assert result["final_answer"] == "Test answer"
            assert "citations_map" in result
            assert len(result["citations_map"]) == 1

    async def test_search_and_analyze_impl_no_index(self, mock_config, mock_ctx):
        """测试没有索引的情况"""
        from tashanrag_server import _tashanrag_search_and_analyze_impl

        with patch("tashanrag_server.config", mock_config), patch("pathlib.Path.exists", return_value=False):
            result = await _tashanrag_search_and_analyze_impl(question="Test question", ctx=mock_ctx)

            # 验证错误处理
            assert result["status"] == "error"
            assert "Index not found" in result["error_message"]
            mock_ctx.error.assert_called_once()

    async def test_search_and_analyze_impl_search_failed(self, mock_config, mock_ctx):
        """测试搜索失败的情况"""
        from tashanrag_server import _tashanrag_search_and_analyze_impl

        mock_search_result = {"status": "error", "message": "Search failed"}

        with (
            patch("tashanrag_server.config", mock_config),
            patch("tashanrag_server.search_papers", return_value=mock_search_result),
            patch("pathlib.Path.exists", return_value=True),
        ):
            result = await _tashanrag_search_and_analyze_impl(question="Test question", ctx=mock_ctx)

            # 验证错误处理
            assert result["status"] == "error"
            assert "Search failed" in result["error_message"]
            mock_ctx.error.assert_called_once()
