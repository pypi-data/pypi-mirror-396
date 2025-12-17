"""Server Coverage Extra Tests

server.py의 미커버 라인 테스트
- 40-47: lifespan 함수
- 431, 434: start_meeting/get_meeting_status 핸들러 호출
- 456-457, 464-465, 469-471: main 함수
"""

import pytest
import asyncio
import signal
from unittest.mock import patch, MagicMock, AsyncMock

from other_agents_mcp.server import (
    app,
    list_available_tools,
    call_tool,
    lifespan,
    main,
)


# Lifespan 테스트는 test_server_lifecycle.py에서 진행됨
# @app.lifespan 데코레이터로 인해 직접 테스트가 어려움


class TestCallToolMeetingHandlers:
    """call_tool의 회의 관련 핸들러 테스트"""

    @pytest.mark.asyncio
    async def test_call_tool_start_meeting(self):
        """start_meeting 도구 호출"""
        with patch("other_agents_mcp.server.handle_start_meeting") as mock_handler:
            mock_handler.return_value = {
                "meeting_id": "test-123",
                "status": "running",
            }

            result = await call_tool("start_meeting", {
                "topic": "테스트",
                "agents": ["claude", "gemini"],
            })

            mock_handler.assert_called_once()
            assert result["meeting_id"] == "test-123"

    @pytest.mark.asyncio
    async def test_call_tool_get_meeting_status(self):
        """get_meeting_status 도구 호출"""
        with patch("other_agents_mcp.server.handle_get_meeting_status") as mock_handler:
            mock_handler.return_value = {
                "meeting_id": "test-456",
                "status": "consensus",
            }

            result = await call_tool("get_meeting_status", {
                "meeting_id": "test-456",
            })

            mock_handler.assert_called_once()
            assert result["status"] == "consensus"


class TestMainFunction:
    """main 함수 테스트"""

    def test_main_signal_handler_setup(self):
        """시그널 핸들러 설정 확인"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run, \
             patch("other_agents_mcp.server.cleanup_stale_temp_files"), \
             patch("signal.signal") as mock_signal:

            mock_run.return_value = None

            main()

            # SIGINT와 SIGTERM 핸들러가 등록되어야 함
            signal_calls = [call[0][0] for call in mock_signal.call_args_list]
            assert signal.SIGINT in signal_calls
            assert signal.SIGTERM in signal_calls

    def test_main_keyboard_interrupt(self):
        """KeyboardInterrupt 처리"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run, \
             patch("other_agents_mcp.server.cleanup_stale_temp_files"), \
             patch("other_agents_mcp.server.logger") as mock_logger, \
             patch("sys.exit") as mock_exit:

            mock_run.side_effect = KeyboardInterrupt()

            main()

            mock_logger.info.assert_any_call("Shutting down...")
            mock_exit.assert_called_once_with(0)

    def test_main_cleanup_called(self):
        """시작 시 임시 파일 정리 호출"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run, \
             patch("other_agents_mcp.server.cleanup_stale_temp_files") as mock_cleanup, \
             patch("signal.signal"):

            mock_run.return_value = None

            main()

            mock_cleanup.assert_called_once()

    def test_main_logs_startup_info(self):
        """시작 정보 로깅"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run, \
             patch("other_agents_mcp.server.cleanup_stale_temp_files"), \
             patch("other_agents_mcp.server.logger") as mock_logger, \
             patch("signal.signal"):

            mock_run.return_value = None

            main()

            # 시작 로그 확인
            log_messages = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("starting" in msg.lower() for msg in log_messages)


class TestListAvailableToolsSchema:
    """list_available_tools의 스키마 구조 테스트"""

    @pytest.mark.asyncio
    async def test_start_meeting_schema_in_tools(self):
        """start_meeting 스키마가 도구 목록에 포함"""
        tools = await list_available_tools()

        start_meeting = next((t for t in tools if t.name == "start_meeting"), None)
        assert start_meeting is not None

        schema = start_meeting.inputSchema
        assert "topic" in schema["properties"]
        assert "agents" in schema["properties"]
        assert "max_rounds" in schema["properties"]
        assert "consensus_type" in schema["properties"]

    @pytest.mark.asyncio
    async def test_get_meeting_status_schema_in_tools(self):
        """get_meeting_status 스키마가 도구 목록에 포함"""
        tools = await list_available_tools()

        get_status = next((t for t in tools if t.name == "get_meeting_status"), None)
        assert get_status is not None

        schema = get_status.inputSchema
        assert "meeting_id" in schema["properties"]
        assert "meeting_id" in schema["required"]
