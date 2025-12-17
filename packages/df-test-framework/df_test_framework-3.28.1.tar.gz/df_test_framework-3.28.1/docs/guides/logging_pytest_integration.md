# pytest 日志集成指南

> **版本要求**: df-test-framework >= 3.26.0
> **更新日期**: 2025-12-14

---

## 概述

本指南介绍框架如何解决 **loguru 日志与 pytest 测试名称混行** 的问题，以及为什么选择 **loguru → logging 桥接** 作为最终方案。

---

## 问题背景

### 症状

使用 loguru 作为日志库时，运行 pytest 会出现以下显示问题：

```
tests/api/test_auth.py::TestAuth::test_login 2025-12-14 16:15:47 | INFO | 数据库连接已建立
PASSED
tests/api/test_auth.py::TestAuth::test_logout 2025-12-14 16:15:48 | INFO | 用户已登出
PASSED
```

日志消息与测试名称混在同一行，可读性很差。

### 根本原因

```
┌─────────────────────────────────────────────────────────────────────────┐
│  pytest 输出流程                                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. pytest 输出测试名称（不换行）                                       │
│     stdout: "tests/api/test_auth.py::test_login "                      │
│                                                                         │
│  2. 测试执行中，loguru 直接输出到 stderr                                │
│     stderr: "2025-12-14 16:15:47 | INFO | 数据库连接已建立\n"          │
│                                                                         │
│  3. 终端合并显示，日志出现在测试名称后面                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**关键点**：
- pytest 在输出测试名称时不换行，等待测试完成后输出 PASSED/FAILED
- loguru 默认输出到 stderr，不受 pytest 控制
- 两个输出流在终端合并，导致混行

---

## 方案对比分析

我们评估了多种方案：

### 方案 1：覆盖 caplog fixture（v3.23.0 方案）

```python
@pytest.fixture
def caplog(caplog):
    """覆盖 pytest 的 caplog fixture"""
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
    )
    yield caplog
    logger.remove(handler_id)
```

**优点**：
- 实现简单
- caplog 能捕获日志

**缺点**：
- ❌ 不解决混行问题（loguru 仍然直接输出到 stderr）
- ❌ 只在使用 caplog fixture 的测试中生效
- ❌ 每个测试都要添加/移除 handler，有性能开销

### 方案 2：禁用 loguru stderr 输出

```python
# 在 conftest.py 中
from loguru import logger
logger.remove()  # 移除默认 stderr handler
```

**优点**：
- 最简单

**缺点**：
- ❌ 完全看不到日志，调试困难
- ❌ 测试失败时没有日志上下文

### 方案 3：配置 pytest live logging

```ini
# pyproject.toml
[tool.pytest.ini_options]
log_cli = true
log_cli_level = "DEBUG"
```

**优点**：
- pytest 原生功能

**缺点**：
- ❌ 只对标准 logging 生效
- ❌ loguru 不受 pytest log_cli 控制
- ❌ 仍然会混行

### 方案 4：loguru → logging 桥接（✅ 最终选择）

```python
def _loguru_sink(message):
    """将 loguru 日志转发到标准 logging"""
    record = message.record
    logging.getLogger(record["name"]).log(
        record["level"].no,
        message.rstrip("\n")
    )

logger.remove()  # 移除 stderr handler
logger.add(_loguru_sink, format="...", level="DEBUG")
```

**优点**：
- ✅ loguru 官方推荐方案
- ✅ pytest 完全控制日志时序
- ✅ 日志显示在 "Captured log" 区域
- ✅ caplog 原生支持
- ✅ 支持 pytest 的 --log-cli-level 等参数
- ✅ 一次配置，全局生效

**缺点**：
- 实现略复杂
- 日志从实时输出变为测试结束后显示

---

## 最终方案：loguru → logging 桥接

### 设计原理

```
┌─────────────────────────────────────────────────────────────────────────┐
│  v3.26.0 架构                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  loguru.info("message")                                                 │
│          │                                                              │
│          ▼                                                              │
│  _loguru_sink(message)          ← 自定义 sink，替代 stderr             │
│          │                                                              │
│          ▼                                                              │
│  logging.getLogger(name).log()  ← 转发到标准 logging                   │
│          │                                                              │
│          ▼                                                              │
│  pytest LogCaptureHandler       ← pytest 捕获日志                      │
│          │                                                              │
│          ▼                                                              │
│  测试结束后显示在 "Captured log call" 区域                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 关键实现细节

1. **移除 loguru 默认 handler**
   ```python
   logger.remove()  # 移除所有 handler，包括 stderr
   ```

2. **添加桥接 sink**
   ```python
   logger.add(_loguru_sink, format="...", level="DEBUG", enqueue=False)
   ```

3. **确保日志传播**
   ```python
   std_logger = logging.getLogger(name)
   std_logger.setLevel(logging.DEBUG)  # 级别足够低
   std_logger.propagate = True          # 传播到根 logger
   ```

4. **pytest 插件自动配置**
   ```python
   def pytest_configure(config):
       setup_pytest_logging()
   ```

5. **与框架 `setup_logger()` 协作**

   框架的 `setup_logger()` 函数会在 Bootstrap 初始化时调用，它会执行 `logger.remove()` 移除所有 handler。为了防止桥接 handler 被移除，我们引入了 pytest 模式标志：

   ```python
   # logging_plugin.py 中
   def pytest_configure(config):
       set_pytest_mode(True)  # 设置 pytest 模式
       setup_pytest_logging()

   # logger.py 中
   def setup_logger(...):
       logger.remove()
       if _PYTEST_MODE:
           # pytest 模式：使用桥接 handler 而不是 stdout
           logger.add(_loguru_sink, ...)
       else:
           # 正常模式：使用 stdout
           logger.add(sys.stdout, ...)
   ```

   这样，即使 `Bootstrap.run()` 调用了 `setup_logger()`，也会正确使用桥接 handler。

---

## 使用方式

### 基本使用

在项目的 `conftest.py` 中启用插件：

```python
pytest_plugins = [
    "df_test_framework.testing.plugins.logging_plugin",
]
```

### 断言日志内容

```python
def test_api_logging(caplog, http_client):
    """测试 API 调用记录日志"""
    import logging

    with caplog.at_level(logging.DEBUG):
        http_client.get("/api/users")

    # 断言日志内容
    assert "GET" in caplog.text
    assert "/api/users" in caplog.text
```

### 验证日志级别

```python
def test_error_logging(caplog):
    """测试错误日志"""
    from loguru import logger

    with caplog.at_level(logging.ERROR):
        logger.error("Something went wrong")

    assert any(r.levelname == "ERROR" for r in caplog.records)
```

### 手动配置（高级）

如果需要自定义配置：

```python
from df_test_framework.infrastructure.logging import (
    setup_pytest_logging,
    teardown_pytest_logging,
)

@pytest.fixture(scope="session", autouse=True)
def custom_logging():
    setup_pytest_logging(
        level="INFO",
        format_string="{time:HH:mm:ss} | {level} | {message}"
    )
    yield
    teardown_pytest_logging()
```

---

## 效果对比

### 修复前（v3.23.0）

```
tests/api/test_auth.py::test_login 2025-12-14 16:15:47 | INFO | 数据库连接已建立
PASSED
```

### 修复后（v3.26.0）

```
tests/api/test_auth.py::test_login PASSED

------------------------------ Captured log call -------------------------------
INFO     mymodule:auth.py:25 2025-12-14 16:15:47 | INFO | 数据库连接已建立
```

---

## 常见问题

### Q: 为什么不用 pytest 的 live logging？

A: pytest 的 live logging (`log_cli`) 只对标准 `logging` 模块生效。loguru 是独立的日志库，直接输出到 stderr，不受 pytest 控制。桥接方案让 loguru 日志走标准 logging 路径。

### Q: 日志不再实时显示了？

A: 是的，这是设计决策。日志现在显示在测试结束后的 "Captured log" 区域。这样：
- 测试名称和结果清晰可见
- 失败测试的日志集中显示
- 调试时可以用 `--log-cli-level=DEBUG` 启用实时显示

### Q: 能否同时输出到 stderr 和 logging？

A: 可以，但不推荐。如果确实需要：

```python
logger.remove()
logger.add(sys.stderr, level="WARNING")  # stderr 只输出警告以上
logger.add(_loguru_sink, level="DEBUG")  # logging 捕获所有
```

### Q: caplog 捕获不到日志？

检查以下几点：
1. 确保 `logging_plugin` 已加载
2. 使用 `caplog.at_level(logging.DEBUG)` 设置捕获级别
3. 确保测试在 `with caplog.at_level()` 上下文中执行

---

## 技术参考

- [loguru 官方迁移指南](https://loguru.readthedocs.io/en/stable/resources/migration.html)
- [pytest 日志捕获文档](https://docs.pytest.org/en/stable/how-to/logging.html)
- [v3.26.0 发布说明](../releases/v3.26.0.md)

---

## 版本历史

| 版本 | 变更 |
|------|------|
| v3.26.0 | 采用 loguru → logging 桥接，彻底解决混行问题 |
| v3.23.0 | 首次尝试通过覆盖 caplog fixture 集成 loguru |
