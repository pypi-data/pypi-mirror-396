""".env 环境配置文件模板"""

ENV_TEMPLATE = """# =============================================================================
# {ProjectName} 测试项目 - 环境配置 (v3.18.0+)
#
# v3.18.0+ 配置格式：
# - ✅ 无 APP_ 前缀（与框架统一）
# - ✅ 使用 __ 嵌套分隔符
# - ✅ 配置驱动清理（CLEANUP__MAPPINGS__*）
# - ✅ Repository 自动发现（TEST__REPOSITORY_PACKAGE）
#
# 说明：
# - 大部分配置已在 settings.py 中设置了默认值
# - 以下环境变量可以覆盖默认值
# =============================================================================

# ============================================================
# 环境配置
# ============================================================
ENV=test
DEBUG=false

# ============================================================
# HTTP 基础配置
# ============================================================
HTTP__BASE_URL=http://localhost:8000/api
HTTP__TIMEOUT=30
HTTP__MAX_RETRIES=3

# ============================================================
# 签名中间件配置 (v3.18.1)
# 注意：列表类型需要使用 JSON 数组格式
# ============================================================
# SIGNATURE__ENABLED=true
# SIGNATURE__PRIORITY=10
# SIGNATURE__ALGORITHM=md5
# SIGNATURE__SECRET=your_secret_key
# SIGNATURE__HEADER=X-Sign
# SIGNATURE__INCLUDE_PATHS=["/api/**"]
# SIGNATURE__EXCLUDE_PATHS=["/health","/metrics"]

# ============================================================
# Bearer Token 中间件配置 (v3.18.1)
# ============================================================
# BEARER_TOKEN__ENABLED=true
# BEARER_TOKEN__PRIORITY=20
# BEARER_TOKEN__SOURCE=login
# BEARER_TOKEN__LOGIN_URL=/auth/login
# BEARER_TOKEN__CREDENTIALS={{"username":"admin","password":"password"}}
# BEARER_TOKEN__TOKEN_PATH=data.token
# BEARER_TOKEN__HEADER=Authorization
# BEARER_TOKEN__TOKEN_PREFIX=Bearer
# BEARER_TOKEN__INCLUDE_PATHS=["/api/**"]
# BEARER_TOKEN__EXCLUDE_PATHS=["/auth/login","/auth/register"]

# ============================================================
# 数据库配置
# ============================================================
# DB__HOST=localhost
# DB__PORT=3306
# DB__NAME=test_db
# DB__USER=root
# DB__PASSWORD=password
# DB__POOL_SIZE=10
# DB__CHARSET=utf8mb4

# ============================================================
# Redis 配置
# ============================================================
# REDIS__HOST=localhost
# REDIS__PORT=6379
# REDIS__DB=0
# REDIS__PASSWORD=

# ============================================================
# 日志配置
# ============================================================
# LOGGING__LEVEL=INFO

# ============================================================
# 业务配置（独立前缀 BUSINESS_）
# ============================================================
BUSINESS_TEST_USER_ID=test_user_001
BUSINESS_TEST_ROLE=admin

# ============================================================
# 测试执行配置 (v3.13.0+)
# ============================================================
# 本地开发调试，保留数据
#TEST__KEEP_TEST_DATA=1
# Repository 自动发现
#TEST__REPOSITORY_PACKAGE={project_name}.repositories

# ============================================================
# 数据清理配置 (v3.18.0)
# ============================================================
# 启用配置驱动的清理
#CLEANUP__ENABLED=true
# 清理映射示例：订单
#CLEANUP__MAPPINGS__orders__table=order_table
#CLEANUP__MAPPINGS__orders__field=order_no

# ============================================================
# 可观测性配置 (v3.23.0+)
# ============================================================
# 总开关（默认 true）
OBSERVABILITY__ENABLED=true
# Allure 记录（默认 true）
OBSERVABILITY__ALLURE_RECORDING=true
# 启用调试输出（需要 pytest -v -s）
#OBSERVABILITY__DEBUG_OUTPUT=true
"""

__all__ = ["ENV_TEMPLATE"]
