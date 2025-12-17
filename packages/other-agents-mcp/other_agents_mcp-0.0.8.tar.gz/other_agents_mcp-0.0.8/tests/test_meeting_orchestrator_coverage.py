"""Meeting Orchestrator Coverage Tests

meeting_orchestrator.py의 미커버 라인 테스트
- 51: list_active_meetings
- 93-121: start_meeting 회의 생성 및 루프
- 138-183: _run_meeting_loop
- 206-261: _execute_round
- 283-284, 298, 302-304, 323: 핸들러 분기
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock

from other_agents_mcp.meeting_orchestrator import (
    get_active_meeting,
    list_active_meetings,
    start_meeting,
    handle_start_meeting,
    handle_get_meeting_status,
    _active_meetings,
    _run_meeting_loop,
    _execute_round,
)
from other_agents_mcp.meeting_schema import (
    MeetingStatus,
    MeetingResult,
    MeetingRound,
    MeetingConfig,
    AgentResponse,
    VoteType,
    ConsensusType,
)


class TestActiveMeetingsManagement:
    """활성 회의 관리 테스트"""

    def test_list_active_meetings_empty(self):
        """빈 활성 회의 목록"""
        # 기존 데이터 백업 및 클리어
        backup = _active_meetings.copy()
        _active_meetings.clear()

        try:
            result = list_active_meetings()
            assert result == []
        finally:
            # 복원
            _active_meetings.clear()
            _active_meetings.update(backup)

    def test_list_active_meetings_with_data(self):
        """활성 회의가 있을 때"""
        backup = _active_meetings.copy()
        _active_meetings.clear()

        try:
            # 테스트 데이터 추가
            _active_meetings["test-123"] = MagicMock()
            _active_meetings["test-456"] = MagicMock()

            result = list_active_meetings()
            assert len(result) == 2
            assert "test-123" in result
            assert "test-456" in result
        finally:
            _active_meetings.clear()
            _active_meetings.update(backup)

    def test_get_active_meeting_not_found(self):
        """존재하지 않는 회의 조회"""
        result = get_active_meeting("nonexistent-id")
        assert result is None


class TestStartMeeting:
    """start_meeting 함수 테스트"""

    @pytest.mark.asyncio
    async def test_start_meeting_success(self):
        """회의 시작 성공"""
        with patch("other_agents_mcp.meeting_orchestrator.list_available_clis") as mock_list, \
             patch("other_agents_mcp.meeting_orchestrator._run_meeting_loop") as mock_loop:

            # 모킹 설정
            mock_cli1 = MagicMock()
            mock_cli1.name = "claude"
            mock_cli2 = MagicMock()
            mock_cli2.name = "gemini"
            mock_list.return_value = [mock_cli1, mock_cli2]

            # 루프가 합의에 도달한 회의 반환
            async def mock_run_loop(meeting, config):
                meeting.status = MeetingStatus.CONSENSUS
                meeting.final_consensus = "테스트 합의"
                return meeting

            mock_loop.side_effect = mock_run_loop

            result = await start_meeting(
                topic="테스트 주제",
                agents=["claude", "gemini"],
                max_rounds=3,
            )

            assert result.topic == "테스트 주제"
            assert result.agents == ["claude", "gemini"]
            assert result.status == MeetingStatus.CONSENSUS

    @pytest.mark.asyncio
    async def test_start_meeting_error_during_loop(self):
        """회의 루프 중 에러 발생"""
        with patch("other_agents_mcp.meeting_orchestrator.list_available_clis") as mock_list, \
             patch("other_agents_mcp.meeting_orchestrator._run_meeting_loop") as mock_loop:

            mock_cli1 = MagicMock()
            mock_cli1.name = "claude"
            mock_cli2 = MagicMock()
            mock_cli2.name = "gemini"
            mock_list.return_value = [mock_cli1, mock_cli2]

            # 루프에서 에러 발생
            mock_loop.side_effect = Exception("테스트 에러")

            result = await start_meeting(
                topic="에러 테스트",
                agents=["claude", "gemini"],
            )

            assert result.status == MeetingStatus.ERROR
            assert "테스트 에러" in result.error_message

    @pytest.mark.asyncio
    async def test_start_meeting_with_consensus_type(self):
        """합의 유형 지정 테스트"""
        with patch("other_agents_mcp.meeting_orchestrator.list_available_clis") as mock_list, \
             patch("other_agents_mcp.meeting_orchestrator._run_meeting_loop") as mock_loop:

            mock_cli1 = MagicMock()
            mock_cli1.name = "claude"
            mock_cli2 = MagicMock()
            mock_cli2.name = "gemini"
            mock_list.return_value = [mock_cli1, mock_cli2]

            async def mock_run_loop(meeting, config):
                meeting.status = MeetingStatus.CONSENSUS
                return meeting

            mock_loop.side_effect = mock_run_loop

            result = await start_meeting(
                topic="과반수 테스트",
                agents=["claude", "gemini"],
                consensus_type=ConsensusType.MAJORITY,
            )

            assert result.status == MeetingStatus.CONSENSUS


class TestRunMeetingLoop:
    """_run_meeting_loop 함수 테스트"""

    @pytest.mark.asyncio
    async def test_loop_reaches_consensus(self):
        """루프가 합의에 도달"""
        meeting = MeetingResult(
            meeting_id="test-loop-1",
            topic="테스트",
            agents=["claude", "gemini"],
            status=MeetingStatus.RUNNING,
        )
        config = MeetingConfig(
            topic="테스트",
            agents=["claude", "gemini"],
            max_rounds=5,
        )

        with patch("other_agents_mcp.meeting_orchestrator._execute_round") as mock_round, \
             patch("other_agents_mcp.meeting_orchestrator.check_consensus") as mock_check:

            # 첫 라운드에서 합의 도달
            mock_round_result = MeetingRound(round_number=1)
            mock_round_result.responses = [
                AgentResponse("claude", "동의 [AGREE]", VoteType.AGREE),
                AgentResponse("gemini", "동의 [AGREE]", VoteType.AGREE),
            ]
            mock_round_result.is_unanimous = True
            mock_round.return_value = mock_round_result
            mock_check.return_value = True

            result = await _run_meeting_loop(meeting, config)

            assert result.status == MeetingStatus.CONSENSUS
            assert len(result.rounds) == 1

    @pytest.mark.asyncio
    async def test_loop_no_consensus_max_rounds(self):
        """최대 라운드까지 합의 실패"""
        meeting = MeetingResult(
            meeting_id="test-loop-2",
            topic="테스트",
            agents=["claude", "gemini"],
            status=MeetingStatus.RUNNING,
        )
        config = MeetingConfig(
            topic="테스트",
            agents=["claude", "gemini"],
            max_rounds=2,
        )

        with patch("other_agents_mcp.meeting_orchestrator._execute_round") as mock_round, \
             patch("other_agents_mcp.meeting_orchestrator.check_consensus") as mock_check:

            # 항상 합의 실패
            mock_round_result = MeetingRound(round_number=1)
            mock_round_result.responses = [
                AgentResponse("claude", "동의 [AGREE]", VoteType.AGREE),
                AgentResponse("gemini", "반대 [DISAGREE]", VoteType.DISAGREE),
            ]
            mock_round.return_value = mock_round_result
            mock_check.return_value = False

            result = await _run_meeting_loop(meeting, config)

            assert result.status == MeetingStatus.NO_CONSENSUS
            assert len(result.rounds) == 2


class TestExecuteRound:
    """_execute_round 함수 테스트"""

    @pytest.mark.asyncio
    async def test_execute_round_success(self):
        """라운드 실행 성공"""
        with patch("other_agents_mcp.meeting_orchestrator.execute_cli_file_based") as mock_exec:
            mock_exec.return_value = "이것은 좋은 제안입니다. [AGREE]"

            result = await _execute_round(
                agents=["claude", "gemini"],
                topic="테스트 주제",
                system_prompt="시스템 프롬프트",
                round_number=1,
                timeout=60,
            )

            assert result.round_number == 1
            assert len(result.responses) == 2
            for response in result.responses:
                assert response.vote == VoteType.AGREE

    @pytest.mark.asyncio
    async def test_execute_round_agent_error(self):
        """에이전트 호출 에러"""
        with patch("other_agents_mcp.meeting_orchestrator.execute_cli_file_based") as mock_exec:
            # 첫 번째는 성공, 두 번째는 에러
            mock_exec.side_effect = [
                "동의합니다 [AGREE]",
                Exception("에이전트 에러"),
            ]

            result = await _execute_round(
                agents=["claude", "gemini"],
                topic="테스트",
                system_prompt="",
                round_number=1,
                timeout=60,
            )

            assert len(result.responses) == 2
            # 에러 발생한 에이전트는 ABSTAIN
            error_response = next(r for r in result.responses if "ERROR" in r.response)
            assert error_response.vote == VoteType.ABSTAIN


class TestHandleStartMeeting:
    """handle_start_meeting 핸들러 테스트"""

    @pytest.mark.asyncio
    async def test_handle_start_meeting_success(self):
        """성공적인 회의 시작 - 비동기로 즉시 meeting_id 반환"""
        with patch("other_agents_mcp.meeting_orchestrator.list_available_clis") as mock_clis, \
             patch("other_agents_mcp.meeting_orchestrator.get_task_manager") as mock_tm:
            # Mock available CLIs
            mock_clis.return_value = [
                type("CLI", (), {"name": "claude"})(),
                type("CLI", (), {"name": "gemini"})(),
            ]

            # Mock TaskManager
            mock_task_manager = MagicMock()
            mock_task_manager.start_async_task = AsyncMock(return_value="test-task-id")
            mock_tm.return_value = mock_task_manager

            result = await handle_start_meeting({
                "topic": "테스트",
                "agents": ["claude", "gemini"],
            })

            # 비동기 동작 확인: 즉시 meeting_id 반환
            assert "meeting_id" in result
            assert result["status"] == "running"
            assert result["topic"] == "테스트"
            assert result["agents"] == ["claude", "gemini"]
            assert "message" in result

    @pytest.mark.asyncio
    async def test_handle_start_meeting_with_options(self):
        """옵션이 있는 회의 시작"""
        with patch("other_agents_mcp.meeting_orchestrator.list_available_clis") as mock_clis, \
             patch("other_agents_mcp.meeting_orchestrator.get_task_manager") as mock_tm:
            mock_clis.return_value = [
                type("CLI", (), {"name": "claude"})(),
                type("CLI", (), {"name": "gemini"})(),
            ]
            mock_task_manager = MagicMock()
            mock_task_manager.start_async_task = AsyncMock(return_value="test-task-id")
            mock_tm.return_value = mock_task_manager

            result = await handle_start_meeting({
                "topic": "테스트",
                "agents": ["claude", "gemini"],
                "max_rounds": 10,
                "timeout_per_round": 120,
                "consensus_type": "majority",
            })

            assert "meeting_id" in result
            assert result["status"] == "running"

    @pytest.mark.asyncio
    async def test_handle_start_meeting_invalid_consensus_type(self):
        """잘못된 consensus_type"""
        result = await handle_start_meeting({
            "topic": "테스트",
            "agents": ["claude", "gemini"],
            "consensus_type": "invalid_type",
        })

        assert "error" in result
        assert result["type"] == "ValidationError"
        assert "consensus_type" in result["error"]

    @pytest.mark.asyncio
    async def test_handle_start_meeting_validation_error(self):
        """검증 에러"""
        result = await handle_start_meeting({
            "topic": "테스트",
            "agents": ["claude"],  # 1개만 - 에러
        })

        assert "error" in result
        assert result["type"] == "ValidationError"

    @pytest.mark.asyncio
    async def test_handle_start_meeting_invalid_agents(self):
        """유효하지 않은 에이전트"""
        with patch("other_agents_mcp.meeting_orchestrator.list_available_clis") as mock_clis:
            mock_clis.return_value = [
                type("CLI", (), {"name": "claude"})(),
            ]

            result = await handle_start_meeting({
                "topic": "테스트",
                "agents": ["claude", "invalid_agent"],
            })

            assert "error" in result
            assert result["type"] == "ValidationError"
            assert "invalid_agent" in result["error"]


class TestHandleGetMeetingStatus:
    """handle_get_meeting_status 핸들러 테스트"""

    @pytest.mark.asyncio
    async def test_handle_get_meeting_status_found(self):
        """회의 상태 조회 성공"""
        backup = _active_meetings.copy()
        _active_meetings.clear()

        try:
            test_meeting = MeetingResult(
                meeting_id="test-status-1",
                topic="테스트",
                agents=["claude", "gemini"],
                status=MeetingStatus.RUNNING,
            )
            _active_meetings["test-status-1"] = test_meeting

            result = await handle_get_meeting_status({
                "meeting_id": "test-status-1"
            })

            assert result["meeting_id"] == "test-status-1"
            assert result["status"] == "running"
        finally:
            _active_meetings.clear()
            _active_meetings.update(backup)

    @pytest.mark.asyncio
    async def test_handle_get_meeting_status_not_found(self):
        """존재하지 않는 회의 조회"""
        result = await handle_get_meeting_status({
            "meeting_id": "nonexistent-id"
        })

        assert "error" in result
        assert result["type"] == "NotFoundError"


class TestConsensusTypes:
    """다양한 합의 유형 테스트"""

    @pytest.mark.asyncio
    async def test_supermajority_consensus(self):
        """절대다수 합의"""
        result = await handle_start_meeting({
            "topic": "테스트",
            "agents": ["claude", "gemini"],
            "consensus_type": "supermajority",
        })

        # ValidationError가 아니어야 함 (유효한 타입)
        assert result.get("type") != "ValidationError" or "consensus_type" not in result.get("error", "")

    @pytest.mark.asyncio
    async def test_unanimous_consensus(self):
        """만장일치 합의"""
        result = await handle_start_meeting({
            "topic": "테스트",
            "agents": ["claude", "gemini"],
            "consensus_type": "unanimous",
        })

        assert result.get("type") != "ValidationError" or "consensus_type" not in result.get("error", "")
