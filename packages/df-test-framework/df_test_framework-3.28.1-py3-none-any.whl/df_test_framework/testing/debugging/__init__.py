"""调试工具模块

v3.28.0 重构：统一使用 ConsoleDebugObserver（事件驱动）

提供测试调试功能：
- ConsoleDebugObserver - 现代化控制台调试器（事件驱动，支持 HTTP + 数据库）
- create_console_debugger - 工厂函数

v3.28.0 调试启用方式（优先级从高到低）：
    1. @pytest.mark.debug       - marker 强制启用
    2. console_debugger fixture - 显式使用时启用
    3. DEBUG_OUTPUT=true        - 全局配置启用
    4. DEBUG_OUTPUT=false       - 全局禁用（默认）

使用方式：
    # 方式1：显式使用 fixture（推荐）
    def test_api(http_client, console_debugger):
        response = http_client.get("/users")
        # 控制台自动输出彩色调试信息

    # 方式2：使用 @pytest.mark.debug marker
    @pytest.mark.debug
    def test_problematic_api(http_client):
        response = http_client.get("/users")
        # 控制台自动输出调试信息

    # 方式3：手动订阅 EventBus
    from df_test_framework.testing.debugging import ConsoleDebugObserver
    from df_test_framework.infrastructure.events import get_event_bus

    observer = ConsoleDebugObserver()
    observer.subscribe(get_event_bus())
    # ... 执行请求，自动输出调试信息 ...
    observer.unsubscribe()

历史版本：
    v3.27.0: HTTPDebugger 标记废弃
    v3.28.0: 移除 HTTPDebugger 和 DBDebugger，统一使用 ConsoleDebugObserver
"""

from .console import (
    ConsoleDebugObserver,
    create_console_debugger,
)

__all__ = [
    # Console Debugger（v3.22.0+，事件驱动，推荐）
    "ConsoleDebugObserver",
    "create_console_debugger",
]
