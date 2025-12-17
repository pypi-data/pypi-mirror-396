"""Logger 테스트

로깅 설정 및 유틸리티 테스트
"""

import logging

from other_agents_mcp.logger import get_logger


class TestGetLogger:
    """get_logger 함수 테스트"""

    def test_returns_logger_instance(self):
        """Logger 인스턴스 반환 테스트"""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_logger_has_handler(self):
        """핸들러 설정 테스트"""
        logger = get_logger("test_with_handler")
        assert len(logger.handlers) >= 1

    def test_logger_level_is_info(self):
        """로그 레벨이 INFO인지 테스트"""
        logger = get_logger("test_level")
        assert logger.level == logging.INFO

    def test_logger_reuses_existing_handlers(self):
        """이미 핸들러가 있으면 재사용하는지 테스트"""
        # 첫 번째 호출 - 핸들러 생성
        logger1 = get_logger("test_reuse")
        handler_count_1 = len(logger1.handlers)

        # 두 번째 호출 - 핸들러 재사용 (추가 안 함)
        logger2 = get_logger("test_reuse")
        handler_count_2 = len(logger2.handlers)

        assert logger1 is logger2
        assert handler_count_1 == handler_count_2

    def test_logger_formatter(self):
        """포매터 설정 테스트"""
        logger = get_logger("test_formatter")
        handler = logger.handlers[0]
        formatter = handler.formatter

        assert formatter is not None
        # 포매터 형식 확인 (asctime, name, levelname, message 포함)
        assert "%(asctime)s" in formatter._fmt
        assert "%(name)s" in formatter._fmt
        assert "%(levelname)s" in formatter._fmt
        assert "%(message)s" in formatter._fmt
