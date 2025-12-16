"""Security Validation 테스트

보안 검증 함수들에 대한 테스트
"""

import pytest

from other_agents_mcp.file_handler import (
    validate_timeout,
    validate_system_prompt,
    validate_env_vars,
    sanitize_arg_value,
    MIN_TIMEOUT,
    MAX_TIMEOUT,
    MAX_SYSTEM_PROMPT_LENGTH,
)


class TestValidateTimeout:
    """validate_timeout 함수 테스트"""

    def test_none_returns_none(self):
        """None 입력 시 None 반환"""
        assert validate_timeout(None) is None

    def test_valid_timeout(self):
        """유효한 타임아웃 값"""
        assert validate_timeout(60) == 60
        assert validate_timeout(1800) == 1800
        assert validate_timeout(MIN_TIMEOUT) == MIN_TIMEOUT
        assert validate_timeout(MAX_TIMEOUT) == MAX_TIMEOUT

    def test_float_converted_to_int(self):
        """float 값이 int로 변환됨"""
        assert validate_timeout(60.5) == 60

    def test_timeout_too_small(self):
        """타임아웃이 너무 작을 때 ValueError"""
        with pytest.raises(ValueError, match="범위"):
            validate_timeout(0)
        with pytest.raises(ValueError, match="범위"):
            validate_timeout(-1)

    def test_timeout_too_large(self):
        """타임아웃이 너무 클 때 ValueError"""
        with pytest.raises(ValueError, match="범위"):
            validate_timeout(MAX_TIMEOUT + 1)
        with pytest.raises(ValueError, match="범위"):
            validate_timeout(999999)

    def test_invalid_type(self):
        """잘못된 타입일 때 ValueError"""
        with pytest.raises(ValueError, match="숫자"):
            validate_timeout("60")
        with pytest.raises(ValueError, match="숫자"):
            validate_timeout([60])


class TestValidateSystemPrompt:
    """validate_system_prompt 함수 테스트"""

    def test_none_returns_none(self):
        """None 입력 시 None 반환"""
        assert validate_system_prompt(None) is None

    def test_valid_prompt(self):
        """유효한 시스템 프롬프트"""
        prompt = "You are a helpful assistant."
        assert validate_system_prompt(prompt) == prompt

    def test_empty_string(self):
        """빈 문자열도 유효"""
        assert validate_system_prompt("") == ""

    def test_prompt_too_long(self):
        """프롬프트가 너무 길 때 ValueError"""
        long_prompt = "x" * (MAX_SYSTEM_PROMPT_LENGTH + 1)
        with pytest.raises(ValueError, match="너무 깁니다"):
            validate_system_prompt(long_prompt)

    def test_max_length_prompt(self):
        """최대 길이 프롬프트는 유효"""
        max_prompt = "x" * MAX_SYSTEM_PROMPT_LENGTH
        assert validate_system_prompt(max_prompt) == max_prompt

    def test_invalid_type(self):
        """잘못된 타입일 때 ValueError"""
        with pytest.raises(ValueError, match="문자열"):
            validate_system_prompt(123)
        with pytest.raises(ValueError, match="문자열"):
            validate_system_prompt(["prompt"])


class TestValidateEnvVars:
    """validate_env_vars 함수 테스트"""

    def test_none_returns_empty_dict(self):
        """None 입력 시 빈 딕셔너리 반환"""
        assert validate_env_vars(None) == {}

    def test_empty_dict_returns_empty_dict(self):
        """빈 딕셔너리 입력 시 빈 딕셔너리 반환"""
        assert validate_env_vars({}) == {}

    def test_allowed_env_vars(self):
        """허용된 환경 변수는 통과"""
        env_vars = {"OPENAI_API_KEY": "sk-xxx", "OPENAI_BASE_URL": "https://api.openai.com"}
        result = validate_env_vars(env_vars)
        assert result == env_vars

    def test_blocked_env_vars_removed(self):
        """차단된 환경 변수는 제거됨"""
        env_vars = {"PATH": "/usr/bin", "LD_PRELOAD": "/tmp/evil.so", "OPENAI_API_KEY": "sk-xxx"}
        result = validate_env_vars(env_vars)
        assert "PATH" not in result
        assert "LD_PRELOAD" not in result
        assert "OPENAI_API_KEY" in result

    def test_unknown_env_vars_allowed(self):
        """알려지지 않은 환경 변수도 허용 (블랙리스트만 차단)"""
        env_vars = {"CUSTOM_VAR": "value", "MY_API_KEY": "xxx"}
        result = validate_env_vars(env_vars)
        assert result == env_vars

    def test_case_insensitive_blocking(self):
        """블랙리스트 체크는 대소문자 무시"""
        env_vars = {
            "path": "/usr/bin",  # 소문자
            "Path": "/usr/bin",  # 혼합
        }
        result = validate_env_vars(env_vars)
        assert "path" not in result
        assert "Path" not in result


class TestSanitizeArgValue:
    """sanitize_arg_value 함수 테스트"""

    def test_valid_values(self):
        """안전한 값은 그대로 반환"""
        assert sanitize_arg_value("claude-3") == "claude-3"
        assert sanitize_arg_value("model_name") == "model_name"
        assert sanitize_arg_value("100") == "100"
        assert sanitize_arg_value("path/to/file") == "path/to/file"

    def test_semicolon_blocked(self):
        """세미콜론 포함 시 ValueError"""
        with pytest.raises(ValueError, match="허용되지 않는 문자"):
            sanitize_arg_value("value; rm -rf /")

    def test_pipe_blocked(self):
        """파이프 포함 시 ValueError"""
        with pytest.raises(ValueError, match="허용되지 않는 문자"):
            sanitize_arg_value("value | cat /etc/passwd")

    def test_ampersand_blocked(self):
        """앰퍼샌드 포함 시 ValueError"""
        with pytest.raises(ValueError, match="허용되지 않는 문자"):
            sanitize_arg_value("value && echo hacked")

    def test_backtick_blocked(self):
        """백틱 포함 시 ValueError"""
        with pytest.raises(ValueError, match="허용되지 않는 문자"):
            sanitize_arg_value("`whoami`")

    def test_dollar_sign_blocked(self):
        """달러 기호 포함 시 ValueError"""
        with pytest.raises(ValueError, match="허용되지 않는 문자"):
            sanitize_arg_value("$(cat /etc/passwd)")

    def test_newline_blocked(self):
        """개행 문자 포함 시 ValueError"""
        with pytest.raises(ValueError, match="허용되지 않는 문자"):
            sanitize_arg_value("value\ninjected")

    def test_quotes_blocked(self):
        """따옴표 포함 시 ValueError"""
        with pytest.raises(ValueError, match="허용되지 않는 문자"):
            sanitize_arg_value('value"injected')
        with pytest.raises(ValueError, match="허용되지 않는 문자"):
            sanitize_arg_value("value'injected")
