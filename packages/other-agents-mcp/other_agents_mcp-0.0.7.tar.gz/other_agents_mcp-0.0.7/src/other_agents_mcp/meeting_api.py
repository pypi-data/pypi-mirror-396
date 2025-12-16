"""Meeting API (RB-13)

다중 회의모드 MCP 도구 정의
- start_meeting: 회의 시작
- get_meeting_status: 회의 상태 조회
"""

from mcp.types import Tool


def get_meeting_tools() -> list[Tool]:
    """회의 관련 MCP 도구 목록 반환"""
    return [
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


# MCP 도구 스키마 (server.py에서 직접 사용할 수 있도록)
MEETING_TOOL_SCHEMAS = {
    "start_meeting": {
        "name": "start_meeting",
        "description": "다중 에이전트 회의를 시작합니다. 지정된 에이전트들이 주제에 대해 만장일치가 나올 때까지 토론합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "회의 주제 (필수). 에이전트들이 토론할 내용",
                },
                "agents": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "참여 에이전트 목록 (필수). 예: ['claude', 'gemini', 'codex']. 최소 2개 이상",
                },
                "max_rounds": {
                    "type": "integer",
                    "default": 5,
                    "description": "최대 라운드 수 (선택, 기본값: 5). 만장일치 없이 이 횟수에 도달하면 종료",
                },
                "timeout_per_round": {
                    "type": "integer",
                    "default": 300,
                    "description": "라운드당 타임아웃 초 (선택, 기본값: 300)",
                },
            },
            "required": ["topic", "agents"],
        },
    },
    "get_meeting_status": {
        "name": "get_meeting_status",
        "description": "진행 중인 회의의 상태를 조회합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "meeting_id": {
                    "type": "string",
                    "description": "회의 ID (start_meeting에서 반환된 값)",
                },
            },
            "required": ["meeting_id"],
        },
    },
}
