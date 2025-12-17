"""Tests for cli_manager module"""

import subprocess
import pytest
from other_agents_mcp.cli_manager import (
    CLIInfo,
    list_available_clis,
    get_cli_version,
    is_cli_installed,
    check_cli_auth,
)


class TestCLIInfo:
    """Test CLIInfo dataclass"""

    def test_cli_info_creation(self):
        """CLIInfo 데이터클래스 생성 테스트"""
        cli_info = CLIInfo(name="test", command="test-cli", version="1.0.0", installed=True)
        assert cli_info.name == "test"
        assert cli_info.command == "test-cli"
        assert cli_info.version == "1.0.0"
        assert cli_info.installed is True

    def test_cli_info_with_none_version(self):
        """버전 정보가 없는 경우"""
        cli_info = CLIInfo(name="test", command="test-cli", version=None, installed=False)
        assert cli_info.version is None
        assert cli_info.installed is False


class TestIsCliInstalled:
    """Test is_cli_installed function"""

    def test_installed_cli(self, mocker):
        """설치된 CLI 감지"""
        mocker.patch("shutil.which", return_value="/usr/bin/some_cli")
        assert is_cli_installed("some_cli") is True

    def test_uninstalled_cli(self, mocker):
        """미설치 CLI 감지"""
        mocker.patch("shutil.which", return_value=None)
        assert is_cli_installed("nonexistent-cli-12345") is False


class TestGetCliVersion:
    """Test get_cli_version function"""

    def test_get_version_success(self, mocker):
        """버전 정보 조회 성공"""
        # 'is_cli_installed'가 True를 반환하도록 모킹하여 함수가 조기 종료되는 것을 방지
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)

        mock_process = mocker.Mock()
        mock_process.stdout = "some-cli version 1.2.3"
        mock_process.stderr = ""  # stderr도 명시적으로 설정
        mock_process.returncode = 0
        mocker.patch("subprocess.run", return_value=mock_process)

        version = get_cli_version("any-cli")
        assert version == "some-cli version 1.2.3"

    def test_get_version_failure_subprocess_error(self, mocker):
        """버전 정보 조회 실패 (subprocess 예외)"""
        mocker.patch("subprocess.run", side_effect=FileNotFoundError)
        version = get_cli_version("nonexistent-cli-12345")
        assert version is None

    def test_get_version_failure_non_zero_exit(self, mocker):
        """버전 정보 조회 실패 (non-zero exit code)"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)
        mock_process = mocker.Mock()
        mock_process.stderr = "command not found"
        mock_process.returncode = 1
        mocker.patch("subprocess.run", return_value=mock_process)

        version = get_cli_version("failing-cli")
        assert version is None

    def test_get_version_timeout_expired(self, mocker):
        """버전 정보 조회 실패 (타임아웃)"""
        import subprocess

        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)
        mocker.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="test", timeout=5))

        version = get_cli_version("slow-cli")
        assert version is None

    def test_get_version_file_not_found(self, mocker):
        """버전 정보 조회 실패 (FileNotFoundError)"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)
        mocker.patch("subprocess.run", side_effect=FileNotFoundError("command not found"))

        version = get_cli_version("missing-cli")
        assert version is None

    def test_get_version_generic_exception(self, mocker):
        """버전 정보 조회 실패 (일반 예외)"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)
        mocker.patch("subprocess.run", side_effect=Exception("unexpected error"))

        version = get_cli_version("error-cli")
        assert version is None


@pytest.mark.usefixtures("reset_cli_registry")
class TestListAvailableClis:
    """Test list_available_clis function"""

    def test_returns_list_of_cli_info_objects(self, mocker):
        """반환값이 CLIInfo 객체들의 리스트인지 확인"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)
        mocker.patch("other_agents_mcp.cli_manager.get_cli_version", return_value="1.0.0")
        clis = list_available_clis()
        assert isinstance(clis, list)
        assert (
            len(clis) >= 4
        )  # 최소 claude, gemini, codex, qwen (다른 테스트에서 추가된 CLI 포함 가능)
        for cli in clis:
            assert isinstance(cli, CLIInfo)

    def test_includes_all_configured_clis(self, mocker):
        """config에 정의된 모든 CLI 포함"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=False)
        clis = list_available_clis()
        cli_names = {cli.name for cli in clis}
        expected_names = {"claude", "gemini", "codex", "qwen"}
        assert expected_names.issubset(cli_names)  # 최소한 기본 CLI들은 포함되어야 함

    def test_installed_and_uninstalled_clis(self, mocker):
        """설치된 CLI와 미설치된 CLI를 정확히 반영하는지 테스트"""

        def mock_is_installed(command: str) -> bool:
            # 'claude'와 'gemini'만 설치된 것으로 시뮬레이션
            return command in ["claude", "gemini"]

        def mock_get_version(command: str) -> str | None:
            if command == "claude":
                return "v1.0-claude"
            if command == "gemini":
                return "v2.0-gemini"
            return None

        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", side_effect=mock_is_installed)
        mocker.patch("other_agents_mcp.cli_manager.get_cli_version", side_effect=mock_get_version)

        clis = list_available_clis()
        cli_map = {cli.name: cli for cli in clis}

        assert cli_map["claude"].installed is True
        assert cli_map["claude"].version == "v1.0-claude"

        assert cli_map["gemini"].installed is True
        assert cli_map["gemini"].version == "v2.0-gemini"

        assert cli_map["codex"].installed is False
        assert cli_map["codex"].version is None

        assert cli_map["qwen"].installed is False
        assert cli_map["qwen"].version is None

    def test_list_clis_with_auth_check(self, mocker):
        """check_auth=True일 때 인증 상태 확인"""

        def mock_is_installed(command: str) -> bool:
            return command in ["claude", "gemini"]

        def mock_get_version(command: str) -> str | None:
            return "1.0" if command in ["claude", "gemini"] else None

        def mock_check_auth(command: str) -> bool | None:
            if command == "claude":
                return True  # 인증됨
            elif command == "gemini":
                return False  # 인증 필요
            return None

        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", side_effect=mock_is_installed)
        mocker.patch("other_agents_mcp.cli_manager.get_cli_version", side_effect=mock_get_version)
        mocker.patch("other_agents_mcp.cli_manager.check_cli_auth", side_effect=mock_check_auth)

        clis = list_available_clis(check_auth=True)
        cli_map = {cli.name: cli for cli in clis}

        # 설치된 CLI만 인증 상태 확인
        assert cli_map["claude"].authenticated is True
        assert cli_map["gemini"].authenticated is False
        # 미설치 CLI는 인증 확인 안 함
        assert cli_map["codex"].authenticated is None


class TestCheckCliAuth:
    """Test check_cli_auth function"""

    def test_not_installed_returns_none(self, mocker):
        """미설치 CLI는 None 반환"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=False)
        result = check_cli_auth("nonexistent-cli")
        assert result is None

    def test_authenticated_cli(self, mocker):
        """인증된 CLI는 True 반환"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)
        mock_process = mocker.Mock()
        mock_process.stdout = "Hello! How can I help you?"
        mock_process.stderr = ""
        mock_process.returncode = 0
        mocker.patch("subprocess.run", return_value=mock_process)

        result = check_cli_auth("claude")
        assert result is True

    def test_auth_required_api_key(self, mocker):
        """API 키 필요 시 False 반환"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)
        mock_process = mocker.Mock()
        mock_process.stdout = ""
        mock_process.stderr = "Error: API key not found"
        mock_process.returncode = 1
        mocker.patch("subprocess.run", return_value=mock_process)

        result = check_cli_auth("claude")
        assert result is False

    def test_auth_required_login(self, mocker):
        """로그인 필요 시 False 반환"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)
        mock_process = mocker.Mock()
        mock_process.stdout = "Please login to continue"
        mock_process.stderr = ""
        mock_process.returncode = 1
        mocker.patch("subprocess.run", return_value=mock_process)

        result = check_cli_auth("gemini")
        assert result is False

    def test_auth_required_unauthorized(self, mocker):
        """unauthorized 에러 시 False 반환"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)
        mock_process = mocker.Mock()
        mock_process.stdout = ""
        mock_process.stderr = "unauthorized access"
        mock_process.returncode = 1
        mocker.patch("subprocess.run", return_value=mock_process)

        result = check_cli_auth("codex")
        assert result is False

    def test_auth_required_authenticate(self, mocker):
        """authenticate 에러 시 False 반환"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)
        mock_process = mocker.Mock()
        mock_process.stdout = ""
        mock_process.stderr = "please authenticate first"
        mock_process.returncode = 1
        mocker.patch("subprocess.run", return_value=mock_process)

        result = check_cli_auth("qwen")
        assert result is False

    def test_non_zero_exit_without_auth_keywords(self, mocker):
        """비정상 종료지만 인증 키워드 없으면 None 반환"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)
        mock_process = mocker.Mock()
        mock_process.stdout = ""
        mock_process.stderr = "some other error"
        mock_process.returncode = 1
        mocker.patch("subprocess.run", return_value=mock_process)

        result = check_cli_auth("cli")
        assert result is None

    def test_timeout_returns_none(self, mocker):
        """타임아웃 시 None 반환"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)
        mocker.patch(
            "subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="test", timeout=10)
        )

        result = check_cli_auth("slow-cli")
        assert result is None

    def test_exception_returns_none(self, mocker):
        """예외 발생 시 None 반환"""
        mocker.patch("other_agents_mcp.cli_manager.is_cli_installed", return_value=True)
        mocker.patch("subprocess.run", side_effect=Exception("unexpected error"))

        result = check_cli_auth("error-cli")
        assert result is None
