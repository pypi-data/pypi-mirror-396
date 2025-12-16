"""
Global Configurations
"""

import os
from pathlib import Path
from typing import TypedDict, Literal


# --- Task Manager Configuration ---
# STORAGE_TYPE: "memory" 또는 "sqlite"
# MCP_STORAGE_TYPE 환경 변수로 오버라이드 가능
STORAGE_TYPE: Literal["memory", "sqlite"] = os.environ.get("MCP_STORAGE_TYPE", "memory")

# SQLite 데이터베이스 경로
# 프로젝트 루트의 .data 폴더에 저장
SQLITE_DB_PATH = Path(__file__).parent.parent.parent / ".data" / "tasks.db"


class CLIConfig(TypedDict):
    """CLI 설정 타입"""

    command: str
    timeout: int
    extra_args: list[str]
    env_vars: dict[str, str]  # 환경 변수
    supports_skip_git_check: bool  # --skip-git-repo-check 플래그 지원 여부
    skip_git_check_position: str  # 플래그 위치: "before_extra_args" 또는 "after_extra_args"
    supported_args: list[str]  # 지원하는 CLI 인자 목록


# CLI별 설정
CLI_CONFIGS: dict[str, CLIConfig] = {
    "claude": {
        "command": "claude",
        "extra_args": [],
        "timeout": 1800,
        "env_vars": {},
        "supports_skip_git_check": False,
        "skip_git_check_position": "before_extra_args",
        "supported_args": [
            "--system-prompt",
            "--append-system-prompt",
            "--print",
            "--model",
            "--debug",
            "--tools",
            "--allowed-tools",
            "--disallowed-tools",
            "--mcp-config",
            "--settings",
            "--permission-mode",
            "--continue",
            "--resume",
            "--output-format",
        ],
    },
    "gemini": {
        "command": "gemini",
        "extra_args": [],
        "timeout": 1800,
        "env_vars": {},
        "supports_skip_git_check": False,
        "skip_git_check_position": "before_extra_args",
        "supported_args": [
            "--model",
            "--approval-mode",
            "--allowed-mcp-server-names",
            "--allowed-tools",
            "--extensions",
            "--output-format",
            "--debug",
            "--sandbox",
            "--yolo",
            "--include-directories",
            "--list-extensions",
            "--resume",
            "--list-sessions",
            "--delete-session",
        ],
    },
    "codex": {
        "command": "codex",
        "extra_args": ["exec", "-"],
        "timeout": 1800,
        "env_vars": {},
        "supports_skip_git_check": True,
        "skip_git_check_position": "after_extra_args",  # codex exec --skip-git-repo-check -
        "supported_args": [
            "--skip-git-repo-check",
            "--model",
            "--sandbox",
            "--config",
            "--enable",
            "--disable",
            "--json",
            "--output-schema",
            "--color",
            "--image",
            "--profile",
            "--full-auto",
            "--cd",
            "--add-dir",
            "--output-last-message",
        ],
    },
    "qwen": {
        "command": "qwen",
        "extra_args": [],
        "timeout": 1800,
        "env_vars": {
            "OPENAI_BASE_URL": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            "OPENAI_MODEL": "qwen3-coder-plus",
        },
        "supports_skip_git_check": False,
        "skip_git_check_position": "before_extra_args",
        "supported_args": [
            "--model",
            "--approval-mode",
            "--allowed-mcp-server-names",
            "--allowed-tools",
            "--extensions",
            "--output-format",
            "--debug",
            "--sandbox",
            "--yolo",
            "--include-directories",
            "--openai-api-key",
            "--openai-base-url",
            "--tavily-api-key",
            "--google-api-key",
            "--google-search-engine-id",
            "--web-search-default",
        ],
    },
}
