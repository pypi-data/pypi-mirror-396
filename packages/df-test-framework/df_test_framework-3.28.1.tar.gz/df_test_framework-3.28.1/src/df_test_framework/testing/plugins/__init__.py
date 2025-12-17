"""Pytest 插件模块

提供 pytest 插件扩展（依赖 pytest）：
- EnvironmentMarker: 环境标记插件
- DebugPlugin: 调试插件，测试失败时收集环境信息
- 环境装饰器: dev_only, prod_only, skip_if_dev, skip_if_prod
- logging_plugin: loguru → logging 桥接插件（v3.26.0）

架构说明：
- fixtures/ - pytest fixture 定义
- plugins/ - pytest hooks/markers（本模块）
- reporting/allure/ - Allure 观察者、工具类（不依赖 pytest）
- debugging/ - 调试器实现（不依赖 pytest）

日志插件使用:
    # 在项目的 conftest.py 中声明
    pytest_plugins = ["df_test_framework.testing.plugins.logging_plugin"]
"""

from .debug import DebugPlugin
from .markers import (
    EnvironmentMarker,
    dev_only,
    get_env,
    is_env,
    prod_only,
    skip_if_dev,
    skip_if_prod,
)

__all__ = [
    # 环境标记插件
    "EnvironmentMarker",
    "get_env",
    "is_env",
    "skip_if_prod",
    "skip_if_dev",
    "dev_only",
    "prod_only",
    # 调试插件
    "DebugPlugin",
]
