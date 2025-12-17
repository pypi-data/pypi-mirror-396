"""调试相关 Fixtures

v3.22.0 新增
v3.22.1 扩展：支持数据库调试
v3.23.0 扩展：通过 ObservabilityConfig 控制是否启用
v3.28.0 改进：显式使用 fixture 或 @pytest.mark.debug 时强制启用
v3.28.1 改进：添加 -s 标志提示

提供测试调试功能的 pytest fixtures:
- console_debugger: 彩色控制台调试输出（HTTP + 数据库）
- debug_mode: 便捷调试模式

v3.28.0 调试输出控制优先级（从高到低）:
    1. @pytest.mark.debug         - 强制启用（最高优先级）
    2. 显式使用 console_debugger  - 启用（用户明确请求）
    3. DEBUG_OUTPUT=true          - 全局启用
    4. DEBUG_OUTPUT=false         - 全局禁用（默认）

注意：调试输出需要 -s 标志才能实时显示：
    pytest -v -s tests/

使用方式：
    # 方式1：显式使用 fixture（推荐，无论全局配置如何都会启用）
    def test_api(http_client, console_debugger):
        response = http_client.get("/users")
        # 控制台自动输出彩色调试信息

    # 方式2：使用 @pytest.mark.debug marker
    @pytest.mark.debug
    def test_problematic_api(http_client):
        response = http_client.get("/users")
        # 控制台自动输出调试信息

    # 方式3：全局配置启用（所有测试都输出）
    # OBSERVABILITY__DEBUG_OUTPUT=true
"""

from __future__ import annotations

import sys
from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest
from loguru import logger

if TYPE_CHECKING:
    from df_test_framework.testing.debugging import ConsoleDebugObserver

# v3.28.1: 是否已经显示过 -s 提示（每个 session 只显示一次）
_s_flag_hint_shown = False


def _is_global_debug_enabled() -> bool:
    """检查全局调试输出配置（v3.23.0）

    读取 ObservabilityConfig 配置决定是否全局启用调试输出。

    Returns:
        True: 全局启用调试输出
        False: 全局禁用调试输出
    """
    try:
        from df_test_framework.infrastructure.config import get_settings

        settings = get_settings()
        if settings is None:
            return False  # 没有配置时默认禁用

        # 检查 observability 配置
        obs = getattr(settings, "observability", None)
        if obs is None:
            return False  # 没有 observability 配置时默认禁用

        # v3.23.0: 使用 ObservabilityConfig
        if not obs.enabled:
            return False  # 总开关关闭
        return obs.debug_output

    except Exception:
        # 配置获取失败时默认禁用
        return False


def _show_s_flag_hint() -> None:
    """显示 -s 标志提示（v3.28.1）

    当调试输出启用但 stderr 被 pytest 捕获时，显示一次提示。
    通过 logger 输出，会显示在 pytest 的日志区域。
    """
    global _s_flag_hint_shown

    # 只提示一次
    if _s_flag_hint_shown:
        return

    # 检查 stderr 是否被捕获（不是 TTY）
    if not sys.stderr.isatty():
        logger.warning("调试输出已启用，使用 -s 标志查看彩色输出: pytest -v -s")
        _s_flag_hint_shown = True


def _create_console_debugger() -> ConsoleDebugObserver:
    """创建控制台调试器实例"""
    from df_test_framework.infrastructure.events import get_event_bus
    from df_test_framework.testing.debugging import ConsoleDebugObserver

    # v3.28.1: 显示 -s 标志提示
    _show_s_flag_hint()

    # 创建调试器
    debugger = ConsoleDebugObserver(
        show_headers=True,
        show_body=True,
        show_params=True,
        max_body_length=500,
        # 数据库调试选项
        show_database=True,
        show_sql=True,
        show_sql_params=True,
        max_sql_length=500,
    )

    # 订阅 EventBus
    event_bus = get_event_bus()
    if event_bus:
        debugger.subscribe(event_bus)

    return debugger


@pytest.fixture
def console_debugger(request: pytest.FixtureRequest) -> Generator[ConsoleDebugObserver, None, None]:
    """控制台调试器 fixture

    v3.22.0 新增
    v3.22.1 扩展：支持数据库调试
    v3.28.0 改进：显式使用时强制启用（忽略全局配置）

    提供事件驱动的彩色控制台调试输出。
    自动订阅 EventBus，在测试结束时自动取消订阅。
    支持 HTTP 请求和数据库查询的调试输出。

    v3.28.0 行为变更：
        显式使用此 fixture 时，无论全局 DEBUG_OUTPUT 配置如何，
        都会创建调试器并输出调试信息。这允许在全局禁用调试的情况下，
        仍然可以为特定测试启用调试。

    使用方式：
        # 显式使用（推荐）- 无论全局配置如何都会启用
        def test_api(http_client, console_debugger):
            response = http_client.get("/users")
            # 控制台自动输出请求/响应调试信息

        # 数据库调试
        def test_db(database, console_debugger):
            database.execute("SELECT * FROM users")
            # 控制台自动输出 SQL 调试信息

        # 自定义配置
        def test_api_custom(http_client, console_debugger):
            console_debugger.show_headers = False
            console_debugger.show_database = False
            console_debugger.max_body_length = 1000
            response = http_client.get("/users")

    Yields:
        ConsoleDebugObserver: 控制台调试器实例（始终创建）
    """
    # v3.28.0: 显式使用 fixture 时，始终创建调试器
    debugger = _create_console_debugger()

    yield debugger

    # 取消订阅
    debugger.unsubscribe()


@pytest.fixture(autouse=True)
def _auto_debug_by_marker(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """自动调试 fixture（通过 marker 或全局配置）

    v3.28.0 新增

    检测 @pytest.mark.debug marker 或全局配置，自动启用调试。
    这是一个 autouse fixture，会在每个测试前自动运行。

    优先级：
        1. @pytest.mark.debug marker - 强制启用
        2. 全局 DEBUG_OUTPUT=true - 启用
        3. 其他情况 - 不启用

    使用方式：
        @pytest.mark.debug
        def test_problematic_api(http_client):
            response = http_client.get("/users")
            # 控制台自动输出调试信息

        @pytest.mark.debug
        class TestDebugAPI:
            def test_get_users(self, http_client):
                response = http_client.get("/users")
    """
    # 检查是否有 debug marker
    has_debug_marker = request.node.get_closest_marker("debug") is not None

    # 检查是否已经显式使用了 console_debugger fixture
    # 如果已经使用了，就不需要再创建了
    if "console_debugger" in request.fixturenames:
        yield
        return

    # 检查是否需要自动启用调试
    should_enable = has_debug_marker or _is_global_debug_enabled()

    if not should_enable:
        yield
        return

    # 自动创建调试器
    debugger = _create_console_debugger()

    yield

    # 取消订阅
    debugger.unsubscribe()


@pytest.fixture
def debug_mode(console_debugger: ConsoleDebugObserver) -> Generator[None, None, None]:
    """调试模式 fixture

    v3.22.0 新增
    v3.28.0 更新：依赖 console_debugger，始终启用

    启用调试模式，显示详细的请求/响应信息。
    这是一个便捷 fixture，只需声明即可启用调试。

    使用方式：
        @pytest.mark.usefixtures("debug_mode")
        def test_api(http_client):
            response = http_client.get("/users")
            # 控制台自动输出调试信息

        # 或者在测试类上使用
        @pytest.mark.usefixtures("debug_mode")
        class TestAPI:
            def test_get_users(self, http_client):
                response = http_client.get("/users")
    """
    yield


__all__ = [
    "console_debugger",
    "debug_mode",
]
