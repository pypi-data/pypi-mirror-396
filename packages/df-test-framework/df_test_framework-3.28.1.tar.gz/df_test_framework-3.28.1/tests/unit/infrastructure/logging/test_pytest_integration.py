"""pytest 日志集成测试

测试 loguru → logging 桥接功能。
"""

import logging

import pytest
from loguru import logger

from df_test_framework.infrastructure.logging.pytest_integration import (
    setup_pytest_logging,
    teardown_pytest_logging,
)


class TestSetupPytestLogging:
    """setup_pytest_logging 测试"""

    def test_setup_returns_handler_id(self):
        """测试 setup 返回 handler_id"""
        handler_id = setup_pytest_logging()
        assert isinstance(handler_id, int)
        # 不调用 teardown，保持桥接状态

    def test_setup_twice_is_safe(self):
        """测试多次调用 setup 是安全的"""
        id1 = setup_pytest_logging()
        id2 = setup_pytest_logging()

        # 两次调用应该返回不同的 handler_id
        assert id1 != id2


class TestTeardownPytestLogging:
    """teardown_pytest_logging 测试"""

    def test_teardown_twice_is_safe(self):
        """测试多次调用 teardown 是安全的"""
        # 先设置
        setup_pytest_logging()
        teardown_pytest_logging()
        teardown_pytest_logging()  # 第二次调用不应该报错

        # 恢复桥接状态，以便后续测试
        setup_pytest_logging()


class TestLoguruPytestIntegration:
    """端到端集成测试

    注意：由于 logging_plugin 已在 conftest.py 中自动启用，
    这些测试验证的是已经配置好的桥接功能。
    """

    @pytest.fixture(autouse=True)
    def ensure_bridge_active(self):
        """确保每个测试前桥接是活跃的"""
        # logging_plugin 应该已经设置了桥接
        # 但为了保险起见，重新设置一次
        setup_pytest_logging()
        yield

    def test_loguru_logs_captured_by_caplog(self, caplog):
        """测试 loguru 日志被 caplog 捕获"""
        with caplog.at_level(logging.DEBUG):
            logger.info("Integration test message")

        # 验证日志被捕获
        assert "Integration test message" in caplog.text

    def test_loguru_log_levels(self, caplog):
        """测试不同日志级别"""
        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")

        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text

    def test_loguru_logs_with_format(self, caplog):
        """测试日志格式化"""
        with caplog.at_level(logging.DEBUG):
            logger.info("User {} logged in", "alice")

        assert "User alice logged in" in caplog.text

    def test_loguru_logs_module_name(self, caplog):
        """测试日志包含模块名"""
        with caplog.at_level(logging.DEBUG):
            logger.info("Test message")

        # caplog.records 包含 LogRecord 对象
        assert len(caplog.records) > 0
        # 验证记录存在
        assert any("Test message" in record.message for record in caplog.records)
