"""Consensus Protocol (RB-10)

에이전트 간 만장일치 합의 프로토콜 구현
- 시스템 프롬프트 생성
- 응답 파싱 (투표 추출)
- 만장일치 판정
"""

import re
from typing import Optional

from .meeting_schema import VoteType, AgentResponse, MeetingRound, ConsensusType
from .logger import get_logger

logger = get_logger(__name__)


# 투표 키워드 패턴 (DISAGREE를 먼저 검사하여 "disagreed"가 "agreed"로 매칭되지 않도록 함)
VOTE_PATTERNS = {
    VoteType.DISAGREE: [
        r"\[DISAGREE\]",
        r"\[반대\]",
        r"\[이의\]",
        r"반대합니다",
        r"동의하지 않습니다",
        r"I disagree",
        r"disagreed",
    ],
    VoteType.AGREE: [
        r"\[AGREE\]",
        r"\[동의\]",
        r"\[찬성\]",
        r"동의합니다",
        r"찬성합니다",
        r"I agree",
        r"(?<!\bdis)agreed",
    ],
    VoteType.ABSTAIN: [
        r"\[ABSTAIN\]",
        r"\[기권\]",
        r"기권합니다",
        r"판단을 유보",
        r"I abstain",
    ],
}


def generate_meeting_system_prompt(topic: str, round_number: int, previous_responses: list[dict] = None) -> str:
    """
    회의용 시스템 프롬프트 생성

    Args:
        topic: 회의 주제
        round_number: 현재 라운드 번호
        previous_responses: 이전 라운드 응답들

    Returns:
        시스템 프롬프트 문자열
    """
    prompt_parts = [
        "당신은 다중 에이전트 회의에 참여하고 있습니다.",
        f"",
        f"## 회의 주제",
        f"{topic}",
        f"",
        f"## 현재 라운드: {round_number}",
        f"",
        "## 규칙",
        "1. 주제에 대해 의견을 제시하세요.",
        "2. 다른 에이전트의 의견을 고려하여 판단하세요.",
        "3. 응답 마지막에 반드시 투표를 표시하세요:",
        "   - 동의: [AGREE]",
        "   - 반대: [DISAGREE]",
        "   - 기권: [ABSTAIN]",
        "",
        "## 중요",
        "- 반드시 [AGREE], [DISAGREE], [ABSTAIN] 중 하나로 투표하세요.",
        "- 투표 없이 응답하면 [ABSTAIN]으로 처리됩니다.",
    ]

    # 이전 라운드 응답 추가 (투표 결과는 마스킹하여 순응성 방지)
    if previous_responses:
        prompt_parts.append("")
        prompt_parts.append("## 이전 라운드 발언")
        prompt_parts.append("(참고: 다른 에이전트의 투표 결과는 공개되지 않습니다. 의견 내용만 참고하세요.)")
        for resp in previous_responses:
            agent = resp.get("agent_name", "Unknown")
            content = resp.get("response", "")[:500]  # 최대 500자
            # 투표 결과 마스킹 - 의견만 공개
            prompt_parts.append(f"- **{agent}**: {content}")

    return "\n".join(prompt_parts)


def parse_vote_from_response(response: str) -> VoteType:
    """
    응답에서 투표 추출

    Args:
        response: 에이전트 응답 문자열

    Returns:
        VoteType (기본값: ABSTAIN)
    """
    response_lower = response.lower()

    # 각 투표 타입별 패턴 검사 (VOTE_PATTERNS 순서: DISAGREE > AGREE > ABSTAIN)
    # DISAGREE를 먼저 검사하여 "disagreed"가 "agreed"로 오인식되지 않도록 함
    for vote_type, patterns in VOTE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, response, re.IGNORECASE):
                logger.debug(f"투표 감지: {vote_type.value} (패턴: {pattern})")
                return vote_type

    # 패턴 미발견 시 기권 처리
    logger.warning("투표 패턴을 찾지 못함. 기권으로 처리")
    return VoteType.ABSTAIN


def check_consensus(
    round_result: MeetingRound,
    consensus_type: ConsensusType = ConsensusType.UNANIMOUS
) -> bool:
    """
    합의 확인 (다양한 합의 유형 지원)

    Args:
        round_result: 라운드 결과
        consensus_type: 합의 유형 (unanimous, supermajority, majority)

    Returns:
        합의 도달 여부
    """
    if not round_result.responses:
        return False

    total_votes = len(round_result.responses)
    agree_votes = sum(1 for r in round_result.responses if r.vote == VoteType.AGREE)
    agree_ratio = agree_votes / total_votes

    # 합의 유형별 임계값 확인
    threshold_met = False
    threshold_name = ""

    if consensus_type == ConsensusType.UNANIMOUS:
        threshold_met = agree_ratio == 1.0
        threshold_name = "만장일치 (100%)"
    elif consensus_type == ConsensusType.SUPERMAJORITY:
        threshold_met = agree_ratio >= 2/3
        threshold_name = "절대다수 (2/3)"
    elif consensus_type == ConsensusType.MAJORITY:
        threshold_met = agree_ratio > 0.5
        threshold_name = "과반수 (50%+)"

    if threshold_met:
        logger.info(
            f"라운드 {round_result.round_number}: {threshold_name} 합의 도달! "
            f"({agree_votes}/{total_votes}, {agree_ratio:.1%})"
        )
        round_result.is_unanimous = True  # 하위 호환성 유지
        return True

    # 투표 요약 로깅
    summary = round_result.get_vote_summary()
    logger.info(
        f"라운드 {round_result.round_number}: 합의 미도달 - {summary} "
        f"(필요: {threshold_name})"
    )

    return False


def check_unanimous(round_result: MeetingRound) -> bool:
    """
    만장일치 확인 (하위 호환성 유지)

    Args:
        round_result: 라운드 결과

    Returns:
        만장일치 여부
    """
    return check_consensus(round_result, ConsensusType.UNANIMOUS)


def should_continue_meeting(
    current_round: int,
    max_rounds: int,
    is_unanimous: bool
) -> bool:
    """
    회의 계속 여부 판단

    Args:
        current_round: 현재 라운드 번호
        max_rounds: 최대 라운드 수
        is_unanimous: 만장일치 여부

    Returns:
        계속 여부
    """
    # 만장일치 도달 시 종료
    if is_unanimous:
        logger.info("만장일치 도달로 회의 종료")
        return False

    # 최대 라운드 도달 시 종료
    if current_round >= max_rounds:
        logger.info(f"최대 라운드({max_rounds}) 도달로 회의 종료")
        return False

    return True


def extract_consensus_statement(round_result: MeetingRound) -> Optional[str]:
    """
    합의된 내용 추출 (만장일치 시)

    Args:
        round_result: 만장일치 라운드 결과

    Returns:
        합의 내용 요약 (첫 번째 AGREE 응답 기준)
    """
    if not round_result.is_unanimous:
        return None

    for response in round_result.responses:
        if response.vote == VoteType.AGREE:
            # 투표 태그 제거 후 첫 200자 반환
            content = response.response
            for pattern in VOTE_PATTERNS[VoteType.AGREE]:
                content = re.sub(pattern, "", content, flags=re.IGNORECASE)
            return content.strip()[:200]

    return None
