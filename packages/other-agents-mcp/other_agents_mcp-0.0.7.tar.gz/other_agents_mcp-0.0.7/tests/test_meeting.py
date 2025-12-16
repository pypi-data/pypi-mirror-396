"""Meeting Mode Tests (RB-15)

다중 회의모드 단위 테스트 및 통합 테스트
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock

from other_agents_mcp.meeting_schema import (
    MeetingStatus,
    VoteType,
    ConsensusType,
    AgentResponse,
    MeetingRound,
    MeetingResult,
    MeetingConfig,
)
from other_agents_mcp.consensus import (
    generate_meeting_system_prompt,
    parse_vote_from_response,
    check_unanimous,
    check_consensus,
    should_continue_meeting,
    extract_consensus_statement,
)


class TestMeetingSchema:
    """회의 스키마 테스트"""

    def test_meeting_config_valid(self):
        """유효한 회의 설정"""
        config = MeetingConfig(
            topic="테스트 주제",
            agents=["claude", "gemini"],
            max_rounds=5,
            timeout_per_round=300,
        )
        config.validate()  # 예외 없이 통과

    def test_meeting_config_empty_topic(self):
        """빈 주제 검증"""
        config = MeetingConfig(
            topic="",
            agents=["claude", "gemini"],
        )
        with pytest.raises(ValueError, match="주제가 비어있습니다"):
            config.validate()

    def test_meeting_config_single_agent(self):
        """단일 에이전트 검증"""
        config = MeetingConfig(
            topic="테스트",
            agents=["claude"],
        )
        with pytest.raises(ValueError, match="최소 2개 이상"):
            config.validate()

    def test_meeting_config_invalid_max_rounds(self):
        """잘못된 max_rounds 검증"""
        config = MeetingConfig(
            topic="테스트",
            agents=["claude", "gemini"],
            max_rounds=100,
        )
        with pytest.raises(ValueError, match="1~20 범위"):
            config.validate()

    def test_agent_response_to_dict(self):
        """AgentResponse 직렬화"""
        response = AgentResponse(
            agent_name="claude",
            response="테스트 응답 [AGREE]",
            vote=VoteType.AGREE,
        )
        data = response.to_dict()
        assert data["agent_name"] == "claude"
        assert data["vote"] == "agree"
        assert "timestamp" in data

    def test_meeting_round_vote_summary(self):
        """라운드 투표 요약"""
        round_result = MeetingRound(round_number=1)
        round_result.responses = [
            AgentResponse("claude", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("gemini", "반대 [DISAGREE]", VoteType.DISAGREE),
            AgentResponse("codex", "기권 [ABSTAIN]", VoteType.ABSTAIN),
        ]
        summary = round_result.get_vote_summary()
        assert summary["agree"] == 1
        assert summary["disagree"] == 1
        assert summary["abstain"] == 1

    def test_meeting_result_to_dict(self):
        """MeetingResult 직렬화"""
        result = MeetingResult(
            meeting_id="test-123",
            topic="테스트 주제",
            agents=["claude", "gemini"],
            status=MeetingStatus.CONSENSUS,
        )
        data = result.to_dict()
        assert data["meeting_id"] == "test-123"
        assert data["status"] == "consensus"
        assert data["total_rounds"] == 0


class TestConsensusProtocol:
    """합의 프로토콜 테스트"""

    def test_parse_vote_agree_bracket(self):
        """[AGREE] 패턴 파싱"""
        response = "좋은 의견입니다. [AGREE]"
        vote = parse_vote_from_response(response)
        assert vote == VoteType.AGREE

    def test_parse_vote_agree_korean(self):
        """한글 동의 패턴 파싱"""
        response = "동의합니다. 좋은 제안이네요."
        vote = parse_vote_from_response(response)
        assert vote == VoteType.AGREE

    def test_parse_vote_disagree_bracket(self):
        """[DISAGREE] 패턴 파싱"""
        response = "다른 의견입니다. [DISAGREE]"
        vote = parse_vote_from_response(response)
        assert vote == VoteType.DISAGREE

    def test_parse_vote_disagree_korean(self):
        """한글 반대 패턴 파싱"""
        response = "반대합니다. 다른 방향이 좋겠습니다."
        vote = parse_vote_from_response(response)
        assert vote == VoteType.DISAGREE

    def test_parse_vote_abstain_bracket(self):
        """[ABSTAIN] 패턴 파싱"""
        response = "판단이 어렵습니다. [ABSTAIN]"
        vote = parse_vote_from_response(response)
        assert vote == VoteType.ABSTAIN

    def test_parse_vote_no_pattern(self):
        """패턴 없음 -> 기권"""
        response = "의견만 제시합니다."
        vote = parse_vote_from_response(response)
        assert vote == VoteType.ABSTAIN

    def test_check_unanimous_all_agree(self):
        """만장일치 확인 - 전원 동의"""
        round_result = MeetingRound(round_number=1)
        round_result.responses = [
            AgentResponse("claude", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("gemini", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("codex", "동의 [AGREE]", VoteType.AGREE),
        ]
        assert check_unanimous(round_result) is True
        assert round_result.is_unanimous is True

    def test_check_unanimous_one_disagree(self):
        """만장일치 실패 - 1명 반대"""
        round_result = MeetingRound(round_number=1)
        round_result.responses = [
            AgentResponse("claude", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("gemini", "반대 [DISAGREE]", VoteType.DISAGREE),
        ]
        assert check_unanimous(round_result) is False
        assert round_result.is_unanimous is False

    def test_check_unanimous_empty(self):
        """빈 응답"""
        round_result = MeetingRound(round_number=1)
        assert check_unanimous(round_result) is False

    def test_should_continue_unanimous(self):
        """만장일치 시 종료"""
        assert should_continue_meeting(1, 5, True) is False

    def test_should_continue_max_rounds(self):
        """최대 라운드 도달 시 종료"""
        assert should_continue_meeting(5, 5, False) is False

    def test_should_continue_ongoing(self):
        """진행 중"""
        assert should_continue_meeting(2, 5, False) is True

    def test_generate_system_prompt(self):
        """시스템 프롬프트 생성"""
        prompt = generate_meeting_system_prompt(
            topic="테스트 주제",
            round_number=1,
        )
        assert "테스트 주제" in prompt
        assert "[AGREE]" in prompt
        assert "[DISAGREE]" in prompt
        assert "라운드: 1" in prompt

    def test_generate_system_prompt_with_previous(self):
        """이전 라운드 포함 프롬프트"""
        previous = [
            {"agent_name": "claude", "response": "이전 응답", "vote": "agree"},
        ]
        prompt = generate_meeting_system_prompt(
            topic="테스트 주제",
            round_number=2,
            previous_responses=previous,
        )
        assert "이전 라운드 발언" in prompt
        assert "claude" in prompt

    def test_extract_consensus_statement(self):
        """합의 내용 추출"""
        round_result = MeetingRound(round_number=1)
        round_result.responses = [
            AgentResponse("claude", "좋은 제안입니다. 구현하겠습니다. [AGREE]", VoteType.AGREE),
        ]
        round_result.is_unanimous = True

        statement = extract_consensus_statement(round_result)
        assert statement is not None
        assert "좋은 제안" in statement
        assert "[AGREE]" not in statement

    def test_extract_consensus_not_unanimous(self):
        """만장일치 아닌 경우"""
        round_result = MeetingRound(round_number=1)
        round_result.is_unanimous = False

        statement = extract_consensus_statement(round_result)
        assert statement is None


class TestMeetingOrchestratorMocked:
    """오케스트레이터 모킹 테스트"""

    @pytest.mark.asyncio
    async def test_handle_start_meeting_validation_error(self):
        """시작 요청 검증 에러"""
        from other_agents_mcp.meeting_orchestrator import handle_start_meeting

        # 빈 에이전트 목록
        result = await handle_start_meeting({
            "topic": "테스트",
            "agents": ["claude"],  # 1개만 - 에러
        })

        assert "error" in result
        assert result["type"] == "ValidationError"

    @pytest.mark.asyncio
    async def test_handle_get_meeting_status_not_found(self):
        """존재하지 않는 회의 조회"""
        from other_agents_mcp.meeting_orchestrator import handle_get_meeting_status

        result = await handle_get_meeting_status({
            "meeting_id": "nonexistent-id",
        })

        assert "error" in result
        assert result["type"] == "NotFoundError"

    @pytest.mark.asyncio
    async def test_start_meeting_invalid_agents(self):
        """유효하지 않은 에이전트"""
        from other_agents_mcp.meeting_orchestrator import start_meeting

        # list_available_clis 모킹
        with patch("other_agents_mcp.meeting_orchestrator.list_available_clis") as mock_list:
            mock_cli = MagicMock()
            mock_cli.name = "claude"
            mock_list.return_value = [mock_cli]

            with pytest.raises(ValueError, match="사용할 수 없는 에이전트"):
                await start_meeting(
                    topic="테스트",
                    agents=["claude", "invalid_agent"],
                )


class TestVotePatterns:
    """투표 패턴 상세 테스트"""

    @pytest.mark.parametrize("response,expected", [
        ("I agree with this proposal. [AGREE]", VoteType.AGREE),
        ("This is great, agreed!", VoteType.AGREE),
        ("[동의] 좋은 의견입니다", VoteType.AGREE),
        ("찬성합니다", VoteType.AGREE),
        ("I disagree. [DISAGREE]", VoteType.DISAGREE),
        ("disagreed with the approach", VoteType.DISAGREE),
        ("[반대] 다른 방법이 좋겠습니다", VoteType.DISAGREE),
        ("동의하지 않습니다", VoteType.DISAGREE),
        ("[ABSTAIN] Need more information", VoteType.ABSTAIN),
        ("기권합니다", VoteType.ABSTAIN),
        ("판단을 유보합니다", VoteType.ABSTAIN),
        ("No vote pattern here", VoteType.ABSTAIN),
    ])
    def test_vote_patterns(self, response, expected):
        """다양한 투표 패턴 테스트"""
        vote = parse_vote_from_response(response)
        assert vote == expected


class TestConsensusTypes:
    """다양한 합의 유형 테스트"""

    def test_check_consensus_unanimous_all_agree(self):
        """만장일치 - 전원 동의"""
        round_result = MeetingRound(round_number=1)
        round_result.responses = [
            AgentResponse("claude", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("gemini", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("codex", "동의 [AGREE]", VoteType.AGREE),
        ]
        assert check_consensus(round_result, ConsensusType.UNANIMOUS) is True

    def test_check_consensus_unanimous_one_disagree(self):
        """만장일치 - 1명 반대 시 실패"""
        round_result = MeetingRound(round_number=1)
        round_result.responses = [
            AgentResponse("claude", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("gemini", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("codex", "반대 [DISAGREE]", VoteType.DISAGREE),
        ]
        assert check_consensus(round_result, ConsensusType.UNANIMOUS) is False

    def test_check_consensus_supermajority_success(self):
        """절대다수 (2/3) - 3명 중 2명 동의 시 성공"""
        round_result = MeetingRound(round_number=1)
        round_result.responses = [
            AgentResponse("claude", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("gemini", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("codex", "반대 [DISAGREE]", VoteType.DISAGREE),
        ]
        assert check_consensus(round_result, ConsensusType.SUPERMAJORITY) is True

    def test_check_consensus_supermajority_fail(self):
        """절대다수 (2/3) - 3명 중 1명 동의 시 실패"""
        round_result = MeetingRound(round_number=1)
        round_result.responses = [
            AgentResponse("claude", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("gemini", "반대 [DISAGREE]", VoteType.DISAGREE),
            AgentResponse("codex", "반대 [DISAGREE]", VoteType.DISAGREE),
        ]
        assert check_consensus(round_result, ConsensusType.SUPERMAJORITY) is False

    def test_check_consensus_majority_success(self):
        """과반수 - 3명 중 2명 동의 시 성공"""
        round_result = MeetingRound(round_number=1)
        round_result.responses = [
            AgentResponse("claude", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("gemini", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("codex", "반대 [DISAGREE]", VoteType.DISAGREE),
        ]
        assert check_consensus(round_result, ConsensusType.MAJORITY) is True

    def test_check_consensus_majority_tie(self):
        """과반수 - 동률 시 실패 (50%는 과반이 아님)"""
        round_result = MeetingRound(round_number=1)
        round_result.responses = [
            AgentResponse("claude", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("gemini", "반대 [DISAGREE]", VoteType.DISAGREE),
        ]
        assert check_consensus(round_result, ConsensusType.MAJORITY) is False

    def test_check_consensus_majority_over_half(self):
        """과반수 - 4명 중 3명 동의 시 성공"""
        round_result = MeetingRound(round_number=1)
        round_result.responses = [
            AgentResponse("a1", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("a2", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("a3", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("a4", "반대 [DISAGREE]", VoteType.DISAGREE),
        ]
        assert check_consensus(round_result, ConsensusType.MAJORITY) is True


class TestBlindVoting:
    """블라인드 투표 (투표 마스킹) 테스트"""

    def test_previous_responses_vote_masked(self):
        """이전 라운드 응답에서 투표 결과가 마스킹되는지 확인"""
        previous = [
            {"agent_name": "claude", "response": "이전 응답 내용", "vote": "agree"},
        ]
        prompt = generate_meeting_system_prompt(
            topic="테스트 주제",
            round_number=2,
            previous_responses=previous,
        )
        # 이전 라운드 발언 섹션 추출
        previous_section_start = prompt.find("## 이전 라운드 발언")
        previous_section = prompt[previous_section_start:]

        # 이전 라운드 섹션에서 투표 결과 "[agree]" 형태가 포함되지 않아야 함
        # (규칙 섹션의 [AGREE] 안내는 제외)
        assert "[agree]" not in previous_section.lower()
        assert "투표 결과는 공개되지 않습니다" in prompt
        # 에이전트 이름과 내용은 포함되어야 함
        assert "claude" in previous_section
        assert "이전 응답 내용" in previous_section


class TestConsensusTypeConfig:
    """합의 유형 설정 테스트"""

    def test_meeting_config_with_consensus_type(self):
        """회의 설정에 합의 유형 포함"""
        config = MeetingConfig(
            topic="테스트",
            agents=["claude", "gemini"],
            consensus_type=ConsensusType.MAJORITY,
        )
        config.validate()
        assert config.consensus_type == ConsensusType.MAJORITY

    def test_meeting_config_default_consensus_type(self):
        """기본 합의 유형은 만장일치"""
        config = MeetingConfig(
            topic="테스트",
            agents=["claude", "gemini"],
        )
        assert config.consensus_type == ConsensusType.UNANIMOUS
