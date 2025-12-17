"""
Primary pytest plugin for df-test-framework v2.

Usage:
    pytest_plugins = ["df_test_framework.fixtures.core"]
"""

from __future__ import annotations

import importlib
import os
from collections.abc import Iterable
from typing import cast

import pytest

from df_test_framework.bootstrap import Bootstrap, RuntimeContext
from df_test_framework.infrastructure.config import FrameworkSettings

_runtime_context: RuntimeContext | None = None


def _resolve_settings_class(path: str) -> type[FrameworkSettings]:
    module_name, _, class_name = path.rpartition(".")
    if not module_name:
        raise RuntimeError(f"Invalid settings class path: {path!r}")
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    if not issubclass(cls, FrameworkSettings):
        raise TypeError(f"{path!r} is not a subclass of FrameworkSettings")
    return cast(type[FrameworkSettings], cls)


def _get_settings_path(config: pytest.Config) -> str:
    ini_value = config.getini("df_settings_class") if "df_settings_class" in config.inicfg else None
    cli_value = config.getoption("--df-settings-class", default=None)
    env_value = os.getenv("DF_SETTINGS_CLASS")
    return (
        cli_value
        or ini_value
        or env_value
        or "df_test_framework.infrastructure.config.schema.FrameworkSettings"
    )


def _get_plugin_paths(config: pytest.Config) -> Iterable[str]:
    collected = []
    cli_value = config.getoption("df_plugin") or []
    ini_value = config.getini("df_plugins") if "df_plugins" in config.inicfg else ""
    env_value = os.getenv("DF_PLUGINS", "")

    def parse(value):
        if not value:
            return []
        if isinstance(value, (list, tuple)):
            return [item.strip() for item in value if item and item.strip()]
        return [item.strip() for item in str(value).split(",") if item.strip()]

    for source in (cli_value, ini_value, env_value):
        collected.extend(parse(source))

    # Preserve order, remove duplicates
    seen = set()
    for plugin in collected:
        if plugin not in seen:
            seen.add(plugin)
            yield plugin


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--df-settings-class",
        action="store",
        default=None,
        help="Dotted path to the FrameworkSettings subclass used for bootstrap",
    )
    parser.addini(
        "df_settings_class",
        "Dotted path to the FrameworkSettings subclass used for bootstrap",
        type="string",
        default="",
    )
    parser.addoption(
        "--df-plugin",
        action="append",
        default=[],
        help="Import path of a df-test-framework plugin (repeatable)",
    )
    parser.addini(
        "df_plugins",
        "Comma separated list of df-test-framework plugins to load",
        type="string",
        default="",
    )
    # v3.11.1: 统一的测试数据保留控制（UoW 数据 + API 数据）
    parser.addoption(
        "--keep-test-data",
        action="store_true",
        default=False,
        help="保留所有测试数据（调试用）。包括 UoW 数据（不回滚）和 API 创建的数据（不清理）。",
    )


def pytest_configure(config: pytest.Config) -> None:
    global _runtime_context

    settings_path = _get_settings_path(config)
    settings_cls = _resolve_settings_class(settings_path)

    bootstrap = Bootstrap().with_settings(settings_cls)
    for plugin_path in _get_plugin_paths(config):
        bootstrap.with_plugin(plugin_path)

    app = bootstrap.build()
    _runtime_context = app.run(force_reload=True)

    config._df_runtime_context = _runtime_context  # type: ignore[attr-defined]

    # v3.11.1: 注册测试数据保留标记（统一控制 UoW + API 数据）
    config.addinivalue_line(
        "markers", "keep_data: 保留此测试的所有数据（调试用）。UoW 数据不回滚，API 数据不清理。"
    )


def pytest_unconfigure(config: pytest.Config) -> None:
    runtime: RuntimeContext | None = getattr(config, "_df_runtime_context", None)
    if runtime:
        runtime.close()


@pytest.fixture(scope="session")
def runtime() -> RuntimeContext:
    if _runtime_context is None:
        raise RuntimeError(
            "Runtime context has not been initialised. Ensure pytest_configure executed."
        )
    return _runtime_context


@pytest.fixture(scope="session")
def http_client(runtime: RuntimeContext):
    return runtime.http_client()


@pytest.fixture(scope="session")
def database(runtime: RuntimeContext):
    return runtime.database()


@pytest.fixture(scope="session")
def redis_client(runtime: RuntimeContext):
    return runtime.redis()


@pytest.fixture(scope="session")
def local_file_client(runtime: RuntimeContext):
    """本地文件存储客户端 fixture

    提供本地文件系统存储能力

    Scope: session（跨测试共享）

    Example:
        >>> def test_upload_file(local_file_client):
        ...     # 上传文件
        ...     result = local_file_client.upload("test.txt", b"Hello")
        ...     assert result["size"] == 5
        ...
        ...     # 下载文件
        ...     content = local_file_client.download("test.txt")
        ...     assert content == b"Hello"
        ...
        ...     # 清理
        ...     local_file_client.delete("test.txt")

    Returns:
        LocalFileClient: 本地文件客户端实例
    """
    return runtime.local_file()


@pytest.fixture(scope="session")
def s3_client(runtime: RuntimeContext):
    """S3 对象存储客户端 fixture

    提供 S3 兼容对象存储能力（AWS S3、MinIO）

    Scope: session（跨测试共享）

    Configuration:
        需要在配置中启用 S3 存储:

        ```python
        from df_test_framework import FrameworkSettings
        from df_test_framework.capabilities.storages import S3Config

        class MySettings(FrameworkSettings):
            storage: StorageConfig = StorageConfig(
                s3=S3Config(
                    endpoint_url="http://localhost:9000",
                    access_key="minioadmin",
                    secret_key="minioadmin",
                    bucket_name="test-bucket"
                )
            )
        ```

    Example:
        >>> def test_s3_upload(s3_client):
        ...     # 上传文件
        ...     result = s3_client.upload("test.txt", b"Hello World")
        ...     assert result["size"] == 11
        ...
        ...     # 下载文件
        ...     content = s3_client.download("test.txt")
        ...     assert content == b"Hello World"
        ...
        ...     # 生成预签名URL
        ...     url = s3_client.generate_presigned_url("test.txt", expiration=300)
        ...
        ...     # 清理
        ...     s3_client.delete("test.txt")

    Returns:
        S3Client: S3 客户端实例

    Raises:
        ConfigurationError: 如果 S3 未配置
    """
    return runtime.s3()


@pytest.fixture(scope="session")
def oss_client(runtime: RuntimeContext):
    """阿里云 OSS 对象存储客户端 fixture

    提供阿里云 OSS 对象存储能力（基于 oss2 官方 SDK）

    Scope: session（跨测试共享）

    Configuration:
        需要在配置中启用 OSS 存储:

        ```python
        from df_test_framework import FrameworkSettings
        from df_test_framework.capabilities.storages import OSSConfig

        class MySettings(FrameworkSettings):
            storage: StorageConfig = StorageConfig(
                oss=OSSConfig(
                    access_key_id="LTAI5t...",
                    access_key_secret="xxx...",
                    bucket_name="my-bucket",
                    endpoint="oss-cn-hangzhou.aliyuncs.com"
                )
            )
        ```

    Example:
        >>> def test_oss_upload(oss_client):
        ...     # 上传文件
        ...     result = oss_client.upload("test.txt", b"Hello OSS")
        ...     assert result["etag"]
        ...
        ...     # 下载文件
        ...     content = oss_client.download("test.txt")
        ...     assert content == b"Hello OSS"
        ...
        ...     # 生成预签名URL
        ...     url = oss_client.generate_presigned_url("test.txt", expiration=300)
        ...
        ...     # 清理
        ...     oss_client.delete("test.txt")

    Returns:
        OSSClient: OSS 客户端实例

    Raises:
        ConfigurationError: 如果 OSS 未配置
    """
    return runtime.oss()


@pytest.fixture
def http_mock(http_client):
    """HTTP Mock fixture（v3.5新增）

    提供HTTP Mock功能，用于测试隔离

    Features:
    - 完全Mock HTTP请求，无需真实服务
    - 支持请求匹配和响应定制
    - 自动清理（测试结束后重置）

    Scope: function（每个测试独立）

    Example:
        >>> def test_get_users(http_mock, http_client):
        ...     # Mock GET /api/users
        ...     http_mock.get("/api/users", json={"users": []})
        ...
        ...     # 发送请求（自动返回Mock响应）
        ...     response = http_client.get("/api/users")
        ...     assert response.json() == {"users": []}
        ...
        ...     # 验证请求被调用
        ...     http_mock.assert_called("/api/users", "GET", times=1)

    Advanced:
        >>> def test_post_user(http_mock, http_client):
        ...     # Mock多个请求
        ...     http_mock.post("/api/users", status_code=201, json={"id": 1})
        ...     http_mock.get("/api/users/1", json={"id": 1, "name": "Alice"})
        ...
        ...     # 测试代码...

    Returns:
        HttpMocker实例
    """
    from ..mocking import HttpMocker

    mocker = HttpMocker(http_client)
    yield mocker
    # 测试结束后自动清理
    mocker.reset()


@pytest.fixture
def time_mock():
    """时间Mock fixture（v3.5新增）

    提供时间Mock功能，用于测试时间敏感逻辑

    Features:
    - 冻结时间到指定时刻
    - 时间旅行（前进/后退）
    - 自动清理（测试结束后恢复真实时间）

    Scope: function（每个测试独立）

    Example:
        >>> from datetime import datetime
        >>> def test_expiration(time_mock):
        ...     # 冻结时间到2024-01-01 12:00:00
        ...     time_mock.freeze("2024-01-01 12:00:00")
        ...
        ...     # 验证时间
        ...     now = datetime.now()
        ...     assert now.year == 2024
        ...     assert now.month == 1
        ...     assert now.hour == 12
        ...
        ...     # 时间前进1小时
        ...     time_mock.move_to("2024-01-01 13:00:00")
        ...     now = datetime.now()
        ...     assert now.hour == 13

    Advanced:
        >>> from datetime import timedelta
        >>> def test_time_calculation(time_mock):
        ...     # 冻结时间
        ...     time_mock.freeze("2024-01-01 00:00:00")
        ...
        ...     # 时间增量前进
        ...     time_mock.tick(seconds=3600)  # 前进1小时
        ...     time_mock.tick(delta=timedelta(days=1))  # 前进1天

    Returns:
        TimeMocker实例
    """
    from ..mocking import TimeMocker

    mocker = TimeMocker()
    yield mocker
    # 测试结束后自动恢复真实时间
    mocker.stop()


@pytest.fixture
def uow(database, request, runtime: RuntimeContext):
    """Unit of Work fixture（v3.13.0：配置驱动架构）

    提供 UnitOfWork 实例，管理事务边界和 Repository 生命周期。
    测试结束后自动回滚（默认），可配置保留数据。

    v3.13.0 重要更新:
    - 支持 repository_package 配置化（无需继承 UnitOfWork）
    - 项目只需在 .env 配置 TEST__REPOSITORY_PACKAGE 即可启用自动发现
    - 无需覆盖此 fixture

    Features:
    - 统一的事务边界管理
    - 多个 Repository 共享同一 Session
    - 默认测试结束自动回滚
    - 灵活的数据清理控制
    - Repository 自动发现（通过配置）
    - 符合 DDD 最佳实践

    Scope: function（每个测试独立）

    Example - 基本用法:
        >>> def test_create_card(uow):
        ...     card = uow.cards.find_by_no("CARD001")
        ...     uow.orders.create({...})
        ...     # ✅ 测试结束后自动回滚

    Example - 启用 Repository 自动发现（v3.13.0）:
        在 .env 文件中配置:
        TEST__REPOSITORY_PACKAGE=my_project.repositories

        测试代码无需修改:
        >>> def test_create_card(uow):
        ...     uow.cards.create({...})  # ✅ 自动发现 CardRepository

    Example - 执行原生 SQL:
        >>> from sqlalchemy import text
        >>> def test_query(uow):
        ...     result = uow.execute(
        ...         "SELECT * FROM users WHERE id = :id",
        ...         {"id": 1}
        ...     )
        ...     user = result.mappings().first()

    Example - 保留数据用于调试:
        方式1 - 显式提交:
        >>> def test_demo(uow):
        ...     uow.cards.create({...})
        ...     uow.commit()  # 显式提交，数据保留

        方式2 - 命令行参数:
        $ pytest tests/ --keep-test-data

        方式3 - 测试标记:
        >>> @pytest.mark.keep_data
        >>> def test_demo(uow):
        ...     pass  # 此测试自动提交

    Control Options (v3.13.0 统一配置):
        1. 显式调用 uow.commit()
        2. 标记: @pytest.mark.keep_data
        3. 命令行: pytest --keep-test-data
        4. Settings 配置: .env 文件中 TEST__KEEP_TEST_DATA=1

    Configuration (v3.13.0):
        在 .env 文件中配置:
        TEST__REPOSITORY_PACKAGE=my_project.repositories  # 启用自动发现
        TEST__KEEP_TEST_DATA=0                            # 默认清理数据

    Returns:
        UnitOfWork: UnitOfWork 实例

    Logs:
        - 默认: "✅ UnitOfWork: 数据已回滚（自动清理）"
        - 保留: "⚠️ UnitOfWork: 数据已提交并保留到数据库"
    """
    from loguru import logger

    from df_test_framework.capabilities.databases.uow import UnitOfWork

    from .cleanup import should_keep_test_data

    # v3.12.1: 使用统一的 should_keep_test_data() 检查配置
    # 优先级：测试标记 > 命令行参数 > Settings 配置（.env / 环境变量）
    auto_commit = should_keep_test_data(request)
    if auto_commit:
        logger.info("检测到保留数据配置，测试数据将被提交")

    # v3.13.0: 从配置读取 repository_package
    repository_package = None
    if runtime.settings.test:
        repository_package = runtime.settings.test.repository_package
        if repository_package:
            logger.debug(f"UoW 配置: repository_package={repository_package}")

    # v3.18.0: 获取测试专用的 EventBus
    from df_test_framework.infrastructure.events import get_event_bus

    test_event_bus = get_event_bus()

    # 创建 UnitOfWork（配置驱动 + 事件驱动）
    unit_of_work = UnitOfWork(
        database.session_factory,
        repository_package=repository_package,
        event_bus=test_event_bus,  # v3.18.0: 传入 EventBus 以发布事务事件
    )

    with unit_of_work:
        yield unit_of_work

        # 如果配置了自动提交且未手动提交
        if auto_commit and not unit_of_work._committed:
            unit_of_work.commit()


@pytest.fixture
def cleanup(database, request, runtime: RuntimeContext):
    """配置驱动的数据清理 fixture（v3.18.0）

    根据 Settings 中的 CleanupConfig 配置自动创建清理管理器。
    项目只需配置 .env 文件，无需编写 cleanup fixture 代码。

    Features:
    - 零代码：只需 .env 配置即可使用
    - 自动注册：根据配置自动注册清理函数
    - 批量删除：使用 SQLAlchemy 批量删除优化
    - 测试隔离：每个测试独立的清理上下文

    Configuration (.env):
        # 配置清理映射
        CLEANUP__ENABLED=true
        CLEANUP__MAPPINGS__orders__table=card_order
        CLEANUP__MAPPINGS__orders__field=customer_order_no
        CLEANUP__MAPPINGS__cards__table=card_inventory
        CLEANUP__MAPPINGS__cards__field=card_no

    Scope: function（每个测试独立）

    Example:
        >>> def test_example(cleanup):
        ...     # 创建测试数据
        ...     order_no = create_order()
        ...
        ...     # 注册清理（使用配置的映射）
        ...     cleanup.add("orders", order_no)
        ...
        ...     # 测试结束后自动清理 card_order 表中 customer_order_no=order_no 的记录

    Example - 与 prepare_data 配合:
        >>> def test_payment(prepare_data, http_client, cleanup):
        ...     # 准备数据（自动提交）
        ...     order_no = prepare_data(
        ...         lambda uow: uow.orders.create({"order_no": "ORD001"}).order_no,
        ...         cleanup=[("orders", "ORD001")]  # 自动注册到 cleanup
        ...     )
        ...     # API 调用...

    Returns:
        ConfigDrivenCleanupManager | SimpleCleanupManager: 清理管理器实例

    Note:
        - 如果未配置 CLEANUP__MAPPINGS，返回空的 SimpleCleanupManager
        - 可通过 @pytest.mark.keep_data 或 --keep-test-data 保留数据
    """
    from loguru import logger

    from .cleanup import ConfigDrivenCleanupManager, SimpleCleanupManager

    # 获取清理配置
    cleanup_config = runtime.settings.cleanup

    if cleanup_config and cleanup_config.enabled and cleanup_config.mappings:
        # 有配置，使用配置驱动管理器
        logger.debug(f"使用配置驱动清理管理器: {len(cleanup_config.mappings)} 个映射")
        manager = ConfigDrivenCleanupManager(
            request=request,
            database=database,
            mappings=cleanup_config.mappings,
        )
    else:
        # 无配置或禁用，使用基础管理器（项目可自行注册）
        logger.debug("未配置清理映射，使用基础 SimpleCleanupManager")
        manager = SimpleCleanupManager(request=request, database=database)

    yield manager

    # 测试结束后执行清理
    manager.cleanup()


@pytest.fixture
def prepare_data(database, runtime: RuntimeContext, cleanup):
    """数据准备 fixture - 回调式（v3.18.0）

    封装"创建 UoW → 执行回调 → 自动提交 → 注册清理"流程。
    适用于需要在测试前准备持久化数据的场景。

    Features:
    - 自动提交：无需手动调用 uow.commit()
    - 自动清理：通过 cleanup_items 参数自动注册到 cleanup
    - Repository 自动发现：继承 TEST__REPOSITORY_PACKAGE 配置
    - 事件驱动：集成 EventBus，发布事务事件

    Scope: function（每个测试独立）

    Args (返回的函数):
        callback: 接收 UoW 实例的回调函数，返回值将被返回
        cleanup_items: 清理项列表，格式为 [(type, id), ...]，
                       会自动注册到 cleanup fixture

    Returns:
        回调函数的返回值

    Example - 基本用法:
        >>> def test_order_payment(prepare_data, http_client, uow):
        ...     # Arrange - 准备数据（自动提交）
        ...     order_no = prepare_data(
        ...         lambda uow: uow.orders.create({"order_no": "ORD001"}).order_no,
        ...         cleanup=[("orders", "ORD001")]
        ...     )
        ...
        ...     # Act
        ...     response = http_client.post(f"/orders/{order_no}/pay")
        ...
        ...     # Assert - 使用独立 uow 验证
        ...     order = uow.orders.find_by_no(order_no)
        ...     assert order.status == 1

    Example - 不需要清理:
        >>> def test_query_only(prepare_data, http_client):
        ...     # 只准备数据，不需要清理（如查询测试）
        ...     user_id = prepare_data(lambda uow: uow.users.create({...}).id)
        ...     response = http_client.get(f"/users/{user_id}")

    Example - 准备多组数据:
        >>> def test_multiple(prepare_data, http_client):
        ...     order1 = prepare_data(
        ...         lambda uow: uow.orders.create({...}).order_no,
        ...         cleanup=[("orders", "ORD001")]
        ...     )
        ...     order2 = prepare_data(
        ...         lambda uow: uow.orders.create({...}).order_no,
        ...         cleanup=[("orders", "ORD002")]
        ...     )
    """
    from loguru import logger

    from df_test_framework.capabilities.databases.uow import UnitOfWork
    from df_test_framework.infrastructure.events import get_event_bus

    def _execute(callback, cleanup_items=None):
        """执行数据准备

        Args:
            callback: 接收 UoW 的回调函数
            cleanup_items: 清理项列表 [(type, id), ...]

        Returns:
            回调函数的返回值
        """
        # 获取 repository_package 配置
        repository_package = None
        if runtime.settings.test:
            repository_package = runtime.settings.test.repository_package

        # 创建临时 UoW
        uow = UnitOfWork(
            database.session_factory,
            repository_package=repository_package,
            event_bus=get_event_bus(),
        )

        # 执行回调并提交
        with uow:
            result = callback(uow)
            uow.commit()
            logger.debug("prepare_data: 事务已提交")

        # 注册清理项
        if cleanup_items:
            for item_type, item_id in cleanup_items:
                cleanup.add(item_type, item_id)
                logger.debug(f"prepare_data: 已注册清理 {item_type}={item_id}")

        return result

    return _execute


@pytest.fixture
def data_preparer(database, runtime: RuntimeContext, cleanup):
    """数据准备器 - 上下文管理器式（v3.18.0）

    提供 with 语法的数据准备方式，适用于需要在一个上下文中
    执行多次操作或需要链式调用的复杂场景。

    Features:
    - with 语法：更清晰的代码结构
    - 链式调用：支持 prep.cleanup("type", "id").cleanup(...)
    - 异常安全：异常时不提交事务
    - 可重复使用：同一测试中可多次使用

    Scope: function（每个测试独立）

    Example - 基本用法:
        >>> def test_complex_scenario(data_preparer, http_client):
        ...     with data_preparer as prep:
        ...         order = prep.uow.orders.create({"order_no": "ORD001"})
        ...         prep.cleanup("orders", order.order_no)
        ...         card = prep.uow.cards.create({"card_no": "CARD001"})
        ...         prep.cleanup("cards", card.card_no)
        ...
        ...     # with 退出后，事务已提交，数据可见
        ...     response = http_client.get("/orders/ORD001")

    Example - 多次使用:
        >>> def test_multiple_prepares(data_preparer, http_client):
        ...     # 第一次准备
        ...     with data_preparer as prep:
        ...         order = prep.uow.orders.create({...})
        ...         prep.cleanup("orders", order.order_no)
        ...
        ...     # 中间执行一些操作
        ...     http_client.post(f"/orders/{order.order_no}/process")
        ...
        ...     # 第二次准备
        ...     with data_preparer as prep:
        ...         item = prep.uow.items.create({...})
        ...         prep.cleanup("items", item.id)

    Example - 链式调用:
        >>> with data_preparer as prep:
        ...     order = prep.uow.orders.create({...})
        ...     prep.cleanup("orders", order.order_no) \\
        ...         .cleanup("cards", card_no) \\
        ...         .cleanup("templates", template_id)
    """
    from typing import Any

    from loguru import logger

    from df_test_framework.capabilities.databases.uow import UnitOfWork
    from df_test_framework.infrastructure.events import get_event_bus

    class DataPreparer:
        """数据准备器上下文管理器"""

        def __init__(self, database, runtime, cleanup_manager):
            self._database = database
            self._runtime = runtime
            self._cleanup_manager = cleanup_manager
            self._uow: UnitOfWork | None = None
            self._cleanup_items: list[tuple[str, Any]] = []

        def __enter__(self) -> DataPreparer:
            """进入上下文：创建 UoW"""
            repository_package = None
            if self._runtime.settings.test:
                repository_package = self._runtime.settings.test.repository_package

            self._uow = UnitOfWork(
                self._database.session_factory,
                repository_package=repository_package,
                event_bus=get_event_bus(),
            )
            self._uow.__enter__()
            self._cleanup_items = []
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """退出上下文：提交或回滚"""
            try:
                if exc_type is None:
                    # 无异常，提交事务
                    self._uow.commit()
                    logger.debug("data_preparer: 事务已提交")

                    # 注册清理项
                    for item_type, item_id in self._cleanup_items:
                        self._cleanup_manager.add(item_type, item_id)
                        logger.debug(f"data_preparer: 已注册清理 {item_type}={item_id}")
                else:
                    # 有异常，不注册清理（数据会回滚）
                    logger.warning("data_preparer: 检测到异常，不注册清理")
            finally:
                self._uow.__exit__(exc_type, exc_val, exc_tb)
                self._uow = None

        @property
        def uow(self) -> UnitOfWork:
            """获取 UnitOfWork 实例"""
            if self._uow is None:
                raise RuntimeError("DataPreparer 必须在 with 语句中使用")
            return self._uow

        def cleanup(self, item_type: str, item_id: Any) -> DataPreparer:
            """注册清理项（支持链式调用）

            Args:
                item_type: 清理类型（对应配置中的映射名）
                item_id: 要清理的 ID

            Returns:
                self（支持链式调用）
            """
            self._cleanup_items.append((item_type, item_id))
            return self

    return DataPreparer(database, runtime, cleanup)
