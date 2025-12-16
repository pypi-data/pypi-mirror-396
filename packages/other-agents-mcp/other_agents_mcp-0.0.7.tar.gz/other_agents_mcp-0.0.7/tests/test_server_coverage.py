"""Tests for increasing code coverage of server.py"""

import pytest
from unittest.mock import patch, AsyncMock
from other_agents_mcp.server import call_tool
from other_agents_mcp.file_handler import CLINotFoundError, CLITimeoutError, CLIExecutionError


class TestServerCoverage:

    @pytest.mark.asyncio
    async def test_call_tool_run_tool_sync_exceptions(self):
        """call_tool (run_tool) 동기 실행 시 예외 처리 테스트"""

        # 1. ValueError (SessionValidationError)
        with patch("other_agents_mcp.server.execute_with_session") as mock_exec:
            mock_exec.side_effect = ValueError("Invalid Session")

            result = await call_tool(
                "use_agent", {"cli_name": "claude", "message": "hi", "session_id": "invalid"}
            )
            assert result["type"] == "SessionValidationError"
            assert "Invalid Session" in result["error"]

        # 2. CLINotFoundError
        with patch("other_agents_mcp.server.execute_cli_file_based") as mock_exec:
            mock_exec.side_effect = CLINotFoundError("Not Found")

            result = await call_tool("use_agent", {"cli_name": "unknown", "message": "hi"})
            assert result["type"] == "CLINotFoundError"

        # 3. CLITimeoutError
        with patch("other_agents_mcp.server.execute_cli_file_based") as mock_exec:
            mock_exec.side_effect = CLITimeoutError("Timeout")

            result = await call_tool("use_agent", {"cli_name": "claude", "message": "hi"})
            assert result["type"] == "CLITimeoutError"

        # 4. CLIExecutionError
        with patch("other_agents_mcp.server.execute_cli_file_based") as mock_exec:
            mock_exec.side_effect = CLIExecutionError("Failed")

            result = await call_tool("use_agent", {"cli_name": "claude", "message": "hi"})
            assert result["type"] == "CLIExecutionError"

    @pytest.mark.asyncio
    async def test_call_tool_add_tool_exception(self):
        """call_tool (add_tool) 예외 처리 테스트"""
        with patch("other_agents_mcp.server.get_cli_registry") as mock_registry:
            mock_registry.return_value.add_cli.side_effect = Exception("Registry Error")

            result = await call_tool("add_agent", {"name": "new", "command": "cmd"})

            assert "error" in result
            assert result["type"] == "AddCLIError"
            assert "Registry Error" in result["error"]

    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self):
        """존재하지 않는 도구 호출"""
        result = await call_tool("weird_tool", {})
        assert "error" in result
        assert "Unknown tool" in result["error"]

    @pytest.mark.asyncio
    async def test_main_execution(self):
        """main 함수 실행 (run은 모킹)"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            from other_agents_mcp.server import main

            main()
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_tool_get_task_status_with_timeout(self):
        """call_tool (get_task_status) timeout 파라미터 전달 테스트"""
        with patch("other_agents_mcp.server.get_task_manager") as mock_get_mgr:
            mock_mgr = mock_get_mgr.return_value
            mock_mgr.get_task_status = AsyncMock(return_value={"status": "running"})

            # timeout 지정 호출
            await call_tool("get_task_status", {"task_id": "t1", "timeout": 30})
            
            mock_mgr.get_task_status.assert_called_with("t1", timeout=30)

            # timeout 미지정 호출 (기본값 0)
            await call_tool("get_task_status", {"task_id": "t2"})
            
            mock_mgr.get_task_status.assert_called_with("t2", timeout=0)
