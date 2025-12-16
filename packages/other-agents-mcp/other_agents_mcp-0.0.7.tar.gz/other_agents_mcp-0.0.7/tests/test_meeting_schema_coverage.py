"""Meeting Schema Coverage Tests

meeting_schema.py의 미커버 라인 테스트
- 60: MeetingRound.to_dict
- 104-118: MeetingResult.get_summary
- 142, 145: MeetingConfig.validate 분기
"""

import pytest
from datetime import datetime

from other_agents_mcp.meeting_schema import (
    MeetingStatus,
    VoteType,
    ConsensusType,
    AgentResponse,
    MeetingRound,
    MeetingResult,
    MeetingConfig,
)


class TestMeetingRoundToDict:
    """MeetingRound.to_dict 테스트"""

    def test_to_dict_with_responses(self):
        """응답이 있는 라운드의 to_dict"""
        round_result = MeetingRound(round_number=1)
        round_result.responses = [
            AgentResponse("claude", "동의 [AGREE]", VoteType.AGREE),
            AgentResponse("gemini", "반대 [DISAGREE]", VoteType.DISAGREE),
        ]
        round_result.is_unanimous = False

        data = round_result.to_dict()

        assert data["round_number"] == 1
        assert len(data["responses"]) == 2
        assert data["is_unanimous"] is False
        assert "vote_summary" in data
        assert data["vote_summary"]["agree"] == 1
        assert data["vote_summary"]["disagree"] == 1

    def test_to_dict_empty_responses(self):
        """빈 응답의 to_dict"""
        round_result = MeetingRound(round_number=2)

        data = round_result.to_dict()

        assert data["round_number"] == 2
        assert data["responses"] == []
        assert data["vote_summary"]["agree"] == 0
        assert data["vote_summary"]["disagree"] == 0
        assert data["vote_summary"]["abstain"] == 0


class TestMeetingResultGetSummary:
    """MeetingResult.get_summary 테스트"""

    def test_get_summary_basic(self):
        """기본 요약"""
        result = MeetingResult(
            meeting_id="test-123",
            topic="테스트 주제",
            agents=["claude", "gemini"],
            status=MeetingStatus.RUNNING,
        )

        summary = result.get_summary()

        assert "회의 결과" in summary
        assert "테스트 주제" in summary
        assert "claude" in summary
        assert "gemini" in summary
        assert "running" in summary

    def test_get_summary_with_consensus(self):
        """합의가 있는 요약"""
        result = MeetingResult(
            meeting_id="test-124",
            topic="합의 주제",
            agents=["claude", "gemini"],
            status=MeetingStatus.CONSENSUS,
            final_consensus="모두 동의합니다",
        )
        result.rounds = [MeetingRound(round_number=1)]

        summary = result.get_summary()

        assert "최종 합의" in summary
        assert "모두 동의합니다" in summary
        assert "총 라운드: 1" in summary

    def test_get_summary_with_error(self):
        """에러가 있는 요약"""
        result = MeetingResult(
            meeting_id="test-125",
            topic="에러 주제",
            agents=["claude"],
            status=MeetingStatus.ERROR,
            error_message="테스트 에러 메시지",
        )

        summary = result.get_summary()

        assert "에러" in summary
        assert "테스트 에러 메시지" in summary
        assert "error" in summary

    def test_get_summary_no_consensus(self):
        """합의 실패 요약"""
        result = MeetingResult(
            meeting_id="test-126",
            topic="불일치 주제",
            agents=["claude", "gemini", "codex"],
            status=MeetingStatus.NO_CONSENSUS,
        )
        result.rounds = [
            MeetingRound(round_number=1),
            MeetingRound(round_number=2),
            MeetingRound(round_number=3),
        ]

        summary = result.get_summary()

        assert "no_consensus" in summary
        assert "총 라운드: 3" in summary
        assert "최종 합의" not in summary  # 합의 없음


class TestMeetingConfigValidate:
    """MeetingConfig.validate 추가 테스트"""

    def test_validate_timeout_too_small(self):
        """타임아웃이 너무 작음"""
        config = MeetingConfig(
            topic="테스트",
            agents=["claude", "gemini"],
            timeout_per_round=10,  # 30 미만
        )

        with pytest.raises(ValueError, match="30~3600초"):
            config.validate()

    def test_validate_timeout_too_large(self):
        """타임아웃이 너무 큼"""
        config = MeetingConfig(
            topic="테스트",
            agents=["claude", "gemini"],
            timeout_per_round=4000,  # 3600 초과
        )

        with pytest.raises(ValueError, match="30~3600초"):
            config.validate()

    def test_validate_invalid_consensus_type(self):
        """잘못된 consensus_type"""
        config = MeetingConfig(
            topic="테스트",
            agents=["claude", "gemini"],
        )
        # 강제로 잘못된 타입 설정
        config.consensus_type = "invalid"

        with pytest.raises(ValueError, match="consensus_type"):
            config.validate()

    def test_validate_valid_timeout_boundaries(self):
        """유효한 타임아웃 경계값"""
        # 최소값
        config_min = MeetingConfig(
            topic="테스트",
            agents=["claude", "gemini"],
            timeout_per_round=30,
        )
        config_min.validate()  # 예외 없음

        # 최대값
        config_max = MeetingConfig(
            topic="테스트",
            agents=["claude", "gemini"],
            timeout_per_round=3600,
        )
        config_max.validate()  # 예외 없음


class TestEnumValues:
    """Enum 값 테스트"""

    def test_meeting_status_values(self):
        """MeetingStatus 값 확인"""
        assert MeetingStatus.WAITING.value == "waiting"
        assert MeetingStatus.RUNNING.value == "running"
        assert MeetingStatus.CONSENSUS.value == "consensus"
        assert MeetingStatus.NO_CONSENSUS.value == "no_consensus"
        assert MeetingStatus.ERROR.value == "error"

    def test_vote_type_values(self):
        """VoteType 값 확인"""
        assert VoteType.AGREE.value == "agree"
        assert VoteType.DISAGREE.value == "disagree"
        assert VoteType.ABSTAIN.value == "abstain"

    def test_consensus_type_values(self):
        """ConsensusType 값 확인"""
        assert ConsensusType.UNANIMOUS.value == "unanimous"
        assert ConsensusType.SUPERMAJORITY.value == "supermajority"
        assert ConsensusType.MAJORITY.value == "majority"


class TestAgentResponseTimestamp:
    """AgentResponse 타임스탬프 테스트"""

    def test_timestamp_auto_generated(self):
        """타임스탬프 자동 생성"""
        response = AgentResponse(
            agent_name="claude",
            response="테스트",
            vote=VoteType.AGREE,
        )

        assert response.timestamp is not None
        assert isinstance(response.timestamp, datetime)

    def test_timestamp_in_to_dict(self):
        """to_dict에 타임스탬프 포함"""
        response = AgentResponse(
            agent_name="gemini",
            response="테스트 응답",
            vote=VoteType.DISAGREE,
        )

        data = response.to_dict()

        assert "timestamp" in data
        # ISO 형식 확인
        datetime.fromisoformat(data["timestamp"])
