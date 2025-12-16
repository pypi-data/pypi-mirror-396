"""CLI Manager Coverage Tests

cli_manager.py의 미커버 라인 테스트
- 107-140: check_cli_auth 함수
- 174: list_available_clis의 authenticated 할당
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock

from other_agents_mcp.cli_manager import (
    check_cli_auth,
    list_available_clis,
    is_cli_installed,
    CLIInfo,
)


class TestCheckCliAuth:
    """check_cli_auth 함수 테스트"""

    def test_cli_not_installed(self):
        """설치되지 않은 CLI"""
        with patch("other_agents_mcp.cli_manager.is_cli_installed") as mock_installed:
            mock_installed.return_value = False

            result = check_cli_auth("nonexistent")
            assert result is None

    def test_auth_success(self):
        """인증 성공"""
        with patch("other_agents_mcp.cli_manager.is_cli_installed") as mock_installed, \
             patch("subprocess.run") as mock_run:

            mock_installed.return_value = True
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Hello!",
                stderr=""
            )

            result = check_cli_auth("claude")
            assert result is True

    def test_auth_failure_keyword_detected(self):
        """인증 실패 키워드 감지"""
        with patch("other_agents_mcp.cli_manager.is_cli_installed") as mock_installed, \
             patch("subprocess.run") as mock_run:

            mock_installed.return_value = True
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="unauthorized access denied"
            )

            result = check_cli_auth("claude")
            assert result is False

    def test_auth_failure_api_key_required(self):
        """API 키 필요 메시지"""
        with patch("other_agents_mcp.cli_manager.is_cli_installed") as mock_installed, \
             patch("subprocess.run") as mock_run:

            mock_installed.return_value = True
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="Please set your api key",  # "api key" (소문자, 공백) - AUTH_FAILURE_KEYWORDS 매칭
                stderr=""
            )

            result = check_cli_auth("gemini")
            assert result is False

    def test_auth_failure_login_required(self):
        """로그인 필요 메시지"""
        with patch("other_agents_mcp.cli_manager.is_cli_installed") as mock_installed, \
             patch("subprocess.run") as mock_run:

            mock_installed.return_value = True
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="login required to continue",
                stderr=""
            )

            result = check_cli_auth("codex")
            assert result is False

    def test_auth_non_zero_no_keyword(self):
        """비정상 종료 but 인증 키워드 없음"""
        with patch("other_agents_mcp.cli_manager.is_cli_installed") as mock_installed, \
             patch("subprocess.run") as mock_run:

            mock_installed.return_value = True
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="Some other error",
                stderr=""
            )

            result = check_cli_auth("claude")
            assert result is None

    def test_auth_timeout(self):
        """타임아웃 발생"""
        with patch("other_agents_mcp.cli_manager.is_cli_installed") as mock_installed, \
             patch("subprocess.run") as mock_run:

            mock_installed.return_value = True
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=10)

            result = check_cli_auth("claude")
            assert result is None

    def test_auth_exception(self):
        """일반 예외 발생"""
        with patch("other_agents_mcp.cli_manager.is_cli_installed") as mock_installed, \
             patch("subprocess.run") as mock_run:

            mock_installed.return_value = True
            mock_run.side_effect = Exception("Unknown error")

            result = check_cli_auth("claude")
            assert result is None


class TestListAvailableClisWithAuth:
    """list_available_clis의 check_auth 옵션 테스트"""

    def test_list_with_check_auth_true(self):
        """check_auth=True일 때 인증 상태 확인"""
        with patch("other_agents_mcp.cli_manager.get_cli_registry") as mock_registry, \
             patch("other_agents_mcp.cli_manager.is_cli_installed") as mock_installed, \
             patch("other_agents_mcp.cli_manager.get_cli_version") as mock_version, \
             patch("other_agents_mcp.cli_manager.check_cli_auth") as mock_auth:

            # 레지스트리 모킹
            mock_reg_instance = MagicMock()
            mock_reg_instance.get_all_clis.return_value = {
                "claude": {"command": "claude"},
                "gemini": {"command": "gemini"},
            }
            mock_registry.return_value = mock_reg_instance

            # 설치 및 버전 모킹
            mock_installed.return_value = True
            mock_version.return_value = "1.0.0"

            # 인증 상태 모킹
            mock_auth.side_effect = [True, False]  # claude: 인증됨, gemini: 인증 필요

            clis = list_available_clis(check_auth=True)

            assert len(clis) == 2
            assert mock_auth.call_count == 2

            claude_cli = next(c for c in clis if c.name == "claude")
            gemini_cli = next(c for c in clis if c.name == "gemini")

            assert claude_cli.authenticated is True
            assert gemini_cli.authenticated is False

    def test_list_with_check_auth_false(self):
        """check_auth=False일 때 인증 상태 확인 안함"""
        with patch("other_agents_mcp.cli_manager.get_cli_registry") as mock_registry, \
             patch("other_agents_mcp.cli_manager.is_cli_installed") as mock_installed, \
             patch("other_agents_mcp.cli_manager.get_cli_version") as mock_version, \
             patch("other_agents_mcp.cli_manager.check_cli_auth") as mock_auth:

            mock_reg_instance = MagicMock()
            mock_reg_instance.get_all_clis.return_value = {
                "claude": {"command": "claude"},
            }
            mock_registry.return_value = mock_reg_instance

            mock_installed.return_value = True
            mock_version.return_value = "1.0.0"

            clis = list_available_clis(check_auth=False)

            # check_auth 호출 안됨
            mock_auth.assert_not_called()
            assert clis[0].authenticated is None

    def test_list_with_uninstalled_cli_no_auth_check(self):
        """설치되지 않은 CLI는 인증 확인 안함"""
        with patch("other_agents_mcp.cli_manager.get_cli_registry") as mock_registry, \
             patch("other_agents_mcp.cli_manager.is_cli_installed") as mock_installed, \
             patch("other_agents_mcp.cli_manager.get_cli_version") as mock_version, \
             patch("other_agents_mcp.cli_manager.check_cli_auth") as mock_auth:

            mock_reg_instance = MagicMock()
            mock_reg_instance.get_all_clis.return_value = {
                "uninstalled_cli": {"command": "uninstalled"},
            }
            mock_registry.return_value = mock_reg_instance

            mock_installed.return_value = False

            clis = list_available_clis(check_auth=True)

            # 설치 안됐으므로 인증 확인 안함
            mock_auth.assert_not_called()
            assert clis[0].authenticated is None
            assert clis[0].installed is False


class TestAuthKeywords:
    """인증 실패 키워드 테스트"""

    # AUTH_FAILURE_KEYWORDS = ['login', 'authenticate', 'unauthorized', '401', 'sign in', 'api key', 'token', 'credential']
    @pytest.mark.parametrize("keyword", [
        "unauthorized",
        "authenticate",
        "api key",
        "token",
        "credential",
        "login",
        "sign in",
        "401",
    ])
    def test_auth_failure_keywords(self, keyword):
        """다양한 인증 실패 키워드 감지"""
        with patch("other_agents_mcp.cli_manager.is_cli_installed") as mock_installed, \
             patch("subprocess.run") as mock_run:

            mock_installed.return_value = True
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout=f"Error: {keyword} issue detected",
                stderr=""
            )

            result = check_cli_auth("test_cli")
            assert result is False
