"""pyproject.toml配置文件模板"""

PYPROJECT_TOML_TEMPLATE = """[project]
name = "{project_name}"
version = "1.0.0"
description = "基于 df-test-framework v3.28.0 的自动化测试项目"
requires-python = ">=3.12"
dependencies = [
    {framework_dependency},
    "pytest>=8.0.0",
    "allure-pytest>=2.13.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "loguru>=0.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest-cov>=5.0.0",
    "ruff>=0.6.0",
    "mypy>=1.11.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.metadata]
allow-direct-references = true

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--alluredir=reports/allure-results",
    "--log-cli-level=INFO",
]
markers = [
    "smoke: 冒烟测试",
    "regression: 回归测试",
    "integration: 集成测试",
    "slow: 执行时间较长的测试",
    # 注意: keep_data 和 debug marker 由框架自动注册，无需在此定义
]
# v3.6.1: 使用 classic 输出模式，避免测试名称与日志混排
console_output_style = "classic"

# v3.13.0: pytest-asyncio 配置（支持 async def test_xxx）
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"

# Live logging: 实时显示日志
log_cli = true
log_cli_level = "INFO"
log_cli_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s | %(message)s"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"

# 过滤警告
filterwarnings = [
    "ignore::pytest.PytestAssertRewriteWarning",
]

# df_settings_class 指定框架使用的 Settings 类
df_settings_class = "{project_name}.config.{ProjectName}Settings"

[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
"""

__all__ = ["PYPROJECT_TOML_TEMPLATE"]
