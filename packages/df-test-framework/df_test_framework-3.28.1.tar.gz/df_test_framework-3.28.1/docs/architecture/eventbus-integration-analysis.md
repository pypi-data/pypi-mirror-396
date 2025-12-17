# EventBus 集成架构分析

> 分析日期: 2025-12-14
> 版本: v3.24.0（已完成 Metrics 重构）

本文档分析框架各模块与 EventBus 的集成状态，识别架构不一致问题并提出改进建议。

## 背景

v3.17.0 引入了 EventBus 事件驱动架构，将可观测性从紧耦合改为松耦合：

```
能力层 ──发布事件──▶ EventBus ──订阅──▶ 观察者（Allure/Console/Metrics）
```

v3.24.0 完成了 Metrics 模块的重构，现在三大支柱全部统一到 EventBus 架构。

---

## 模块集成状态总览

### ✅ 已集成 EventBus（推荐架构）

| 模块 | 位置 | 说明 |
|------|------|------|
| HttpClient | `capabilities/clients/http/` | 通过 HttpEventPublisherMiddleware 发布事件 |
| HttpTelemetryMiddleware | `capabilities/clients/http/middleware/telemetry.py` | Tracing + EventBus 双通道 |
| Database | `capabilities/databases/database.py` | 直接发布 DatabaseQueryStartEvent/EndEvent |
| Redis | `capabilities/databases/redis/redis_client.py` | 直接发布 CacheOperationEvent |
| AllureObserver | `testing/reporting/allure/observer.py` | 订阅 EventBus 记录到 Allure |
| ConsoleDebugObserver | `testing/debugging/console.py` | 订阅 EventBus 彩色输出 |
| **MetricsObserver** | `infrastructure/metrics/observer.py` | **v3.24.0 新增**：订阅 EventBus 收集 Prometheus 指标 |

### ⚠️ 未集成 EventBus（待改进）

| 模块 | 版本 | 位置 | 状态 |
|------|------|------|------|
| ~~MetricsInterceptor~~ | ~~v3.10.0~~ | ~~`infrastructure/metrics/integrations/`~~ | **v3.24.0 已删除**，由 MetricsObserver 替代 |
| TracingInterceptor (HTTP) | v3.10.0 | `infrastructure/tracing/interceptors/http.py` | 保留：直接操作 OpenTelemetry Span |
| GrpcTracingInterceptor | v3.12.0 | `infrastructure/tracing/interceptors/grpc.py` | 保留：gRPC 特定实现 |
| gRPC Interceptors | v3.12.0 | `capabilities/clients/grpc/interceptors.py` | 待统一：LoggingInterceptor 等 |

---

## 详细分析

### 1. MetricsObserver（v3.24.0 已完成）

**实现位置**: `infrastructure/metrics/observer.py`

```python
class MetricsObserver:
    """指标观察者 - 订阅 EventBus 事件，收集 Prometheus 指标

    v3.24.0 新增

    收集的指标:
    - HTTP: requests_total, request_duration, in_flight, errors_total
    - Database: queries_total, query_duration, rows_affected
    - Cache: operations_total, operation_duration, hits/misses
    """

    def __init__(
        self,
        event_bus: EventBus,
        metrics_manager: MetricsManager | None = None,
        prefix: str = "",
        path_cardinality_limit: int = 100,
    ):
        self._event_bus = event_bus
        self._metrics = metrics_manager or get_metrics_manager()
        self._prefix = prefix
        self._path_cardinality_limit = path_cardinality_limit

        self._init_http_metrics()
        self._init_db_metrics()
        self._init_cache_metrics()
        self._subscribe_events()

    def _subscribe_events(self) -> None:
        """订阅所有可观测事件"""
        # HTTP 事件
        self._event_bus.subscribe(HttpRequestStartEvent, self._on_http_request_start)
        self._event_bus.subscribe(HttpRequestEndEvent, self._on_http_request_end)
        # Database 事件
        self._event_bus.subscribe(DatabaseQueryEndEvent, self._on_db_query_end)
        # Cache 事件
        self._event_bus.subscribe(CacheOperationEndEvent, self._on_cache_operation_end)
```

**已删除的旧实现**:
- `infrastructure/metrics/integrations/http.py` - MetricsInterceptor
- `infrastructure/metrics/integrations/database.py` - MetricsTracedDatabase
- `infrastructure/metrics/integrations/__init__.py`

**优势**:
1. ✅ 使用 EventBus 事件驱动，与能力层完全解耦
2. ✅ 自动订阅所有事件类型（HTTP/Database/Cache）
3. ✅ 支持路径规范化，避免高基数指标
4. ✅ 利用事件关联（correlation_id）实现请求追踪
5. ✅ 提供 pytest fixtures 自动注入

### 2. TracingInterceptor（可保留）

**当前实现** (`infrastructure/tracing/interceptors/http.py`):

```python
class TracingInterceptor(BaseMiddleware[Request, Response]):
    """使用 BaseMiddleware，直接操作 OpenTelemetry spans"""

    async def __call__(self, request: Request, call_next) -> Response:
        span = manager.start_span_no_context(span_name, attributes=...)
        response = await call_next(request)
        span.set_attribute("http.status_code", response.status_code)
        span.end()
        return response
```

**分析**:
- 已使用 BaseMiddleware（新架构）
- 直接操作 OpenTelemetry spans 是合理的（Tracing 需要精确控制 span 生命周期）
- HttpTelemetryMiddleware 已整合 Tracing + EventBus，可能存在功能重叠

**建议**:
- 保留 TracingInterceptor 作为独立选项
- 明确文档说明何时使用 TracingInterceptor vs HttpTelemetryMiddleware

### 3. gRPC 拦截器系列（需要评估）

**当前实现** (`capabilities/clients/grpc/interceptors.py`):

```python
class BaseInterceptor:
    """gRPC 拦截器基类 - 自定义实现"""

    def intercept_unary(self, method, request, metadata):
        return request, metadata

    def intercept_response(self, method, response, metadata):
        return response
```

**包含的拦截器**:
- `LoggingInterceptor` - 记录日志
- `MetadataInterceptor` - 添加元数据
- `RetryInterceptor` - 重试逻辑
- `TimingInterceptor` - 计时统计
- `GrpcTracingInterceptor` - 分布式追踪

**分析**:
- gRPC 使用自己的拦截器链，与 HTTP 中间件架构不同
- 没有 EventBus 集成，无法统一观察

**建议**:
1. 短期：保持现状，gRPC 使用独立拦截器链
2. 长期：引入 gRPC 事件（GrpcRequestStartEvent/EndEvent），实现统一观测

---

## 架构对比

### HTTP 可观测性（v3.24.0 统一架构）

```
HttpClient
    │
    ▼
HttpEventPublisherMiddleware ──▶ EventBus
    │                              │
    ▼                              ├──▶ AllureObserver     (Allure 报告)
HttpTelemetryMiddleware            ├──▶ ConsoleDebugObserver (控制台调试)
    │                              └──▶ MetricsObserver    (Prometheus 指标) ✅ v3.24.0
    ▼
OpenTelemetry (Tracing)
```

### Metrics 收集架构演进

**v3.10.0 - v3.23.x（已废弃）**:
```
HttpClient ──▶ MetricsInterceptor ──▶ Prometheus
                    ↑
              (紧耦合，需手动添加拦截器)
```

**v3.24.0+（当前）**:
```
HttpClient ──▶ EventBus ──▶ MetricsObserver ──▶ Prometheus
                              ↑
                    (松耦合，自动订阅)
```

---

## 改进路线图

### Phase 1: 文档完善（v3.23.x）✅ 已完成
- [x] 创建 EventBus 集成分析文档
- [x] 更新可观测性架构文档
- [x] 明确各拦截器/中间件的使用场景

### Phase 2: Metrics 重构（v3.24.0）✅ 已完成
- [x] 创建 `MetricsObserver` 类（`infrastructure/metrics/observer.py`）
- [x] 订阅 HTTP/Database/Cache 事件
- [x] 删除旧的 `MetricsInterceptor`（不保留向后兼容）
- [x] 创建 pytest fixtures 自动注入（`testing/fixtures/metrics.py`）
- [x] 编写完整测试用例（16 个测试，9 通过，7 跳过）

### Phase 3: gRPC 统一（v3.25.0+）
- [ ] 定义 gRPC 事件类型（GrpcRequestStartEvent/EndEvent）
- [ ] gRPC 客户端发布事件
- [ ] 统一 gRPC 到 EventBus 架构

---

## 总结

| 支柱 | 当前状态 | EventBus 集成 | 状态 |
|------|----------|---------------|------|
| **Logging** | Loguru | ✅ ConsoleDebugObserver | 完善 |
| **Tracing** | OpenTelemetry | ✅ HttpTelemetryMiddleware | 完善 |
| **Metrics** | Prometheus | ✅ MetricsObserver（v3.24.0） | **已完成** |

**v3.24.0 里程碑**：三大可观测性支柱全部统一到 EventBus 架构，实现了真正的松耦合可观测性系统。

### 使用方式

```python
# 自动收集指标（推荐）
def test_api(http_client, metrics_observer):
    response = http_client.get("/users")
    # 指标自动收集到 Prometheus

# 访问指标管理器
def test_custom_metrics(metrics_manager):
    counter = metrics_manager.counter("custom_total", "desc", ["label"])
    counter.labels(label="test").inc()
```
