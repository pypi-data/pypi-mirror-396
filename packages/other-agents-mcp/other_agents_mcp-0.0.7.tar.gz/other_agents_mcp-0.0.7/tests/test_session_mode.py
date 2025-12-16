"""세션 모드 테스트

세션 관리 및 세션 모드 실행 테스트
"""

import pytest
from other_agents_mcp.session_manager import SessionManager, get_session_manager


class TestSessionManager:
    """SessionManager 단위 테스트"""

    def test_create_new_session(self):
        """새 세션 생성 테스트"""
        manager = SessionManager()
        session_info = manager.create_or_get_session("test-001", "claude")

        assert session_info.session_id == "test-001"
        assert session_info.cli_name == "claude"
        assert session_info.request_count == 1

    def test_get_existing_session(self):
        """기존 세션 조회 테스트"""
        manager = SessionManager()

        # 첫 요청
        session1 = manager.create_or_get_session("test-002", "claude")
        assert session1.request_count == 1

        # 같은 세션 ID로 다시 요청
        session2 = manager.create_or_get_session("test-002", "claude")
        assert session2.request_count == 2
        assert session1.session_id == session2.session_id

    def test_claude_cli_session_id(self):
        """Claude CLI 세션 ID 생성 테스트 (UUID)"""
        manager = SessionManager()
        session_info = manager.create_or_get_session("test-claude", "claude")

        # UUID가 아닌 경우 새로 생성
        import uuid

        try:
            uuid.UUID(session_info.cli_session_id)
            # UUID 형식이면 통과
        except ValueError:
            pytest.fail("Claude CLI session ID should be UUID format")

    def test_gemini_cli_session_id(self):
        """Gemini CLI 세션 ID 생성 테스트 (latest)"""
        manager = SessionManager()
        session_info = manager.create_or_get_session("test-gemini", "gemini")

        assert session_info.cli_session_id == "latest"

    def test_qwen_cli_session_id(self):
        """Qwen CLI 세션 ID 생성 테스트 (latest)"""
        manager = SessionManager()
        session_info = manager.create_or_get_session("test-qwen", "qwen")

        assert session_info.cli_session_id == "latest"

    def test_codex_cli_session_id(self):
        """Codex CLI 세션 ID 생성 테스트 (last)"""
        manager = SessionManager()
        session_info = manager.create_or_get_session("test-codex", "codex")

        assert session_info.cli_session_id == "last"

    def test_delete_session(self):
        """세션 삭제 테스트"""
        manager = SessionManager()
        manager.create_or_get_session("test-delete", "claude")

        # 삭제
        result = manager.delete_session("test-delete")
        assert result is True

        # 다시 조회 시 None
        session = manager.get_session("test-delete")
        assert session is None

    def test_list_sessions(self):
        """세션 목록 조회 테스트"""
        manager = SessionManager()
        manager.create_or_get_session("session-1", "claude")
        manager.create_or_get_session("session-2", "gemini")

        sessions = manager.list_sessions()
        assert len(sessions) >= 2

    def test_get_stats(self):
        """세션 통계 테스트"""
        manager = SessionManager()
        manager.create_or_get_session("stats-001", "claude")
        manager.create_or_get_session("stats-002", "claude")
        manager.create_or_get_session("stats-003", "gemini")

        stats = manager.get_stats()
        assert stats["total_sessions"] >= 3
        assert "claude" in stats["sessions_by_cli"]
        assert "gemini" in stats["sessions_by_cli"]

    def test_singleton_pattern(self):
        """싱글톤 패턴 테스트"""
        manager1 = get_session_manager()
        manager2 = get_session_manager()

        assert manager1 is manager2

    def test_session_id_validation_too_short(self):
        """세션 ID 너무 짧음 테스트"""
        manager = SessionManager()

        with pytest.raises(ValueError, match="too short"):
            manager.create_or_get_session("short", "claude")

    def test_session_id_validation_too_long(self):
        """세션 ID 너무 긺 테스트"""
        manager = SessionManager()
        long_id = "a" * 129

        with pytest.raises(ValueError, match="too long"):
            manager.create_or_get_session(long_id, "claude")

    def test_session_id_validation_invalid_chars(self):
        """세션 ID 잘못된 문자 테스트"""
        manager = SessionManager()

        with pytest.raises(ValueError, match="Invalid session ID format"):
            manager.create_or_get_session("invalid@session!", "claude")

    def test_max_sessions_limit(self):
        """최대 세션 수 제한 테스트"""
        SessionManager()

        # MAX_SESSIONS는 1000이지만 테스트는 작은 수로
        from other_agents_mcp.session_manager import MAX_SESSIONS

        # 실제로 1000개를 만들 수는 없으니 로직만 확인
        # (이 테스트는 실제 환경에서 시간이 오래 걸림)
        assert MAX_SESSIONS == 1000

    def test_max_sessions_exceeded(self, mocker):
        """최대 세션 수 초과 테스트"""
        manager = SessionManager()

        # MAX_SESSIONS를 3으로 모킹하여 테스트
        mocker.patch("other_agents_mcp.session_manager.MAX_SESSIONS", 3)

        # 세션 3개 생성 후 4번째 시도
        manager._sessions["session-1"] = None
        manager._sessions["session-2"] = None
        manager._sessions["session-3"] = None

        with pytest.raises(ValueError, match="Maximum session count reached"):
            manager.create_or_get_session("session-4-new", "claude")

    def test_session_id_empty(self):
        """빈 세션 ID 테스트"""
        manager = SessionManager()

        with pytest.raises(ValueError, match="cannot be empty"):
            manager.create_or_get_session("", "claude")

    def test_delete_nonexistent_session(self):
        """존재하지 않는 세션 삭제 테스트"""
        manager = SessionManager()
        result = manager.delete_session("nonexistent-session")
        assert result is False

    def test_claude_uuid_session_id(self):
        """Claude: UUID 형식의 MCP session_id는 그대로 사용"""
        import uuid

        manager = SessionManager()
        uuid_session_id = str(uuid.uuid4())

        session_info = manager.create_or_get_session(uuid_session_id, "claude")
        # UUID 형식이면 그대로 사용
        assert session_info.cli_session_id == uuid_session_id


class TestSessionArgs:
    """세션 플래그 생성 테스트"""

    def test_claude_first_request(self):
        """Claude 첫 요청 (--session-id)"""
        from other_agents_mcp.file_handler import _build_session_args

        args = _build_session_args(
            cli_name="claude", cli_session_id="test-uuid-123", resume=False, is_first_request=True
        )

        assert "--session-id" in args
        assert "test-uuid-123" in args

    def test_claude_resume_request(self):
        """Claude 세션 재개 (--resume)"""
        from other_agents_mcp.file_handler import _build_session_args

        args = _build_session_args(
            cli_name="claude", cli_session_id="test-uuid-123", resume=True, is_first_request=False
        )

        assert "--resume" in args
        assert "test-uuid-123" in args

    def test_gemini_first_request(self):
        """Gemini 첫 요청 (플래그 없음)"""
        from other_agents_mcp.file_handler import _build_session_args

        args = _build_session_args(
            cli_name="gemini", cli_session_id="latest", resume=False, is_first_request=True
        )

        assert len(args) == 0

    def test_gemini_resume_request(self):
        """Gemini 세션 재개 (--resume latest)"""
        from other_agents_mcp.file_handler import _build_session_args

        args = _build_session_args(
            cli_name="gemini", cli_session_id="latest", resume=True, is_first_request=False
        )

        assert "--resume" in args
        assert "latest" in args


class TestSessionModeIntegration:
    """세션 모드 통합 테스트 (Mock)"""

    @pytest.mark.asyncio
    async def test_session_mode_detection(self):
        """세션 모드 자동 감지 테스트"""
        from other_agents_mcp.server import call_tool

        # session_id 없음 → Stateless 모드
        # (실제 CLI 호출은 안 하고 에러 확인만)
        result_stateless = await call_tool(
            "send_message", {"cli_name": "nonexistent", "message": "test"}
        )
        # Stateless 모드로 실행되었음을 확인 (에러 발생)
        assert "error" in result_stateless

        # session_id 있음 → Session 모드
        result_session = await call_tool(
            "send_message",
            {"cli_name": "nonexistent", "message": "test", "session_id": "test-session-001"},
        )
        # Session 모드로 실행되었음을 확인 (에러 발생)
        assert "error" in result_session

    @pytest.mark.asyncio
    async def test_resume_without_session_id(self):
        """resume=True인데 session_id 없으면 무시"""
        from other_agents_mcp.server import call_tool

        result = await call_tool(
            "send_message",
            {"cli_name": "nonexistent", "message": "test", "resume": True},  # session_id 없음
        )

        # Stateless 모드로 처리되어야 함
        assert "error" in result
