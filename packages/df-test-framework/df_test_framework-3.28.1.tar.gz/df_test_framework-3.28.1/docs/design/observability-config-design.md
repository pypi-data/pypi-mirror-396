# 可观测性配置架构设计

## 版本信息

- **版本**: v3.23.0
- **日期**: 2025-01-13
- **状态**: 已确认

## 问题背景

v3.22.0 引入了事件驱动的调试和 Allure 记录功能：
- `HttpEventPublisherMiddleware` 发布 HTTP 事件
- `ConsoleDebugObserver` 订阅事件输出调试信息
- `AllureObserver` 订阅事件记录到 Allure 报告

v3.22.1 扩展了 `ConsoleDebugObserver` 支持数据库事件。

**问题**：如何统一控制这些可观测性功能？

### 现状分析

| 能力模块 | 事件发布 | 控制开关 |
|----------|----------|----------|
| HTTP | ✅ | `HTTPConfig.enable_event_publisher` |
| Database | ✅ | 无 |
| Redis | ✅ | 无 |
| Storage | ✅ | 无 |

问题：
1. 配置分散，无法统一控制
2. 混淆了"事件发布"和"事件消费"两个关注点
3. 未来模块扩展时需要重复添加开关

## 方案对比

### 方案1：分散配置（当前）

```python
HTTPConfig.enable_event_publisher = True
DatabaseConfig.enable_event_publisher = True  # 待添加
RedisConfig.enable_event_publisher = True     # 待添加
```

- ✅ 细粒度控制
- ❌ 配置分散
- ❌ 无法统一开关
- ❌ 混淆发布和消费

### 方案2：事件始终发布 + 观察者开关

```python
class TestConfig(BaseModel):
    allure_events: bool = True
    console_debug: bool = False
```

- ✅ 简单
- ✅ 事件发布无开销（无订阅者时）
- ❌ 无法一键禁用所有功能

### 方案3：统一可观测性配置（✅ 采用）

```python
class ObservabilityConfig(BaseModel):
    """可观测性配置"""

    # 总开关（一键禁用所有可观测性功能）
    enabled: bool = True

    # 调试输出（ConsoleDebugObserver）
    debug_output: bool = False

    # Allure 记录（AllureObserver）
    allure_recording: bool = True
```

- ✅ 总开关一键控制
- ✅ 清晰区分观察者
- ✅ 易于扩展
- ✅ 配置集中

## 设计决策

### 核心原则

1. **事件始终发布**：能力层（HTTP/DB/Redis/Storage）始终发布事件
2. **观察者控制消费**：通过配置控制观察者是否订阅/输出
3. **总开关优先**：`enabled=False` 时，所有观察者都不工作

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      能力层（始终发布事件）                    │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│    HTTP     │  Database   │    Redis    │      Storage        │
│ http.req.*  │ db.query.*  │ cache.op.*  │   storage.op.*      │
└──────┬──────┴──────┬──────┴──────┬──────┴──────────┬──────────┘
       │             │             │                 │
       └─────────────┴─────────────┴─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    EventBus     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌────────────────┐ ┌────────────┐ ┌────────────┐
     │ AllureObserver │ │ Console    │ │  Future    │
     │ (allure_rec.)  │ │ (debug_out)│ │ Observers  │
     └────────────────┘ └────────────┘ └────────────┘
              │              │              │
              └──────────────┴──────────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ ObservabilityConfig │
                  │   enabled: bool     │
                  │   debug_output      │
                  │   allure_recording  │
                  └─────────────────────┘
```

### 配置使用

```bash
# 正常测试：记录 Allure，不输出调试
OBSERVABILITY__ENABLED=true
OBSERVABILITY__ALLURE_RECORDING=true
OBSERVABILITY__DEBUG_OUTPUT=false

# 调试模式：同时启用
OBSERVABILITY__DEBUG_OUTPUT=true

# CI 快速运行：禁用所有可观测性
OBSERVABILITY__ENABLED=false

# 纯单元测试：禁用所有
OBSERVABILITY__ENABLED=false
```

### 使用场景矩阵

| 场景 | enabled | debug_output | allure_recording |
|------|---------|--------------|------------------|
| 正常测试 | true | false | true |
| 调试模式 | true | true | true |
| 只调试不记录 | true | true | false |
| CI 快速跑 | false | - | - |
| 纯单元测试 | false | - | - |

## 实现计划

### 变更清单

1. **新增配置**
   - `infrastructure/config/schema.py`: 添加 `ObservabilityConfig`
   - `infrastructure/config/__init__.py`: 导出配置类

2. **移除旧配置**
   - `HTTPConfig.enable_event_publisher`: 删除（事件始终发布）

3. **更新观察者**
   - `AllureObserver`: 读取 `ObservabilityConfig.allure_recording`
   - `ConsoleDebugObserver`: 读取 `ObservabilityConfig.debug_output`
   - Fixtures: 根据配置决定是否订阅

4. **更新能力层**
   - `HttpClient`: 移除 `enable_event_publisher` 参数判断
   - `HttpEventPublisherMiddleware`: 始终添加（无需判断）

5. **文档更新**
   - 更新 CHANGELOG.md
   - 更新使用指南

### 向后兼容

- `HTTPConfig.enable_event_publisher` 保留但标记废弃
- 打印警告提示迁移到 `ObservabilityConfig`

## 性能考量

**事件发布开销分析**：

```python
# EventBus.publish 实现
async def publish(self, event):
    handlers = self._handlers.get(event_type, [])
    for handler in handlers:  # 无订阅者 = 空循环
        await handler(event)
```

- 无订阅者时：仅创建事件对象 + 空循环，开销 < 1μs
- 有订阅者时：正常执行观察者逻辑

**结论**：事件始终发布的性能影响可忽略不计。

## 能力层事件发布方式

不同能力层根据自身架构特点，采用不同的事件发布方式：

### 发布方式对比

| 能力层 | 有中间件链？ | 事件发布方式 | 原因 |
|--------|-------------|-------------|------|
| HTTP   | ✅ 有       | 通过中间件   | 需要在中间件处理后发布，确保信息完整 |
| Database | ❌ 无     | 直接发布     | 无中间件，直接在执行前后发布 |
| Redis  | ❌ 无       | 直接发布     | 无中间件，直接在执行前后发布 |
| Storage | ❌ 无      | 直接发布     | 无中间件，直接在执行前后发布 |

### HTTP：中间件内发布

```
Request → [Retry] → [Signature] → [BearerToken] → [EventPublisher] → 实际请求
                                                        ↑
                                    放在最内层，记录完整的 headers（含中间件添加的）
```

HTTP 请求会经过多个中间件处理（签名、认证、重试等），这些中间件会修改请求内容。
因此事件发布中间件 `HttpEventPublisherMiddleware` 必须放在链的最内层（`priority=999`），
才能记录到完整的请求信息（包括所有中间件添加的 headers 和 params）。

### Database/Redis/Storage：直接发布

```python
# 示例：Database._publish_event()
def _publish_event(self, event: Any) -> None:
    event_bus = self._get_event_bus()
    if event_bus:
        event_bus.publish_sync(event)
```

这些能力层没有中间件链，查询参数不会被"加工"，所以直接在操作执行前后发布事件即可。

### 设计原则

1. **适配各自架构**：有中间件用中间件发布，无中间件直接发布
2. **信息完整性**：HTTP 中间件链内发布确保记录到完整信息
3. **简单高效**：无中间件的能力层直接发布，避免不必要的复杂度

### 未来扩展

如果 Database 等能力层将来需要"拦截器"功能（如 SQL 审计、慢查询预警），
可以考虑引入中间件模式。届时事件发布也应迁移到中间件内完成。
