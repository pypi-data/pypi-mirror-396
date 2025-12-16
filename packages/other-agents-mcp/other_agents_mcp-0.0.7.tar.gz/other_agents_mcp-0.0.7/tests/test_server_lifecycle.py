"""Tests for MCP Server lifecycle and main function

서버 생명주기 및 진입점 테스트
"""

import pytest
from unittest.mock import patch

from other_agents_mcp.server import app, main


class MockExceptionGroup(Exception):
    """테스트용 ExceptionGroup 모의 클래스"""

    def __init__(self, msg, exceptions):
        super().__init__(msg)
        self.exceptions = exceptions


class TestServerLifecycle:
    """서버 생명주기 테스트"""

    @pytest.mark.asyncio
    async def test_lifespan_context_manager(self):
        """lifespan이 정상적으로 컨텍스트 매니저로 동작"""
        # 간단한 lifespan 테스트 - 실제 server 동작 확인
        # lifespan은 실제 서버 실행 시에만 완전히 테스트 가능
        assert hasattr(app, "lifespan")
        assert callable(app.lifespan)


class TestMainFunction:
    """main() 함수 테스트"""

    def test_main_function_imports_and_calls_asyncio_run(self):
        """main()이 asyncio.run을 호출"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            # asyncio.run을 모킹하여 실제 서버 시작 방지
            mock_run.return_value = None

            main()

            # asyncio.run이 호출되었는지 확인
            assert mock_run.called

            # 코루틴이 전달되었는지 확인
            args = mock_run.call_args[0]
            assert len(args) == 1
            import inspect

            assert inspect.iscoroutine(args[0])

    def test_main_function_logs_startup_info(self, caplog):
        """main()이 시작 정보를 로깅"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            # asyncio.run을 모킹하여 실제 서버 시작 방지
            mock_run.return_value = None

            import logging

            caplog.set_level(logging.INFO)

            main()

            # 로그 메시지 확인
            log_messages = [record.message for record in caplog.records]
            assert any("Other Agents MCP Server starting" in msg for msg in log_messages)
            assert any("MCP SDK version: 1.22.0" in msg for msg in log_messages)
            assert any("Server name: other-agents-mcp" in msg for msg in log_messages)
            assert any("use_agents" in msg for msg in log_messages)


class TestConnectionClosedErrorHandling:
    """연결 종료 에러 처리 테스트 (BrokenPipeError, ConnectionResetError, ExceptionGroup)"""

    def test_direct_broken_pipe_error_graceful_shutdown(self):
        """BrokenPipeError 발생 시 graceful shutdown"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            mock_run.side_effect = BrokenPipeError("pipe closed")

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

    def test_direct_connection_reset_error_graceful_shutdown(self):
        """ConnectionResetError 발생 시 graceful shutdown"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            mock_run.side_effect = ConnectionResetError("connection reset")

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

    def test_exception_group_with_broken_pipe_graceful_shutdown(self):
        """ExceptionGroup 내 BrokenPipeError 발생 시 graceful shutdown"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            mock_run.side_effect = MockExceptionGroup(
                "group", [BrokenPipeError("inner pipe error"), ValueError("other")]
            )

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

    def test_nested_exception_group_graceful_shutdown(self):
        """중첩된 ExceptionGroup 내 BrokenPipeError 발생 시 graceful shutdown"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            inner_group = MockExceptionGroup("inner", [BrokenPipeError("deep")])
            outer_group = MockExceptionGroup("outer", [inner_group, ValueError("other")])
            mock_run.side_effect = outer_group

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

    def test_deeply_nested_exception_group_graceful_shutdown(self):
        """3단계 이상 중첩된 ExceptionGroup 내 BrokenPipeError 감지"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            deep_group = MockExceptionGroup("deep", [ConnectionResetError("deepest")])
            middle_group = MockExceptionGroup("middle", [deep_group])
            outer_group = MockExceptionGroup("outer", [middle_group])
            mock_run.side_effect = outer_group

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

    def test_exception_with_cause_chain(self):
        """__cause__ 체인에 BrokenPipeError가 있는 경우"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            cause = BrokenPipeError("original cause")
            wrapper = RuntimeError("wrapper")
            wrapper.__cause__ = cause
            mock_run.side_effect = wrapper

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

    def test_unrelated_exception_propagates(self):
        """연결 종료와 무관한 예외는 재발생"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            mock_run.side_effect = ValueError("unrelated error")

            with pytest.raises(ValueError) as exc_info:
                main()

            assert "unrelated error" in str(exc_info.value)

    def test_exception_group_without_connection_error_propagates(self):
        """연결 종료 에러가 없는 ExceptionGroup은 재발생"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            mock_run.side_effect = MockExceptionGroup(
                "group", [ValueError("error1"), TypeError("error2")]
            )

            with pytest.raises(MockExceptionGroup):
                main()

    def test_keyboard_interrupt_graceful_shutdown(self):
        """KeyboardInterrupt 발생 시 graceful shutdown"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            mock_run.side_effect = KeyboardInterrupt()

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0
