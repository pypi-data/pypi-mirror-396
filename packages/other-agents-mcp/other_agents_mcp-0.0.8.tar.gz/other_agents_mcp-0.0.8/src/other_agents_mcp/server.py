"""MCP Server

Other Agents MCP 서버 진입점
"""

import asyncio
import functools
from dataclasses import asdict
from typing import Any, Dict, AsyncGenerator

# MCP SDK import
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .cli_manager import list_available_clis
from .cli_registry import get_cli_registry
from .file_handler import (
    execute_cli_file_based,
    execute_with_session,
    cleanup_stale_temp_files,
    get_cli_semaphore,
    CLINotFoundError,
    CLIExecutionError,
    CLITimeoutError,
)
from .logger import get_logger
from .task_manager import get_task_manager
from .meeting_orchestrator import handle_start_meeting, handle_get_meeting_status

logger = get_logger(__name__)


# MCP Server 인스턴스 생성
app = Server("other-agents-mcp")


@app.lifespan
async def lifespan(app: Server) -> AsyncGenerator[Dict[str, Any], None]:
    """서버 생명주기 동안 TaskManager를 관리합니다."""
    logger.info("서버 시작... TaskManager를 초기화하고 시작합니다.")
    task_manager = get_task_manager()
    await task_manager.start()

    yield {}

    logger.info("서버 종료... TaskManager를 중지합니다.")
    await task_manager.stop()


@app.list_tools()
async def list_available_tools():
    """도구 목록 반환"""
    from mcp.types import Tool

    return [
        Tool(
            name="list_agents",
            description="사용 가능한 AI CLI 목록 조회. 기본 제공: claude, gemini, codex (Cursor), qwen. 각 CLI의 설치 여부와 버전 정보를 확인할 수 있습니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "check_auth": {
                        "type": "boolean",
                        "description": "인증 상태 확인 여부 (기본값: false). true면 각 CLI에 짧은 프롬프트를 보내 인증 상태를 확인합니다.",
                    },
                },
            },
        ),
        Tool(
            name="use_agent",
            description="특정 AI CLI에게 프롬프트를 전송하여 응답을 받습니다. 사용 가능한 CLI: 'claude' (Claude AI), 'gemini' (Google Gemini), 'codex' (Cursor의 Codex), 'qwen' (Alibaba Qwen). 예: 'codex에게 리뷰 요청' → cli_name='codex'로 호출",
            inputSchema={
                "type": "object",
                "properties": {
                    "cli_name": {
                        "type": "string",
                        "description": "실행할 AI CLI 이름. 가능한 값: 'claude', 'gemini', 'codex', 'qwen' 또는 add_agent로 추가한 커스텀 CLI",
                    },
                    "message": {"type": "string", "description": "전송할 프롬프트"},
                    "run_async": {
                        "type": "boolean",
                        "description": "비동기 실행 여부. true면 즉시 task_id 반환 (기본값: false)",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "세션 ID (선택사항). 제공하면 session 모드, 없으면 stateless 모드",
                    },
                    "resume": {
                        "type": "boolean",
                        "description": "세션 이어가기 (session_id와 함께 사용, 기본값: false)",
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "시스템 프롬프트 (선택사항). Claude는 --append-system-prompt, 나머지는 YAML 형식으로 처리됨",
                    },
                    "skip_git_repo_check": {
                        "type": "boolean",
                        "description": "Git 저장소 체크 건너뛰기 (Codex만 지원, 기본값: true)",
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "추가 CLI 인자 (선택사항). 각 CLI가 지원하는 옵션만 전달되며, 지원하지 않는 옵션은 로그에 기록되고 무시됨",
                    },
                    "timeout": {
                        "type": "number",
                        "description": "타임아웃 초 (선택사항, 기본값: 1800). Stateless/Session 모드 모두 지원",
                    },
                },
                "required": ["cli_name", "message"],
            },
        ),
        Tool(
            name="use_agents",
            description="여러 AI에게 동시에 같은 질문을 보내 다양한 관점의 답변을 받습니다. 리뷰 요청, 의견 수렴, 비교 분석에 유용합니다. 사용 가능한 CLI: claude, gemini, codex, qwen. 예: '모든 AI에게 리뷰 요청' → cli_names=['claude', 'gemini', 'codex', 'qwen'] 또는 생략",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "모든 AI CLI에 전송할 프롬프트 또는 질문",
                    },
                    "cli_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "응답을 받을 AI CLI 목록 (선택사항). 예: ['claude', 'codex', 'gemini']. 생략 시 모든 사용 가능한 CLI에게 전송",
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "시스템 프롬프트 (선택사항)",
                    },
                    "skip_git_repo_check": {
                        "type": "boolean",
                        "description": "Git 저장소 체크 건너뛰기 (기본값: true)",
                    },
                    "timeout": {
                        "type": "number",
                        "description": "각 CLI의 타임아웃 초 (선택사항, 기본값: 1800)",
                    },
                },
                "required": ["message"],
            },
        ),
        Tool(
            name="get_task_status",
            description="비동기 실행(use_agent run_async=true)의 상태 및 결과를 조회합니다. timeout을 설정하면 완료될 때까지 대기합니다(Long Polling).",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "use_agent로부터 받은 작업 ID"},
                    "timeout": {
                        "type": "number",
                        "description": "상태가 running일 경우 대기할 최대 시간 (초). 설정 시 Long Polling으로 동작하여 폴링 횟수를 줄일 수 있습니다. (권장: 30)",
                    },
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            name="add_agent",
            description="동적으로 새로운 AI CLI 도구 추가 (런타임)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "CLI 이름 (필수, 예: deepseek)"},
                    "command": {
                        "type": "string",
                        "description": "실행 명령어 (필수, 예: deepseek)",
                    },
                    "extra_args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "추가 인자 (선택, 기본값: [])",
                    },
                    "timeout": {
                        "type": "number",
                        "description": "타임아웃 초 (선택, 기본값: 1800)",
                    },
                    "env_vars": {"type": "object", "description": "환경 변수 (선택, 기본값: {})"},
                    "supports_skip_git_check": {
                        "type": "boolean",
                        "description": "Git 체크 스킵 지원 (선택, 기본값: false)",
                    },
                    "skip_git_check_position": {
                        "type": "string",
                        "enum": ["before_extra_args", "after_extra_args"],
                        "description": "플래그 위치 (선택, 기본값: before_extra_args)",
                    },
                    "supported_args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "지원하는 CLI 인자 목록 (선택, 기본값: [])",
                    },
                },
                "required": ["name", "command"],
            },
        ),
        Tool(
            name="start_meeting",
            description="다중 에이전트 회의를 시작합니다. 지정된 에이전트들이 주제에 대해 합의가 나올 때까지 토론합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "회의 주제 (필수). 에이전트들이 토론할 내용",
                    },
                    "agents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "description": "참여 에이전트 목록 (필수). 예: ['claude', 'gemini', 'codex']. 최소 2개 이상",
                    },
                    "max_rounds": {
                        "type": "integer",
                        "default": 5,
                        "description": "최대 라운드 수 (선택, 기본값: 5). 합의 없이 이 횟수에 도달하면 종료",
                    },
                    "timeout_per_round": {
                        "type": "integer",
                        "default": 300,
                        "description": "라운드당 타임아웃 초 (선택, 기본값: 300)",
                    },
                    "consensus_type": {
                        "type": "string",
                        "enum": ["unanimous", "supermajority", "majority"],
                        "default": "unanimous",
                        "description": "합의 유형 (선택, 기본값: unanimous). unanimous=만장일치(100%), supermajority=절대다수(2/3), majority=과반수(50%+)",
                    },
                },
                "required": ["topic", "agents"],
            },
        ),
        Tool(
            name="get_meeting_status",
            description="진행 중인 회의의 상태를 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "meeting_id": {
                        "type": "string",
                        "description": "회의 ID (start_meeting에서 반환된 값)",
                    },
                },
                "required": ["meeting_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]):
    """도구 실행 (비동기 처리 개선)"""
    if name == "list_agents":
        # 비동기로 실행하여 블로킹 방지
        check_auth = arguments.get("check_auth", False)
        clis = await asyncio.to_thread(list_available_clis, check_auth)
        return {"clis": [asdict(cli) for cli in clis]}

    elif name == "use_agent":
        cli_name = arguments["cli_name"]
        message = arguments["message"]
        run_async = arguments.get("run_async", False)
        session_id = arguments.get("session_id", None)
        resume = arguments.get("resume", False)
        system_prompt = arguments.get("system_prompt", None)
        skip_git_repo_check = arguments.get("skip_git_repo_check", True)
        args = arguments.get("args", [])
        timeout = arguments.get("timeout", None)

        # 실행할 로직 선택 (Session vs Stateless)
        if session_id:
            # Session 모드
            logger.info(f"Session mode: {session_id} (resume: {resume})")
            execution_func = functools.partial(
                execute_with_session,
                cli_name,
                message,
                session_id,
                resume,
                skip_git_repo_check,
                system_prompt,
                args,
                timeout,
            )
        else:
            # Stateless 모드
            logger.info("Stateless mode")
            execution_func = functools.partial(
                execute_cli_file_based,
                cli_name,
                message,
                skip_git_repo_check,
                system_prompt,
                args,
                timeout,
            )

        # 비동기 실행 여부에 따른 분기
        if run_async:
            # 비동기 실행: TaskManager에 등록하고 ID 즉시 반환
            task_manager = get_task_manager()
            task_id = await task_manager.start_task(execution_func)
            return {
                "task_id": task_id,
                "status": "running",
                "message": "Task started asynchronously",
            }
        else:
            # 동기 실행: 세마포어로 동시성 제어
            semaphore = get_cli_semaphore()
            async with semaphore:
                try:
                    response = await asyncio.to_thread(execution_func)
                    return {"response": response}
                except ValueError as e:
                    logger.error(f"Session validation error: {e}")
                    return {"error": str(e), "type": "SessionValidationError"}
                except CLINotFoundError as e:
                    logger.error(f"CLI not found: {e}")
                    return {"error": str(e), "type": "CLINotFoundError"}
                except CLITimeoutError as e:
                    logger.error(f"CLI timeout: {e}")
                    return {"error": str(e), "type": "CLITimeoutError"}
                except CLIExecutionError as e:
                    logger.error(f"CLI execution error: {e}")
                    return {"error": str(e), "type": "CLIExecutionError"}

    elif name == "get_task_status":
        task_id = arguments["task_id"]
        timeout = arguments.get("timeout", 0)
        task_manager = get_task_manager()
        status = await task_manager.get_task_status(task_id, timeout=timeout)
        return status

    elif name == "add_agent":
        # 필수 필드
        cli_name = arguments["name"]
        command = arguments["command"]

        # 선택 필드 (기본값 자동 적용)
        extra_args = arguments.get("extra_args")
        timeout = arguments.get("timeout")
        env_vars = arguments.get("env_vars")
        supports_skip_git_check = arguments.get("supports_skip_git_check")
        skip_git_check_position = arguments.get("skip_git_check_position")
        supported_args = arguments.get("supported_args")

        try:
            registry = get_cli_registry()
            registry.add_cli(
                name=cli_name,
                command=command,
                extra_args=extra_args,
                timeout=timeout,
                env_vars=env_vars,
                supports_skip_git_check=supports_skip_git_check,
                skip_git_check_position=skip_git_check_position,
                supported_args=supported_args,
            )
            logger.info(f"CLI '{cli_name}' 추가 성공")
            return {
                "success": True,
                "message": f"CLI '{cli_name}' 추가 완료",
                "cli": {"name": cli_name, "command": command},
            }
        except Exception as e:
            logger.error(f"CLI 추가 실패: {e}")
            return {"error": str(e), "type": "AddCLIError"}

    elif name == "use_agents":
        message = arguments["message"]
        cli_names = arguments.get("cli_names", None)
        system_prompt = arguments.get("system_prompt", None)
        skip_git_repo_check = arguments.get("skip_git_repo_check", True)
        timeout = arguments.get("timeout", None)

        # CLI 목록 결정: 지정되지 않은 경우 모든 활성화된 CLI
        if cli_names is None:
            clis = await asyncio.to_thread(list_available_clis)
            cli_names = [cli.name for cli in clis]
            logger.info(f"대상 CLI 목록(전체): {cli_names}")
        else:
            logger.info(f"대상 CLI 목록(지정): {cli_names}")

        # 병렬 실행 함수 (세마포어로 동시성 제어)
        semaphore = get_cli_semaphore()

        async def run_single_cli(cli_name: str) -> tuple[str, dict]:
            """단일 CLI를 실행하고 결과 반환"""
            async with semaphore:
                try:
                    execution_func = functools.partial(
                        execute_cli_file_based,
                        cli_name,
                        message,
                        skip_git_repo_check,
                        system_prompt,
                        [],
                        timeout,
                    )
                    response = await asyncio.to_thread(execution_func)
                    return (cli_name, {"response": response, "success": True})
                except CLINotFoundError as e:
                    logger.warning(f"CLI '{cli_name}' not found: {e}")
                    return (
                        cli_name,
                        {"error": str(e), "type": "CLINotFoundError", "success": False},
                    )
                except CLITimeoutError as e:
                    logger.warning(f"CLI '{cli_name}' timeout: {e}")
                    return (
                        cli_name,
                        {"error": str(e), "type": "CLITimeoutError", "success": False},
                    )
                except CLIExecutionError as e:
                    logger.warning(f"CLI '{cli_name}' execution error: {e}")
                    return (
                        cli_name,
                        {"error": str(e), "type": "CLIExecutionError", "success": False},
                    )
                except Exception as e:
                    logger.error(f"CLI '{cli_name}' unexpected error: {e}")
                    return (
                        cli_name,
                        {"error": str(e), "type": "UnexpectedError", "success": False},
                    )

        # 모든 CLI를 병렬로 실행
        tasks = [run_single_cli(cli_name) for cli_name in cli_names]
        results = await asyncio.gather(*tasks)

        # 결과를 딕셔너리로 변환
        responses = {cli_name: result for cli_name, result in results}

        return {"prompt": message, "responses": responses}

    elif name == "start_meeting":
        return await handle_start_meeting(arguments)

    elif name == "get_meeting_status":
        return await handle_get_meeting_status(arguments)

    else:
        logger.warning(f"Unknown tool: {name}")
        return {"error": f"Unknown tool: {name}"}


def main():
    """메인 함수"""
    import signal
    import sys

    logger.info("Other Agents MCP Server starting...")
    logger.info("MCP SDK version: 1.22.0")
    logger.info("Server name: other-agents-mcp")
    logger.info("Available tools: list_agents, use_agent, use_agents, get_task_status, add_agent, start_meeting, get_meeting_status")

    # 시작 시 오래된 임시 파일 정리
    cleanup_stale_temp_files()

    # 시그널 핸들러 설정
    def signal_handler(sig, frame):
        logger.info("Shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # stdio 서버 시작
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    def _is_connection_closed_error(exc: BaseException) -> bool:
        """연결 종료 에러인지 재귀적으로 확인 (중첩된 ExceptionGroup 지원)"""
        # 직접적인 연결 종료 에러
        if isinstance(exc, (BrokenPipeError, ConnectionResetError)):
            return True
        # ExceptionGroup으로 감싸진 경우 재귀 탐색
        if hasattr(exc, "exceptions"):
            return any(_is_connection_closed_error(e) for e in exc.exceptions)
        # __cause__ 체인 확인
        if exc.__cause__ is not None:
            return _is_connection_closed_error(exc.__cause__)
        return False

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
    except Exception as e:
        if _is_connection_closed_error(e):
            logger.debug("Client closed connection, shutting down gracefully")
            sys.exit(0)
        else:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    main()
