"""pytest 日志集成模块 - loguru → logging 桥接

通过将 loguru 日志桥接到标准 logging 模块，让 pytest 能够原生控制日志时序。

设计原理:
    pytest 的日志系统基于标准 logging 模块，它控制日志何时显示：
    - 测试运行时：收集日志到 "Captured log" 缓冲区
    - 测试结束后：统一显示日志（在测试名称之后）
    - live logging：可配置实时显示

    loguru 是一个独立的日志库，默认直接输出到 stderr，
    这会导致日志与测试名称混在一起。

    解决方案是将 loguru 桥接到标准 logging，让 pytest 控制时序。

使用方式:
    # 在 conftest.py 中
    from df_test_framework.infrastructure.logging import setup_pytest_logging

    @pytest.fixture(scope="session", autouse=True)
    def _configure_logging():
        setup_pytest_logging()

    # 或者使用框架提供的 pytest 插件（推荐）
    pytest_plugins = ["df_test_framework.testing.plugins.logging_plugin"]

参考:
    - https://loguru.readthedocs.io/en/stable/resources/migration.html
    - https://docs.pytest.org/en/stable/how-to/logging.html
"""

import logging
import sys

from loguru import logger

# 模块级别的 handler_id，用于追踪已添加的 handler
_handler_id: int | None = None


def _loguru_sink(message: str) -> None:
    """loguru sink 函数 - 将日志转发到标准 logging 模块

    这个函数作为 loguru 的 sink，接收日志消息，
    并将原始消息文本发送到标准 logging 模块。
    pytest 会通过 logging 捕获这些日志并使用自己的格式。

    Args:
        message: loguru 的消息对象（包含 record 属性）
    """
    # loguru 的 message 是一个特殊的 str 子类，包含 record 属性
    record = message.record

    # 获取对应的 logging 级别
    level = record["level"].no

    # 获取 logger 名称（使用模块名）
    name = record["name"]

    # 获取标准 logging 的 logger
    std_logger = logging.getLogger(name)
    std_logger.setLevel(logging.DEBUG)
    std_logger.propagate = True

    # 创建 LogRecord 并设置正确的函数名和行号
    # 这样 pytest 的 log_cli_format 中的 %(funcName)s 会显示正确的函数名
    log_record = logging.LogRecord(
        name=name,
        level=level,
        pathname=record["file"].path if record["file"] else "",
        lineno=record["line"],
        msg=record["message"],
        args=(),
        exc_info=None,
        func=record["function"],
    )

    # 通过 handle 方法处理，确保 pytest 能捕获
    std_logger.handle(log_record)


def setup_pytest_logging(level: str = "DEBUG") -> int:
    """配置 loguru 与 pytest 集成

    此函数移除 loguru 默认的 stderr handler，添加一个将日志
    桥接到标准 logging 模块的 handler。这样 pytest 就能控制
    日志的显示时序和格式。

    日志格式由 pytest 的 log_cli_format 配置控制，而不是 loguru。

    Args:
        level: 日志级别，默认 DEBUG

    Returns:
        handler_id: 新添加的 handler ID，可用于后续移除

    Note:
        此函数应在 pytest session 开始时调用一次。
        框架的 pytest 插件会自动调用此函数。
    """
    global _handler_id

    # 如果已经配置过，先移除旧的 handler
    if _handler_id is not None:
        try:
            logger.remove(_handler_id)
        except ValueError:
            pass  # handler 已被移除

    # 移除 loguru 默认的 stderr handler
    logger.remove()

    # 确保根 logger 级别足够低，以便捕获所有日志
    # pytest 会添加自己的 handler 来捕获日志
    logging.getLogger().setLevel(logging.DEBUG)

    # 添加桥接 sink 到 loguru
    # 不使用 format，因为格式化由 pytest/logging 负责
    _handler_id = logger.add(
        _loguru_sink,
        format="{message}",  # 只传递原始消息
        level=level,
        enqueue=False,  # 不使用队列，保持同步
    )

    return _handler_id


def teardown_pytest_logging() -> None:
    """清理 pytest 日志集成

    移除桥接 handler，恢复 loguru 默认行为。
    通常在测试 session 结束时调用。
    """
    global _handler_id

    if _handler_id is not None:
        try:
            logger.remove(_handler_id)
        except ValueError:
            pass
        _handler_id = None

    # 恢复 loguru 默认 handler
    logger.add(sys.stderr)


__all__ = [
    "setup_pytest_logging",
    "teardown_pytest_logging",
]
