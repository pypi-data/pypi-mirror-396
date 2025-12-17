# 可观测性架构设计

## 版本信息

- **版本**: v3.28.0
- **日期**: 2025-12-14
- **状态**: 已实现（三大支柱统一 EventBus 架构 + 调试系统统一）

## 概述

df-test-framework 提供完整的可观测性体系，覆盖日志、追踪、指标三个维度，帮助开发者调试测试、定位问题、生成报告。

**v3.24.0 里程碑**：三大可观测性支柱全部统一到 EventBus 事件驱动架构。

## 架构总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            可观测性三大支柱                                   │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│       Logging       │       Tracing       │           Metrics               │
│    (日志记录)        │    (分布式追踪)      │         (指标监控)               │
│                     │                     │                                 │
│    ┌─────────┐      │   ┌─────────────┐   │     ┌─────────────────┐         │
│    │ Loguru  │      │   │OpenTelemetry│   │     │   Prometheus    │         │
│    └────┬────┘      │   └──────┬──────┘   │     │   (v3.24.0)     │         │
│         │           │          │          │     └────────┬────────┘         │
└─────────┼───────────┴──────────┼──────────┴──────────────┼──────────────────┘
          │                      │                         │
          ▼                      ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EventBus (事件总线)                              │
│                                                                             │
│  ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────────┐    │
│  │ HttpRequest*    │    │ DatabaseQuery*   │    │ CacheOperation*      │    │
│  │ • correlation_id│    │ • correlation_id │    │ • correlation_id     │    │
│  │ • trace_id ─────┼────┼──• trace_id ─────┼────┼──• trace_id          │    │
│  │ • span_id       │    │ • span_id        │    │ • span_id            │    │
│  └────────┬────────┘    └────────┬─────────┘    └──────────┬───────────┘    │
│           │                      │                         │                │
│           └──────────────────────┴─────────────────────────┘                │
│                                  │                                          │
└──────────────────────────────────┼──────────────────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
┌───────────────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│     Observers (观察者)         │ │  MetricsObserver   │ │   Pytest Fixtures  │
├───────────────────────────────┤ │    (v3.24.0)       │ ├────────────────────┤
│ ┌───────────────────────────┐ │ ├────────────────────┤ │ metrics_observer   │
│ │    AllureObserver         │ │ │ • 订阅 EventBus    │ │ console_debugger   │
│ │ • 记录 HTTP/DB/Cache 到   │ │ │ • HTTP 指标        │ │ caplog             │
│ │   Allure 报告             │ │ │ • Database 指标    │ │ debug_mode         │
│ │ • 包含 trace_id 可追溯    │ │ │ • Cache 指标       │ └────────────────────┘
│ └───────────────────────────┘ │ │ • 路径规范化       │
│ ┌───────────────────────────┐ │ │ • Prometheus 输出  │
│ │  ConsoleDebugObserver     │ │ └────────────────────┘
│ │ • 订阅 EventBus           │ │
│ │ • 彩色控制台输出           │ │
│ └───────────────────────────┘ │
└───────────────────────────────┘
```

## 组件详解

### 1. Logging（日志记录）

**技术选型**: [Loguru](https://github.com/Delgan/loguru)

**特点**:
- 零配置开箱即用
- 彩色控制台输出
- 结构化日志支持
- 自动异常追踪

**框架集成**:
```python
from loguru import logger

# 框架内部使用
logger.info("HTTP客户端已初始化: base_url={}", base_url)
logger.debug("执行SQL: {}", sql)
logger.error("请求失败: {}", error)
```

**pytest 集成**（v3.26.0 重构）:
```python
# 方式1: 使用 logging_plugin 自动配置（推荐）
# conftest.py
pytest_plugins = ["df_test_framework.testing.plugins.logging_plugin"]

# 方式2: 手动配置
from df_test_framework.infrastructure.logging import setup_pytest_logging

@pytest.fixture(scope="session", autouse=True)
def _configure_logging():
    setup_pytest_logging()

# 测试中使用 caplog（pytest 原生支持）
def test_example(http_client, caplog):
    import logging
    with caplog.at_level(logging.DEBUG):
        response = http_client.get("/api/users")
    assert "HTTP" in caplog.text
```

**v3.26.0 改进**:
- 采用 loguru → logging 桥接模式
- 日志显示在测试结束后的 "Captured log" 区域
- 解决了日志与测试名称混行的问题

### 2. Metrics（指标监控）

**技术选型**: [Prometheus](https://prometheus.io/) (v3.10.0 引入，v3.24.0 重构)

**特点**:
- 行业标准时序数据库
- 多种指标类型支持
- Grafana 集成
- 零配置模式（无 prometheus_client 时自动降级）
- **v3.24.0**: 事件驱动自动收集（MetricsObserver）

**指标类型**:

| 类型 | 描述 | 使用场景 |
|------|------|----------|
| Counter | 计数器（只增不减） | 请求总数、错误次数 |
| Gauge | 仪表盘（可增可减） | 活跃连接数、队列深度 |
| Histogram | 直方图（分布统计） | 请求耗时分布 |
| Summary | 摘要（百分位统计） | P99 延迟 |

**内置指标（MetricsObserver 自动收集）**:

```python
# HTTP 请求指标
http_requests_total          # 请求总数（method, path, status）
http_request_duration_seconds # 请求耗时直方图
http_requests_in_flight      # 进行中的请求数
http_errors_total            # 错误总数

# 数据库查询指标
db_queries_total             # 查询总数（operation, table, status）
db_query_duration_seconds    # 查询耗时直方图
db_rows_affected             # 影响行数直方图

# 缓存操作指标
cache_operations_total       # 操作总数（operation, status）
cache_operation_duration_seconds # 操作耗时直方图
cache_hits_total             # 缓存命中
cache_misses_total           # 缓存未命中
```

**使用方式**:

```python
# 方式1: 自动收集（推荐，v3.24.0+）
def test_api(http_client, metrics_observer):
    response = http_client.get("/api/users")
    # 指标自动收集到 Prometheus

# 方式2: 手动创建指标
from df_test_framework.infrastructure.metrics import MetricsManager

metrics = MetricsManager(service_name="my-service").init()
requests_total = metrics.counter(
    "custom_requests_total",
    "Custom counter",
    labels=["type"]
)
requests_total.labels(type="test").inc()

# 启动指标服务器（供 Prometheus 抓取）
metrics.start_server(port=8000)
```

**装饰器支持**:
```python
from df_test_framework.infrastructure.metrics import count_calls, time_calls

@count_calls("api_calls_total")
@time_calls("api_duration_seconds")
def call_api():
    ...
```

详见: [Prometheus 指标监控指南](../guides/prometheus_metrics.md)

### 3. Tracing（分布式追踪）

**技术选型**: [OpenTelemetry](https://opentelemetry.io/)

**特点**:
- 行业标准（CNCF 项目）
- 多后端支持（Jaeger、Zipkin、OTLP）
- 自动上下文传播
- 与事件系统深度整合

**追踪上下文注入**:
```python
# 所有事件自动包含追踪上下文
@dataclass(frozen=True)
class Event:
    event_id: str
    timestamp: datetime
    trace_id: str | None  # OpenTelemetry trace ID
    span_id: str | None   # OpenTelemetry span ID
```

**中间件集成**:
```python
# TelemetryMiddleware 自动创建 Span
client = HttpClient(
    base_url="https://api.example.com",
    middlewares=[
        TelemetryMiddleware(),  # 自动追踪
        SignatureMiddleware(...),
    ]
)
```

### 3. EventBus（事件总线）

**设计模式**: 发布-订阅模式

**核心事件类型**:

| 事件类型 | 描述 | 来源 |
|----------|------|------|
| `HttpRequestStartEvent` | HTTP 请求开始 | HttpClient |
| `HttpRequestEndEvent` | HTTP 请求完成 | HttpClient |
| `HttpRequestErrorEvent` | HTTP 请求错误 | HttpClient |
| `DatabaseQueryStartEvent` | SQL 查询开始 | Database |
| `DatabaseQueryEndEvent` | SQL 查询完成 | Database |
| `CacheOperationStartEvent` | 缓存操作开始 | RedisClient |
| `CacheOperationEndEvent` | 缓存操作完成 | RedisClient |
| `StorageOperationStartEvent` | 存储操作开始 | StorageClient |
| `MessagePublishEvent` | 消息发布 | MQ Client |
| `MessageConsumeEvent` | 消息消费 | MQ Client |

**事件关联机制**:
```python
# Start/End 事件通过 correlation_id 关联
start_event, correlation_id = HttpRequestStartEvent.create(...)
# ... 执行请求 ...
end_event = HttpRequestEndEvent.create(correlation_id, ...)

# 同一追踪通过 trace_id 关联
assert start_event.trace_id == end_event.trace_id
```

### 4. Observers（观察者）

#### AllureObserver

**职责**: 将事件记录到 Allure 报告

**订阅事件**:
- HTTP 事件（请求/响应/错误）
- 数据库事件（查询/错误）
- 缓存事件（Redis 操作）
- 存储事件（文件操作）
- 消息队列事件（发布/消费）
- 事务事件（提交/回滚）

**报告效果**:
```
🌐 POST /api/users
  ├─ 📤 Request Details (JSON附件)
  │   {"method": "POST", "url": "/api/users", "json": {"name": "Alice"}}
  ├─ ⚙️ SignatureMiddleware (sub-step)
  │   └─ Changes: {"headers": {"added": {"X-Sign": "md5_..."}}}
  └─ ✅ Response (201) - 145ms (JSON附件)
      {"status_code": 201, "body": "{\"id\": 1, \"name\": \"Alice\"}"}
      trace_id: abc123def456...
```

#### ConsoleDebugObserver

**职责**: 实时彩色控制台调试输出

**支持事件**（v3.22.1）:
- HTTP 请求/响应
- 数据库 SQL 查询

**控制台效果**:
```
🌐 POST /api/v1/users
📤 Request: method=POST, url=https://api.example.com/api/v1/users
   Headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ***'}
   Body: {"name": "Alice", "email": "alice@example.com"}
📥 Response: 201 Created in 145.23ms
   Body: {"id": 1, "name": "Alice", "email": "alice@example.com"}

🗄️ SELECT users
📝 SQL: SELECT * FROM users WHERE id = :id
📊 Params: {'id': 1}
✅ 完成: 1 row(s) in 5.23ms
```

#### MetricsObserver（v3.24.0 新增）

**职责**: 订阅 EventBus 收集 Prometheus 指标

**位置**: `infrastructure/metrics/observer.py`

**订阅事件**:
- HTTP 事件（HttpRequestStart/End/Error）
- 数据库事件（DatabaseQueryStart/End/Error）
- 缓存事件（CacheOperationStart/End/Error）

**设计特点**:
- 事件驱动：订阅 EventBus 而非使用拦截器
- 松耦合：能力层只发布事件，MetricsObserver 负责收集
- 路径规范化：自动将 `/users/123` 规范化为 `/users/{id}`，避免高基数
- 零侵入：不修改能力层代码，只需注册观察者

**使用方式**:
```python
# 通过 fixture 自动注入（推荐）
def test_api(http_client, metrics_observer):
    response = http_client.get("/users")
    # 指标自动收集

# 手动创建
from df_test_framework.infrastructure.events import EventBus
from df_test_framework.infrastructure.metrics import MetricsObserver, MetricsManager

event_bus = EventBus()
metrics = MetricsManager().init()
observer = MetricsObserver(event_bus, metrics)
```

## 数据流

### HTTP 请求完整链路

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ HttpClient  │────▶│ TelemetryMW     │────▶│ 创建 Span       │
│   .get()    │     │ (可选)           │     │ trace_id/span_id│
└─────────────┘     └────────┬─────────┘     └────────┬────────┘
                             │                        │
                             ▼                        │
                   ┌──────────────────┐               │
                   │ 其他中间件        │               │
                   │ Signature/Token  │               │
                   └────────┬─────────┘               │
                            │                         │
                            ▼                         │
                   ┌──────────────────┐               │
                   │EventPublisherMW │◀───────────────┘
                   │ 发布 HttpRequest │    注入 trace_id
                   │ StartEvent      │
                   └────────┬─────────┘
                            │
                            ▼
                      ┌──────────┐
                      │ EventBus │
                      └────┬─────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ AllureObserver │  │ConsoleDebug    │  │MetricsObserver │
│  → Allure报告  │  │  → 控制台      │  │  → Prometheus  │
└────────────────┘  └────────────────┘  └────────────────┘
                                               ↓ (v3.24.0)
```

## 配置控制

### ObservabilityConfig（v3.23.0）

```python
class ObservabilityConfig(BaseModel):
    """可观测性配置"""

    # 总开关（控制所有观察者）
    enabled: bool = True

    # Allure 记录开关
    allure_recording: bool = True

    # 调试输出开关
    debug_output: bool = False
```

### 环境变量

```bash
# 正常测试（默认）
OBSERVABILITY__ENABLED=true
OBSERVABILITY__ALLURE_RECORDING=true
OBSERVABILITY__DEBUG_OUTPUT=false

# 调试模式
OBSERVABILITY__DEBUG_OUTPUT=true

# CI 快速运行（禁用所有可观测性）
OBSERVABILITY__ENABLED=false
```

### 设计原则

1. **事件始终发布**: 能力层（HTTP/DB/Redis/Storage）始终发布事件
2. **观察者控制消费**: 通过配置控制观察者是否订阅
3. **零开销设计**: 无订阅者时，事件发布开销可忽略（空循环）

## Pytest Fixtures

| Fixture | 来源 | 职责 |
|---------|------|------|
| `caplog` | pytest 原生（通过 logging_plugin 桥接） | loguru → logging 桥接，pytest 原生捕获 |
| `console_debugger` | debugging.py | 事件驱动的控制台调试输出 |
| `debug_mode` | debugging.py | 便捷调试模式（依赖 console_debugger） |
| `_auto_debug_by_marker` | debugging.py | 自动检测 @pytest.mark.debug（autouse，v3.28.0） |
| `_auto_allure_observer` | allure.py | 自动 Allure 记录（autouse） |
| `metrics_manager` | metrics.py | Prometheus 指标管理器（Session 级别） |
| `metrics_observer` | metrics.py | 事件驱动指标收集（Session 级别） |
| `test_metrics_observer` | metrics.py | 测试级别指标收集（Function 级别） |

**注意**: v3.28.0 移除了 `http_debugger` fixture，统一使用 `console_debugger`。

**注意**: v3.26.0 移除了 `core.py` 中的 `caplog` fixture 覆盖，改用 `logging_plugin` 提供 loguru → logging 桥接。

### 使用示例

```python
# 方式1: 使用 debug_mode 便捷调试
@pytest.mark.usefixtures("debug_mode")
def test_api(http_client):
    response = http_client.get("/users")
    # 控制台自动输出彩色调试信息

# 方式2: 使用 console_debugger 自定义配置
def test_api_custom(http_client, console_debugger):
    console_debugger.show_headers = False
    console_debugger.max_body_length = 1000
    response = http_client.get("/users")

# 方式3: 检查日志内容
def test_with_logging(http_client, caplog):
    response = http_client.get("/users")
    assert "HTTP客户端" in caplog.text

# 方式4: 环境变量全局启用
# OBSERVABILITY__DEBUG_OUTPUT=true pytest -v -s
```

## 能力层事件发布方式

不同能力层根据自身架构特点，采用不同的事件发布方式：

| 能力层 | 有中间件链？ | 事件发布方式 | 原因 |
|--------|-------------|-------------|------|
| HTTP   | ✅ 有       | 中间件内发布 | 需要在中间件处理后发布，确保信息完整 |
| Database | ❌ 无     | 直接发布     | 无中间件，直接在执行前后发布 |
| Redis  | ❌ 无       | 直接发布     | 无中间件，直接在执行前后发布 |
| Storage | ❌ 无      | 直接发布     | 无中间件，直接在执行前后发布 |

详见: [observability-config-design.md](../design/observability-config-design.md)

## EventBus 集成状态

> 详细分析见 [EventBus 集成架构分析](./eventbus-integration-analysis.md)

### 已集成 EventBus（v3.24.0 统一架构）

| 模块 | 发布方式 | 说明 |
|------|----------|------|
| HttpClient | HttpEventPublisherMiddleware | 中间件链最后发布 |
| Database | 直接发布 | 无中间件，执行前后发布 |
| Redis | 直接发布 | 无中间件，执行前后发布 |
| AllureObserver | 订阅 EventBus | 自动记录到 Allure |
| ConsoleDebugObserver | 订阅 EventBus | 彩色控制台输出 |
| **MetricsObserver** | 订阅 EventBus | **v3.24.0 新增**：Prometheus 指标收集 |

### 待集成 EventBus（规划中）

| 模块 | 当前模式 | 建议 |
|------|----------|------|
| gRPC Interceptors | 自定义拦截器链 | v3.25.0+：引入 gRPC 事件类型 |

**三大支柱集成现状（v3.24.0 已全部统一）**:

```
Logging ─────▶ ConsoleDebugObserver ─────▶ EventBus  ✅ 已集成
Tracing ─────▶ HttpTelemetryMiddleware ──▶ EventBus  ✅ 已集成
Metrics ─────▶ MetricsObserver ──────────▶ EventBus  ✅ 已集成 (v3.24.0)
```

## 版本演进

| 版本 | 特性 |
|------|------|
| v3.10.0 | Prometheus 指标监控，MetricsManager，HTTP/DB 指标集成 |
| v3.17.0 | EventBus 重构，事件关联（correlation_id），OpenTelemetry 整合 |
| v3.18.0 | AllureObserver 事件驱动，统一各能力层集成 |
| v3.22.0 | ConsoleDebugObserver，HttpEventPublisherMiddleware |
| v3.22.1 | ConsoleDebugObserver 支持数据库调试 |
| v3.23.0 | ObservabilityConfig 统一配置，caplog fixture |
| v3.24.0 | MetricsObserver 事件驱动架构，三大支柱全部统一到 EventBus |
| v3.26.0 | pytest 日志集成重构：loguru → logging 桥接，解决混行问题 |
| v3.27.0 | ConsoleDebugObserver pytest 模式自动检测，HTTPDebugger 废弃 |
| **v3.28.0** | **调试系统统一：移除 HTTPDebugger/DBDebugger，新增 @pytest.mark.debug** |

## 相关文档

- [EventBus 集成架构分析](./eventbus-integration-analysis.md) - 各模块 EventBus 集成状态分析
- [可观测性与调试系统统一设计](./observability-debugging-unification.md) - v3.28.0 调试系统重构
- [ObservabilityConfig 设计](../design/observability-config-design.md)
- [Prometheus 指标监控指南](../guides/prometheus_metrics.md)
- [pytest 日志集成指南](../guides/logging_pytest_integration.md) - loguru → logging 桥接设计（v3.26.0）
- [V3.17 事件系统重设计](V3.17_EVENT_SYSTEM_REDESIGN.md)
- [Allure 集成设计](../archive/reports/ALLURE_INTEGRATION_DESIGN.md)
