# 认证与 Session 管理指南

> **版本要求**: df-test-framework >= 3.19.0
> **更新日期**: 2025-12-14
> **最新版本**: v3.25.0

---

## 概述

本指南介绍如何正确处理 **Bearer Token 认证** 与 **HTTP Session（Cookies）** 的交互问题，特别是在测试登出流程时可能遇到的 **Token 复用** 问题。

**v3.25.0 新增**:
- ✅ `reset_auth_state()` - 组合方法，一次调用完全清除认证状态（推荐）
- ✅ `get_auth_info()` - 查询当前认证状态，方便调试
- ✅ `clear_cookie(name)` - 精细控制，只删除指定的 Cookie
- ✅ `get_cookies()` - 获取当前所有 Cookies

**v3.21.0 新增**:
- ✅ `clear_cookies()` - 清除 httpx 客户端的 Cookies
- ✅ 完整的认证流程测试支持

**v3.19.0 特性**:
- ✅ `clear_auth_cache()` - 清除 Token 缓存
- ✅ `skip_auth` - 跳过认证中间件
- ✅ `token` - 使用自定义 Token

---

## 问题场景

### 典型问题：登出后 Token 仍被复用

在测试认证流程时，可能遇到以下问题：

```python
def test_admin_logout(admin_auth_api):
    """测试登出功能"""
    # 1. 登录
    admin_auth_api.login(username, password)

    # 2. 登出
    admin_auth_api.logout()

    # 3. 清除框架缓存
    admin_auth_api.http_client.clear_auth_cache()

    # ❌ 后续测试仍然失败 401！
```

**症状**：
- `clear_auth_cache()` 已调用，但后续测试仍返回 401
- 重新登录后获取的 Token 与登出前相同
- Token 已被加入服务器黑名单，导致请求失败

---

## 根本原因

### Session Token 复用机制

```
┌─────────────────────────────────────────────────────────────────────────┐
│  问题根源：服务器基于 Session（Cookies）返回相同的 Token                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  test_admin_logout:                                                     │
│    1. login() → 服务器生成 Token A，设置 Session Cookie                 │
│    2. logout() → Token A 加入 Redis 黑名单                              │
│    3. clear_auth_cache() → 清除框架层 Token 缓存                        │
│    4. ❌ httpx cookies 未清除 → Session 仍存在                          │
│                                                                         │
│  test_full_auth_flow（下一个测试）:                                      │
│    1. login() → 携带同一 Session Cookie                                 │
│    2. 服务器检测到 Session → 返回 Token A（已被黑名单！）                │
│    3. get_current_user() → ❌ 401 Unauthorized                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 原因分析

1. **框架层缓存**：`BearerTokenMiddleware` 中的 `LoginTokenProvider` 会缓存 Token
2. **HTTP 层缓存**：`httpx.Client` 的 cookies 维护 Session
3. **服务器层缓存**：很多后端服务会基于 Session 复用 Token（性能优化）

三层缓存任一存在，都可能导致 Token 复用：

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  框架层         │     │  HTTP 层        │     │  服务器层       │
│  Token 缓存     │ ──→ │  Session Cookie │ ──→ │  Session Token  │
│                 │     │                 │     │  缓存           │
└─────────────────┘     └─────────────────┘     └─────────────────┘
   clear_auth_cache()      clear_cookies()         无法直接控制
```

---

## 解决方案

### 推荐做法：使用 reset_auth_state()（v3.25.0+）

```python
def test_admin_logout(admin_auth_api):
    """测试登出功能"""
    # 1. 登录
    admin_auth_api.login(username, password)

    # 2. 登出
    admin_auth_api.logout()

    # 3. ✅ v3.25.0 推荐：一次调用完全清除
    admin_auth_api.http_client.reset_auth_state()
```

### 备选做法：分别清除两层缓存

```python
def test_admin_logout(admin_auth_api):
    """测试登出功能"""
    # 1. 登录
    admin_auth_api.login(username, password)

    # 2. 登出
    admin_auth_api.logout()

    # 3. 分别清除两层缓存（等价于 reset_auth_state()）
    admin_auth_api.http_client.clear_auth_cache()  # 清除框架 Token 缓存
    admin_auth_api.http_client.clear_cookies()     # 清除 httpx cookies（强制新 Session）
```

### API 说明

#### `reset_auth_state()`（v3.25.0）- 推荐

组合调用 `clear_auth_cache()` 和 `clear_cookies()`，一次调用完全清除认证状态。

```python
# 一次调用，完全清除认证状态
http_client.reset_auth_state()
```

#### `get_auth_info()`（v3.25.0）

查询当前认证状态，返回包含 Token 缓存、Cookies 等信息的字典。

```python
info = http_client.get_auth_info()
# {
#     'has_token_cache': True,
#     'token_preview': 'eyJhbGciOiJIUzI1NiIs...',
#     'middleware_count': 1,
#     'cookies_count': 2,
#     'cookies': ['JSESSIONID', 'XSRF-TOKEN']
# }
```

#### `clear_cookie(name)`（v3.25.0）

只删除指定的 Cookie，精细控制。

```python
# 只删除 Session Cookie
deleted = http_client.clear_cookie("JSESSIONID")
```

#### `get_cookies()`（v3.25.0）

获取当前所有 Cookies。

```python
cookies = http_client.get_cookies()
# {'JSESSIONID': 'abc123', 'XSRF-TOKEN': 'xyz789'}
```

#### `clear_auth_cache()`（v3.19.0）

清除 `BearerTokenMiddleware` 中 `LoginTokenProvider` 缓存的 Token。

```python
# 清除 Token 缓存，下次请求将重新登录获取新 Token
http_client.clear_auth_cache()
```

#### `clear_cookies()`（v3.21.0）

清除 httpx 客户端的 Cookies，强制服务器创建新 Session。

```python
# 清除 cookies，服务器将创建新 Session 并生成新 Token
http_client.clear_cookies()
```

---

## 使用场景

### 场景 1：测试完整登录-登出流程

```python
@pytest.mark.integration
def test_full_auth_flow(admin_auth_api, settings):
    """测试完整的登录-获取用户-登出流程"""
    from df_test_framework import BusinessError
    from httpx import HTTPStatusError

    username = settings.business.admin_username
    password = settings.business.admin_password

    # 1. 登录，获取 Token
    login_response = admin_auth_api.login(username, password)
    token = login_response.data.token

    # 2. 用 Token 获取当前用户（使用 token 参数绕过缓存）
    user_response = admin_auth_api.get_current_user(token=token)
    assert user_response.success

    # 3. 用 Token 登出
    admin_auth_api.logout(token=token)

    # 4. 验证 Token 已失效
    with pytest.raises((BusinessError, HTTPStatusError)):
        admin_auth_api.get_current_user(token=token)

    # 5. 清理（确保不影响其他测试）
    admin_auth_api.http_client.clear_auth_cache()
    admin_auth_api.http_client.clear_cookies()
```

### 场景 2：测试未登录状态

```python
def test_get_current_user_without_login(admin_auth_api):
    """测试未登录状态下获取当前用户"""
    from df_test_framework import BusinessError
    from httpx import HTTPStatusError

    # 使用 skip_auth=True 跳过认证中间件
    with pytest.raises((BusinessError, HTTPStatusError)):
        admin_auth_api.get_current_user(skip_auth=True)
```

### 场景 3：测试特定 Token

```python
def test_with_specific_token(admin_auth_api):
    """使用特定 Token 测试"""
    # 使用 token 参数，绕过中间件缓存
    response = admin_auth_api.get_current_user(token="my_specific_token")
```

### 场景 4：Session 作用域的 API 实例

当使用 `@api_class(scope="session")` 时，API 实例在整个测试会话中共享：

```python
@api_class("admin_auth_api", scope="session")
class AdminAuthAPI(GiftCardBaseAPI):
    """Session 作用域的 API 实例"""
    pass
```

**注意事项**：
- 登出测试可能影响后续使用同一 API 实例的测试
- 必须在登出后清理缓存和 cookies

```python
def test_admin_logout(admin_auth_api):
    """测试登出"""
    admin_auth_api.login(username, password)
    admin_auth_api.logout()

    # ✅ 必须清理，否则影响后续测试
    admin_auth_api.http_client.clear_auth_cache()
    admin_auth_api.http_client.clear_cookies()
```

---

## 最佳实践

### 1. 登出后必须清理

```python
# ✅ v3.25.0 推荐：使用 reset_auth_state()
admin_auth_api.logout()
admin_auth_api.http_client.reset_auth_state()

# 或者分别清除（v3.21.0）
admin_auth_api.logout()
admin_auth_api.http_client.clear_auth_cache()
admin_auth_api.http_client.clear_cookies()
```

### 2. 使用 token 参数测试特定 Token

```python
# ✅ 推荐：使用 token 参数确保使用特定 Token
login_response = admin_auth_api.login(username, password)
token = login_response.data.token

# 后续操作都使用这个 Token
admin_auth_api.get_current_user(token=token)
admin_auth_api.logout(token=token)
```

### 3. 使用 skip_auth 测试未认证场景

```python
# ✅ 推荐：使用 skip_auth 测试未登录场景
with pytest.raises((BusinessError, HTTPStatusError)):
    admin_auth_api.get_current_user(skip_auth=True)
```

### 4. 考虑测试隔离

如果担心测试之间的影响，可以在测试开始时清理：

```python
@pytest.fixture(autouse=True)
def clean_auth_state(admin_auth_api):
    """每个测试前后清理认证状态"""
    # 测试前清理
    admin_auth_api.http_client.clear_auth_cache()
    admin_auth_api.http_client.clear_cookies()

    yield

    # 测试后清理
    admin_auth_api.http_client.clear_auth_cache()
    admin_auth_api.http_client.clear_cookies()
```

---

## 技术细节

### 为什么服务器会返回相同的 Token？

这是很多后端框架的常见设计模式：

1. **性能优化**：避免频繁生成 JWT（签名计算开销）
2. **Session 一致性**：同一 Session 内保持相同的认证状态
3. **Spring Security**：可能在 Session 中缓存 authentication token

### 框架内部实现

```python
# BearerTokenMiddleware 处理流程
async def __call__(self, request, call_next):
    # 1. 检查 skip_auth
    if request.get_metadata("skip_auth"):
        return await call_next(request)

    # 2. 检查 custom_token
    custom_token = request.get_metadata("custom_token")
    if custom_token:
        token = custom_token
    else:
        # 3. 从缓存或登录获取 Token
        token = await self._get_token()

    # 4. 添加 Authorization 头
    request = request.with_header("Authorization", f"Bearer {token}")
    return await call_next(request)
```

### LoginTokenProvider 的缓存机制

```python
class LoginTokenProvider:
    async def get_token(self, http_client):
        # 如果有缓存，直接返回
        if self._cached_token:
            return self._cached_token

        # 否则调用登录接口（会携带 httpx cookies）
        response = await self._do_login(http_client)
        self._cached_token = self._extract_token(response)
        return self._cached_token

    def clear_cache(self):
        self._cached_token = None
```

---

## 常见问题

### Q: 为什么 `clear_auth_cache()` 不够？

A: `clear_auth_cache()` 只清除框架层的 Token 缓存。如果服务器基于 Session（cookies）返回相同的 Token，需要同时清除 cookies。

### Q: 什么时候需要调用 `clear_cookies()`？

A: 当测试登出功能，或需要强制服务器创建新 Session 时。

### Q: 会影响其他 HTTP 请求吗？

A: `clear_cookies()` 会清除当前 httpx 客户端的所有 cookies，包括非认证相关的 cookies。如果后端依赖其他 cookies，需要注意影响。

### Q: 如何只清除认证相关的 Cookie？

A: 目前 `clear_cookies()` 会清除所有 cookies。如果需要精细控制，可以直接操作 httpx 客户端：

```python
# 只删除特定 cookie
del http_client.client.cookies["JSESSIONID"]
```

---

## 相关文档

- [中间件使用指南](middleware_guide.md) - 了解 BearerTokenMiddleware
- [httpx 高级用法](httpx_advanced_usage.md) - httpx 客户端详细用法
