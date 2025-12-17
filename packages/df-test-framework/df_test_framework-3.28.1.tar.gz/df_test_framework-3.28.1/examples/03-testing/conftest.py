"""
Pytest 配置文件 (v3.28.0)

基于 df-test-framework v3.28.0 的测试配置示例。
展示如何使用框架提供的自动 fixtures。
"""

import pytest
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from df_test_framework.infrastructure.config import FrameworkSettings, HTTPConfig


class TestSettings(FrameworkSettings):
    """测试环境配置"""

    http: HTTPConfig = Field(
        default_factory=lambda: HTTPConfig(
            base_url="https://jsonplaceholder.typicode.com",
            timeout=30,
        ),
        description="HTTP 配置"
    )

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )


# ========== 启用框架的 pytest 插件 ==========
# 框架自动提供: runtime, http_client, database, redis_client
pytest_plugins = [
    "df_test_framework.testing.fixtures.core",
    "df_test_framework.testing.fixtures.debugging",  # console_debugger, debug_mode
    "df_test_framework.testing.plugins.logging_plugin",  # loguru → logging 桥接
]


# ========== 提供 settings fixture ==========
@pytest.fixture(scope="session")
def settings(runtime):
    """配置对象（从 RuntimeContext 获取）"""
    return runtime.settings


# ========== 测试数据 fixtures ==========
@pytest.fixture
def sample_user_data():
    """提供测试用户数据"""
    return {
        "name": "张三",
        "username": "zhangsan",
        "email": "zhangsan@example.com"
    }


@pytest.fixture
def sample_post_data():
    """提供测试文章数据"""
    return {
        "userId": 1,
        "title": "测试文章标题",
        "body": "这是测试文章的内容"
    }
