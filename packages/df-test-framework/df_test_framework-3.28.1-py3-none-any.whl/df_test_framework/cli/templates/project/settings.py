"""API项目配置模板"""

SETTINGS_TEMPLATE = """\"\"\"项目配置 - v3.18.0+ 现代化配置

基于 df-test-framework v3.18.0+ 的测试项目配置。

v3.18.0+ 配置格式：
- ✅ 无 APP_ 前缀（与框架统一）
- ✅ 使用 __ 嵌套分隔符（HTTP__BASE_URL）
- ✅ 中间件列表配置（SignatureMiddlewareConfig, BearerTokenMiddlewareConfig）
- ✅ 配置驱动清理（CLEANUP__MAPPINGS__*）
- ✅ Repository 自动发现（TEST__REPOSITORY_PACKAGE）
- ✅ 可观测性配置（OBSERVABILITY__*）

使用方式:
    >>> from {project_name}.config import {ProjectName}Settings
    >>> settings = {ProjectName}Settings()
    >>> print(settings.http.base_url)
\"\"\"

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from df_test_framework.infrastructure.config import (
    FrameworkSettings,
    HTTPConfig,
    DatabaseConfig,
    RedisConfig,
    ObservabilityConfig,
    SignatureMiddlewareConfig,
    BearerTokenMiddlewareConfig,
    SignatureAlgorithm,
    TokenSource,
)


class BusinessConfig:
    \"\"\"业务配置（使用 BUSINESS_ 前缀）

    清晰的配置分层:
    - 独立于框架配置
    - 包含业务特定的测试数据和配置

    环境变量:
        BUSINESS_TEST_USER_ID - 测试用户ID
        BUSINESS_TEST_ROLE - 测试角色
    \"\"\"

    def __init__(self):
        import os
        self.test_user_id = os.getenv("BUSINESS_TEST_USER_ID", "test_user_001")
        self.test_role = os.getenv("BUSINESS_TEST_ROLE", "admin")


class {ProjectName}Settings(FrameworkSettings):
    \"\"\"项目测试配置（v3.18.0+ 现代化配置）

    v3.18.0+ 特性:
    - ✅ 无 APP_ 前缀（与框架统一）
    - ✅ 中间件列表配置（自动按优先级排序）
    - ✅ 配置驱动清理（CLEANUP__MAPPINGS__*）
    - ✅ 可观测性配置（OBSERVABILITY__*）
    - ✅ Repository 自动发现

    环境变量配置:
        # 基础配置
        ENV - 环境（dev/test/staging/prod）
        DEBUG - 调试模式

        # HTTP 配置
        HTTP__BASE_URL - API基础URL
        HTTP__TIMEOUT - 请求超时时间
        HTTP__MAX_RETRIES - 最大重试次数

        # 签名中间件配置
        SIGNATURE__ENABLED - 签名中间件开关
        SIGNATURE__ALGORITHM - 签名算法（md5/sha256/hmac-sha256）
        SIGNATURE__SECRET - 签名密钥
        SIGNATURE__INCLUDE_PATHS - 包含路径（JSON数组）
        SIGNATURE__EXCLUDE_PATHS - 排除路径（JSON数组）

        # Bearer Token 中间件配置
        BEARER_TOKEN__ENABLED - Token中间件开关
        BEARER_TOKEN__SOURCE - Token来源（login/static/env）
        BEARER_TOKEN__LOGIN_URL - 登录URL
        BEARER_TOKEN__CREDENTIALS - 登录凭证（JSON对象）
        BEARER_TOKEN__TOKEN_PATH - Token路径

        # 数据库配置
        DB__HOST - 数据库主机
        DB__PORT - 数据库端口
        DB__NAME - 数据库名称
        DB__USER - 数据库用户
        DB__PASSWORD - 数据库密码

        # Redis 配置
        REDIS__HOST - Redis主机
        REDIS__PORT - Redis端口
        REDIS__DB - Redis数据库索引
        REDIS__PASSWORD - Redis密码

        # 可观测性配置
        OBSERVABILITY__ENABLED - 总开关
        OBSERVABILITY__DEBUG_OUTPUT - 调试输出（需要 pytest -s）
        OBSERVABILITY__ALLURE_RECORDING - Allure记录

        # 数据清理配置
        CLEANUP__ENABLED - 启用配置驱动清理
        CLEANUP__MAPPINGS__<name>__table - 表名
        CLEANUP__MAPPINGS__<name>__field - 字段名

        # 测试配置
        TEST__KEEP_TEST_DATA - 保留测试数据
        TEST__REPOSITORY_PACKAGE - Repository包路径

    使用方式:
        >>> from {project_name}.config import {ProjectName}Settings
        >>> settings = {ProjectName}Settings()
        >>> print(settings.http.base_url)
    \"\"\"

    # ========== HTTP 配置 ==========
    http: HTTPConfig = Field(
        default_factory=lambda: HTTPConfig(
            base_url="http://localhost:8000/api",
            timeout=30,
            max_retries=3,
        ),
        description="HTTP配置"
    )

    # ========== 签名中间件配置（可选）==========
    # 取消注释以启用签名中间件
    # signature: SignatureMiddlewareConfig = Field(
    #     default_factory=lambda: SignatureMiddlewareConfig(
    #         enabled=True,
    #         priority=10,
    #         algorithm=SignatureAlgorithm.MD5,
    #         secret="your-secret-key",  # ⚠️ 通过环境变量覆盖
    #         header="X-Sign",
    #         include_paths=["/api/**"],
    #         exclude_paths=["/health", "/metrics"],
    #     ),
    #     description="签名中间件配置"
    # )

    # ========== Bearer Token 中间件配置（可选）==========
    # 取消注释以启用 Bearer Token 中间件
    # bearer_token: BearerTokenMiddlewareConfig = Field(
    #     default_factory=lambda: BearerTokenMiddlewareConfig(
    #         enabled=True,
    #         priority=20,
    #         source=TokenSource.LOGIN,
    #         login_url="/auth/login",
    #         credentials={{"username": "admin", "password": "password"}},  # ⚠️ 通过环境变量覆盖
    #         token_path="data.token",
    #         header="Authorization",
    #         token_prefix="Bearer",
    #         include_paths=["/api/**"],
    #         exclude_paths=["/auth/login", "/auth/register"],
    #     ),
    #     description="Bearer Token中间件配置"
    # )

    # ========== 数据库配置（可选）==========
    # 取消注释以启用数据库
    # db: DatabaseConfig = Field(
    #     default_factory=lambda: DatabaseConfig(
    #         host="localhost",
    #         port=3306,
    #         name="test_db",
    #         user="root",
    #         password="password",  # ⚠️ 通过环境变量覆盖
    #         pool_size=10,
    #         charset="utf8mb4",
    #     ),
    #     description="数据库配置"
    # )

    # ========== Redis 配置（可选）==========
    # 取消注释以启用 Redis
    # redis: RedisConfig = Field(
    #     default_factory=lambda: RedisConfig(
    #         host="localhost",
    #         port=6379,
    #         db=0,
    #         password=None,
    #     ),
    #     description="Redis配置"
    # )

    # ========== 可观测性配置 ==========
    observability: ObservabilityConfig = Field(
        default_factory=lambda: ObservabilityConfig(
            enabled=True,
            debug_output=False,  # 设为 True 启用调试输出（需要 pytest -s）
            allure_recording=True,
        ),
        description="可观测性配置"
    )

    # ========== 业务配置 ==========
    @property
    def business(self) -> BusinessConfig:
        \"\"\"获取业务配置\"\"\"
        return BusinessConfig()

    # Pydantic v2 配置
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


__all__ = ["{ProjectName}Settings", "BusinessConfig"]
"""

__all__ = ["SETTINGS_TEMPLATE"]
