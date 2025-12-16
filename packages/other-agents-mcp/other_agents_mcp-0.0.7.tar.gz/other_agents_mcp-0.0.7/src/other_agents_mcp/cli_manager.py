"""CLI Manager

시스템에 설치된 CLI 감지 및 정보 조회
"""

import shutil
import subprocess
from dataclasses import dataclass
from typing import Optional

from .cli_registry import get_cli_registry
from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class CLIInfo:
    """CLI 정보"""

    name: str
    command: str
    version: Optional[str]
    installed: bool
    authenticated: Optional[bool] = None  # None: 미확인, True: 인증됨, False: 인증필요


# 인증 실패 키워드
AUTH_FAILURE_KEYWORDS = [
    "login",
    "authenticate",
    "unauthorized",
    "401",
    "sign in",
    "api key",
    "token",
    "credential",
]


def is_cli_installed(command: str) -> bool:
    """
    CLI가 설치되어 있는지 확인

    Args:
        command: CLI 명령어 (예: "claude", "gemini")

    Returns:
        설치 여부 (True/False)
    """
    return shutil.which(command) is not None


def get_cli_version(command: str) -> Optional[str]:
    """
    CLI 버전 정보 조회

    Args:
        command: CLI 명령어

    Returns:
        버전 문자열 또는 None (조회 실패 시)
    """
    if not is_cli_installed(command):
        return None

    try:
        # --version 옵션으로 버전 정보 조회 시도
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            stdin=subprocess.DEVNULL,  # 인터랙티브 블로킹 방지
        )

        if result.returncode == 0:
            # stdout 또는 stderr에서 버전 정보 추출
            version_output = result.stdout.strip() or result.stderr.strip()
            return version_output if version_output else None
        else:
            # --version이 실패하면 None 반환
            logger.debug(f"{command} --version 실패 (코드 {result.returncode})")
            return None

    except subprocess.TimeoutExpired:
        logger.warning(f"{command} --version 타임아웃")
        return None
    except FileNotFoundError:
        logger.debug(f"{command} 명령어를 찾을 수 없음")
        return None
    except Exception as e:
        logger.error(f"{command} 버전 조회 중 예외: {e}")
        return None


def check_cli_auth(command: str) -> Optional[bool]:
    """
    CLI 인증 상태 확인 (간단한 프롬프트로 테스트)

    Args:
        command: CLI 명령어

    Returns:
        True: 인증됨, False: 인증 필요, None: 확인 불가
    """
    if not is_cli_installed(command):
        return None

    try:
        # 아주 짧은 프롬프트로 인증 상태 확인 (2초 타임아웃)
        result = subprocess.run(
            [command, "-p", "hi"],
            capture_output=True,
            text=True,
            timeout=10,
            stdin=subprocess.DEVNULL,
        )

        output = (result.stdout + result.stderr).lower()

        # 인증 실패 키워드 확인
        for keyword in AUTH_FAILURE_KEYWORDS:
            if keyword in output:
                logger.debug(f"{command} 인증 필요: '{keyword}' 감지")
                return False

        # 정상 응답이면 인증됨
        if result.returncode == 0:
            return True

        # 비정상 종료지만 인증 키워드 없음 → 확인 불가
        return None

    except subprocess.TimeoutExpired:
        logger.warning(f"{command} 인증 체크 타임아웃")
        return None
    except Exception as e:
        logger.debug(f"{command} 인증 체크 실패: {e}")
        return None


def list_available_clis(check_auth: bool = False) -> list[CLIInfo]:
    """
    설치된 CLI 목록 반환

    CLI Registry에서 모든 CLI를 조회하며,
    각 CLI의 설치 여부와 버전 정보를 조회합니다.

    Registry는 3단계 병합을 수행합니다:
    1. 기본 CLI (config.py)
    2. 파일 기반 (custom_clis.json)
    3. 런타임 추가 (add_cli 도구)

    Args:
        check_auth: True면 각 CLI의 인증 상태도 확인 (시간 소요)

    Returns:
        CLIInfo 객체들의 리스트
    """
    registry = get_cli_registry()
    all_clis = registry.get_all_clis()

    clis = []

    for cli_name, config in all_clis.items():
        command = config["command"]
        installed = is_cli_installed(command)
        version = get_cli_version(command) if installed else None

        # 인증 상태 확인 (옵션)
        authenticated = None
        if check_auth and installed:
            authenticated = check_cli_auth(command)

        cli_info = CLIInfo(
            name=cli_name,
            command=command,
            version=version,
            installed=installed,
            authenticated=authenticated,
        )
        clis.append(cli_info)

    return clis
