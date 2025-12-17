"""Tests for increasing code coverage of file_handler.py"""

import pytest
from unittest.mock import patch, MagicMock
from other_agents_mcp.file_handler import (
    execute_cli_file_based,
    execute_with_session,
    _execute_cli,
    _validate_and_filter_args,
    _build_session_args,
    _cleanup_temp_files,
    CLIExecutionError,
    CLINotFoundError,
)


class TestFileHandlerCoverage:
    """file_handler.py 커버리지 향상을 위한 추가 테스트"""

    @patch("other_agents_mcp.file_handler.get_session_manager")
    @patch("other_agents_mcp.file_handler.get_cli_registry")
    @patch("other_agents_mcp.file_handler.is_cli_installed")
    @patch("other_agents_mcp.file_handler._execute_cli")
    @patch("other_agents_mcp.file_handler._cleanup_temp_files")
    @patch("tempfile.mkstemp")
    @patch("os.fdopen")
    @patch("os.close")
    @patch("builtins.open")
    def test_execute_with_session_success(
        self,
        mock_file_open,
        mock_close,
        mock_fdopen,
        mock_mkstemp,
        mock_cleanup,
        mock_execute_cli,
        mock_is_installed,
        mock_registry,
        mock_session_manager,
    ):
        """세션 모드 실행 성공 테스트"""
        # Setup
        mock_session = MagicMock()
        mock_session.cli_session_id = "session-123"
        mock_session.request_count = 1
        mock_session_manager.return_value.create_or_get_session.return_value = mock_session

        mock_registry.return_value.get_all_clis.return_value = {
            "claude": {
                "command": "claude",
                "timeout": 30,
                "supported_args": ["--session-id", "--resume"],  # 세션 인자 지원 추가
            }
        }
        mock_is_installed.return_value = True
        mock_mkstemp.side_effect = [(1, "/tmp/in"), (2, "/tmp/out")]

        mock_file_handle = MagicMock()
        mock_fdopen.return_value.__enter__.return_value = mock_file_handle
        mock_file_open.return_value.__enter__.return_value.read.return_value = "Session Response"

        # Execute
        execute_with_session(
            cli_name="claude", message="Hello", session_id="user-session-1", resume=False
        )

        # Verify
        mock_session_manager.return_value.create_or_get_session.assert_called_with(
            "user-session-1", "claude"
        )
        mock_execute_cli.assert_called()

        # 세션 인자가 포함되었는지 확인 (claude, first request -> --session-id)
        call_args = mock_execute_cli.call_args
        additional_args = call_args[1]["additional_args"]
        assert "--session-id" in additional_args
        assert "session-123" in additional_args

    @patch("other_agents_mcp.file_handler.get_session_manager")
    @patch("other_agents_mcp.file_handler.get_cli_registry")
    def test_execute_with_session_cli_not_found(self, mock_registry, mock_session_manager):
        """세션 모드: 알 수 없는 CLI"""
        mock_registry.return_value.get_all_clis.return_value = {}

        with pytest.raises(CLINotFoundError):
            execute_with_session(cli_name="unknown", message="test", session_id="sid")

    @patch("other_agents_mcp.file_handler.get_session_manager")
    @patch("other_agents_mcp.file_handler.get_cli_registry")
    @patch("other_agents_mcp.file_handler.is_cli_installed")
    def test_execute_with_session_cli_not_installed(
        self, mock_is_installed, mock_registry, mock_session_manager
    ):
        """세션 모드: CLI 미설치"""
        mock_registry.return_value.get_all_clis.return_value = {
            "claude": {"command": "claude", "timeout": 30}
        }
        mock_is_installed.return_value = False

        with pytest.raises(CLINotFoundError):
            execute_with_session(cli_name="claude", message="test", session_id="sid")

    @patch("other_agents_mcp.file_handler.get_session_manager")
    @patch("other_agents_mcp.file_handler.get_cli_registry")
    @patch("other_agents_mcp.file_handler.is_cli_installed")
    @patch("other_agents_mcp.file_handler._execute_cli")
    @patch("other_agents_mcp.file_handler._cleanup_temp_files")
    @patch("tempfile.mkstemp")
    @patch("os.fdopen")
    @patch("os.close")
    @patch("builtins.open")
    @patch("yaml.dump")
    def test_execute_with_session_yaml_prompt(
        self,
        mock_yaml_dump,
        mock_file_open,
        mock_close,
        mock_fdopen,
        mock_mkstemp,
        mock_cleanup,
        mock_execute_cli,
        mock_is_installed,
        mock_registry,
        mock_session_manager,
    ):
        """세션 모드: YAML 시스템 프롬프트 (Gemini)"""
        mock_session = MagicMock()
        mock_session.cli_session_id = "session-gemini"
        mock_session.request_count = 2  # Not first request
        mock_session_manager.return_value.create_or_get_session.return_value = mock_session

        mock_registry.return_value.get_all_clis.return_value = {
            "gemini": {
                "command": "gemini",
                "timeout": 30,
                "supported_args": ["--resume"],  # 세션 인자 지원 추가
            }
        }
        mock_is_installed.return_value = True
        mock_mkstemp.side_effect = [(1, "/tmp/in"), (2, "/tmp/out")]

        mock_file_handle = MagicMock()
        mock_fdopen.return_value.__enter__.return_value = mock_file_handle
        mock_file_open.return_value.__enter__.return_value.read.return_value = "Response"

        execute_with_session(
            cli_name="gemini",
            message="Msg",
            session_id="sid",
            resume=True,
            system_prompt="SysPrompt",
        )

        # YAML dump 확인
        mock_yaml_dump.assert_called()

        # 세션 인자 확인 (gemini, resume, not first -> --resume latest)
        additional_args = mock_execute_cli.call_args[1]["additional_args"]
        assert "--resume" in additional_args
        assert "latest" in additional_args

    @patch("other_agents_mcp.file_handler.get_cli_registry")
    @patch("other_agents_mcp.file_handler.is_cli_installed")
    @patch("other_agents_mcp.file_handler._execute_cli")
    @patch("other_agents_mcp.file_handler._cleanup_temp_files")
    @patch("tempfile.mkstemp")
    @patch("os.fdopen")
    @patch("os.close")
    @patch("builtins.open")
    def test_execute_cli_file_based_claude_system_prompt(
        self,
        mock_file_open,
        mock_close,
        mock_fdopen,
        mock_mkstemp,
        mock_cleanup,
        mock_execute_cli,
        mock_is_installed,
        mock_registry,
    ):
        # Setup
        mock_registry.return_value.get_all_clis.return_value = {
            "claude": {"command": "claude", "timeout": 30}
        }
        mock_is_installed.return_value = True
        mock_mkstemp.side_effect = [(1, "/tmp/in"), (2, "/tmp/out")]

        # File mocking
        mock_file_handle = MagicMock()
        mock_fdopen.return_value.__enter__.return_value = mock_file_handle
        mock_file_open.return_value.__enter__.return_value.read.return_value = "Response"

        # Execute
        execute_cli_file_based(
            cli_name="claude", message="User message", system_prompt="System prompt"
        )

        # Verify: 파일에는 User message만 쓰여야 함
        mock_file_handle.write.assert_called_with("User message")

        # _execute_cli에는 system_prompt가 인자로 전달되어야 함
        args = mock_execute_cli.call_args[1]
        assert args["system_prompt"] == "System prompt"

    @patch("other_agents_mcp.file_handler.get_cli_registry")
    @patch("other_agents_mcp.file_handler.is_cli_installed")
    @patch("other_agents_mcp.file_handler._execute_cli")
    @patch("other_agents_mcp.file_handler._cleanup_temp_files")
    @patch("tempfile.mkstemp")
    @patch("os.fdopen")
    @patch("os.close")
    @patch("builtins.open")
    @patch("yaml.dump")
    def test_execute_cli_file_based_yaml_system_prompt(
        self,
        mock_yaml_dump,
        mock_file_open,
        mock_close,
        mock_fdopen,
        mock_mkstemp,
        mock_cleanup,
        mock_execute_cli,
        mock_is_installed,
        mock_registry,
    ):
        # Setup
        mock_registry.return_value.get_all_clis.return_value = {
            "gemini": {"command": "gemini", "timeout": 30}
        }
        mock_is_installed.return_value = True
        mock_mkstemp.side_effect = [(1, "/tmp/in"), (2, "/tmp/out")]

        mock_file_handle = MagicMock()
        mock_fdopen.return_value.__enter__.return_value = mock_file_handle
        mock_file_open.return_value.__enter__.return_value.read.return_value = "Response"

        # Execute
        execute_cli_file_based(
            cli_name="gemini", message="User message", system_prompt="System prompt"
        )

        # Verify: yaml.dump가 호출되어야 함
        mock_yaml_dump.assert_called()
        call_args = mock_yaml_dump.call_args
        data = call_args[0][0]
        assert data["system_prompt"] == "System prompt"
        assert data["prompt"] == "User message"

    def test_validate_and_filter_args_empty(self):
        assert _validate_and_filter_args("test", [], {}) == []
        assert _validate_and_filter_args("test", ["--flag"], {}) == []

    def test_validate_and_filter_args_complex(self):
        config = {"supported_args": ["--model", "--verbose", "-n"]}
        args = ["--model", "gpt-4", "--verbose", "--unknown", "value", "-n", "10", "standalone"]

        result = _validate_and_filter_args("test", args, config)

        assert "--model" in result
        assert "gpt-4" in result
        assert "--verbose" in result
        assert "--unknown" not in result
        assert "-n" in result
        assert "10" in result
        assert "standalone" in result

    @patch("subprocess.run")
    @patch("builtins.open")
    @patch("os.environ")
    def test_execute_cli_claude_flags(self, mock_environ, mock_open, mock_run):
        mock_environ.copy.return_value = {}
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        _execute_cli(
            command="claude",
            extra_args=[],
            env_vars={},
            input_path="/tmp/in",
            output_path="/tmp/out",
            timeout=30,
            cli_name="claude",
            system_prompt="System Prompt",
        )

        call_args = mock_run.call_args
        cmd = call_args[0][0]

        assert "--print" in cmd
        assert "--append-system-prompt" in cmd
        assert "System Prompt" in cmd

    @patch("subprocess.run")
    @patch("builtins.open")
    @patch("os.environ")
    def test_execute_cli_skip_git_before(self, mock_environ, mock_open, mock_run):
        mock_environ.copy.return_value = {}
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        _execute_cli(
            command="codex",
            extra_args=["exec", "-"],
            env_vars={},
            input_path="/tmp/in",
            output_path="/tmp/out",
            timeout=30,
            skip_git_repo_check=True,
            supports_skip_git_check=True,
            skip_git_check_position="before_extra_args",
        )

        cmd = mock_run.call_args[0][0]
        idx_skip = cmd.index("--skip-git-repo-check")
        idx_exec = cmd.index("exec")
        assert idx_skip < idx_exec

    @patch("subprocess.run")
    @patch("builtins.open")
    @patch("os.environ")
    def test_execute_cli_skip_git_after(self, mock_environ, mock_open, mock_run):
        mock_environ.copy.return_value = {}
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        _execute_cli(
            command="codex",
            extra_args=["exec", "-"],
            env_vars={},
            input_path="/tmp/in",
            output_path="/tmp/out",
            timeout=30,
            skip_git_repo_check=True,
            supports_skip_git_check=True,
            skip_git_check_position="after_extra_args",
        )

        cmd = mock_run.call_args[0][0]
        idx_exec = cmd.index("exec")
        idx_skip = cmd.index("--skip-git-repo-check")
        assert idx_exec < idx_skip

    @patch("subprocess.run")
    @patch("builtins.open")
    @patch("os.environ")
    def test_execute_cli_error_return_code(self, mock_environ, mock_open, mock_run):
        mock_environ.copy.return_value = {}
        mock_run.return_value = MagicMock(returncode=1, stderr="Error Occurred")

        with pytest.raises(CLIExecutionError) as exc:
            _execute_cli(
                command="test",
                extra_args=[],
                env_vars={},
                input_path="/in",
                output_path="/out",
                timeout=30,
            )

        assert "Error Occurred" in str(exc.value)

    @patch("subprocess.run")
    @patch("builtins.open")
    @patch("os.environ")
    def test_execute_cli_error_no_stderr(self, mock_environ, mock_open, mock_run):
        """stderr가 없는 에러 케이스"""
        mock_environ.copy.return_value = {}
        mock_run.return_value = MagicMock(returncode=1, stderr=None)

        with pytest.raises(CLIExecutionError) as exc:
            _execute_cli(
                command="test",
                extra_args=[],
                env_vars={},
                input_path="/in",
                output_path="/out",
                timeout=30,
            )

        assert "알 수 없는 에러" in str(exc.value)

    @patch("subprocess.run")
    @patch("builtins.open")
    @patch("os.environ")
    def test_execute_cli_file_not_found(self, mock_environ, mock_open, mock_run):
        mock_environ.copy.return_value = {}
        mock_run.side_effect = FileNotFoundError

        with pytest.raises(CLINotFoundError):
            _execute_cli(
                command="unknown",
                extra_args=[],
                env_vars={},
                input_path="/in",
                output_path="/out",
                timeout=30,
            )

    def test_build_session_args(self):
        assert _build_session_args("claude", "sid", False, True) == ["--session-id", "sid"]
        assert _build_session_args("claude", "sid", True, False) == ["--resume", "sid"]

        assert _build_session_args("gemini", "sid", False, True) == []
        assert _build_session_args("gemini", "sid", True, False) == ["--resume", "latest"]

        assert _build_session_args("codex", "sid", True, False) == []

    @patch("os.remove")
    @patch("os.path.exists")
    def test_cleanup_temp_files_error(self, mock_exists, mock_remove):
        mock_exists.return_value = True
        mock_remove.side_effect = OSError("Cannot delete")

        _cleanup_temp_files("/tmp/file1")

        mock_remove.assert_called_once()
