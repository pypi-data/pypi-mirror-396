"""Meeting API Tests

meeting_api.py 커버리지 테스트
"""

import pytest
from other_agents_mcp.meeting_api import get_meeting_tools, MEETING_TOOL_SCHEMAS


class TestGetMeetingTools:
    """get_meeting_tools 함수 테스트"""

    def test_returns_list_of_tools(self):
        """Tool 객체 리스트를 반환하는지 확인"""
        tools = get_meeting_tools()
        assert isinstance(tools, list)
        assert len(tools) == 2

    def test_start_meeting_tool_definition(self):
        """start_meeting 도구 정의 확인"""
        tools = get_meeting_tools()
        start_meeting = next((t for t in tools if t.name == "start_meeting"), None)

        assert start_meeting is not None
        assert "회의" in start_meeting.description
        assert start_meeting.inputSchema["type"] == "object"
        assert "topic" in start_meeting.inputSchema["properties"]
        assert "agents" in start_meeting.inputSchema["properties"]
        assert "max_rounds" in start_meeting.inputSchema["properties"]
        assert "timeout_per_round" in start_meeting.inputSchema["properties"]
        assert "topic" in start_meeting.inputSchema["required"]
        assert "agents" in start_meeting.inputSchema["required"]

    def test_get_meeting_status_tool_definition(self):
        """get_meeting_status 도구 정의 확인"""
        tools = get_meeting_tools()
        status_tool = next((t for t in tools if t.name == "get_meeting_status"), None)

        assert status_tool is not None
        assert "상태" in status_tool.description
        assert status_tool.inputSchema["type"] == "object"
        assert "meeting_id" in status_tool.inputSchema["properties"]
        assert "meeting_id" in status_tool.inputSchema["required"]


class TestMeetingToolSchemas:
    """MEETING_TOOL_SCHEMAS 상수 테스트"""

    def test_schema_keys(self):
        """스키마 키 확인"""
        assert "start_meeting" in MEETING_TOOL_SCHEMAS
        assert "get_meeting_status" in MEETING_TOOL_SCHEMAS

    def test_start_meeting_schema_structure(self):
        """start_meeting 스키마 구조 확인"""
        schema = MEETING_TOOL_SCHEMAS["start_meeting"]
        assert schema["name"] == "start_meeting"
        assert "description" in schema
        assert "inputSchema" in schema
        assert schema["inputSchema"]["type"] == "object"

    def test_get_meeting_status_schema_structure(self):
        """get_meeting_status 스키마 구조 확인"""
        schema = MEETING_TOOL_SCHEMAS["get_meeting_status"]
        assert schema["name"] == "get_meeting_status"
        assert "description" in schema
        assert "inputSchema" in schema
        assert "meeting_id" in schema["inputSchema"]["properties"]

    def test_start_meeting_schema_properties(self):
        """start_meeting 스키마 속성들 확인"""
        props = MEETING_TOOL_SCHEMAS["start_meeting"]["inputSchema"]["properties"]

        # topic
        assert props["topic"]["type"] == "string"

        # agents
        assert props["agents"]["type"] == "array"
        assert props["agents"]["items"]["type"] == "string"

        # max_rounds
        assert props["max_rounds"]["type"] == "integer"
        assert props["max_rounds"]["default"] == 5

        # timeout_per_round
        assert props["timeout_per_round"]["type"] == "integer"
        assert props["timeout_per_round"]["default"] == 300
