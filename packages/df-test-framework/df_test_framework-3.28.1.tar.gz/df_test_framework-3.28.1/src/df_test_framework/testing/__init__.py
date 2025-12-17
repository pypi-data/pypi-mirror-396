"""测试支持层 - Fixtures、Plugins、Debug工具、Reporting

v3.28.0: 调试系统统一，使用 ConsoleDebugObserver
"""

from .debugging import (
    ConsoleDebugObserver,
    create_console_debugger,
)
from .fixtures import database, http_client, redis_client, runtime
from .plugins import EnvironmentMarker
from .reporting.allure import AllureHelper, attach_json, attach_log, step

__all__ = [
    # Fixtures
    "runtime",
    "http_client",
    "database",
    "redis_client",
    # Reporting
    "AllureHelper",
    "attach_json",
    "attach_log",
    "step",
    # Plugins
    "EnvironmentMarker",
    # Debug工具（v3.28.0 统一使用 ConsoleDebugObserver）
    "ConsoleDebugObserver",
    "create_console_debugger",
]
