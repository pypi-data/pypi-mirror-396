"""API基类

v3.3.0 重构:
- 简化为只提供HTTP方法封装和响应解析
- 拦截器功能移至HttpClient统一管理
- 不再支持BaseAPI层级的拦截器（请使用HttpClient的配置化拦截器系统）

v3.19.0 新增:
- 支持 skip_auth 参数: 跳过认证中间件
- 支持 token 参数: 使用自定义 Token

v3.20.0 新增:
- 支持 files 参数: multipart/form-data 文件上传
- 新增 head() 方法: 获取资源元信息
- 新增 options() 方法: 获取资源支持的 HTTP 方法

详见: docs/INTERCEPTOR_ARCHITECTURE.md
"""

from typing import Any, TypeVar

import httpx
from loguru import logger
from pydantic import BaseModel, ValidationError

from df_test_framework.capabilities.clients.http.core.request import FilesTypes

from .client import HttpClient

T = TypeVar("T", bound=BaseModel)


# ========== 业务异常 ==========


class BusinessError(Exception):
    """业务错误异常

    当API返回的业务状态码表示失败时抛出此异常

    Attributes:
        message: 错误消息
        code: 业务错误码
        data: 原始响应数据
    """

    def __init__(
        self, message: str, code: int | str | None = None, data: dict[str, Any] | None = None
    ):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(message)

    def __str__(self) -> str:
        if self.code:
            return f"[业务错误 {self.code}] {self.message}"
        return f"[业务错误] {self.message}"


class BaseAPI:
    """
    API基类

    职责:
    - 管理HttpClient
    - 提供便捷的get/post/put/delete方法
    - 解析响应为Pydantic模型
    - 处理业务错误

    v3.3.0 简化:
    - ❌ 移除拦截器管理（请使用HttpClient的配置化拦截器系统）
    - ✅ 专注于API封装和响应解析

    使用拦截器的推荐方式:
        # 在HTTPConfig中配置拦截器（全局生效）
        >>> settings = FrameworkSettings(
        ...     http=HTTPConfig(
        ...         interceptors=[
        ...             SignatureInterceptorConfig(type="signature", ...),
        ...             BearerTokenInterceptorConfig(type="bearer_token", ...)
        ...         ]
        ...     )
        ... )
        >>> client = HttpClient(base_url="...", config=settings.http)
        >>> api = MyAPI(client)

        # 或者编程式添加拦截器
        >>> client = HttpClient(base_url="...")
        >>> client.request_interceptors.append(
        ...     InterceptorFactory.create(SignatureInterceptorConfig(...))
        ... )
    """

    def __init__(self, http_client: HttpClient):
        """
        初始化API基类

        Args:
            http_client: HTTP客户端实例
        """
        self.http_client = http_client

    def _check_business_error(self, response_data: dict[str, Any]) -> None:
        """
        检查业务错误 (可在子类中重写)

        默认实现不检查业务错误,适用于没有统一响应格式的项目
        子类可以根据自己的业务响应格式重写此方法

        常见实现示例:

        # 示例1: 检查 success 字段
        def _check_business_error(self, response_data):
            if not response_data.get("success", True):
                raise BusinessError(
                    message=response_data.get("message", "未知错误"),
                    code=response_data.get("code"),
                    data=response_data
                )

        # 示例2: 检查 code 字段
        def _check_business_error(self, response_data):
            code = response_data.get("code", 200)
            if code not in [200, 0]:  # 假设200和0表示成功
                raise BusinessError(
                    message=response_data.get("message", "未知错误"),
                    code=code,
                    data=response_data
                )

        Args:
            response_data: 响应数据字典

        Raises:
            BusinessError: 业务错误
        """
        pass  # 默认不检查,由子类决定是否实现

    def _parse_response(
        self,
        response: httpx.Response,
        model: type[T] | None = None,
        raise_for_status: bool = True,
        check_business_error: bool = True,
    ) -> T | dict[str, Any]:
        """
        解析响应数据

        Args:
            response: HTTP响应对象
            model: Pydantic模型类,如果提供则解析为模型实例
            raise_for_status: 是否在HTTP错误时抛出异常
            check_business_error: 是否检查业务错误 (调用_check_business_error方法)

        Returns:
            解析后的数据 (Pydantic模型实例或字典)

        Raises:
            httpx.HTTPStatusError: 当HTTP状态码表示错误且raise_for_status=True时
            BusinessError: 当业务状态码表示错误且check_business_error=True时
            ValidationError: 当响应数据验证失败时
        """
        # 检查HTTP状态码
        if raise_for_status:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP错误: {e.response.status_code} - {e.response.text}")
                raise

        # 解析JSON响应
        try:
            response_data = response.json()
        except Exception as e:
            logger.error(f"解析JSON失败: {str(e)}, 响应内容: {response.text}")
            raise

        # 检查业务错误
        if check_business_error:
            try:
                self._check_business_error(response_data)
            except BusinessError as e:
                logger.error(f"业务错误: {e}")
                logger.debug(f"响应数据: {response_data}")
                raise

        # 如果提供了模型,则解析为模型实例
        if model:
            try:
                return model.model_validate(response_data)
            except ValidationError as e:
                logger.error(f"响应数据验证失败: {e.error_count()} 个错误")
                logger.debug(f"验证错误详情: {e.errors()}")
                logger.debug(f"原始响应数据: {response_data}")
                raise
            except Exception as e:
                logger.error(f"解析响应模型失败: {str(e)}")
                logger.debug(f"响应数据: {response_data}")
                raise

        return response_data

    def _build_url(self, endpoint: str) -> str:
        """
        构建请求路径

        遵循 httpx 官方 URL 拼接规范
        - base_url 不需要尾部 /（如 "https://api.example.com"）
        - endpoint 以 / 开头（如 "/users"）

        根据 httpx 官方文档:
        https://github.com/encode/httpx/blob/master/docs/advanced/clients.md

            with httpx.Client(base_url='http://httpbin.org') as client:
                r = client.get('/headers')  # → http://httpbin.org/headers

        Args:
            endpoint: API端点路径，应以 / 开头（如 "/admin/current"）

        Returns:
            确保以 / 开头的路径

        Examples:
            base_url="https://api.example.com"
            endpoint="/users" → 返回 "/users"
            最终URL: "https://api.example.com/users" ✅

            endpoint="users" → 返回 "/users"（自动补全）
        """
        # 确保 endpoint 以 / 开头，遵循 httpx 官方规范
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return endpoint

    def get(
        self,
        endpoint: str,
        model: type[T] | None = None,
        skip_auth: bool = False,
        token: str | None = None,
        **kwargs,
    ) -> T | dict[str, Any]:
        """
        发送GET请求

        Args:
            endpoint: API端点
            model: 响应模型类
            skip_auth: v3.19.0 跳过认证中间件（不添加 Token）
            token: v3.19.0 使用自定义 Token（绕过中间件缓存）
            **kwargs: 其他请求参数
                - params: 查询参数（支持 dict 或 Pydantic 模型）

        Returns:
            解析后的响应数据

        Note:
            如果 params 参数是 Pydantic BaseModel 实例，会自动序列化为字典。
            序列化时会使用 by_alias=True（使用字段别名）和 exclude_none=True（排除 None 值）。

            示例:
                >>> class QueryRequest(BaseModel):
                ...     user_id: str = Field(alias="userId")
                ...     status: str | None = None
                >>>
                >>> request = QueryRequest(user_id="user_001")
                >>> api.get("/users", params=request)  # 自动转换为 {"userId": "user_001"}

            v3.19.0 认证控制:
                >>> # 跳过认证（测试未登录场景）
                >>> api.get("/users/current", skip_auth=True)
                >>> # 使用自定义 Token（测试特定 Token）
                >>> api.get("/users/current", token="my_token")
        """
        # 自动处理 Pydantic 模型序列化为查询参数
        if "params" in kwargs and isinstance(kwargs["params"], BaseModel):
            kwargs["params"] = kwargs["params"].model_dump(
                mode="json", by_alias=True, exclude_none=True
            )

        # v3.19.0: 传递认证控制参数
        if skip_auth:
            kwargs["skip_auth"] = True
        if token:
            kwargs["token"] = token

        url = self._build_url(endpoint)
        response = self.http_client.get(url, **kwargs)
        return self._parse_response(response, model)

    def post(
        self,
        endpoint: str,
        model: type[T] | None = None,
        skip_auth: bool = False,
        token: str | None = None,
        files: FilesTypes | None = None,
        **kwargs,
    ) -> T | dict[str, Any]:
        """
        发送POST请求

        Args:
            endpoint: API端点
            model: 响应模型类
            skip_auth: v3.19.0 跳过认证中间件（不添加 Token）
            token: v3.19.0 使用自定义 Token（绕过中间件缓存）
            files: v3.20.0 文件上传（multipart/form-data）
            **kwargs: 其他请求参数

        Returns:
            解析后的响应数据

        Note:
            如果 json 参数是 Pydantic BaseModel 实例，会自动序列化为字典

        Example:
            >>> # JSON 请求
            >>> api.post("/users", json={"name": "Alice"}, model=UserResponse)
            >>>
            >>> # v3.20.0: 文件上传
            >>> api.post("/templates", files={
            ...     "name": (None, "模板名称"),
            ...     "image": ("img.jpg", img_bytes, "image/jpeg"),
            ... }, model=TemplateResponse)
        """
        # 自动处理 Pydantic 模型序列化
        if "json" in kwargs and isinstance(kwargs["json"], BaseModel):
            kwargs["json"] = kwargs["json"].model_dump(mode="json", by_alias=True)

        # v3.19.0: 传递认证控制参数
        if skip_auth:
            kwargs["skip_auth"] = True
        if token:
            kwargs["token"] = token

        # v3.20.0: 传递 files 参数
        if files is not None:
            kwargs["files"] = files

        url = self._build_url(endpoint)
        response = self.http_client.post(url, **kwargs)
        return self._parse_response(response, model)

    def put(
        self,
        endpoint: str,
        model: type[T] | None = None,
        skip_auth: bool = False,
        token: str | None = None,
        files: FilesTypes | None = None,
        **kwargs,
    ) -> T | dict[str, Any]:
        """
        发送PUT请求

        Args:
            endpoint: API端点
            model: 响应模型类
            skip_auth: v3.19.0 跳过认证中间件（不添加 Token）
            token: v3.19.0 使用自定义 Token（绕过中间件缓存）
            files: v3.20.0 文件上传（multipart/form-data）
            **kwargs: 其他请求参数

        Returns:
            解析后的响应数据

        Note:
            如果 json 参数是 Pydantic BaseModel 实例，会自动序列化为字典
        """
        # 自动处理 Pydantic 模型序列化
        if "json" in kwargs and isinstance(kwargs["json"], BaseModel):
            kwargs["json"] = kwargs["json"].model_dump(mode="json", by_alias=True)

        # v3.19.0: 传递认证控制参数
        if skip_auth:
            kwargs["skip_auth"] = True
        if token:
            kwargs["token"] = token

        # v3.20.0: 传递 files 参数
        if files is not None:
            kwargs["files"] = files

        url = self._build_url(endpoint)
        response = self.http_client.put(url, **kwargs)
        return self._parse_response(response, model)

    def delete(
        self,
        endpoint: str,
        model: type[T] | None = None,
        skip_auth: bool = False,
        token: str | None = None,
        **kwargs,
    ) -> T | dict[str, Any]:
        """
        发送DELETE请求

        Args:
            endpoint: API端点
            model: 响应模型类
            skip_auth: v3.19.0 跳过认证中间件（不添加 Token）
            token: v3.19.0 使用自定义 Token（绕过中间件缓存）
            **kwargs: 其他请求参数

        Returns:
            解析后的响应数据
        """
        # v3.19.0: 传递认证控制参数
        if skip_auth:
            kwargs["skip_auth"] = True
        if token:
            kwargs["token"] = token

        url = self._build_url(endpoint)
        response = self.http_client.delete(url, **kwargs)
        return self._parse_response(response, model)

    def patch(
        self,
        endpoint: str,
        model: type[T] | None = None,
        skip_auth: bool = False,
        token: str | None = None,
        files: FilesTypes | None = None,
        **kwargs,
    ) -> T | dict[str, Any]:
        """
        发送PATCH请求

        Args:
            endpoint: API端点
            model: 响应模型类
            skip_auth: v3.19.0 跳过认证中间件（不添加 Token）
            token: v3.19.0 使用自定义 Token（绕过中间件缓存）
            files: v3.20.0 文件上传（multipart/form-data）
            **kwargs: 其他请求参数

        Returns:
            解析后的响应数据

        Note:
            如果 json 参数是 Pydantic BaseModel 实例，会自动序列化为字典
        """
        # 自动处理 Pydantic 模型序列化
        if "json" in kwargs and isinstance(kwargs["json"], BaseModel):
            kwargs["json"] = kwargs["json"].model_dump(mode="json", by_alias=True)

        # v3.19.0: 传递认证控制参数
        if skip_auth:
            kwargs["skip_auth"] = True
        if token:
            kwargs["token"] = token

        # v3.20.0: 传递 files 参数
        if files is not None:
            kwargs["files"] = files

        url = self._build_url(endpoint)
        response = self.http_client.patch(url, **kwargs)
        return self._parse_response(response, model)

    # ==================== v3.20.0: 新增 HTTP 方法 ====================

    def head(
        self,
        endpoint: str,
        skip_auth: bool = False,
        token: str | None = None,
        **kwargs,
    ) -> httpx.Response:
        """
        发送HEAD请求（v3.20.0 新增）

        获取资源元信息，不返回响应体。
        注意: HEAD 请求不解析响应体，直接返回 httpx.Response。

        Args:
            endpoint: API端点
            skip_auth: 跳过认证中间件
            token: 使用自定义 Token
            **kwargs: 其他请求参数

        Returns:
            httpx.Response（可访问 headers、status_code）

        Example:
            >>> response = api.head("/files/123")
            >>> if response.status_code == 200:
            ...     file_size = response.headers.get("Content-Length")
        """
        # v3.19.0: 传递认证控制参数
        if skip_auth:
            kwargs["skip_auth"] = True
        if token:
            kwargs["token"] = token

        url = self._build_url(endpoint)
        return self.http_client.head(url, **kwargs)

    def options(
        self,
        endpoint: str,
        skip_auth: bool = False,
        token: str | None = None,
        **kwargs,
    ) -> httpx.Response:
        """
        发送OPTIONS请求（v3.20.0 新增）

        获取资源支持的 HTTP 方法。
        注意: OPTIONS 请求不解析响应体，直接返回 httpx.Response。

        Args:
            endpoint: API端点
            skip_auth: 跳过认证中间件
            token: 使用自定义 Token
            **kwargs: 其他请求参数

        Returns:
            httpx.Response（可访问 headers.Allow）

        Example:
            >>> response = api.options("/users")
            >>> allowed = response.headers.get("Allow")
        """
        # v3.19.0: 传递认证控制参数
        if skip_auth:
            kwargs["skip_auth"] = True
        if token:
            kwargs["token"] = token

        url = self._build_url(endpoint)
        return self.http_client.options(url, **kwargs)


__all__ = [
    "BaseAPI",
    "BusinessError",
]
