"""认证控制功能单元测试 (v3.19.0)

测试 skip_auth 和 custom_token 功能。
"""

import pytest

from df_test_framework.capabilities.clients.http.core.request import Request
from df_test_framework.capabilities.clients.http.core.response import Response
from df_test_framework.capabilities.clients.http.middleware.auth import (
    BearerTokenMiddleware,
    LoginTokenProvider,
)


class TestRequestMetadata:
    """测试 Request.metadata 功能"""

    def test_request_with_metadata(self):
        """测试创建带 metadata 的 Request"""
        request = Request(
            method="GET",
            url="/users",
            metadata={"skip_auth": True, "custom_token": "my_token"},
        )

        assert request.metadata["skip_auth"] is True
        assert request.metadata["custom_token"] == "my_token"

    def test_with_metadata_method(self):
        """测试 with_metadata 方法"""
        request = Request(method="GET", url="/users")
        new_request = request.with_metadata("skip_auth", True)

        # 原 request 不变
        assert request.metadata.get("skip_auth") is None
        # 新 request 有 metadata
        assert new_request.metadata["skip_auth"] is True

    def test_get_metadata_method(self):
        """测试 get_metadata 方法"""
        request = Request(
            method="GET",
            url="/users",
            metadata={"skip_auth": True},
        )

        assert request.get_metadata("skip_auth") is True
        assert request.get_metadata("custom_token") is None
        assert request.get_metadata("custom_token", "default") == "default"


class TestBearerTokenMiddlewareSkipAuth:
    """测试 BearerTokenMiddleware 的 skip_auth 功能"""

    @pytest.mark.asyncio
    async def test_skip_auth_skips_token(self):
        """测试 skip_auth=True 时跳过添加 Token"""
        middleware = BearerTokenMiddleware(token="static_token")

        # 创建带 skip_auth 的请求
        request = Request(
            method="GET",
            url="/users",
            metadata={"skip_auth": True},
        )

        # 模拟 call_next
        called_request = None

        async def call_next(req):
            nonlocal called_request
            called_request = req
            return Response(status_code=200, headers={}, body="")

        await middleware(request, call_next)

        # 验证：请求中没有 Authorization 头
        assert "Authorization" not in called_request.headers

    @pytest.mark.asyncio
    async def test_normal_request_adds_token(self):
        """测试正常请求添加 Token"""
        middleware = BearerTokenMiddleware(token="static_token")

        request = Request(method="GET", url="/users")

        called_request = None

        async def call_next(req):
            nonlocal called_request
            called_request = req
            return Response(status_code=200, headers={}, body="")

        await middleware(request, call_next)

        # 验证：请求中有 Authorization 头
        assert called_request.headers.get("Authorization") == "Bearer static_token"


class TestBearerTokenMiddlewareCustomToken:
    """测试 BearerTokenMiddleware 的 custom_token 功能"""

    @pytest.mark.asyncio
    async def test_custom_token_overrides_cache(self):
        """测试 custom_token 覆盖缓存的 Token"""
        middleware = BearerTokenMiddleware(token="static_token")

        # 创建带 custom_token 的请求
        request = Request(
            method="GET",
            url="/users",
            metadata={"custom_token": "my_custom_token"},
        )

        called_request = None

        async def call_next(req):
            nonlocal called_request
            called_request = req
            return Response(status_code=200, headers={}, body="")

        await middleware(request, call_next)

        # 验证：使用自定义 Token
        assert called_request.headers.get("Authorization") == "Bearer my_custom_token"


class TestBearerTokenMiddlewareClearCache:
    """测试 BearerTokenMiddleware 的 clear_cache 功能"""

    def test_clear_cache_with_login_provider(self):
        """测试 LOGIN 模式下清除缓存"""
        provider = LoginTokenProvider(
            login_url="/admin/login",
            credentials={"username": "admin", "password": "pass"},
        )
        # 模拟缓存了 Token
        provider._cached_token = "cached_token"

        middleware = BearerTokenMiddleware(login_token_provider=provider)
        middleware.clear_cache()

        # 验证缓存已清除
        assert provider._cached_token is None

    def test_clear_cache_without_login_provider(self):
        """测试非 LOGIN 模式下 clear_cache 不报错"""
        middleware = BearerTokenMiddleware(token="static_token")
        # 不应该报错
        middleware.clear_cache()


class TestLoginTokenProviderClearCache:
    """测试 LoginTokenProvider 的 clear_cache 功能"""

    def test_clear_cache(self):
        """测试清除缓存"""
        provider = LoginTokenProvider(
            login_url="/admin/login",
            credentials={"username": "admin", "password": "pass"},
        )
        provider._cached_token = "cached_token"

        provider.clear_cache()

        assert provider._cached_token is None


class TestEdgeCases:
    """边缘场景测试"""

    @pytest.mark.asyncio
    async def test_skip_auth_and_token_both_provided(self):
        """测试 skip_auth 和 custom_token 同时提供时，skip_auth 优先"""
        middleware = BearerTokenMiddleware(token="static_token")

        request = Request(
            method="GET",
            url="/users",
            metadata={"skip_auth": True, "custom_token": "custom_token"},
        )

        called_request = None

        async def call_next(req):
            nonlocal called_request
            called_request = req
            return Response(status_code=200, headers={}, body="")

        await middleware(request, call_next)

        # skip_auth=True 时应该跳过认证，不添加任何 Token
        assert "Authorization" not in called_request.headers

    @pytest.mark.asyncio
    async def test_custom_token_empty_string(self):
        """测试 custom_token 为空字符串时回退到默认 Token（空字符串是 falsy）"""
        middleware = BearerTokenMiddleware(token="static_token")

        request = Request(
            method="GET",
            url="/users",
            metadata={"custom_token": ""},
        )

        called_request = None

        async def call_next(req):
            nonlocal called_request
            called_request = req
            return Response(status_code=200, headers={}, body="")

        await middleware(request, call_next)

        # 空字符串是 falsy，会回退到默认的 static_token
        assert called_request.headers.get("Authorization") == "Bearer static_token"

    @pytest.mark.asyncio
    async def test_metadata_with_other_keys(self):
        """测试 metadata 中包含其他键不影响认证"""
        middleware = BearerTokenMiddleware(token="static_token")

        request = Request(
            method="GET",
            url="/users",
            metadata={"other_key": "other_value", "another_key": 123},
        )

        called_request = None

        async def call_next(req):
            nonlocal called_request
            called_request = req
            return Response(status_code=200, headers={}, body="")

        await middleware(request, call_next)

        # 其他 metadata 不影响认证，应该正常添加 Token
        assert called_request.headers.get("Authorization") == "Bearer static_token"


class TestHttpClientClearAuthCache:
    """测试 HttpClient.clear_auth_cache() 的边缘场景"""

    def test_clear_auth_cache_with_path_filtered_middleware(self):
        """测试清除被 PathFilteredMiddleware 包装的 BearerTokenMiddleware 缓存"""
        from df_test_framework import HttpClient
        from df_test_framework.capabilities.clients.http.middleware import (
            PathFilteredMiddleware,
        )

        provider = LoginTokenProvider(
            login_url="/admin/login",
            credentials={"username": "admin", "password": "pass"},
        )
        provider._cached_token = "cached_token"

        bearer_middleware = BearerTokenMiddleware(login_token_provider=provider)
        filtered_middleware = PathFilteredMiddleware(
            middleware=bearer_middleware,
            include_paths=["/admin/**"],
        )

        client = HttpClient(
            base_url="https://api.example.com",
            middlewares=[filtered_middleware],
        )

        # 清除缓存
        client.clear_auth_cache()

        # 验证缓存已清除
        assert provider._cached_token is None

    def test_clear_auth_cache_with_multiple_middlewares(self):
        """测试清除多个中间件的缓存"""
        from df_test_framework import HttpClient
        from df_test_framework.capabilities.clients.http.middleware.signature import (
            SignatureMiddleware,
        )

        provider1 = LoginTokenProvider(
            login_url="/admin/login",
            credentials={"username": "admin", "password": "pass"},
        )
        provider1._cached_token = "cached_token_1"

        provider2 = LoginTokenProvider(
            login_url="/user/login",
            credentials={"username": "user", "password": "pass"},
        )
        provider2._cached_token = "cached_token_2"

        middleware1 = BearerTokenMiddleware(login_token_provider=provider1)
        middleware2 = SignatureMiddleware(secret="secret", algorithm="md5")
        middleware3 = BearerTokenMiddleware(login_token_provider=provider2)

        client = HttpClient(
            base_url="https://api.example.com",
            middlewares=[middleware1, middleware2, middleware3],
        )

        # 清除缓存
        client.clear_auth_cache()

        # 验证所有 BearerTokenMiddleware 的缓存都被清除
        assert provider1._cached_token is None
        assert provider2._cached_token is None

    def test_clear_auth_cache_without_bearer_token_middleware(self):
        """测试没有 BearerTokenMiddleware 时 clear_auth_cache 不报错"""
        from df_test_framework import HttpClient
        from df_test_framework.capabilities.clients.http.middleware.signature import (
            SignatureMiddleware,
        )

        client = HttpClient(
            base_url="https://api.example.com",
            middlewares=[SignatureMiddleware(secret="secret", algorithm="md5")],
        )

        # 不应该报错
        client.clear_auth_cache()


class TestRequestMetadataImmutability:
    """测试 Request metadata 的不可变性"""

    def test_with_metadata_creates_new_request(self):
        """测试 with_metadata 创建新的 Request，不修改原对象"""
        request1 = Request(method="GET", url="/users")
        request2 = request1.with_metadata("skip_auth", True)

        # request1 不变
        assert request1.metadata == {}
        assert request1 is not request2

        # request2 有新的 metadata
        assert request2.metadata == {"skip_auth": True}

    def test_multiple_with_metadata_calls(self):
        """测试多次调用 with_metadata"""
        request = Request(method="GET", url="/users")
        request = request.with_metadata("skip_auth", True)
        request = request.with_metadata("custom_token", "my_token")
        request = request.with_metadata("other_key", "other_value")

        assert request.metadata == {
            "skip_auth": True,
            "custom_token": "my_token",
            "other_key": "other_value",
        }


# ==================== v3.25.0: 新增测试 ====================


class TestApiKeyMiddlewareSkipAndCustom:
    """测试 ApiKeyMiddleware 的 skip_api_key 和 custom_api_key 功能 (v3.25.0)"""

    @pytest.mark.asyncio
    async def test_skip_api_key_skips_adding_key(self):
        """测试 skip_api_key=True 时跳过添加 API Key"""
        from df_test_framework.capabilities.clients.http.middleware.auth import (
            ApiKeyMiddleware,
        )

        middleware = ApiKeyMiddleware(api_key="default_key", header_name="X-API-Key")

        # 创建带 skip_api_key 的请求
        request = Request(
            method="GET",
            url="/users",
            metadata={"skip_api_key": True},
        )

        called_request = None

        async def call_next(req):
            nonlocal called_request
            called_request = req
            return Response(status_code=200, headers={}, body="")

        await middleware(request, call_next)

        # 验证：请求中没有 X-API-Key 头
        assert "X-API-Key" not in called_request.headers

    @pytest.mark.asyncio
    async def test_normal_request_adds_api_key(self):
        """测试正常请求添加 API Key"""
        from df_test_framework.capabilities.clients.http.middleware.auth import (
            ApiKeyMiddleware,
        )

        middleware = ApiKeyMiddleware(api_key="default_key", header_name="X-API-Key")

        request = Request(method="GET", url="/users")

        called_request = None

        async def call_next(req):
            nonlocal called_request
            called_request = req
            return Response(status_code=200, headers={}, body="")

        await middleware(request, call_next)

        # 验证：请求中有 X-API-Key 头
        assert called_request.headers.get("X-API-Key") == "default_key"

    @pytest.mark.asyncio
    async def test_custom_api_key_overrides_default(self):
        """测试 custom_api_key 覆盖默认 API Key"""
        from df_test_framework.capabilities.clients.http.middleware.auth import (
            ApiKeyMiddleware,
        )

        middleware = ApiKeyMiddleware(api_key="default_key", header_name="X-API-Key")

        # 创建带 custom_api_key 的请求
        request = Request(
            method="GET",
            url="/users",
            metadata={"custom_api_key": "my_custom_key"},
        )

        called_request = None

        async def call_next(req):
            nonlocal called_request
            called_request = req
            return Response(status_code=200, headers={}, body="")

        await middleware(request, call_next)

        # 验证：使用自定义 API Key
        assert called_request.headers.get("X-API-Key") == "my_custom_key"

    @pytest.mark.asyncio
    async def test_api_key_in_query_param(self):
        """测试 API Key 作为查询参数"""
        from df_test_framework.capabilities.clients.http.middleware.auth import (
            ApiKeyMiddleware,
        )

        middleware = ApiKeyMiddleware(
            api_key="default_key",
            param_name="api_key",
            in_header=False,
        )

        request = Request(method="GET", url="/users")

        called_request = None

        async def call_next(req):
            nonlocal called_request
            called_request = req
            return Response(status_code=200, headers={}, body="")

        await middleware(request, call_next)

        # 验证：API Key 在查询参数中
        assert called_request.params.get("api_key") == "default_key"


class TestHttpClientResetAuthState:
    """测试 HttpClient.reset_auth_state() 功能 (v3.25.0)"""

    def test_reset_auth_state_clears_both_caches(self):
        """测试 reset_auth_state 同时清除 Token 缓存和 Cookies"""
        from df_test_framework import HttpClient

        provider = LoginTokenProvider(
            login_url="/admin/login",
            credentials={"username": "admin", "password": "pass"},
        )
        provider._cached_token = "cached_token"

        middleware = BearerTokenMiddleware(login_token_provider=provider)

        client = HttpClient(
            base_url="https://api.example.com",
            middlewares=[middleware],
        )

        # 模拟设置 Cookie
        client.client.cookies.set("JSESSIONID", "abc123")

        # 重置认证状态
        client.reset_auth_state()

        # 验证：Token 缓存已清除
        assert provider._cached_token is None
        # 验证：Cookies 已清除
        assert len(client.client.cookies) == 0


class TestHttpClientCookieManagement:
    """测试 HttpClient Cookie 管理功能 (v3.25.0)"""

    def test_get_cookies_returns_all_cookies(self):
        """测试 get_cookies 返回所有 Cookies"""
        from df_test_framework import HttpClient

        client = HttpClient(base_url="https://api.example.com")

        # 设置多个 Cookies
        client.client.cookies.set("JSESSIONID", "abc123")
        client.client.cookies.set("XSRF-TOKEN", "xyz789")

        cookies = client.get_cookies()

        assert cookies == {"JSESSIONID": "abc123", "XSRF-TOKEN": "xyz789"}

    def test_get_cookies_returns_empty_dict_when_no_cookies(self):
        """测试没有 Cookies 时返回空字典"""
        from df_test_framework import HttpClient

        client = HttpClient(base_url="https://api.example.com")

        cookies = client.get_cookies()

        assert cookies == {}

    def test_clear_cookie_removes_specific_cookie(self):
        """测试 clear_cookie 删除指定的 Cookie"""
        from df_test_framework import HttpClient

        client = HttpClient(base_url="https://api.example.com")

        # 设置多个 Cookies
        client.client.cookies.set("JSESSIONID", "abc123")
        client.client.cookies.set("XSRF-TOKEN", "xyz789")

        # 删除指定 Cookie
        result = client.clear_cookie("JSESSIONID")

        assert result is True
        assert "JSESSIONID" not in client.get_cookies()
        assert client.get_cookies().get("XSRF-TOKEN") == "xyz789"

    def test_clear_cookie_returns_false_when_not_exists(self):
        """测试 clear_cookie 删除不存在的 Cookie 返回 False"""
        from df_test_framework import HttpClient

        client = HttpClient(base_url="https://api.example.com")

        result = client.clear_cookie("NOT_EXISTS")

        assert result is False


class TestHttpClientGetAuthInfo:
    """测试 HttpClient.get_auth_info() 功能 (v3.25.0)"""

    def test_get_auth_info_with_cached_token(self):
        """测试有缓存 Token 时的认证信息"""
        from df_test_framework import HttpClient

        provider = LoginTokenProvider(
            login_url="/admin/login",
            credentials={"username": "admin", "password": "pass"},
        )
        provider._cached_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"

        middleware = BearerTokenMiddleware(login_token_provider=provider)

        client = HttpClient(
            base_url="https://api.example.com",
            middlewares=[middleware],
        )
        client.client.cookies.set("JSESSIONID", "abc123")

        info = client.get_auth_info()

        assert info["has_token_cache"] is True
        # Token 预览取前 20 个字符 + "..."
        assert info["token_preview"].startswith("eyJhbGciOiJIUzI1NiIs")
        assert info["token_preview"].endswith("...")
        assert info["middleware_count"] == 1
        assert info["cookies_count"] == 1
        assert "JSESSIONID" in info["cookies"]

    def test_get_auth_info_without_cached_token(self):
        """测试没有缓存 Token 时的认证信息"""
        from df_test_framework import HttpClient

        middleware = BearerTokenMiddleware(token="static_token")

        client = HttpClient(
            base_url="https://api.example.com",
            middlewares=[middleware],
        )

        info = client.get_auth_info()

        assert info["has_token_cache"] is False
        assert info["token_preview"] is None
        assert info["middleware_count"] == 1
        assert info["cookies_count"] == 0

    def test_get_auth_info_without_bearer_middleware(self):
        """测试没有 BearerTokenMiddleware 时的认证信息"""
        from df_test_framework import HttpClient
        from df_test_framework.capabilities.clients.http.middleware.signature import (
            SignatureMiddleware,
        )

        client = HttpClient(
            base_url="https://api.example.com",
            middlewares=[SignatureMiddleware(secret="secret", algorithm="md5")],
        )

        info = client.get_auth_info()

        assert info["has_token_cache"] is False
        assert info["middleware_count"] == 0
