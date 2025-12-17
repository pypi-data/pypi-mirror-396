"""Meeting Schema (RB-12)

회의 결과 출력 스키마 및 데이터 구조 정의
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional


class MeetingStatus(Enum):
    """회의 상태"""
    WAITING = "waiting"      # 시작 대기
    RUNNING = "running"      # 진행 중
    CONSENSUS = "consensus"  # 합의 도달
    NO_CONSENSUS = "no_consensus"  # 합의 실패 (최대 라운드 도달)
    ERROR = "error"          # 에러 발생


class VoteType(Enum):
    """투표 타입"""
    AGREE = "agree"
    DISAGREE = "disagree"
    ABSTAIN = "abstain"


class ConsensusType(Enum):
    """합의 유형"""
    UNANIMOUS = "unanimous"      # 만장일치 (100%)
    SUPERMAJORITY = "supermajority"  # 절대다수 (2/3 이상)
    MAJORITY = "majority"        # 과반수 (50% 초과)


@dataclass
class AgentResponse:
    """에이전트 응답"""
    agent_name: str
    response: str
    vote: VoteType
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "response": self.response,
            "vote": self.vote.value,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class MeetingRound:
    """회의 라운드"""
    round_number: int
    responses: list[AgentResponse] = field(default_factory=list)
    is_unanimous: bool = False

    def to_dict(self) -> dict:
        return {
            "round_number": self.round_number,
            "responses": [r.to_dict() for r in self.responses],
            "is_unanimous": self.is_unanimous,
            "vote_summary": self.get_vote_summary(),
        }

    def get_vote_summary(self) -> dict:
        """투표 요약"""
        summary = {VoteType.AGREE.value: 0, VoteType.DISAGREE.value: 0, VoteType.ABSTAIN.value: 0}
        for response in self.responses:
            summary[response.vote.value] += 1
        return summary


@dataclass
class MeetingResult:
    """회의 결과"""
    meeting_id: str
    topic: str
    agents: list[str]
    status: MeetingStatus
    rounds: list[MeetingRound] = field(default_factory=list)
    final_consensus: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "meeting_id": self.meeting_id,
            "topic": self.topic,
            "agents": self.agents,
            "status": self.status.value,
            "rounds": [r.to_dict() for r in self.rounds],
            "total_rounds": len(self.rounds),
            "final_consensus": self.final_consensus,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "error_message": self.error_message,
        }

    def get_summary(self) -> str:
        """회의 결과 요약 문자열"""
        lines = [
            f"=== 회의 결과 ===",
            f"주제: {self.topic}",
            f"참여 에이전트: {', '.join(self.agents)}",
            f"상태: {self.status.value}",
            f"총 라운드: {len(self.rounds)}",
        ]

        if self.final_consensus:
            lines.append(f"최종 합의: {self.final_consensus}")

        if self.error_message:
            lines.append(f"에러: {self.error_message}")

        return "\n".join(lines)


@dataclass
class MeetingConfig:
    """회의 설정"""
    topic: str
    agents: list[str]
    max_rounds: int = 5
    timeout_per_round: int = 300  # 초
    consensus_type: ConsensusType = ConsensusType.UNANIMOUS

    def validate(self) -> None:
        """설정 유효성 검사"""
        if not self.topic or not self.topic.strip():
            raise ValueError("회의 주제가 비어있습니다")

        if not self.agents or len(self.agents) < 2:
            raise ValueError("최소 2개 이상의 에이전트가 필요합니다")

        if self.max_rounds < 1 or self.max_rounds > 20:
            raise ValueError("max_rounds는 1~20 범위여야 합니다")

        if self.timeout_per_round < 30 or self.timeout_per_round > 3600:
            raise ValueError("timeout_per_round는 30~3600초 범위여야 합니다")

        if not isinstance(self.consensus_type, ConsensusType):
            raise ValueError("consensus_type은 ConsensusType이어야 합니다")
