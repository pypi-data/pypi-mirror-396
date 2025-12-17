"""指标收集 Fixtures

v3.24.0 新增

提供基于 EventBus 的 Prometheus 指标自动收集。

配置方式:
    # 启用指标收集（默认）
    OBSERVABILITY__ENABLED=true

    # 禁用指标收集
    OBSERVABILITY__ENABLED=false

使用方式:
    # 自动收集指标（Session 级别）
    # 只需导入 pytest plugin 即可自动启用

    # 访问指标
    def test_api(http_client, metrics_observer):
        response = http_client.get("/users")
        # 指标自动收集到 Prometheus

    # 启动指标服务器（供 Prometheus 抓取）
    def test_with_server(metrics_manager):
        metrics_manager.start_server(port=9090)
"""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from df_test_framework.infrastructure.metrics import MetricsManager, MetricsObserver


def _is_metrics_enabled() -> bool:
    """检查是否启用指标收集

    Returns:
        True: 启用指标收集
        False: 禁用指标收集
    """
    try:
        from df_test_framework.infrastructure.config import get_settings

        settings = get_settings()
        if settings is None:
            return True  # 没有配置时默认启用

        # 检查 observability 配置
        obs = getattr(settings, "observability", None)
        if obs is None:
            return True  # 没有 observability 配置时默认启用

        return obs.enabled

    except Exception:
        # 配置获取失败时默认启用
        return True


@pytest.fixture(scope="session")
def metrics_manager() -> Generator[MetricsManager, None, None]:
    """指标管理器 fixture（Session 级别）

    v3.24.0 新增

    提供全局的 MetricsManager 实例，用于创建和管理 Prometheus 指标。

    使用方式:
        def test_custom_metrics(metrics_manager):
            # 创建自定义指标
            counter = metrics_manager.counter(
                "my_custom_total",
                "My custom counter",
                labels=["type"]
            )
            counter.labels(type="test").inc()

            # 启动指标服务器
            metrics_manager.start_server(port=9090)

    Yields:
        MetricsManager: 指标管理器实例
    """
    from df_test_framework.infrastructure.metrics import MetricsManager

    manager = MetricsManager(service_name="df-test-framework")
    manager.init()

    yield manager

    manager.shutdown()


@pytest.fixture(scope="session")
def metrics_observer(
    metrics_manager: MetricsManager,
) -> Generator[MetricsObserver | None, None, None]:
    """指标观察者 fixture（Session 级别）

    v3.24.0 新增

    自动订阅 EventBus 收集 HTTP、Database、Cache 指标。
    这是推荐的指标收集方式，无需手动配置。

    收集的指标:
    - HTTP:
      - http_requests_total: 请求总数
      - http_request_duration_seconds: 请求耗时
      - http_requests_in_flight: 进行中请求数
      - http_errors_total: 错误总数

    - Database:
      - db_queries_total: 查询总数
      - db_query_duration_seconds: 查询耗时
      - db_rows_affected: 影响行数

    - Cache:
      - cache_operations_total: 操作总数
      - cache_operation_duration_seconds: 操作耗时
      - cache_hits_total / cache_misses_total: 命中/未命中

    使用方式:
        # 自动收集（推荐）
        def test_api(http_client, metrics_observer):
            response = http_client.get("/users")
            # 指标自动收集

        # 访问收集到的指标
        def test_check_metrics(metrics_manager):
            data = metrics_manager.collect()
            # 检查指标数据

    Yields:
        MetricsObserver: 指标观察者实例（如果启用）
        None: 如果 ObservabilityConfig.enabled=False
    """
    from df_test_framework.infrastructure.events import get_event_bus
    from df_test_framework.infrastructure.metrics import MetricsObserver

    # 检查是否启用指标收集
    if not _is_metrics_enabled():
        yield None
        return

    # 获取全局 EventBus
    event_bus = get_event_bus()
    if event_bus is None:
        yield None
        return

    # 创建观察者并订阅事件
    observer = MetricsObserver(
        event_bus=event_bus,
        metrics_manager=metrics_manager,
    )

    yield observer

    # 取消订阅
    observer.unsubscribe()


@pytest.fixture(scope="function")
def test_metrics_observer(
    metrics_manager: MetricsManager,
) -> Generator[MetricsObserver | None, None, None]:
    """测试级别指标观察者 fixture

    v3.24.0 新增

    与 metrics_observer 类似，但是 function 级别。
    每个测试独立的指标收集，适合需要隔离指标的场景。

    使用方式:
        def test_isolated_metrics(http_client, test_metrics_observer):
            # 这个测试的指标独立收集
            response = http_client.get("/users")

    Yields:
        MetricsObserver: 指标观察者实例（如果启用）
        None: 如果禁用
    """
    from df_test_framework.infrastructure.events import get_event_bus
    from df_test_framework.infrastructure.metrics import MetricsObserver

    # 检查是否启用指标收集
    if not _is_metrics_enabled():
        yield None
        return

    # 获取当前测试的 EventBus（可能是隔离的）
    event_bus = get_event_bus()
    if event_bus is None:
        yield None
        return

    # 创建观察者并订阅事件（带测试前缀避免指标名冲突）
    observer = MetricsObserver(
        event_bus=event_bus,
        metrics_manager=metrics_manager,
        prefix="test",
    )

    yield observer

    # 取消订阅
    observer.unsubscribe()


__all__ = [
    "metrics_manager",
    "metrics_observer",
    "test_metrics_observer",
]
