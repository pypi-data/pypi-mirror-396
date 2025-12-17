"""监控指标模块

基于 Prometheus 提供监控指标收集能力。

核心组件:
- MetricsManager: 指标管理器，负责初始化和配置
- MetricsRegistry: 指标注册表，管理所有指标
- MetricsObserver: 事件驱动的指标收集器（v3.24.0 新增）

支持的指标类型:
- Counter: 计数器（只增不减）
- Gauge: 仪表盘（可增可减）
- Histogram: 直方图（分布统计）
- Summary: 摘要（百分位统计）

使用示例:

    方式1: 自动收集（推荐，v3.24.0+）
    >>> from df_test_framework.infrastructure.events import EventBus
    >>> from df_test_framework.infrastructure.metrics import MetricsManager, MetricsObserver
    >>>
    >>> event_bus = EventBus()
    >>> metrics = MetricsManager(service_name="my-service").init()
    >>> observer = MetricsObserver(event_bus, metrics)
    >>>
    >>> # HTTP/DB/Cache 请求会自动收集指标
    >>> http_client.get("/api/users")

    方式2: 手动收集
    >>> from df_test_framework.infrastructure.metrics import MetricsManager
    >>>
    >>> metrics = MetricsManager(service_name="my-service").init()
    >>> requests_total = metrics.counter(
    ...     "http_requests_total",
    ...     "Total HTTP requests",
    ...     labels=["method", "endpoint", "status"]
    ... )
    >>> requests_total.labels(method="GET", endpoint="/api/users", status="200").inc()

v3.10.0 新增 - P2.3 Prometheus监控
v3.24.0 重构 - MetricsObserver 事件驱动架构
"""

from .decorators import (
    count_calls,
    time_calls,
    track_in_progress,
)
from .manager import PROMETHEUS_AVAILABLE, MetricsConfig, MetricsManager, get_metrics_manager
from .observer import MetricsObserver
from .registry import MetricsRegistry
from .types import (
    Counter,
    Gauge,
    Histogram,
    MetricWrapper,
    Summary,
)

__all__ = [
    # 核心
    "MetricsManager",
    "MetricsConfig",
    "MetricsRegistry",
    "get_metrics_manager",
    "PROMETHEUS_AVAILABLE",
    # 观察者（v3.24.0）
    "MetricsObserver",
    # 指标类型
    "Counter",
    "Gauge",
    "Histogram",
    "Summary",
    "MetricWrapper",
    # 装饰器
    "count_calls",
    "time_calls",
    "track_in_progress",
]
