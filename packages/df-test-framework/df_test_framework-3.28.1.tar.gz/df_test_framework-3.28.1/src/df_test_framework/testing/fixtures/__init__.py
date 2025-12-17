"""
df-test-framework fixture entry points.

The primary pytest plugin lives in `df_test_framework.fixtures.core`.

v3.18.0 新增:
- ConfigDrivenCleanupManager: 配置驱动的数据清理管理器
- cleanup: 配置驱动的清理 fixture（零代码配置）
- prepare_data: 数据准备 fixture（回调式）
- data_preparer: 数据准备器（上下文管理器式）

v3.22.0 新增:
- console_debugger: 彩色控制台调试输出（事件驱动）
- debug_mode: 调试模式便捷 fixture

v3.28.0 变更:
- 移除 http_debugger，统一使用 console_debugger
- 新增 @pytest.mark.debug marker 支持

v3.24.0 新增:
- metrics_manager: Prometheus 指标管理器
- metrics_observer: 事件驱动的指标收集器
- test_metrics_observer: 测试级别的指标收集器
"""

# Allure fixture（薄包装层，依赖 reporting.allure 的核心实现）
from .allure import _auto_allure_observer  # noqa: F401
from .cleanup import (  # noqa: F401
    CleanupManager,
    ConfigDrivenCleanupManager,  # v3.18.0
    ListCleanup,
    SimpleCleanupManager,
    should_keep_test_data,
)
from .core import (  # noqa: F401
    cleanup,  # v3.18.0
    data_preparer,  # v3.18.0
    database,
    http_client,
    prepare_data,  # v3.18.0
    redis_client,
    runtime,
    uow,  # v3.13.0
)

# v3.22.0: 调试相关 fixtures（v3.28.0 移除 http_debugger）
from .debugging import (  # noqa: F401
    console_debugger,
    debug_mode,
)

# v3.24.0: 指标收集 fixtures
from .metrics import (  # noqa: F401
    metrics_manager,
    metrics_observer,
    test_metrics_observer,
)
from .ui import (  # noqa: F401
    browser,
    browser_manager,
    context,
    goto,
    page,
    screenshot,
    ui_manager,
)

__all__ = [
    # API测试fixtures
    "runtime",
    "http_client",
    "database",
    "redis_client",
    "uow",  # v3.13.0
    # 数据清理（v3.18.0 增强）
    "should_keep_test_data",
    "CleanupManager",
    "SimpleCleanupManager",
    "ListCleanup",
    "ConfigDrivenCleanupManager",  # v3.18.0
    "cleanup",  # v3.18.0
    # 数据准备（v3.18.0）
    "prepare_data",  # v3.18.0
    "data_preparer",  # v3.18.0
    # 调试工具（v3.22.0，v3.28.0 移除 http_debugger）
    "console_debugger",
    "debug_mode",
    # 指标收集（v3.24.0）
    "metrics_manager",
    "metrics_observer",
    "test_metrics_observer",
    # UI测试fixtures
    "browser_manager",
    "browser",
    "context",
    "page",
    "ui_manager",
    "goto",
    "screenshot",
]
