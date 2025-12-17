"""pytest 日志插件 - 自动配置 loguru 与 pytest 集成

此插件自动将 loguru 日志桥接到标准 logging 模块，
让 pytest 能够正确控制日志的显示时序。

使用方式:
    # 方式 1: 在 conftest.py 中声明插件（推荐）
    pytest_plugins = ["df_test_framework.testing.plugins.logging_plugin"]

    # 方式 2: 手动在 conftest.py 中调用
    from df_test_framework.infrastructure.logging import setup_pytest_logging

    @pytest.fixture(scope="session", autouse=True)
    def _configure_logging():
        setup_pytest_logging()

效果:
    - 日志不再与测试名称混在同一行
    - 测试失败时日志显示在 "Captured log" 区域
    - 支持 pytest 的 --log-cli-level 等日志参数
    - 支持 pytest 的 live logging 配置
"""

import pytest

from df_test_framework.infrastructure.logging import (
    setup_pytest_logging,
    teardown_pytest_logging,
)
from df_test_framework.infrastructure.logging.logger import set_pytest_mode


def pytest_configure(config: pytest.Config) -> None:
    """pytest 配置阶段钩子

    在 pytest 开始收集测试之前调用，配置 loguru → logging 桥接。
    """
    # 设置 pytest 模式标志，让 setup_logger() 知道应该使用桥接 handler
    set_pytest_mode(True)

    # 从 pytest 配置中获取日志级别
    log_level = config.getini("log_level") or "DEBUG"

    # 配置 loguru 桥接
    setup_pytest_logging(level=log_level.upper())


def pytest_unconfigure(config: pytest.Config) -> None:
    """pytest 退出阶段钩子

    在 pytest 退出之前调用，清理 loguru 配置。
    """
    teardown_pytest_logging()
    # 恢复 pytest 模式标志
    set_pytest_mode(False)
