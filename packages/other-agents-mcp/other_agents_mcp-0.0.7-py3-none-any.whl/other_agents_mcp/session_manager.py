"""Session Manager

세션 관리 및 CLI별 세션 전략 적용
"""

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

from .logger import get_logger

logger = get_logger(__name__)

# 세션 ID 검증 상수
MAX_SESSION_ID_LENGTH = 128
MIN_SESSION_ID_LENGTH = 8
SESSION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9\-_]{8,128}$")
MAX_SESSIONS = 1000


@dataclass
class SessionInfo:
    """세션 정보"""

    session_id: str
    cli_name: str
    cli_session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    request_count: int = 0


class SessionManager:
    """
    세션 관리자

    - MCP session_id → CLI session_id 매핑
    - CLI별 세션 전략 적용
    - 세션 생명주기 관리
    """

    def __init__(self):
        self._sessions: Dict[str, SessionInfo] = {}

    def create_or_get_session(self, session_id: str, cli_name: str) -> SessionInfo:
        """
        세션 생성 또는 조회

        Args:
            session_id: MCP 클라이언트가 제공한 세션 ID
            cli_name: CLI 이름

        Returns:
            SessionInfo 객체

        Raises:
            ValueError: 세션 ID 검증 실패 또는 최대 세션 수 초과
        """
        # 세션 ID 검증
        self._validate_session_id(session_id)

        if session_id in self._sessions:
            # 기존 세션 조회
            session_info = self._sessions[session_id]
            session_info.last_used = datetime.now()
            session_info.request_count += 1

            logger.debug(
                f"Existing session found: {session_id} "
                f"(CLI: {cli_name}, count: {session_info.request_count})"
            )

            return session_info

        # 세션 수 제한 확인
        if len(self._sessions) >= MAX_SESSIONS:
            raise ValueError(
                f"Maximum session count reached ({MAX_SESSIONS}). "
                f"Please delete unused sessions or wait for expiration."
            )

        # 새 세션 생성
        cli_session_id = self._generate_cli_session_id(cli_name, session_id)

        session_info = SessionInfo(
            session_id=session_id, cli_name=cli_name, cli_session_id=cli_session_id, request_count=1
        )

        self._sessions[session_id] = session_info

        logger.info(
            f"New session created: {session_id} "
            f"(CLI: {cli_name}, CLI session: {cli_session_id})"
        )

        return session_info

    def _validate_session_id(self, session_id: str) -> None:
        """
        세션 ID 검증

        Args:
            session_id: 검증할 세션 ID

        Raises:
            ValueError: 검증 실패 시
        """
        if not session_id:
            raise ValueError("Session ID cannot be empty")

        if len(session_id) < MIN_SESSION_ID_LENGTH:
            raise ValueError(f"Session ID too short: {len(session_id)} < {MIN_SESSION_ID_LENGTH}")

        if len(session_id) > MAX_SESSION_ID_LENGTH:
            raise ValueError(f"Session ID too long: {len(session_id)} > {MAX_SESSION_ID_LENGTH}")

        if not SESSION_ID_PATTERN.match(session_id):
            raise ValueError(
                f"Invalid session ID format: '{session_id}'. "
                f"Only alphanumeric characters, hyphens, and underscores allowed (8-128 chars)"
            )

        logger.debug(f"Session ID validation passed: {session_id}")

    def _generate_cli_session_id(self, cli_name: str, mcp_session_id: str) -> str:
        """
        CLI별 세션 ID 생성 전략

        Args:
            cli_name: CLI 이름
            mcp_session_id: MCP 세션 ID

        Returns:
            CLI용 세션 ID
        """
        if cli_name == "claude":
            # Claude: UUID 그대로 사용 (또는 새로 생성)
            # MCP session_id가 UUID 형식이면 그대로, 아니면 새로 생성
            try:
                uuid.UUID(mcp_session_id)
                return mcp_session_id
            except ValueError:
                # UUID가 아니면 새로 생성
                return str(uuid.uuid4())

        elif cli_name in ["gemini", "qwen"]:
            # Gemini/Qwen: "latest" 사용
            return "latest"

        elif cli_name == "codex":
            # Codex: "last" 사용
            return "last"

        else:
            # 커스텀 CLI: UUID 생성
            return str(uuid.uuid4())

    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        세션 조회

        Args:
            session_id: 세션 ID

        Returns:
            SessionInfo 또는 None
        """
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """
        세션 삭제

        Args:
            session_id: 세션 ID

        Returns:
            삭제 성공 여부
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Session deleted: {session_id}")
            return True

        logger.warning(f"Session not found for deletion: {session_id}")
        return False

    def list_sessions(self) -> list[SessionInfo]:
        """
        모든 세션 목록 조회

        Returns:
            세션 정보 리스트
        """
        return list(self._sessions.values())

    def get_stats(self) -> dict:
        """
        세션 통계

        Returns:
            통계 정보
        """
        return {
            "total_sessions": len(self._sessions),
            "sessions_by_cli": self._count_by_cli(),
            "total_requests": sum(s.request_count for s in self._sessions.values()),
        }

    def _count_by_cli(self) -> Dict[str, int]:
        """CLI별 세션 수 집계"""
        counts = {}
        for session in self._sessions.values():
            cli_name = session.cli_name
            counts[cli_name] = counts.get(cli_name, 0) + 1
        return counts


# 싱글톤 인스턴스
_session_manager = None


def get_session_manager() -> SessionManager:
    """세션 매니저 싱글톤 인스턴스 반환"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
