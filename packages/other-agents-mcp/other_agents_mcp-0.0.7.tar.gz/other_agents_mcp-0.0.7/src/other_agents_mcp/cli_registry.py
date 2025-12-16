"""CLI Registry

동적 CLI 관리 시스템
- 기본 CLI (config.py)
- 파일 기반 (custom_clis.json)
- 런타임 추가 (add_cli)
"""

import json
from pathlib import Path
from typing import Dict, Optional

from .config import CLI_CONFIGS, CLIConfig
from .logger import get_logger

logger = get_logger(__name__)


class CLIRegistry:
    """CLI 레지스트리 (싱글톤)"""

    _instance: Optional["CLIRegistry"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """초기화는 한 번만 실행"""
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._runtime_clis: Dict[str, CLIConfig] = {}
            logger.info("CLI Registry initialized")

    def get_all_clis(self) -> Dict[str, CLIConfig]:
        """
        모든 CLI 설정 반환 (3단계 병합)

        병합 우선순위: 런타임 > 파일 > 기본

        Returns:
            병합된 CLI 설정 딕셔너리
        """
        # 1. 기본 CLI (config.py)
        merged = dict(CLI_CONFIGS)
        logger.debug(f"Loaded {len(merged)} base CLIs from config.py")

        # 2. 파일 기반 (custom_clis.json)
        file_clis = self._load_from_file()
        if file_clis:
            merged.update(file_clis)
            logger.debug(f"Loaded {len(file_clis)} CLIs from custom_clis.json")

        # 3. 런타임 추가
        if self._runtime_clis:
            merged.update(self._runtime_clis)
            logger.debug(f"Loaded {len(self._runtime_clis)} runtime CLIs")

        logger.info(f"Total {len(merged)} CLIs available")
        return merged

    def add_cli(
        self,
        name: str,
        command: str,
        extra_args: Optional[list] = None,
        timeout: Optional[int] = None,
        env_vars: Optional[dict] = None,
        supports_skip_git_check: Optional[bool] = None,
        skip_git_check_position: Optional[str] = None,
        supported_args: Optional[list] = None,
    ) -> None:
        """
        런타임에 CLI 추가

        Args:
            name: CLI 이름 (필수)
            command: 실행 명령어 (필수)
            extra_args: 추가 인자 (선택, 기본값: [])
            timeout: 타임아웃 초 (선택, 기본값: 1800)
            env_vars: 환경 변수 (선택, 기본값: {})
            supports_skip_git_check: Git 체크 스킵 지원 (선택, 기본값: False)
            skip_git_check_position: 플래그 위치 (선택, 기본값: "before_extra_args")
            supported_args: 지원하는 CLI 인자 (선택, 기본값: [])
        """
        cli_config: CLIConfig = {
            "command": command,
            "timeout": timeout if timeout is not None else 1800,
            "extra_args": extra_args if extra_args is not None else [],
            "env_vars": env_vars if env_vars is not None else {},
            "supports_skip_git_check": (
                supports_skip_git_check if supports_skip_git_check is not None else False
            ),
            "skip_git_check_position": (
                skip_git_check_position
                if skip_git_check_position is not None
                else "before_extra_args"
            ),
            "supported_args": supported_args if supported_args is not None else [],
        }

        self._runtime_clis[name] = cli_config
        logger.info(f"Added runtime CLI: {name} -> {command}")

    def _load_from_file(self) -> Dict[str, CLIConfig]:
        """custom_clis.json 파일에서 CLI 로드"""
        config_path = Path(__file__).parent.parent.parent / "custom_clis.json"

        if not config_path.exists():
            logger.debug(f"custom_clis.json not found at {config_path}")
            return {}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                custom_clis = json.load(f)

            validated = {}
            for name, config in custom_clis.items():
                # 메타 필드 무시 (_로 시작하는 키)
                if name.startswith("_"):
                    logger.debug(f"Skipping meta field: {name}")
                    continue

                if not isinstance(config, dict):
                    logger.warning(f"Invalid config for {name} in custom_clis.json")
                    continue

                # 필수 필드 검증
                if "command" not in config:
                    logger.warning(f"Missing 'command' for {name} in custom_clis.json")
                    continue

                # 기본값 적용
                validated[name] = self._apply_defaults(config)

            logger.info(f"Loaded {len(validated)} CLIs from custom_clis.json")
            return validated

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse custom_clis.json: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading custom_clis.json: {e}")
            return {}

    def _apply_defaults(self, config: dict) -> CLIConfig:
        """설정에 기본값 적용"""
        return {
            "command": config["command"],
            "timeout": config.get("timeout", 1800),
            "extra_args": config.get("extra_args", []),
            "env_vars": config.get("env_vars", {}),
            "supports_skip_git_check": config.get("supports_skip_git_check", False),
            "skip_git_check_position": config.get("skip_git_check_position", "before_extra_args"),
            "supported_args": config.get("supported_args", []),
        }


def get_cli_registry() -> CLIRegistry:
    """CLI Registry 싱글톤 인스턴스 반환"""
    return CLIRegistry()
