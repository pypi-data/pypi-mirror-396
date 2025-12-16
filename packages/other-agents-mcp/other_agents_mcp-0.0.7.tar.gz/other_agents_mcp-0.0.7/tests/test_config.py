"""Tests for config module"""

from other_agents_mcp.config import CLI_CONFIGS


class TestCLIConfigs:
    """Test CLI_CONFIGS dictionary"""

    def test_cli_configs_exists(self):
        """CLI_CONFIGS 딕셔너리가 존재해야 함"""
        assert CLI_CONFIGS is not None
        assert isinstance(CLI_CONFIGS, dict)

    def test_cli_configs_has_all_clis(self):
        """4개 CLI (claude, gemini, codex, qwen) 설정이 존재해야 함"""
        required_clis = ["claude", "gemini", "codex", "qwen"]
        for cli_name in required_clis:
            assert cli_name in CLI_CONFIGS, f"{cli_name} 설정이 없습니다"

    def test_cli_config_structure(self):
        """각 CLI 설정이 필수 필드를 포함해야 함"""

        for cli_name, config in CLI_CONFIGS.items():
            assert "command" in config, f"{cli_name}: command 필드 없음"
            assert "timeout" in config, f"{cli_name}: timeout 필드 없음"
            assert "extra_args" in config, f"{cli_name}: extra_args 필드 없음"
            assert "env_vars" in config, f"{cli_name}: env_vars 필드 없음"

            # timeout은 양수
            assert isinstance(config["timeout"], int), f"{cli_name}: timeout은 정수여야 함"
            assert config["timeout"] > 0, f"{cli_name}: timeout은 양수여야 함"

            # extra_args는 리스트
            assert isinstance(config["extra_args"], list), f"{cli_name}: extra_args는 리스트여야 함"

            # env_vars는 딕셔너리
            assert isinstance(config["env_vars"], dict), f"{cli_name}: env_vars는 딕셔너리여야 함"

    def test_claude_config(self):
        """Claude CLI 설정 검증"""
        claude = CLI_CONFIGS["claude"]
        assert claude["command"] == "claude"
        assert claude["timeout"] == 1800
        assert claude["extra_args"] == []
        assert claude["env_vars"] == {}

    def test_gemini_config(self):
        """Gemini CLI 설정 검증"""
        gemini = CLI_CONFIGS["gemini"]
        assert gemini["command"] == "gemini"
        assert gemini["timeout"] == 1800
        assert gemini["env_vars"] == {}

    def test_codex_config(self):
        """Codex CLI 설정 검증"""
        codex = CLI_CONFIGS["codex"]
        assert codex["command"] == "codex"
        assert codex["timeout"] == 1800
        assert "exec" in codex["extra_args"]

    def test_qwen_config(self):
        """Qwen CLI 설정 검증"""
        qwen = CLI_CONFIGS["qwen"]
        assert qwen["command"] == "qwen"
        assert qwen["timeout"] == 1800
        # Qwen은 환경 변수 필요
        assert "OPENAI_BASE_URL" in qwen["env_vars"]
        assert "OPENAI_MODEL" in qwen["env_vars"]
