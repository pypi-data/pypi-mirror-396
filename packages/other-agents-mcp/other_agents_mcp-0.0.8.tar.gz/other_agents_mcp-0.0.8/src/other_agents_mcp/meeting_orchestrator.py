"""Meeting Orchestrator (RB-9, RB-11, RB-14 통합)

다중 회의모드 핵심 오케스트레이터
- 회의 세션 관리
- 라운드 루프 실행
- 에이전트 통신 (기존 use_agents 활용)
- 로깅
"""

import asyncio
import functools
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from .consensus import (
    generate_meeting_system_prompt,
    parse_vote_from_response,
    check_consensus,
    check_unanimous,
    should_continue_meeting,
    extract_consensus_statement,
)
from .meeting_schema import (
    MeetingConfig,
    MeetingResult,
    MeetingRound,
    MeetingStatus,
    AgentResponse,
    VoteType,
    ConsensusType,
)
from .file_handler import execute_cli_file_based, get_cli_semaphore
from .cli_manager import list_available_clis
from .task_manager import get_task_manager
from .logger import get_logger

logger = get_logger(__name__)


# 진행 중인 회의 저장소
_active_meetings: Dict[str, MeetingResult] = {}


def get_active_meeting(meeting_id: str) -> Optional[MeetingResult]:
    """진행 중인 회의 조회"""
    return _active_meetings.get(meeting_id)


def list_active_meetings() -> list[str]:
    """진행 중인 회의 ID 목록"""
    return list(_active_meetings.keys())


async def start_meeting(
    topic: str,
    agents: list[str],
    max_rounds: int = 5,
    timeout_per_round: int = 300,
    consensus_type: ConsensusType = ConsensusType.UNANIMOUS,
) -> MeetingResult:
    """
    다중 에이전트 회의 시작

    Args:
        topic: 회의 주제
        agents: 참여 에이전트 목록
        max_rounds: 최대 라운드 수
        timeout_per_round: 라운드당 타임아웃 (초)
        consensus_type: 합의 유형 (unanimous, supermajority, majority)

    Returns:
        MeetingResult 객체
    """
    # 1. 설정 검증
    config = MeetingConfig(
        topic=topic,
        agents=agents,
        max_rounds=max_rounds,
        timeout_per_round=timeout_per_round,
        consensus_type=consensus_type,
    )
    config.validate()

    # 2. 에이전트 유효성 확인
    available_clis = await asyncio.to_thread(list_available_clis)
    available_names = {cli.name for cli in available_clis}

    invalid_agents = [a for a in agents if a not in available_names]
    if invalid_agents:
        raise ValueError(f"사용할 수 없는 에이전트: {invalid_agents}")

    # 3. 회의 생성
    meeting_id = str(uuid.uuid4())[:8]
    meeting = MeetingResult(
        meeting_id=meeting_id,
        topic=topic,
        agents=agents,
        status=MeetingStatus.RUNNING,
        started_at=datetime.now(),
    )

    _active_meetings[meeting_id] = meeting
    logger.info(f"회의 시작: {meeting_id} - 주제: {topic}")
    logger.info(f"참여 에이전트: {agents}")

    try:
        # 4. 라운드 루프 실행
        meeting = await _run_meeting_loop(meeting, config)

    except Exception as e:
        logger.error(f"회의 중 에러 발생: {e}")
        meeting.status = MeetingStatus.ERROR
        meeting.error_message = str(e)

    finally:
        meeting.ended_at = datetime.now()
        # 완료된 회의는 저장소에서 제거
        _active_meetings.pop(meeting_id, None)

    logger.info(f"회의 종료: {meeting_id} - 상태: {meeting.status.value}")
    return meeting


async def _run_meeting_loop(
    meeting: MeetingResult,
    config: MeetingConfig,
) -> MeetingResult:
    """
    회의 라운드 루프 실행

    Args:
        meeting: 회의 결과 객체
        config: 회의 설정

    Returns:
        업데이트된 MeetingResult
    """
    current_round = 0
    previous_responses: list[dict] = []

    while current_round < config.max_rounds:
        current_round += 1
        logger.info(f"=== 라운드 {current_round}/{config.max_rounds} 시작 ===")

        # 1. 시스템 프롬프트 생성
        system_prompt = generate_meeting_system_prompt(
            topic=config.topic,
            round_number=current_round,
            previous_responses=previous_responses,
        )

        # 2. 모든 에이전트에게 동시 질문
        round_result = await _execute_round(
            agents=config.agents,
            topic=config.topic,
            system_prompt=system_prompt,
            round_number=current_round,
            timeout=config.timeout_per_round,
        )

        meeting.rounds.append(round_result)

        # 3. 합의 확인 (설정된 합의 유형에 따라)
        is_consensus = check_consensus(round_result, config.consensus_type)

        if is_consensus:
            meeting.status = MeetingStatus.CONSENSUS
            meeting.final_consensus = extract_consensus_statement(round_result)
            logger.info(f"합의 도달! ({config.consensus_type.value}) 합의 내용: {meeting.final_consensus}")
            break

        # 4. 다음 라운드를 위한 이전 응답 저장
        previous_responses = [r.to_dict() for r in round_result.responses]

        # 5. 계속 여부 판단
        if not should_continue_meeting(current_round, config.max_rounds, is_consensus):
            meeting.status = MeetingStatus.NO_CONSENSUS
            break

    if meeting.status == MeetingStatus.RUNNING:
        meeting.status = MeetingStatus.NO_CONSENSUS

    return meeting


async def _execute_round(
    agents: list[str],
    topic: str,
    system_prompt: str,
    round_number: int,
    timeout: int,
) -> MeetingRound:
    """
    단일 라운드 실행 (모든 에이전트 병렬 호출)

    Args:
        agents: 에이전트 목록
        topic: 회의 주제
        system_prompt: 시스템 프롬프트
        round_number: 라운드 번호
        timeout: 타임아웃 (초)

    Returns:
        MeetingRound 객체
    """
    round_result = MeetingRound(round_number=round_number)

    # 유저 프롬프트 (간단하게)
    user_prompt = f"회의 주제: {topic}\n\n이 주제에 대한 의견을 제시하고, 마지막에 [AGREE], [DISAGREE], [ABSTAIN] 중 하나로 투표해주세요."

    # 병렬 실행 함수
    semaphore = get_cli_semaphore()

    async def call_agent(agent_name: str) -> AgentResponse:
        """단일 에이전트 호출"""
        async with semaphore:
            try:
                logger.debug(f"에이전트 호출: {agent_name}")

                execution_func = functools.partial(
                    execute_cli_file_based,
                    agent_name,
                    user_prompt,
                    True,  # skip_git_repo_check
                    system_prompt,
                    [],  # args
                    timeout,
                )

                response_text = await asyncio.to_thread(execution_func)

                # 투표 파싱
                vote = parse_vote_from_response(response_text)

                logger.info(f"에이전트 {agent_name} 응답 완료 - 투표: {vote.value}")

                return AgentResponse(
                    agent_name=agent_name,
                    response=response_text,
                    vote=vote,
                )

            except Exception as e:
                logger.error(f"에이전트 {agent_name} 호출 실패: {e}")
                return AgentResponse(
                    agent_name=agent_name,
                    response=f"ERROR: {str(e)}",
                    vote=VoteType.ABSTAIN,
                )

    # 모든 에이전트 병렬 호출
    tasks = [call_agent(agent) for agent in agents]
    responses = await asyncio.gather(*tasks)

    round_result.responses = list(responses)

    # 라운드 요약 로깅
    vote_summary = round_result.get_vote_summary()
    logger.info(f"라운드 {round_number} 완료 - 투표 결과: {vote_summary}")

    return round_result


async def handle_start_meeting(arguments: Dict[str, Any]) -> dict:
    """
    start_meeting MCP 도구 핸들러

    회의를 비동기로 시작하고 즉시 meeting_id를 반환합니다.
    get_meeting_status로 진행 상황을 조회할 수 있습니다.

    Args:
        arguments: MCP 도구 인자

    Returns:
        meeting_id와 상태를 포함한 딕셔너리
    """
    topic = arguments["topic"]
    agents = arguments["agents"]
    max_rounds = arguments.get("max_rounds", 5)
    timeout_per_round = arguments.get("timeout_per_round", 300)
    consensus_type_str = arguments.get("consensus_type", "unanimous")

    # consensus_type 문자열을 enum으로 변환
    try:
        consensus_type = ConsensusType(consensus_type_str)
    except ValueError:
        return {
            "error": f"잘못된 consensus_type: {consensus_type_str}. "
                     f"가능한 값: unanimous, supermajority, majority",
            "type": "ValidationError"
        }

    # 설정 검증
    try:
        config = MeetingConfig(
            topic=topic,
            agents=agents,
            max_rounds=max_rounds,
            timeout_per_round=timeout_per_round,
            consensus_type=consensus_type,
        )
        config.validate()
    except ValueError as e:
        return {"error": str(e), "type": "ValidationError"}

    # 에이전트 유효성 확인
    try:
        available_clis = await asyncio.to_thread(list_available_clis)
        available_names = {cli.name for cli in available_clis}

        invalid_agents = [a for a in agents if a not in available_names]
        if invalid_agents:
            return {
                "error": f"사용할 수 없는 에이전트: {invalid_agents}",
                "type": "ValidationError"
            }
    except Exception as e:
        return {"error": str(e), "type": "ValidationError"}

    # 회의 ID 생성 및 초기 상태 설정
    meeting_id = str(uuid.uuid4())[:8]
    meeting = MeetingResult(
        meeting_id=meeting_id,
        topic=topic,
        agents=agents,
        status=MeetingStatus.RUNNING,
        started_at=datetime.now(),
    )

    # _active_meetings에 등록
    _active_meetings[meeting_id] = meeting

    # 비동기로 회의 실행
    coro = _run_meeting_async(meeting, config)
    task_manager = get_task_manager()
    await task_manager.start_async_task(coro, task_id=meeting_id)

    logger.info(f"회의 시작됨: {meeting_id} - 주제: {topic}")
    logger.info(f"참여 에이전트: {agents}")

    return {
        "meeting_id": meeting_id,
        "status": "running",
        "message": f"회의가 시작되었습니다. get_meeting_status로 진행 상황을 조회하세요.",
        "topic": topic,
        "agents": agents,
    }


async def _run_meeting_async(meeting: MeetingResult, config: MeetingConfig) -> dict:
    """
    비동기로 회의를 실행합니다.

    Args:
        meeting: 회의 결과 객체
        config: 회의 설정

    Returns:
        회의 결과 딕셔너리
    """
    meeting_id = meeting.meeting_id

    try:
        # 라운드 루프 실행
        meeting = await _run_meeting_loop(meeting, config)

    except Exception as e:
        logger.error(f"회의 중 에러 발생: {e}")
        meeting.status = MeetingStatus.ERROR
        meeting.error_message = str(e)

    finally:
        meeting.ended_at = datetime.now()
        # _active_meetings 업데이트 (결과 반영)
        _active_meetings[meeting_id] = meeting

    logger.info(f"회의 종료: {meeting_id} - 상태: {meeting.status.value}")

    # TTL 후 _active_meetings에서 제거 (메모리 누수 방지)
    asyncio.create_task(_cleanup_meeting_after_ttl(meeting_id, ttl_seconds=3600))

    return meeting.to_dict()


async def _cleanup_meeting_after_ttl(meeting_id: str, ttl_seconds: int = 3600):
    """
    지정된 시간 후 완료된 회의를 _active_meetings에서 제거합니다.

    Args:
        meeting_id: 회의 ID
        ttl_seconds: TTL (기본값: 3600초 = 1시간)
    """
    await asyncio.sleep(ttl_seconds)
    removed = _active_meetings.pop(meeting_id, None)
    if removed:
        logger.debug(f"TTL 만료로 회의 정리됨: {meeting_id}")


async def handle_get_meeting_status(arguments: Dict[str, Any]) -> dict:
    """
    get_meeting_status MCP 도구 핸들러

    Args:
        arguments: MCP 도구 인자

    Returns:
        회의 상태 딕셔너리
    """
    meeting_id = arguments["meeting_id"]

    meeting = get_active_meeting(meeting_id)
    if meeting is None:
        return {"error": f"회의를 찾을 수 없습니다: {meeting_id}", "type": "NotFoundError"}

    return meeting.to_dict()
