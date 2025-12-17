"""MetricsObserver 测试

v3.24.0 新增

测试 MetricsObserver 的事件驱动指标收集功能。
"""

import pytest

from df_test_framework.core.events import (
    CacheOperationEndEvent,
    CacheOperationStartEvent,
    DatabaseQueryEndEvent,
    DatabaseQueryStartEvent,
    HttpRequestEndEvent,
    HttpRequestStartEvent,
)
from df_test_framework.infrastructure.events import EventBus
from df_test_framework.infrastructure.metrics import (
    PROMETHEUS_AVAILABLE,
    MetricsManager,
    MetricsObserver,
)


@pytest.fixture
def event_bus() -> EventBus:
    """创建测试用 EventBus"""
    return EventBus()


@pytest.fixture
def metrics_manager() -> MetricsManager:
    """创建测试用 MetricsManager"""
    manager = MetricsManager(service_name="test-service")
    manager.init()
    return manager


@pytest.fixture
def observer(event_bus: EventBus, metrics_manager: MetricsManager) -> MetricsObserver:
    """创建测试用 MetricsObserver"""
    return MetricsObserver(event_bus=event_bus, metrics_manager=metrics_manager)


class TestMetricsObserverInit:
    """MetricsObserver 初始化测试"""

    def test_init_creates_http_metrics(self, observer: MetricsObserver) -> None:
        """测试初始化时创建 HTTP 指标"""
        assert observer._http_requests_total is not None
        assert observer._http_request_duration is not None
        assert observer._http_in_flight is not None
        assert observer._http_errors_total is not None

    def test_init_creates_db_metrics(self, observer: MetricsObserver) -> None:
        """测试初始化时创建数据库指标"""
        assert observer._db_queries_total is not None
        assert observer._db_query_duration is not None
        assert observer._db_rows_affected is not None

    def test_init_creates_cache_metrics(self, observer: MetricsObserver) -> None:
        """测试初始化时创建缓存指标"""
        assert observer._cache_operations_total is not None
        assert observer._cache_operation_duration is not None
        assert observer._cache_hits_total is not None
        assert observer._cache_misses_total is not None

    def test_init_subscribes_to_events(
        self, event_bus: EventBus, metrics_manager: MetricsManager
    ) -> None:
        """测试初始化时订阅事件"""
        # 创建 observer 前检查订阅者数量
        initial_count = len(event_bus._handlers.get(HttpRequestStartEvent, []))

        # 创建 observer
        observer = MetricsObserver(event_bus=event_bus, metrics_manager=metrics_manager)

        # 验证订阅者数量增加
        assert len(event_bus._handlers.get(HttpRequestStartEvent, [])) > initial_count

        # 清理
        observer.unsubscribe()


class TestMetricsObserverHttpEvents:
    """HTTP 事件处理测试"""

    def test_http_request_start_increments_in_flight(
        self, event_bus: EventBus, observer: MetricsObserver
    ) -> None:
        """测试 HTTP 请求开始时增加进行中请求数"""
        if not PROMETHEUS_AVAILABLE:
            pytest.skip("prometheus_client 未安装")

        # 发布开始事件
        event, _ = HttpRequestStartEvent.create(
            method="GET",
            url="/api/users",
        )
        event_bus.publish_sync(event)

        # 验证 in_flight 指标（Prometheus 实际收集需要验证）
        # 这里只验证事件处理不报错

    def test_http_request_end_records_metrics(
        self, event_bus: EventBus, observer: MetricsObserver
    ) -> None:
        """测试 HTTP 请求结束时记录指标"""
        if not PROMETHEUS_AVAILABLE:
            pytest.skip("prometheus_client 未安装")

        # 先发布开始事件
        start_event, correlation_id = HttpRequestStartEvent.create(
            method="GET",
            url="/api/users",
        )
        event_bus.publish_sync(start_event)

        # 发布结束事件
        end_event = HttpRequestEndEvent.create(
            correlation_id=correlation_id,
            method="GET",
            url="/api/users",
            status_code=200,
            duration=0.5,
        )
        event_bus.publish_sync(end_event)

        # 验证事件处理不报错

    def test_http_request_with_query_params_normalizes_path(
        self, event_bus: EventBus, observer: MetricsObserver
    ) -> None:
        """测试带查询参数的 URL 路径规范化"""
        if not PROMETHEUS_AVAILABLE:
            pytest.skip("prometheus_client 未安装")

        # 发布带查询参数的请求
        event, correlation_id = HttpRequestStartEvent.create(
            method="GET",
            url="/api/users?page=1&size=10",
        )
        event_bus.publish_sync(event)

        end_event = HttpRequestEndEvent.create(
            correlation_id=correlation_id,
            method="GET",
            url="/api/users?page=1&size=10",
            status_code=200,
            duration=0.1,
        )
        event_bus.publish_sync(end_event)

        # 路径应该被规范化为 /api/users（移除查询参数）

    def test_http_request_with_id_normalizes_path(
        self, event_bus: EventBus, observer: MetricsObserver
    ) -> None:
        """测试带 ID 的 URL 路径规范化"""
        if not PROMETHEUS_AVAILABLE:
            pytest.skip("prometheus_client 未安装")

        # 发布带数字 ID 的请求
        event, correlation_id = HttpRequestStartEvent.create(
            method="GET",
            url="/api/users/12345",
        )
        event_bus.publish_sync(event)

        end_event = HttpRequestEndEvent.create(
            correlation_id=correlation_id,
            method="GET",
            url="/api/users/12345",
            status_code=200,
            duration=0.1,
        )
        event_bus.publish_sync(end_event)

        # 路径应该被规范化为 /api/users/{id}


class TestMetricsObserverDatabaseEvents:
    """数据库事件处理测试"""

    def test_db_query_end_records_metrics(
        self, event_bus: EventBus, observer: MetricsObserver
    ) -> None:
        """测试数据库查询结束时记录指标"""
        if not PROMETHEUS_AVAILABLE:
            pytest.skip("prometheus_client 未安装")

        # 发布查询事件
        start_event, correlation_id = DatabaseQueryStartEvent.create(
            operation="SELECT",
            table="users",
            sql="SELECT * FROM users WHERE id = :id",
            params={"id": 1},
        )
        event_bus.publish_sync(start_event)

        end_event = DatabaseQueryEndEvent.create(
            correlation_id=correlation_id,
            operation="SELECT",
            table="users",
            sql="SELECT * FROM users WHERE id = :id",
            duration_ms=50.0,
            row_count=1,
        )
        event_bus.publish_sync(end_event)

        # 验证事件处理不报错


class TestMetricsObserverCacheEvents:
    """缓存事件处理测试"""

    def test_cache_hit_records_metrics(
        self, event_bus: EventBus, observer: MetricsObserver
    ) -> None:
        """测试缓存命中时记录指标"""
        if not PROMETHEUS_AVAILABLE:
            pytest.skip("prometheus_client 未安装")

        # 发布缓存事件
        start_event, correlation_id = CacheOperationStartEvent.create(
            operation="GET",
            key="user:123",
        )
        event_bus.publish_sync(start_event)

        end_event = CacheOperationEndEvent.create(
            correlation_id=correlation_id,
            operation="GET",
            key="user:123",
            duration_ms=1.0,
            hit=True,
        )
        event_bus.publish_sync(end_event)

        # 验证事件处理不报错

    def test_cache_miss_records_metrics(
        self, event_bus: EventBus, observer: MetricsObserver
    ) -> None:
        """测试缓存未命中时记录指标"""
        if not PROMETHEUS_AVAILABLE:
            pytest.skip("prometheus_client 未安装")

        # 发布缓存未命中事件
        start_event, correlation_id = CacheOperationStartEvent.create(
            operation="GET",
            key="user:999",
        )
        event_bus.publish_sync(start_event)

        end_event = CacheOperationEndEvent.create(
            correlation_id=correlation_id,
            operation="GET",
            key="user:999",
            duration_ms=1.0,
            hit=False,
        )
        event_bus.publish_sync(end_event)

        # 验证事件处理不报错


class TestMetricsObserverUnsubscribe:
    """取消订阅测试"""

    def test_unsubscribe_removes_handlers(
        self, event_bus: EventBus, metrics_manager: MetricsManager
    ) -> None:
        """测试取消订阅移除事件处理器"""
        # 创建 observer
        observer = MetricsObserver(event_bus=event_bus, metrics_manager=metrics_manager)

        # 记录订阅后的处理器数量
        count_before = len(event_bus._handlers.get(HttpRequestStartEvent, []))

        # 取消订阅
        observer.unsubscribe()

        # 验证处理器已移除
        count_after = len(event_bus._handlers.get(HttpRequestStartEvent, []))
        assert count_after < count_before


class TestMetricsObserverPathNormalization:
    """路径规范化测试"""

    def test_normalize_path_removes_query_params(self, observer: MetricsObserver) -> None:
        """测试移除查询参数"""
        path = observer._normalize_path("/api/users?page=1&size=10")
        assert path == "/api/users"

    def test_normalize_path_replaces_numeric_id(self, observer: MetricsObserver) -> None:
        """测试替换数字 ID"""
        path = observer._normalize_path("/api/users/12345")
        assert path == "/api/users/{id}"

    def test_normalize_path_replaces_uuid(self, observer: MetricsObserver) -> None:
        """测试替换 UUID"""
        path = observer._normalize_path("/api/users/a1b2c3d4-e5f6-7890-abcd-ef1234567890")
        assert path == "/api/users/{uuid}"

    def test_normalize_path_multiple_ids(self, observer: MetricsObserver) -> None:
        """测试多个 ID 的替换"""
        path = observer._normalize_path("/api/users/123/orders/456")
        assert path == "/api/users/{id}/orders/{id}"
