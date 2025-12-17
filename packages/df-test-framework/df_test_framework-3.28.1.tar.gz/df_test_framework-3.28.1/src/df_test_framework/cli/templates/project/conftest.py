"""API项目pytest配置模板"""

CONFTEST_TEMPLATE = """\"\"\"Pytest 全局配置和 Fixtures (v3.28.0)

基于 df-test-framework v3.28.0 提供测试运行时环境和公共 fixtures。

框架自动提供的核心 fixtures:
- runtime: 运行时上下文（Session级别）
- http_client: HTTP客户端（Session级别）
- database: 数据库连接（Session级别）
- redis_client: Redis客户端（Session级别）
- uow: Unit of Work（事务管理 + Repository）
- cleanup: 配置驱动的数据清理（v3.18.0）
- prepare_data: 数据准备 fixture（v3.18.0）
- data_preparer: 数据准备器（v3.18.0）
- metrics_manager: Prometheus 指标管理器（v3.24.0）
- metrics_observer: 事件驱动指标收集（v3.24.0）

v3.28.0 调试系统:
- console_debugger: 彩色控制台调试输出（HTTP + 数据库）
- debug_mode: 便捷调试模式
- @pytest.mark.debug: 为特定测试启用调试

注意: 调试输出需要 -s 标志才能实时显示:
    pytest -v -s tests/
\"\"\"

import pytest
from loguru import logger

# ========== 导入项目的业务 fixtures（如果有）==========
# from {project_name}.fixtures import (
#     # API fixtures
#     # some_api,
#     # 清理 fixtures
#     # cleanup_api_test_data,
# )

# ========== 启用框架的 pytest 插件 ==========
# 框架会自动提供：runtime, http_client, database, redis_client 等
# 框架会自动初始化 RuntimeContext（根据 pytest.ini 中的 df_settings_class）
pytest_plugins = [
    "df_test_framework.testing.fixtures.core",       # 核心 fixtures
    "df_test_framework.testing.fixtures.allure",     # Allure 自动记录
    "df_test_framework.testing.fixtures.debugging",  # 调试工具（console_debugger, debug_mode）
    "df_test_framework.testing.fixtures.metrics",    # 指标收集（metrics_manager, metrics_observer）
    "df_test_framework.testing.plugins.logging_plugin",  # loguru → logging 桥接
]


# ============================================================
# 配置对象 Fixture
# ============================================================

@pytest.fixture(scope="session")
def settings(runtime):
    \"\"\"配置对象 - Session 级别

    从 RuntimeContext 获取配置对象（单例）。

    Args:
        runtime: RuntimeContext 对象（框架自动提供）

    Returns:
        {ProjectName}Settings 配置对象

    使用方式:
        >>> def test_example(settings):
        ...     base_url = settings.http.base_url
        ...     db_host = settings.db.host
    \"\"\"
    return runtime.settings


# ============================================================
# 调试相关说明
# ============================================================
# v3.28.0: 框架提供以下调试方式（通过 df_test_framework.testing.fixtures.debugging）:
#
# 方式1（推荐）: 使用 @pytest.mark.debug marker
#   @pytest.mark.debug
#   def test_problematic_api(http_client):
#       response = http_client.get("/users")
#       # 控制台自动输出彩色调试信息
#
# 方式2: 使用 console_debugger fixture
#   def test_db(database, console_debugger):
#       database.execute("SELECT * FROM users")
#       # 控制台自动输出 SQL 调试信息
#
# 方式3: 使用 debug_mode fixture
#   @pytest.mark.usefixtures("debug_mode")
#   def test_api(http_client):
#       response = http_client.get("/users")
#
# 方式4: 环境变量全局启用
#   OBSERVABILITY__DEBUG_OUTPUT=true pytest -v -s
#
# 注意: 需要 -s 标志才能看到调试输出！


# ============================================================
# Pytest 配置钩子
# ============================================================

def pytest_configure(config: pytest.Config) -> None:
    \"\"\"Pytest 配置钩子 - 在测试运行前执行

    注册自定义标记。

    注意: 框架已自动注册 keep_data 和 debug 标记，无需重复注册。
    \"\"\"
    config.addinivalue_line("markers", "smoke: 冒烟测试，核心功能验证")
    config.addinivalue_line("markers", "regression: 回归测试，全量功能验证")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "slow: 执行时间较长的测试")


def pytest_sessionstart(session: pytest.Session) -> None:
    \"\"\"Session 开始时执行 - 配置 Allure 环境信息

    添加测试环境信息到 Allure 报告。
    \"\"\"
    try:
        from df_test_framework.testing.reporting.allure import AllureHelper

        from {project_name}.config import {ProjectName}Settings

        settings = {ProjectName}Settings()

        AllureHelper.add_environment_info({{
            "环境": settings.env,
            "API地址": settings.http.base_url,
            # "数据库": f"{{settings.db.host}}:{{settings.db.port}}",
            "Python版本": "3.12+",
            "框架版本": "df-test-framework v3.28.0",
            "项目版本": "{project_name} v1.0.0",
            "测试类型": "API自动化测试",
        }})
    except Exception as e:
        logger.warning(f"无法加载 Allure 环境信息: {{e}}")


# ============================================================
# API 测试数据清理示例
# ============================================================
# v3.18.0+: 推荐使用配置驱动的清理（CLEANUP__MAPPINGS__*）
# 框架自动提供 cleanup fixture，只需在 .env 中配置映射即可
#
# .env 示例:
#   CLEANUP__ENABLED=true
#   CLEANUP__MAPPINGS__orders__table=order_table
#   CLEANUP__MAPPINGS__orders__field=order_no
#
# 使用方式:
#   def test_create_order(http_client, cleanup):
#       order_no = DataGenerator.test_id("TEST_ORD")
#       response = http_client.post("/orders", json={{"order_no": order_no}})
#       cleanup.add("orders", order_no)  # 自动清理
#
# 如果需要自定义清理逻辑，可以使用 ListCleanup:
# from df_test_framework.testing.fixtures.cleanup import ListCleanup
#
# @pytest.fixture
# def cleanup_orders(request, http_client):
#     orders = ListCleanup(request)
#     yield orders
#     if orders.should_do_cleanup():
#         for order_id in orders:
#             http_client.delete(f"/orders/{{order_id}}")


# ============================================================
# 导出
# ============================================================

__all__ = [
    "settings",
]
"""

__all__ = ["CONFTEST_TEMPLATE"]
