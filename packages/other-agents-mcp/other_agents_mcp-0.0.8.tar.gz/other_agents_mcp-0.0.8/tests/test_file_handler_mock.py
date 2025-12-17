"""Mock-based tests for file_handler module"""

import subprocess
from unittest.mock import Mock, patch
import pytest

from other_agents_mcp.file_handler import (
    execute_cli_file_based,
    CLINotFoundError,
    CLITimeoutError,
    CLIExecutionError,
)


class TestFileHandlerMocked:
    """Mock 기반 file_handler 테스트"""

    @patch("other_agents_mcp.file_handler.is_cli_installed")
    @patch("other_agents_mcp.file_handler.subprocess.run")
    @patch("other_agents_mcp.file_handler.tempfile.mkstemp")
    @patch("other_agents_mcp.file_handler.os.fdopen")
    @patch("other_agents_mcp.file_handler.os.close")
    @patch("builtins.open", create=True)
    @patch("other_agents_mcp.file_handler.os.remove")
    @patch("other_agents_mcp.file_handler.os.path.exists")
    def test_execute_cli_success(
        self,
        mock_exists,
        mock_remove,
        mock_open_builtin,
        mock_close,
        mock_fdopen,
        mock_mkstemp,
        mock_run,
        mock_installed,
    ):
        """CLI 실행 성공 케이스"""
        # Mock 설정
        mock_installed.return_value = True
        mock_mkstemp.side_effect = [(1, "/tmp/input_test.txt"), (2, "/tmp/output_test.txt")]
        mock_fdopen.return_value.__enter__.return_value.write = Mock()
        mock_run.return_value = Mock(returncode=0, stderr="")
        mock_open_builtin.return_value.__enter__.return_value.read.return_value = "Test response"
        mock_exists.return_value = True

        # 실행
        result = execute_cli_file_based("claude", "test message")

        # 검증
        assert result == "Test response"
        assert mock_run.called
        assert mock_remove.call_count == 2  # input, output 파일 삭제

    @patch("other_agents_mcp.file_handler.is_cli_installed")
    def test_cli_not_installed(self, mock_installed):
        """미설치 CLI 에러"""
        mock_installed.return_value = False

        with pytest.raises(CLINotFoundError):
            execute_cli_file_based("nonexistent", "test")

    @patch("other_agents_mcp.file_handler.is_cli_installed")
    @patch("other_agents_mcp.file_handler.subprocess.run")
    @patch("other_agents_mcp.file_handler.tempfile.mkstemp")
    @patch("other_agents_mcp.file_handler.os.fdopen")
    @patch("other_agents_mcp.file_handler.os.close")
    @patch("builtins.open", create=True)
    @patch("other_agents_mcp.file_handler.os.remove")
    @patch("other_agents_mcp.file_handler.os.path.exists")
    def test_timeout_exception(
        self,
        mock_exists,
        mock_remove,
        mock_open_builtin,
        mock_close,
        mock_fdopen,
        mock_mkstemp,
        mock_run,
        mock_installed,
    ):
        """타임아웃 예외 처리"""
        mock_installed.return_value = True
        mock_mkstemp.side_effect = [(1, "/tmp/input.txt"), (2, "/tmp/output.txt")]
        mock_fdopen.return_value.__enter__.return_value.write = Mock()
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="cli", timeout=60)
        mock_exists.return_value = True

        with pytest.raises(CLITimeoutError):
            execute_cli_file_based("claude", "test")

        # 파일 정리 확인
        assert mock_remove.call_count == 2

    @patch("other_agents_mcp.file_handler.is_cli_installed")
    @patch("other_agents_mcp.file_handler.subprocess.run")
    @patch("other_agents_mcp.file_handler.tempfile.mkstemp")
    @patch("other_agents_mcp.file_handler.os.fdopen")
    @patch("other_agents_mcp.file_handler.os.close")
    @patch("builtins.open", create=True)
    @patch("other_agents_mcp.file_handler.os.remove")
    @patch("other_agents_mcp.file_handler.os.path.exists")
    def test_cli_execution_error(
        self,
        mock_exists,
        mock_remove,
        mock_open_builtin,
        mock_close,
        mock_fdopen,
        mock_mkstemp,
        mock_run,
        mock_installed,
    ):
        """CLI 실행 에러"""
        mock_installed.return_value = True
        mock_mkstemp.side_effect = [(1, "/tmp/input.txt"), (2, "/tmp/output.txt")]
        mock_fdopen.return_value.__enter__.return_value.write = Mock()
        mock_run.return_value = Mock(returncode=1, stderr="Error occurred")
        mock_exists.return_value = True

        with pytest.raises(CLIExecutionError) as exc_info:
            execute_cli_file_based("claude", "test")

        assert "Error occurred" in str(exc_info.value)
        assert mock_remove.call_count == 2

    @patch("other_agents_mcp.file_handler.is_cli_installed")
    @patch("other_agents_mcp.file_handler.subprocess.run")
    @patch("other_agents_mcp.file_handler.tempfile.mkstemp")
    @patch("other_agents_mcp.file_handler.os.fdopen")
    @patch("other_agents_mcp.file_handler.os.close")
    @patch("builtins.open", create=True)
    @patch("other_agents_mcp.file_handler.os.remove")
    @patch("other_agents_mcp.file_handler.os.path.exists")
    def test_extra_args_passed(
        self,
        mock_exists,
        mock_remove,
        mock_open_builtin,
        mock_close,
        mock_fdopen,
        mock_mkstemp,
        mock_run,
        mock_installed,
    ):
        """extra_args(headless/yolo/sandbox 플래그)가 올바르게 전달되는지 확인"""
        mock_installed.return_value = True
        mock_mkstemp.side_effect = [(1, "/tmp/input.txt"), (2, "/tmp/output.txt")]
        mock_fdopen.return_value.__enter__.return_value.write = Mock()
        mock_run.return_value = Mock(returncode=0, stderr="")
        mock_open_builtin.return_value.__enter__.return_value.read.return_value = "OK"
        mock_exists.return_value = True

        # Qwen CLI (headless/yolo/sandbox 플래그)
        execute_cli_file_based("qwen", "test")

        # subprocess.run 호출 확인
        assert mock_run.called
        call_args = mock_run.call_args[0][0]  # 실행된 명령어 리스트

        # headless 모드 플래그 전달 확인
        assert "--headless" in call_args
        assert "--yolo" in call_args
        assert "--sandbox" in call_args


class TestExceptionCoverage:
    """예외 경로 커버리지 향상"""

    @patch("other_agents_mcp.file_handler.is_cli_installed")
    @patch("other_agents_mcp.file_handler.subprocess.run")
    @patch("other_agents_mcp.file_handler.tempfile.mkstemp")
    @patch("other_agents_mcp.file_handler.os.fdopen")
    @patch("other_agents_mcp.file_handler.os.close")
    @patch("builtins.open", create=True)
    @patch("other_agents_mcp.file_handler.os.remove")
    @patch("other_agents_mcp.file_handler.os.path.exists")
    def test_file_not_found_exception(
        self,
        mock_exists,
        mock_remove,
        mock_open_builtin,
        mock_close,
        mock_fdopen,
        mock_mkstemp,
        mock_run,
        mock_installed,
    ):
        """FileNotFoundError 처리"""
        mock_installed.return_value = True
        mock_mkstemp.side_effect = [(1, "/tmp/input.txt"), (2, "/tmp/output.txt")]
        mock_fdopen.return_value.__enter__.return_value.write = Mock()
        mock_run.side_effect = FileNotFoundError("CLI not found")
        mock_exists.return_value = True

        with pytest.raises(CLINotFoundError):
            execute_cli_file_based("claude", "test")

        assert mock_remove.call_count == 2

    def test_unknown_cli_name(self):
        """알 수 없는 CLI 이름"""
        with pytest.raises(CLINotFoundError) as exc_info:
            execute_cli_file_based("unknown_cli", "test")

        assert "unknown_cli" in str(exc_info.value)
