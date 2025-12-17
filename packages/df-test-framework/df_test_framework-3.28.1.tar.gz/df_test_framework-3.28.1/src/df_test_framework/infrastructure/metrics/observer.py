"""指标观察者

通过订阅 EventBus 事件收集 Prometheus 指标。

v3.24.0 新增 - 统一可观测性架构

设计理念:
- 事件驱动：订阅 EventBus 而非使用拦截器
- 松耦合：能力层只发布事件，MetricsObserver 负责收集
- 零侵入：不修改能力层代码，只需注册观察者

支持的事件:
- HTTP: HttpRequestStartEvent, HttpRequestEndEvent, HttpRequestErrorEvent
- Database: DatabaseQueryStartEvent, DatabaseQueryEndEvent, DatabaseQueryErrorEvent
- Cache: CacheOperationStartEvent, CacheOperationEndEvent, CacheOperationErrorEvent

使用示例:
    >>> from df_test_framework.infrastructure.events import EventBus
    >>> from df_test_framework.infrastructure.metrics import MetricsManager
    >>> from df_test_framework.infrastructure.metrics.observer import MetricsObserver
    >>>
    >>> event_bus = EventBus()
    >>> metrics_manager = MetricsManager().init()
    >>> observer = MetricsObserver(event_bus, metrics_manager)
    >>>
    >>> # HTTP 请求会自动收集指标
    >>> http_client.get("/api/users")
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from loguru import logger

from df_test_framework.core.events import (
    CacheOperationEndEvent,
    CacheOperationErrorEvent,
    CacheOperationStartEvent,
    DatabaseQueryEndEvent,
    DatabaseQueryErrorEvent,
    DatabaseQueryStartEvent,
    HttpRequestEndEvent,
    HttpRequestErrorEvent,
    HttpRequestStartEvent,
)

from .manager import PROMETHEUS_AVAILABLE, MetricsManager, get_metrics_manager
from .types import Counter, Gauge, Histogram

if TYPE_CHECKING:
    from df_test_framework.infrastructure.events import EventBus


class MetricsObserver:
    """指标观察者

    订阅 EventBus 事件，收集 Prometheus 指标。

    支持的指标:
    - HTTP:
      - http_requests_total: 请求总数（method, path, status）
      - http_request_duration_seconds: 请求耗时直方图
      - http_requests_in_flight: 进行中的请求数

    - Database:
      - db_queries_total: 查询总数（operation, table, status）
      - db_query_duration_seconds: 查询耗时直方图

    - Cache:
      - cache_operations_total: 操作总数（operation, status）
      - cache_operation_duration_seconds: 操作耗时直方图
      - cache_hits_total / cache_misses_total: 缓存命中/未命中

    Attributes:
        event_bus: EventBus 实例
        metrics_manager: MetricsManager 实例
        prefix: 指标名称前缀

    v3.24.0 新增
    """

    # 用于路径规范化的正则表达式
    _ID_PATTERN = re.compile(r"/\d+")
    _UUID_PATTERN = re.compile(r"/[a-f0-9-]{32,}")

    def __init__(
        self,
        event_bus: EventBus,
        metrics_manager: MetricsManager | None = None,
        prefix: str = "",
        path_cardinality_limit: int = 100,
    ):
        """初始化指标观察者

        Args:
            event_bus: EventBus 实例
            metrics_manager: MetricsManager 实例（默认使用全局实例）
            prefix: 指标名称前缀
            path_cardinality_limit: 路径标签基数限制（防止高基数）
        """
        self._event_bus = event_bus
        self._metrics = metrics_manager or get_metrics_manager()
        self._prefix = prefix
        self._path_cardinality_limit = path_cardinality_limit

        # 路径去重集合
        self._seen_paths: set[str] = set()

        # 初始化指标
        self._init_http_metrics()
        self._init_db_metrics()
        self._init_cache_metrics()

        # 订阅事件
        self._subscribe_events()

        logger.debug("MetricsObserver 已初始化")

    def _init_http_metrics(self) -> None:
        """初始化 HTTP 指标"""
        prefix = f"{self._prefix}_" if self._prefix else ""

        # 请求总数
        self._http_requests_total: Counter = self._metrics.counter(
            f"{prefix}http_requests_total",
            "Total HTTP requests",
            labels=["method", "path", "status"],
        )

        # 请求耗时直方图
        self._http_request_duration: Histogram = self._metrics.histogram(
            f"{prefix}http_request_duration_seconds",
            "HTTP request duration in seconds",
            labels=["method", "path"],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
        )

        # 进行中的请求数
        self._http_in_flight: Gauge = self._metrics.gauge(
            f"{prefix}http_requests_in_flight",
            "HTTP requests currently in flight",
            labels=["method"],
        )

        # 错误总数
        self._http_errors_total: Counter = self._metrics.counter(
            f"{prefix}http_errors_total",
            "Total HTTP request errors",
            labels=["method", "error_type"],
        )

    def _init_db_metrics(self) -> None:
        """初始化数据库指标"""
        prefix = f"{self._prefix}_" if self._prefix else ""

        # 查询总数
        self._db_queries_total: Counter = self._metrics.counter(
            f"{prefix}db_queries_total",
            "Total database queries",
            labels=["operation", "table", "status"],
        )

        # 查询耗时直方图
        self._db_query_duration: Histogram = self._metrics.histogram(
            f"{prefix}db_query_duration_seconds",
            "Database query duration in seconds",
            labels=["operation", "table"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5),
        )

        # 查询行数直方图
        self._db_rows_affected: Histogram = self._metrics.histogram(
            f"{prefix}db_rows_affected",
            "Database rows affected per query",
            labels=["operation"],
            buckets=(1, 10, 50, 100, 500, 1000, 5000, 10000),
        )

    def _init_cache_metrics(self) -> None:
        """初始化缓存指标"""
        prefix = f"{self._prefix}_" if self._prefix else ""

        # 操作总数
        self._cache_operations_total: Counter = self._metrics.counter(
            f"{prefix}cache_operations_total",
            "Total cache operations",
            labels=["operation", "status"],
        )

        # 操作耗时直方图
        self._cache_operation_duration: Histogram = self._metrics.histogram(
            f"{prefix}cache_operation_duration_seconds",
            "Cache operation duration in seconds",
            labels=["operation"],
            buckets=(0.0001, 0.0005, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1),
        )

        # 缓存命中/未命中
        self._cache_hits_total: Counter = self._metrics.counter(
            f"{prefix}cache_hits_total",
            "Total cache hits",
        )
        self._cache_misses_total: Counter = self._metrics.counter(
            f"{prefix}cache_misses_total",
            "Total cache misses",
        )

    def _subscribe_events(self) -> None:
        """订阅 EventBus 事件"""
        # HTTP 事件
        self._event_bus.subscribe(HttpRequestStartEvent, self._on_http_request_start)
        self._event_bus.subscribe(HttpRequestEndEvent, self._on_http_request_end)
        self._event_bus.subscribe(HttpRequestErrorEvent, self._on_http_request_error)

        # Database 事件
        self._event_bus.subscribe(DatabaseQueryStartEvent, self._on_db_query_start)
        self._event_bus.subscribe(DatabaseQueryEndEvent, self._on_db_query_end)
        self._event_bus.subscribe(DatabaseQueryErrorEvent, self._on_db_query_error)

        # Cache 事件
        self._event_bus.subscribe(CacheOperationStartEvent, self._on_cache_operation_start)
        self._event_bus.subscribe(CacheOperationEndEvent, self._on_cache_operation_end)
        self._event_bus.subscribe(CacheOperationErrorEvent, self._on_cache_operation_error)

    def unsubscribe(self) -> None:
        """取消订阅所有事件"""
        # HTTP 事件
        self._event_bus.unsubscribe(HttpRequestStartEvent, self._on_http_request_start)
        self._event_bus.unsubscribe(HttpRequestEndEvent, self._on_http_request_end)
        self._event_bus.unsubscribe(HttpRequestErrorEvent, self._on_http_request_error)

        # Database 事件
        self._event_bus.unsubscribe(DatabaseQueryStartEvent, self._on_db_query_start)
        self._event_bus.unsubscribe(DatabaseQueryEndEvent, self._on_db_query_end)
        self._event_bus.unsubscribe(DatabaseQueryErrorEvent, self._on_db_query_error)

        # Cache 事件
        self._event_bus.unsubscribe(CacheOperationStartEvent, self._on_cache_operation_start)
        self._event_bus.unsubscribe(CacheOperationEndEvent, self._on_cache_operation_end)
        self._event_bus.unsubscribe(CacheOperationErrorEvent, self._on_cache_operation_error)

        logger.debug("MetricsObserver 已取消订阅")

    # =========================================================================
    # HTTP 事件处理
    # =========================================================================

    def _on_http_request_start(self, event: HttpRequestStartEvent) -> None:
        """处理 HTTP 请求开始事件"""
        if not PROMETHEUS_AVAILABLE:
            return

        # 增加进行中请求数
        self._http_in_flight.labels(method=event.method).inc()

    def _on_http_request_end(self, event: HttpRequestEndEvent) -> None:
        """处理 HTTP 请求结束事件"""
        if not PROMETHEUS_AVAILABLE:
            return

        # 规范化路径
        path = self._normalize_path(event.url)
        status = str(event.status_code)

        # 请求总数
        self._http_requests_total.labels(
            method=event.method,
            path=path,
            status=status,
        ).inc()

        # 请求耗时
        self._http_request_duration.labels(
            method=event.method,
            path=path,
        ).observe(event.duration)

        # 减少进行中请求数
        self._http_in_flight.labels(method=event.method).dec()

    def _on_http_request_error(self, event: HttpRequestErrorEvent) -> None:
        """处理 HTTP 请求错误事件"""
        if not PROMETHEUS_AVAILABLE:
            return

        # 错误计数
        self._http_errors_total.labels(
            method=event.method,
            error_type=event.error_type,
        ).inc()

        # 减少进行中请求数
        self._http_in_flight.labels(method=event.method).dec()

    # =========================================================================
    # Database 事件处理
    # =========================================================================

    def _on_db_query_start(self, event: DatabaseQueryStartEvent) -> None:
        """处理数据库查询开始事件"""
        # Start 事件目前不需要处理
        pass

    def _on_db_query_end(self, event: DatabaseQueryEndEvent) -> None:
        """处理数据库查询结束事件"""
        if not PROMETHEUS_AVAILABLE:
            return

        # 查询总数
        self._db_queries_total.labels(
            operation=event.operation,
            table=event.table or "unknown",
            status="success",
        ).inc()

        # 查询耗时（转换为秒）
        duration_seconds = event.duration_ms / 1000.0
        self._db_query_duration.labels(
            operation=event.operation,
            table=event.table or "unknown",
        ).observe(duration_seconds)

        # 影响行数
        if event.row_count > 0:
            self._db_rows_affected.labels(
                operation=event.operation,
            ).observe(event.row_count)

    def _on_db_query_error(self, event: DatabaseQueryErrorEvent) -> None:
        """处理数据库查询错误事件"""
        if not PROMETHEUS_AVAILABLE:
            return

        # 错误计数
        self._db_queries_total.labels(
            operation=event.operation,
            table=event.table or "unknown",
            status="error",
        ).inc()

    # =========================================================================
    # Cache 事件处理
    # =========================================================================

    def _on_cache_operation_start(self, event: CacheOperationStartEvent) -> None:
        """处理缓存操作开始事件"""
        # Start 事件目前不需要处理
        pass

    def _on_cache_operation_end(self, event: CacheOperationEndEvent) -> None:
        """处理缓存操作结束事件"""
        if not PROMETHEUS_AVAILABLE:
            return

        status = "success" if event.success else "error"

        # 操作总数
        self._cache_operations_total.labels(
            operation=event.operation,
            status=status,
        ).inc()

        # 操作耗时（转换为秒）
        duration_seconds = event.duration_ms / 1000.0
        self._cache_operation_duration.labels(
            operation=event.operation,
        ).observe(duration_seconds)

        # 缓存命中/未命中（仅 GET 操作）
        if event.hit is not None:
            if event.hit:
                self._cache_hits_total.inc()
            else:
                self._cache_misses_total.inc()

    def _on_cache_operation_error(self, event: CacheOperationErrorEvent) -> None:
        """处理缓存操作错误事件"""
        if not PROMETHEUS_AVAILABLE:
            return

        # 错误计数
        self._cache_operations_total.labels(
            operation=event.operation,
            status="error",
        ).inc()

    # =========================================================================
    # 辅助方法
    # =========================================================================

    def _normalize_path(self, path: str) -> str:
        """规范化路径（减少基数）

        Args:
            path: 原始路径

        Returns:
            规范化后的路径
        """
        # 移除查询参数
        if "?" in path:
            path = path.split("?")[0]

        # 替换数字 ID 为占位符
        path = self._ID_PATTERN.sub("/{id}", path)
        path = self._UUID_PATTERN.sub("/{uuid}", path)

        # 基数限制
        if len(self._seen_paths) >= self._path_cardinality_limit:
            if path not in self._seen_paths:
                return "/other"

        self._seen_paths.add(path)
        return path


__all__ = ["MetricsObserver"]
