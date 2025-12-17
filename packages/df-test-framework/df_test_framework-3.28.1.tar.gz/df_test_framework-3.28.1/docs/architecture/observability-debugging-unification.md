# 可观测性与调试系统统一设计

> **版本**: v3.28.0
> **日期**: 2025-12-14
> **状态**: 已实施

---

## 1. 背景

在 v3.26.0 完成 loguru → logging 桥接后，对整个可观测性和调试系统进行了全面审查。v3.27.0 将 HTTPDebugger 标记为废弃，v3.28.0 完成了调试系统的统一重构。

---

## 2. 演进历史

| 版本 | 变更 |
|------|------|
| v3.22.0 | 引入 ConsoleDebugObserver（事件驱动） |
| v3.26.0 | loguru → logging 桥接（pytest 兼容） |
| v3.27.0 | ConsoleDebugObserver pytest 模式，HTTPDebugger 废弃 |
| v3.28.0 | **移除 HTTPDebugger/DBDebugger，统一使用 ConsoleDebugObserver** |

---

## 3. 当前架构（v3.28.0）

### 3.1 组件清单

| 组件 | 位置 | 类型 | 输出方式 | 触发方式 |
|------|------|------|----------|----------|
| AllureObserver | testing/reporting/allure/ | 事件驱动 | Allure API | EventBus 订阅 |
| ConsoleDebugObserver | testing/debugging/console.py | 事件驱动 | loguru/stderr | EventBus 订阅 |
| MetricsObserver | infrastructure/metrics/observer.py | 事件驱动 | Prometheus | EventBus 订阅 |
| ObservabilityLogger | infrastructure/logging/observability.py | 日志封装 | loguru | 直接调用 |

**注意**：v3.28.0 移除了 HTTPDebugger 和 DBDebugger。

### 3.2 架构图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           可观测性与调试统一架构（v3.28.0）                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        能力层 (Capabilities)                              │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────────┐    │   │
│  │  │HttpClient │  │ Database  │  │   Redis   │  │ Storage/Messenger │    │   │
│  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────────┬─────────┘    │   │
│  └────────┼──────────────┼──────────────┼──────────────────┼──────────────┘   │
│           │              │              │                  │                   │
│           ▼              ▼              ▼                  ▼                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         EventBus (事件总线)                               │   │
│  │   http.request.*  │  db.query.*  │  cache.operation.*  │  storage.*     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                    │                    │                    │                 │
│        ┌───────────┼────────────────────┼────────────────────┼───────────┐    │
│        ▼           ▼                    ▼                    ▼           │    │
│  ┌───────────┐ ┌───────────┐    ┌───────────────┐                        │    │
│  │  Allure   │ │  Console  │    │    Metrics    │                        │    │
│  │ Observer  │ │  Debug    │    │   Observer    │                        │    │
│  │           │ │ Observer  │    │               │                        │    │
│  │→ Allure   │ │→ loguru   │    │→ Prometheus   │                        │    │
│  │  报告     │ │  /stderr  │    │               │                        │    │
│  └───────────┘ └───────────┘    └───────────────┘                        │    │
│                      │                                                         │
│                      ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         日志系统                                          │   │
│  │                                                                           │   │
│  │  ConsoleDebugObserver._output()                                          │   │
│  │          │                                                                │   │
│  │          ├─── pytest 模式 ───► loguru ───► logging ───► pytest caplog   │   │
│  │          │                                                                │   │
│  │          └─── 正常模式 ────► sys.stderr (彩色输出)                        │   │
│  │                                                                           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. 调试输出控制

### 4.1 控制优先级（v3.28.0）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        调试输出控制优先级（从高到低）                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. @pytest.mark.debug       ──► 强制启用（最高优先级）                       │
│                                                                             │
│  2. 显式使用 console_debugger ──► 启用（用户明确请求）                        │
│                                                                             │
│  3. DEBUG_OUTPUT=true        ──► 全局启用                                   │
│                                                                             │
│  4. DEBUG_OUTPUT=false       ──► 全局禁用（默认）                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 使用方式

**重要**：需要 `-s` 标志才能看到调试输出：

```bash
# 使用 -s 标志禁用 pytest 输出捕获
pytest -v -s tests/
```

```python
# 方式1：@pytest.mark.debug marker
@pytest.mark.debug
def test_problematic_api(http_client):
    response = http_client.get("/users")
    # 控制台自动输出调试信息

# 方式2：显式使用 fixture
def test_with_debug(http_client, console_debugger):
    response = http_client.get("/users")
    # 控制台自动输出调试信息

# 方式3：全局配置
# .env 文件中设置：
# OBSERVABILITY__DEBUG_OUTPUT=true
# 然后运行：pytest -v -s tests/
```

---

## 5. 设计决策

### 5.1 v3.27.0 决策

| 决策项 | 决策 | 理由 |
|--------|------|------|
| ConsoleDebugObserver 输出 | 增加 pytest 模式自动检测 | 与日志系统保持一致 |
| HTTPDebugger | 标记为废弃 | 被 ConsoleDebugObserver 取代 |

### 5.2 v3.28.0 决策

| 决策项 | 决策 | 理由 |
|--------|------|------|
| HTTPDebugger | **移除** | 已在 v3.27.0 废弃，功能完全被 ConsoleDebugObserver 取代 |
| DBDebugger | **移除** | 同样是旧模式，ConsoleDebugObserver 已支持数据库调试 |
| http_debugger fixture | **移除** | 改用 console_debugger |
| 显式 fixture 优先 | **新增** | 允许在全局禁用时为特定测试启用调试 |
| @pytest.mark.debug | **新增** | 提供更便捷的调试启用方式 |

---

## 6. 技术实现

### 6.1 ConsoleDebugObserver 输出（v3.28.0）

```python
def _output(self, text: str) -> None:
    """输出到控制台

    调试输出直接写入 stderr，保持彩色格式和结构化输出。
    需要使用 pytest -s 标志才能看到输出。
    """
    print(text, file=sys.stderr)
    if self.output_to_logger:
        logger.debug(text)
```

**注意**：调试输出需要 `-s` 标志才能实时显示：
```bash
# ✅ 正确：使用 -s 查看调试输出
pytest -v -s tests/

# ❌ 无 -s：stderr 被 pytest 捕获，只有测试失败时才显示
pytest -v tests/
```

### 6.2 自动调试 fixture（v3.28.0）

```python
@pytest.fixture(autouse=True)
def _auto_debug_by_marker(request: pytest.FixtureRequest):
    """自动检测 marker 或全局配置"""
    has_debug_marker = request.node.get_closest_marker("debug") is not None

    if "console_debugger" in request.fixturenames:
        yield
        return

    should_enable = has_debug_marker or _is_global_debug_enabled()

    if should_enable:
        debugger = _create_console_debugger()
        yield
        debugger.unsubscribe()
    else:
        yield
```

---

## 7. 迁移指南

### 从 HTTPDebugger 迁移

```python
# ❌ 旧方式（v3.28.0 已移除）
from df_test_framework.testing.debugging import HTTPDebugger
debugger = HTTPDebugger()
debugger.log_request("GET", "/users")

# ✅ 新方式
def test_api(http_client, console_debugger):
    response = http_client.get("/users")
```

### 从 DBDebugger 迁移

```python
# ❌ 旧方式（v3.28.0 已移除）
from df_test_framework.testing.debugging import enable_db_debug
debugger = enable_db_debug()

# ✅ 新方式
def test_db(database, console_debugger):
    database.execute("SELECT * FROM users")
```

---

## 8. 相关文档

- [可观测性架构设计](./observability-architecture.md)
- [pytest 日志集成指南](../guides/logging_pytest_integration.md)
- [v3.27.0 发布说明](../releases/v3.27.0.md)
- [v3.28.0 发布说明](../releases/v3.28.0.md)
