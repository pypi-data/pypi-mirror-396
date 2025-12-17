# 数据准备与清理 Fixture 设计文档

**版本**: v3.18.0
**作者**: DF Test Framework Team
**日期**: 2025-12-10
**状态**: 设计评审中

---

## 1. 背景与问题

### 1.1 当前痛点

#### 痛点 1：必须显式 commit()

在测试中通过 UoW 修改数据后，必须显式调用 `commit()` 才能让 HTTP API 可见：

```python
# test_payment_exceptions.py 实际代码
def test_payment_frozen_card(uow, h5_card_api, cleanup_api_test_data):
    # 1. 通过 API 创建卡片
    response = master_card_api.create_cards(request)
    card_no = response.data.sample_card_nos[0]

    # 2. 通过 UoW 修改卡片状态
    uow.cards.update(
        conditions={"card_no": card_no},
        data={"status": 0, "unavailable_reason": 3, "is_frozen": 1},
    )
    uow.commit()  # ❌ 必须显式提交，否则 HTTP API 查不到修改后的状态

    # 3. 调用 API 测试
    h5_card_api.pay(payment_request)

    # 4. 清理
    cleanup_api_test_data.add("orders", order_no)
    cleanup_api_test_data.add("cards", card_no)
```

#### 痛点 2：每个项目都要实现 cleanup fixture

当前框架只提供 `CleanupManager` 基类，项目需要自己实现 cleanup fixture：

```python
# gift_card_test/fixtures/cleanup_fixtures.py（项目需要实现的代码）
@pytest.fixture
def cleanup_api_test_data(request, database):
    manager = SimpleCleanupManager(request, database)

    # ❌ 每个项目都要手动注册这些映射
    manager.register_cleanup("orders", _make_cleanup_func(database, "card_order", "customer_order_no"))
    manager.register_cleanup("cards", _make_cleanup_func(database, "card_inventory", "card_no"))
    manager.register_cleanup("templates", _make_cleanup_func(database, "card_template", "template_id"))

    yield manager
    manager.cleanup()
```

### 1.2 设计目标

1. **简化数据准备**：封装 `uow.commit()` 操作，减少样板代码
2. **零代码清理配置**：通过配置文件定义清理映射，无需项目实现 cleanup fixture
3. **统一配置体验**：与框架现有的配置驱动设计保持一致
4. **向后兼容**：不影响现有代码，项目仍可自定义 fixture

---

## 2. 整体架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           项目配置 (.env)                                │
│  # 清理映射配置                                                          │
│  CLEANUP__MAPPINGS__orders__table=card_order                            │
│  CLEANUP__MAPPINGS__orders__field=customer_order_no                     │
│  CLEANUP__MAPPINGS__cards__table=card_inventory                         │
│  CLEANUP__MAPPINGS__cards__field=card_no                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Framework Settings                                │
│  class FrameworkSettings:                                               │
│      cleanup: CleanupConfig | None  # 清理配置                           │
│      test: TestExecutionConfig      # 测试配置                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌───────────────────────────────┐   ┌───────────────────────────────────┐
│      cleanup fixture          │   │   prepare_data / data_preparer    │
│  - 配置驱动                    │   │   - 创建临时 UoW                   │
│  - 自动注册清理函数             │   │   - 自动提交事务                   │
│  - 测试结束自动清理             │   │   - 自动注册清理项                 │
└───────────────────────────────┘   └───────────────────────────────────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            测试代码                                      │
│  def test_order_payment(prepare_data, http_client, uow):               │
│      order_no = prepare_data(                                           │
│          lambda uow: uow.orders.create({...}).order_no,                 │
│          cleanup=[("orders", "ORD001")]  # 自动清理                      │
│      )                                                                  │
│      response = http_client.post(f"/orders/{order_no}/pay")            │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 层级归属

根据五层架构设计：

| 组件 | 层级 | 位置 |
|------|------|------|
| `CleanupConfig` | Layer 1 | `infrastructure/config/schema.py` |
| `ConfigDrivenCleanupManager` | Layer 3 | `testing/fixtures/cleanup.py` |
| `cleanup` fixture | Layer 3 | `testing/fixtures/core.py` |
| `prepare_data` fixture | Layer 3 | `testing/fixtures/core.py` |
| `data_preparer` fixture | Layer 3 | `testing/fixtures/core.py` |

---

## 3. 配置驱动的通用 Cleanup

### 3.1 配置模型

**位置**: `infrastructure/config/schema.py`

```python
class CleanupMapping(BaseModel):
    """单个清理映射配置

    定义一个清理类型到数据库表的映射关系。

    Attributes:
        table: 数据库表名
        field: 用于匹配的字段名（通常是主键或业务ID）

    Example:
        CleanupMapping(table="card_order", field="customer_order_no")
    """
    table: str = Field(..., description="数据库表名")
    field: str = Field(default="id", description="ID 字段名")


class CleanupConfig(BaseModel):
    """清理配置

    配置测试数据清理的行为和映射关系。

    Attributes:
        enabled: 是否启用自动清理（默认 True）
        mappings: 清理类型到表的映射

    配置方式（.env）:
        CLEANUP__ENABLED=true
        CLEANUP__MAPPINGS__orders__table=card_order
        CLEANUP__MAPPINGS__orders__field=customer_order_no
        CLEANUP__MAPPINGS__cards__table=card_inventory
        CLEANUP__MAPPINGS__cards__field=card_no
    """
    enabled: bool = Field(default=True, description="是否启用自动清理")
    mappings: dict[str, CleanupMapping] = Field(
        default_factory=dict,
        description="清理类型到表的映射"
    )
```

### 3.2 Settings 集成

**位置**: `infrastructure/config/schema.py`

```python
class FrameworkSettings(BaseSettings):
    """框架配置"""

    # ... 其他配置 ...

    # v3.18.0: 清理配置
    cleanup: CleanupConfig | None = Field(
        default=None,
        description="测试数据清理配置"
    )
```

### 3.3 ConfigDrivenCleanupManager

**位置**: `testing/fixtures/cleanup.py`

```python
class ConfigDrivenCleanupManager(SimpleCleanupManager):
    """配置驱动的清理管理器

    根据 Settings 中的 cleanup.mappings 配置自动注册清理函数，
    实现零代码配置的测试数据清理。

    设计理念:
    - 配置优于代码：通过 .env 文件配置，无需编写 Python 代码
    - 约定优于配置：提供合理的默认值
    - 向后兼容：仍支持手动注册清理函数

    配置方式（.env）:
        CLEANUP__MAPPINGS__orders__table=card_order
        CLEANUP__MAPPINGS__orders__field=customer_order_no
        CLEANUP__MAPPINGS__cards__table=card_inventory
        CLEANUP__MAPPINGS__cards__field=card_no

    使用方式:
        def test_example(cleanup):
            cleanup.add("orders", "ORD001")  # 自动映射到 card_order 表
            cleanup.add("cards", "CARD001")  # 自动映射到 card_inventory 表
            # 测试结束后自动清理

    高级用法 - 手动注册额外的清理函数:
        def test_example(cleanup):
            # 注册自定义清理函数
            cleanup.register_cleanup("custom", lambda ids: custom_cleanup(ids))
            cleanup.add("custom", "ID001")
    """

    def __init__(
        self,
        request: pytest.FixtureRequest,
        database: Any,
        mappings: dict[str, CleanupMapping]
    ):
        """初始化配置驱动的清理管理器

        Args:
            request: pytest fixture request 对象
            database: 数据库连接
            mappings: 清理类型到表的映射配置
        """
        super().__init__(request, database)
        self._mappings = mappings

        # 根据配置自动注册清理函数
        for item_type, mapping in mappings.items():
            cleanup_func = self._make_db_cleanup_func(mapping.table, mapping.field)
            self.register_cleanup(item_type, cleanup_func)
            logger.debug(f"cleanup: 注册映射 {item_type} -> {mapping.table}.{mapping.field}")

        if mappings:
            logger.info(f"✅ cleanup: 已加载 {len(mappings)} 个清理映射")

    def _make_db_cleanup_func(self, table: str, field: str) -> Callable[[list], None]:
        """创建数据库清理函数

        Args:
            table: 表名
            field: ID 字段名

        Returns:
            清理函数，接收 ID 列表作为参数
        """
        def cleanup(ids: list) -> None:
            if not ids:
                return

            from sqlalchemy import bindparam, text

            with self._db.session() as session:
                stmt = text(f"DELETE FROM {table} WHERE {field} IN :ids").bindparams(
                    bindparam("ids", expanding=True)
                )
                result = session.execute(stmt, {"ids": ids})
                session.commit()
                logger.debug(f"cleanup: 已删除 {table} 表 {result.rowcount} 行")

        return cleanup

    def add(self, item_type: str, item_id: Any) -> None:
        """添加需要清理的项目

        如果 item_type 未配置映射，会记录警告但不会失败。

        Args:
            item_type: 项目类型（如 "orders", "cards"）
            item_id: 项目标识符
        """
        if item_type not in self._cleanup_funcs and item_type not in self._mappings:
            logger.warning(f"cleanup: 类型 '{item_type}' 未配置映射，请检查 CLEANUP__MAPPINGS 配置")

        super().add(item_type, item_id)
```

### 3.4 通用 cleanup fixture

**位置**: `testing/fixtures/core.py`

```python
@pytest.fixture
def cleanup(request, database, runtime):
    """通用数据清理 fixture（配置驱动）

    v3.18.0 新增 - 零代码配置的测试数据清理。

    根据 Settings 中的 cleanup.mappings 配置自动注册清理函数，
    无需项目自定义 fixture，只需配置即可使用。

    Scope: function（每个测试独立）

    配置方式（.env）:
        # 启用清理（默认 true）
        CLEANUP__ENABLED=true

        # 映射配置：cleanup.add("orders", id) -> DELETE FROM card_order WHERE customer_order_no = id
        CLEANUP__MAPPINGS__orders__table=card_order
        CLEANUP__MAPPINGS__orders__field=customer_order_no

        # 映射配置：cleanup.add("cards", id) -> DELETE FROM card_inventory WHERE card_no = id
        CLEANUP__MAPPINGS__cards__table=card_inventory
        CLEANUP__MAPPINGS__cards__field=card_no

    使用方式:
        >>> def test_create_order(http_client, cleanup):
        ...     response = http_client.post("/orders", json={...})
        ...     order_no = response.json()["order_no"]
        ...
        ...     cleanup.add("orders", order_no)  # 注册清理
        ...
        ...     # 测试逻辑...
        ...     # 测试结束后自动清理

    控制选项（跳过清理）:
        1. @pytest.mark.keep_data - 测试标记
        2. --keep-test-data - 命令行参数
        3. KEEP_TEST_DATA=1 - 环境变量

    向后兼容:
        如果项目已有自定义 cleanup fixture，可以继续使用。
        框架的 cleanup fixture 不会与项目自定义的冲突。

    Returns:
        ConfigDrivenCleanupManager: 清理管理器实例
    """
    from .cleanup import ConfigDrivenCleanupManager

    # 从配置读取映射
    mappings = {}
    if runtime.settings.cleanup and runtime.settings.cleanup.mappings:
        mappings = runtime.settings.cleanup.mappings
        logger.debug(f"cleanup: 从配置加载 {len(mappings)} 个映射")
    else:
        logger.debug("cleanup: 未配置清理映射，可通过 CLEANUP__MAPPINGS 配置")

    manager = ConfigDrivenCleanupManager(request, database, mappings)
    yield manager
    manager.cleanup()
```

---

## 4. 数据准备 Fixture

### 4.1 prepare_data（回调式）

**位置**: `testing/fixtures/core.py`

```python
@pytest.fixture
def prepare_data(database, runtime, cleanup):
    """数据准备 fixture - 回调式

    v3.18.0 新增 - 简化测试数据准备，自动提交 + 自动清理。

    专门用于测试的 Arrange 阶段准备数据，解决以下问题：
    1. 自动提交事务（让 HTTP API 等外部系统可见数据）
    2. 自动注册清理（测试结束后删除数据）
    3. 支持 Repository 自动发现（继承 TEST__REPOSITORY_PACKAGE 配置）
    4. 集成 EventBus（发布事务事件）

    Scope: function（每个测试独立）

    配置依赖:
        需要配置 cleanup.mappings 才能使用 cleanup 参数：
        CLEANUP__MAPPINGS__orders__table=card_order
        CLEANUP__MAPPINGS__orders__field=customer_order_no

    Example - 基本用法（无清理）:
        >>> def test_update_status(prepare_data, http_client, uow):
        ...     # 准备数据（修改已有数据的状态）
        ...     prepare_data(lambda uow: uow.cards.update(
        ...         conditions={"card_no": "CARD001"},
        ...         data={"status": 0, "is_frozen": 1}
        ...     ))  # ✅ 自动提交
        ...
        ...     # 调用 API
        ...     response = http_client.post("/cards/CARD001/unfreeze")
        ...
        ...     # 验证
        ...     card = uow.cards.find_by_card_no("CARD001")
        ...     assert card["is_frozen"] == 0

    Example - 创建数据并清理:
        >>> def test_create_order(prepare_data, http_client, uow):
        ...     # 准备数据（自动提交 + 清理）
        ...     order_no = prepare_data(
        ...         lambda uow: uow.orders.create({"order_no": "ORD001"}).order_no,
        ...         cleanup=[("orders", "ORD001")]
        ...     )
        ...
        ...     # 调用 API
        ...     response = http_client.post(f"/orders/{order_no}/pay")
        ...
        ...     # 验证
        ...     order = uow.orders.find_by_no(order_no)
        ...     assert order.status == 1
        ...
        ...     # ✅ 测试结束后自动清理 ORD001

    Example - 准备多个数据:
        >>> def test_batch(prepare_data, http_client):
        ...     # 准备订单
        ...     order_no = prepare_data(
        ...         lambda uow: uow.orders.create({...}).order_no,
        ...         cleanup=[("orders", "ORD001")]
        ...     )
        ...
        ...     # 准备卡片
        ...     card_no = prepare_data(
        ...         lambda uow: uow.cards.create({...}).card_no,
        ...         cleanup=[("cards", "CARD001")]
        ...     )
        ...
        ...     # 调用 API
        ...     response = http_client.post("/bindcard", json={
        ...         "order_no": order_no,
        ...         "card_no": card_no
        ...     })

    Notes:
        - 回调函数应返回简单类型（str, int）而非 ORM 对象
        - ORM 对象在 UoW 关闭后可能无法访问懒加载属性
        - 如果需要完整对象，使用独立的 uow fixture 重新查询

    Args:
        database: 数据库 fixture
        runtime: 运行时上下文 fixture
        cleanup: 清理管理器 fixture

    Returns:
        可调用对象，签名为 (callback, cleanup) -> Any
    """
    from loguru import logger

    from df_test_framework.capabilities.databases.uow import UnitOfWork
    from df_test_framework.infrastructure.events import get_event_bus

    def _execute(callback, cleanup_items=None):
        """执行数据准备

        Args:
            callback: 回调函数 (uow) -> result
            cleanup_items: 清理项列表 [("type", "id"), ...]，可选

        Returns:
            回调函数的返回值
        """
        # 继承 repository_package 配置
        repository_package = None
        if runtime.settings.test:
            repository_package = runtime.settings.test.repository_package
            if repository_package:
                logger.debug(f"prepare_data: 使用 repository_package={repository_package}")

        # 创建临时 UoW
        uow = UnitOfWork(
            database.session_factory,
            repository_package=repository_package,
            event_bus=get_event_bus(),
        )

        # 执行回调并提交
        with uow:
            logger.debug("prepare_data: 开始执行数据准备")
            result = callback(uow)
            uow.commit()
            logger.info("✅ prepare_data: 数据准备完成并已提交")

        # 注册清理
        if cleanup_items:
            for item_type, item_id in cleanup_items:
                cleanup.add(item_type, item_id)
            logger.debug(f"prepare_data: 已注册 {len(cleanup_items)} 个清理项")

        return result

    return _execute
```

### 4.2 data_preparer（上下文管理器式）

**位置**: `testing/fixtures/core.py`

```python
@pytest.fixture
def data_preparer(database, runtime, cleanup):
    """数据准备器 - 上下文管理器式

    v3.18.0 新增 - 提供上下文管理器语法的数据准备工具。

    特点:
    1. 支持 with 语法，代码结构更清晰
    2. 可在一个测试中多次使用
    3. 支持链式调用 cleanup
    4. 自动提交 + 自动清理
    5. 支持 Repository 自动发现
    6. 集成 EventBus

    适用场景:
    - 需要准备多个相关数据
    - 准备逻辑较复杂
    - 需要在准备过程中做多次操作

    Scope: function（每个测试独立）

    Example - 基本用法:
        >>> def test_order(data_preparer, http_client, uow):
        ...     # 准备数据
        ...     with data_preparer as prep:
        ...         order = prep.uow.orders.create({"order_no": "ORD001"})
        ...         prep.cleanup("orders", order.order_no)
        ...     # ✅ 退出 with 时自动提交
        ...
        ...     # 调用 API
        ...     response = http_client.post(f"/orders/{order.order_no}/pay")
        ...
        ...     # 验证
        ...     order = uow.orders.find_by_no("ORD001")
        ...     assert order.status == 1

    Example - 准备多组数据:
        >>> def test_complex(data_preparer, http_client):
        ...     # 准备订单数据
        ...     with data_preparer as prep:
        ...         order1 = prep.uow.orders.create({...})
        ...         order2 = prep.uow.orders.create({...})
        ...         prep.cleanup("orders", order1.order_no) \\
        ...             .cleanup("orders", order2.order_no)  # 链式调用
        ...
        ...     # 准备卡片数据（单独的事务）
        ...     with data_preparer as prep:
        ...         card = prep.uow.cards.create({...})
        ...         prep.cleanup("cards", card.card_no)
        ...
        ...     # 调用 API
        ...     response = http_client.post("/batch-process")

    Example - 修改已有数据状态:
        >>> def test_frozen_card(data_preparer, h5_card_api):
        ...     # 修改卡片状态为冻结
        ...     with data_preparer as prep:
        ...         prep.uow.cards.update(
        ...             conditions={"card_no": "CARD001"},
        ...             data={"status": 0, "is_frozen": 1}
        ...         )
        ...     # ✅ 自动提交，HTTP API 可见
        ...
        ...     # 测试冻结卡片支付
        ...     with pytest.raises(BusinessError):
        ...         h5_card_api.pay(request)

    Args:
        database: 数据库 fixture
        runtime: 运行时上下文 fixture
        cleanup: 清理管理器 fixture

    Returns:
        DataPreparer: 数据准备器实例
    """
    from typing import Any

    from loguru import logger

    from df_test_framework.capabilities.databases.uow import UnitOfWork
    from df_test_framework.infrastructure.events import get_event_bus

    class DataPreparer:
        """数据准备器 - 上下文管理器"""

        def __init__(self, database, runtime, cleanup_manager):
            self._database = database
            self._runtime = runtime
            self._cleanup_manager = cleanup_manager
            self._uow = None
            self._cleanup_items = []

        def __enter__(self):
            """进入上下文，创建 UoW"""
            # 继承 repository_package 配置
            repository_package = None
            if self._runtime.settings.test:
                repository_package = self._runtime.settings.test.repository_package
                if repository_package:
                    logger.debug(f"data_preparer: 使用 repository_package={repository_package}")

            # 创建临时 UoW
            self._uow = UnitOfWork(
                self._database.session_factory,
                repository_package=repository_package,
                event_bus=get_event_bus(),
            )
            self._uow.__enter__()
            self._cleanup_items = []
            logger.debug("data_preparer: 进入数据准备上下文")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """退出上下文，提交并清理"""
            try:
                # 提交事务（如果没有异常）
                if exc_type is None:
                    self._uow.commit()
                    logger.info("✅ data_preparer: 数据准备完成并已提交")

                    # 注册清理
                    for item_type, item_id in self._cleanup_items:
                        self._cleanup_manager.add(item_type, item_id)
                    if self._cleanup_items:
                        logger.debug(f"data_preparer: 已注册 {len(self._cleanup_items)} 个清理项")
                else:
                    logger.warning(f"data_preparer: 发生异常，数据已回滚: {exc_val}")
            finally:
                # 关闭 UoW
                self._uow.__exit__(exc_type, exc_val, exc_tb)
                self._uow = None

        @property
        def uow(self) -> UnitOfWork:
            """访问当前 UoW

            Returns:
                UnitOfWork: 当前 UoW 实例

            Raises:
                RuntimeError: 如果不在 with 语句中使用
            """
            if self._uow is None:
                raise RuntimeError("DataPreparer 必须在 with 语句中使用")
            return self._uow

        def cleanup(self, item_type: str, item_id: Any):
            """注册清理项（支持链式调用）

            Args:
                item_type: 项目类型（如 "orders", "cards"）
                item_id: 项目标识符

            Returns:
                Self: 返回自身，支持链式调用

            Example:
                >>> prep.cleanup("orders", "ORD001") \\
                ...     .cleanup("cards", "CARD001")
            """
            self._cleanup_items.append((item_type, item_id))
            logger.debug(f"data_preparer: 注册清理项: {item_type} = {item_id}")
            return self

    return DataPreparer(database, runtime, cleanup)
```

---

## 5. 使用场景与示例

### 5.1 场景对比

| 场景 | Before（当前） | After（v3.18.0） |
|------|---------------|------------------|
| 修改数据状态 | `uow.update()` + `uow.commit()` | `prepare_data(lambda uow: uow.update())` |
| 创建数据 + 清理 | `uow.create()` + `uow.commit()` + `cleanup.add()` | `prepare_data(..., cleanup=[...])` |
| 清理配置 | 项目实现 cleanup fixture | .env 配置映射 |

### 5.2 实际场景：支付异常测试

**Before（当前代码）**：
```python
def test_payment_frozen_card(uow, h5_card_api, master_card_api, cleanup_api_test_data):
    # 1. 通过 API 创建卡片
    response = master_card_api.create_cards(request)
    card_no = response.data.sample_card_nos[0]

    # 2. 修改卡片状态（必须显式 commit）
    uow.cards.update(
        conditions={"card_no": card_no},
        data={"status": 0, "unavailable_reason": 3, "is_frozen": 1},
    )
    uow.commit()  # ❌ 必须显式提交

    # 3. 测试冻结卡片支付
    with pytest.raises(BusinessError):
        h5_card_api.pay(payment_request)

    # 4. 清理
    cleanup_api_test_data.add("orders", order_no)
    cleanup_api_test_data.add("cards", card_no)
```

**After（使用 prepare_data）**：
```python
def test_payment_frozen_card(prepare_data, h5_card_api, master_card_api, cleanup):
    # 1. 通过 API 创建卡片
    response = master_card_api.create_cards(request)
    card_no = response.data.sample_card_nos[0]

    # 2. 修改卡片状态（自动提交）
    prepare_data(lambda uow: uow.cards.update(
        conditions={"card_no": card_no},
        data={"status": 0, "unavailable_reason": 3, "is_frozen": 1},
    ))  # ✅ 自动提交

    # 3. 测试冻结卡片支付
    with pytest.raises(BusinessError):
        h5_card_api.pay(payment_request)

    # 4. 清理（使用框架通用 cleanup）
    cleanup.add("orders", order_no)
    cleanup.add("cards", card_no)
```

**After（使用 data_preparer）**：
```python
def test_payment_frozen_card(data_preparer, h5_card_api, master_card_api, cleanup):
    # 1. 通过 API 创建卡片
    response = master_card_api.create_cards(request)
    card_no = response.data.sample_card_nos[0]

    # 2. 修改卡片状态（上下文管理器）
    with data_preparer as prep:
        prep.uow.cards.update(
            conditions={"card_no": card_no},
            data={"status": 0, "unavailable_reason": 3, "is_frozen": 1},
        )
    # ✅ 退出时自动提交

    # 3. 测试冻结卡片支付
    with pytest.raises(BusinessError):
        h5_card_api.pay(payment_request)

    # 4. 清理
    cleanup.add("orders", order_no)
    cleanup.add("cards", card_no)
```

### 5.3 实际场景：创建并清理数据

```python
def test_order_payment(prepare_data, http_client, uow):
    # Arrange - 创建订单（自动提交 + 自动清理）
    order_no = prepare_data(
        lambda uow: uow.orders.create({
            "order_no": "ORD001",
            "status": 0,
            "amount": 100.00
        }).order_no,
        cleanup=[("orders", "ORD001")]  # 自动注册清理
    )

    # Act - 调用支付 API
    response = http_client.post(f"/orders/{order_no}/pay")

    # Assert - 验证订单状态
    assert response.status_code == 200
    order = uow.orders.find_by_no(order_no)
    assert order.status == 1

    # ✅ 测试结束后自动清理 ORD001
```

### 5.4 项目配置示例

**gift-card-test/.env**：
```bash
# ========== 清理映射配置 ==========
# 格式：CLEANUP__MAPPINGS__{type}__{field}={value}

# orders -> card_order 表，使用 customer_order_no 字段
CLEANUP__MAPPINGS__orders__table=card_order
CLEANUP__MAPPINGS__orders__field=customer_order_no

# cards -> card_inventory 表，使用 card_no 字段
CLEANUP__MAPPINGS__cards__table=card_inventory
CLEANUP__MAPPINGS__cards__field=card_no

# templates -> card_template 表，使用 template_id 字段
CLEANUP__MAPPINGS__templates__table=card_template
CLEANUP__MAPPINGS__templates__field=template_id

# users -> gc_users 表，使用 user_id 字段
CLEANUP__MAPPINGS__users__table=gc_users
CLEANUP__MAPPINGS__users__field=user_id
```

配置后，项目无需实现 cleanup fixture，直接使用框架的 `cleanup`：
```python
def test_example(cleanup):
    cleanup.add("orders", "ORD001")  # ✅ 自动映射到 card_order 表
    cleanup.add("cards", "CARD001")  # ✅ 自动映射到 card_inventory 表
```

---

## 6. 测试计划

### 6.1 单元测试

**测试文件**: `tests/testing/fixtures/test_cleanup_config.py`

```python
class TestCleanupConfig:
    """测试清理配置"""

    def test_cleanup_mapping_model(self):
        """测试 CleanupMapping 模型"""
        mapping = CleanupMapping(table="card_order", field="customer_order_no")
        assert mapping.table == "card_order"
        assert mapping.field == "customer_order_no"

    def test_cleanup_mapping_default_field(self):
        """测试默认字段名"""
        mapping = CleanupMapping(table="users")
        assert mapping.field == "id"

    def test_cleanup_config_from_env(self):
        """测试从环境变量加载配置"""
        # 模拟环境变量
        os.environ["CLEANUP__MAPPINGS__orders__table"] = "card_order"
        os.environ["CLEANUP__MAPPINGS__orders__field"] = "customer_order_no"

        config = CleanupConfig()
        assert "orders" in config.mappings
        assert config.mappings["orders"].table == "card_order"


class TestConfigDrivenCleanupManager:
    """测试配置驱动的清理管理器"""

    def test_auto_register_cleanup_funcs(self, request, database):
        """测试自动注册清理函数"""
        mappings = {
            "orders": CleanupMapping(table="test_orders", field="order_no"),
            "cards": CleanupMapping(table="test_cards", field="card_no"),
        }

        manager = ConfigDrivenCleanupManager(request, database, mappings)

        # 验证清理函数已注册
        assert "orders" in manager._cleanup_funcs
        assert "cards" in manager._cleanup_funcs

    def test_cleanup_execution(self, request, database):
        """测试清理执行"""
        # 插入测试数据
        with database.session() as session:
            session.execute(text("INSERT INTO test_table (id) VALUES ('TEST001')"))
            session.commit()

        mappings = {"test": CleanupMapping(table="test_table", field="id")}
        manager = ConfigDrivenCleanupManager(request, database, mappings)
        manager.add("test", "TEST001")
        manager.cleanup()

        # 验证数据已清理
        with database.session() as session:
            count = session.execute(text("SELECT COUNT(*) FROM test_table WHERE id = 'TEST001'")).scalar()
            assert count == 0


class TestCleanupFixture:
    """测试 cleanup fixture"""

    def test_cleanup_with_config(self, cleanup, database):
        """测试配置驱动的 cleanup"""
        # 假设已配置 CLEANUP__MAPPINGS__test__table=test_table
        cleanup.add("test", "TEST001")

        # 验证清理项已注册
        assert "TEST001" in cleanup.get_items("test")
```

### 6.2 集成测试

**测试文件**: `tests/testing/fixtures/test_prepare_data_integration.py`

```python
class TestPrepareDataIntegration:
    """测试 prepare_data 集成"""

    def test_prepare_and_cleanup(self, prepare_data, cleanup, database):
        """测试准备数据并清理"""
        # 准备数据
        test_id = prepare_data(
            lambda uow: uow.execute(
                text("INSERT INTO test_table (id) VALUES ('TEST001') RETURNING id")
            ).scalar(),
            cleanup=[("test", "TEST001")]
        )

        # 验证数据已提交
        with database.session() as session:
            count = session.execute(text("SELECT COUNT(*) FROM test_table WHERE id = 'TEST001'")).scalar()
            assert count == 1

        # 验证清理项已注册
        assert "TEST001" in cleanup.get_items("test")

    def test_with_repository_auto_discovery(self, prepare_data, runtime):
        """测试 Repository 自动发现"""
        # 模拟配置
        runtime.settings.test.repository_package = "test_package.repositories"

        # 准备数据
        prepare_data(lambda uow: uow.orders.create({...}))

        # 验证使用了自动发现的 Repository


class TestDataPreparerIntegration:
    """测试 data_preparer 集成"""

    def test_context_manager(self, data_preparer, cleanup, database):
        """测试上下文管理器"""
        with data_preparer as prep:
            prep.uow.execute(text("INSERT INTO test_table (id) VALUES ('TEST001')"))
            prep.cleanup("test", "TEST001")

        # 验证数据已提交
        with database.session() as session:
            count = session.execute(text("SELECT COUNT(*) FROM test_table WHERE id = 'TEST001'")).scalar()
            assert count == 1

    def test_chain_cleanup(self, data_preparer, cleanup):
        """测试链式调用"""
        with data_preparer as prep:
            prep.cleanup("orders", "ORD001") \
                .cleanup("orders", "ORD002") \
                .cleanup("cards", "CARD001")

        # 验证所有清理项已注册
        assert "ORD001" in cleanup.get_items("orders")
        assert "ORD002" in cleanup.get_items("orders")
        assert "CARD001" in cleanup.get_items("cards")
```

---

## 7. 文档更新计划

### 7.1 需要更新的文档

| 文档 | 更新内容 |
|------|----------|
| `CHANGELOG.md` | 添加 v3.18.0 版本说明 |
| `docs/releases/v3.18.0.md` | 完整发布说明 |
| `docs/guides/testing.md` | 测试最佳实践 |
| `CLAUDE.md` | 更新使用示例 |

### 7.2 CHANGELOG.md 格式

```markdown
## [3.18.0] - 2025-12-XX

### 数据准备与清理

**核心特性**: 零代码配置的测试数据清理 + 简化的数据准备。

**主要功能**:
- ✨ 新增 `cleanup` fixture - 配置驱动的通用数据清理
- ✨ 新增 `prepare_data` fixture - 回调式数据准备，自动提交
- ✨ 新增 `data_preparer` fixture - 上下文管理器式数据准备
- ✨ 新增 `CleanupConfig` - 清理映射配置模型
- ✨ 新增 `ConfigDrivenCleanupManager` - 配置驱动的清理管理器

**详细内容**: 查看完整发布说明 [v3.18.0](docs/releases/v3.18.0.md)

### 新增
- 新增 `cleanup` fixture - 通用数据清理（配置驱动）
- 新增 `prepare_data` fixture - 数据准备（回调式）
- 新增 `data_preparer` fixture - 数据准备（上下文管理器式）
- 新增 `CleanupConfig` 配置模型
- 新增 `ConfigDrivenCleanupManager` 清理管理器

### 配置
- 支持 `CLEANUP__MAPPINGS` 环境变量配置清理映射
- 支持 `CLEANUP__ENABLED` 控制是否启用自动清理

### 文档
- 新增 `docs/releases/v3.18.0.md` - 完整版本发布说明
- 更新 `docs/guides/testing.md` - 测试最佳实践

### 测试
- 新增清理配置单元测试
- 新增数据准备集成测试

---
```

---

## 8. 实施计划

### 8.1 开发阶段

| 阶段 | 任务 | 文件 |
|------|------|------|
| Phase 1 | 配置模型 | `infrastructure/config/schema.py` |
| Phase 2 | 清理管理器 | `testing/fixtures/cleanup.py` |
| Phase 3 | Fixtures | `testing/fixtures/core.py` |
| Phase 4 | 单元测试 | `tests/testing/fixtures/test_*.py` |
| Phase 5 | 文档更新 | `CHANGELOG.md`, `docs/releases/v3.18.0.md` |

### 8.2 验收标准

1. ✅ 所有单元测试通过
2. ✅ 所有集成测试通过
3. ✅ 代码覆盖率 ≥ 80%
4. ✅ Ruff 检查通过
5. ✅ 文档完整且准确
6. ✅ 向后兼容（不影响现有代码）
7. ✅ gift-card-test 项目验证通过

---

## 9. 向后兼容性

### 9.1 兼容保证

| 现有功能 | 影响 | 说明 |
|---------|------|------|
| `CleanupManager` 基类 | 无影响 | 保留，仍可使用 |
| `SimpleCleanupManager` | 无影响 | 保留，仍可使用 |
| `ListCleanup` | 无影响 | 保留，仍可使用 |
| `should_keep_test_data()` | 无影响 | 保留，cleanup fixture 内部使用 |
| `uow` fixture | 无影响 | 保留，仍可显式 commit |
| 项目自定义 cleanup fixture | 无影响 | 可继续使用，或迁移到配置驱动 |

### 9.2 迁移指南

**从项目 cleanup fixture 迁移到配置驱动**：

1. 在 `.env` 文件中添加清理映射配置：
   ```bash
   CLEANUP__MAPPINGS__orders__table=card_order
   CLEANUP__MAPPINGS__orders__field=customer_order_no
   ```

2. 将测试中的 `cleanup_api_test_data` 改为 `cleanup`：
   ```python
   # Before
   def test_example(cleanup_api_test_data):
       cleanup_api_test_data.add("orders", "ORD001")

   # After
   def test_example(cleanup):
       cleanup.add("orders", "ORD001")
   ```

3. 删除项目中的 `cleanup_api_test_data` fixture（可选）

---

## 10. 总结

### 10.1 核心价值

| 方面 | 价值 |
|------|------|
| 开发效率 | 减少样板代码，无需显式 commit |
| 配置简化 | 零代码配置清理映射 |
| 一致性 | 统一的数据准备和清理方式 |
| 可维护性 | 配置集中管理，易于修改 |
| 向后兼容 | 不影响现有代码 |

### 10.2 推荐使用

| 场景 | 推荐方案 |
|------|----------|
| 简单数据准备 | `prepare_data`（回调式） |
| 复杂数据准备 | `data_preparer`（上下文管理器式） |
| 纯数据库操作（无需提交给 API） | `uow`（默认回滚） |
| 数据清理 | `cleanup`（配置驱动） |

---

**审批**：
- [ ] 技术负责人审批
- [ ] 架构负责人审批
- [ ] 测试负责人审批

**版本**: v2.0
**最后更新**: 2025-12-10