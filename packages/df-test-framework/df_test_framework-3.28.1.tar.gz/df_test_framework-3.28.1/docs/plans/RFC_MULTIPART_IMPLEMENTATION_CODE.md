# Multipart/Form-Data 实现代码参考

> 本文档包含 RFC_MULTIPART_FORM_DATA_SUPPORT.md 的具体实现代码，可直接用于开发。

## 1. Request 对象修改

**文件**: `src/df_test_framework/capabilities/clients/http/core/request.py`

### 1.1 添加类型定义

在文件开头添加：

```python
from typing import Any, BinaryIO, Union

# v3.20.0: 文件类型定义
FileContent = Union[bytes, BinaryIO]
FileTypes = Union[
    # 简单文件: bytes
    bytes,
    # 带文件名: ("filename", bytes)
    tuple[str, FileContent],
    # 带 MIME: ("filename", bytes, "mime/type")
    tuple[str | None, FileContent, str | None],
    # 带 headers: ("filename", bytes, "mime/type", {"X-Custom": "value"})
    tuple[str | None, FileContent, str | None, dict[str, str]],
]

# files 参数类型：字典或列表（支持同名字段）
FilesTypes = Union[
    dict[str, FileTypes],
    list[tuple[str, FileTypes]],
]
```

### 1.2 修改 Request 类

```python
@dataclass(frozen=True)
class Request:
    """HTTP请求对象（不可变）

    v3.19.0: 新增 metadata 字段
    v3.20.0: 新增 files 字段，支持 multipart/form-data
    """

    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    json: dict[str, Any] | None = None
    data: Any | None = None
    files: FilesTypes | None = None  # 🆕 v3.20.0: multipart/form-data
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # ... 现有方法 ...

    # 🆕 v3.20.0: 新增方法
    def with_file(self, name: str, file: FileTypes) -> "Request":
        """添加单个文件

        Args:
            name: 字段名
            file: 文件数据

        Returns:
            新的 Request 对象

        Example:
            >>> request.with_file("image", image_bytes)
            >>> request.with_file("image", ("photo.jpg", image_bytes, "image/jpeg"))
        """
        current_files = dict(self.files) if isinstance(self.files, dict) else {}
        current_files[name] = file
        return replace(self, files=current_files)

    def with_files(self, files: FilesTypes) -> "Request":
        """设置文件/表单字段

        Args:
            files: 文件字典或列表

        Returns:
            新的 Request 对象
        """
        return replace(self, files=files)

    def with_form_field(self, name: str, value: str) -> "Request":
        """添加 multipart 表单字段

        便捷方法，等价于 with_file(name, (None, value.encode(), None))

        Args:
            name: 字段名
            value: 字段值

        Returns:
            新的 Request 对象

        Example:
            >>> request.with_form_field("name", "模板名称")
        """
        value_bytes = value.encode("utf-8") if isinstance(value, str) else value
        return self.with_file(name, (None, value_bytes, None))

    def with_form_fields(self, fields: dict[str, str]) -> "Request":
        """批量添加 multipart 表单字段

        Args:
            fields: 字段字典

        Returns:
            新的 Request 对象

        Example:
            >>> request.with_form_fields({
            ...     "name": "模板名称",
            ...     "price": "100.00",
            ... })
        """
        result = self
        for name, value in fields.items():
            result = result.with_form_field(name, value)
        return result
```

## 2. HttpClient 修改

**文件**: `src/df_test_framework/capabilities/clients/http/rest/httpx/client.py`

### 2.1 修改 _send_request_async

```python
async def _send_request_async(self, request: Request) -> Response:
    """异步发送 HTTP 请求（中间件链的最终处理器）

    v3.20.0: 支持 files 参数
    """
    params: dict[str, Any] = {}

    if request.headers:
        params["headers"] = dict(request.headers)
    if request.params:
        params["params"] = dict(request.params)
    if request.json is not None:
        params["json"] = request.json
    if request.data is not None:
        params["data"] = request.data
    # 🆕 v3.20.0: 支持 files 参数
    if request.files is not None:
        params["files"] = request.files

    # 使用线程池执行同步请求
    loop = asyncio.get_event_loop()
    httpx_response = await loop.run_in_executor(
        None,
        lambda: self.client.request(request.method, request.url, **params),
    )

    return self._create_response_object(httpx_response)
```

### 2.2 修改 _prepare_request_object

```python
def _prepare_request_object(
    self,
    method: str,
    url: str,
    **kwargs,
) -> Request:
    """准备 Request 对象

    v3.20.0: 支持 files 参数
    """
    # v3.19.0: 提取 metadata 相关参数
    skip_auth = kwargs.pop("skip_auth", None)
    custom_token = kwargs.pop("token", None)

    # 🆕 v3.20.0: 提取 files 参数
    files = kwargs.pop("files", None)

    # ... 现有的 Pydantic 模型处理代码 ...

    # v3.19.0: 构建 metadata
    metadata: dict[str, Any] = {}
    if skip_auth:
        metadata["skip_auth"] = True
    if custom_token:
        metadata["custom_token"] = custom_token

    return Request(
        method=method,
        url=url,
        headers=kwargs.get("headers", {}),
        params=kwargs.get("params"),
        json=kwargs.get("json"),
        data=kwargs.get("data"),
        files=files,  # 🆕 v3.20.0
        context={"base_url": self.base_url},
        metadata=metadata,
    )
```

### 2.3 修改 post/put 方法签名

```python
def post(
    self,
    url: str,
    json: dict[str, Any] | BaseModel | None = None,
    data: dict[str, Any] | None = None,
    files: FilesTypes | None = None,  # 🆕 v3.20.0
    **kwargs,
) -> httpx.Response:
    """POST请求

    v3.20.0 新增: 支持 files 参数（multipart/form-data）

    Args:
        url: 请求路径
        json: JSON 请求体
        data: 表单数据 (application/x-www-form-urlencoded)
        files: 文件上传 (multipart/form-data)
        **kwargs: 其他请求参数

    注意:
        - json 和 files 不能同时使用
        - data 和 files 可以同时使用（httpx 会合并）
    """
    return self.request("POST", url, json=json, data=data, files=files, **kwargs)


def put(
    self,
    url: str,
    json: dict[str, Any] | BaseModel | None = None,
    data: dict[str, Any] | None = None,
    files: FilesTypes | None = None,  # 🆕 v3.20.0
    **kwargs,
) -> httpx.Response:
    """PUT请求（v3.20.0 新增 files 支持）"""
    return self.request("PUT", url, json=json, data=data, files=files, **kwargs)


def patch(
    self,
    url: str,
    json: dict[str, Any] | BaseModel | None = None,
    data: dict[str, Any] | None = None,
    files: FilesTypes | None = None,  # 🆕 v3.20.0
    **kwargs,
) -> httpx.Response:
    """PATCH请求（v3.20.0 新增 files 支持）"""
    return self.request("PATCH", url, json=json, data=data, files=files, **kwargs)
```

## 3. BaseAPI 修改

**文件**: `src/df_test_framework/capabilities/clients/http/rest/httpx/base_api.py`

### 3.1 修改 post/put/patch 方法

```python
def post(
    self,
    endpoint: str,
    model: type[T] | None = None,
    skip_auth: bool = False,
    token: str | None = None,
    files: FilesTypes | None = None,  # 🆕 v3.20.0
    **kwargs,
) -> T | dict[str, Any]:
    """发送POST请求

    v3.20.0 新增: 支持 files 参数（multipart/form-data）

    Args:
        endpoint: API端点
        model: 响应模型类
        skip_auth: 跳过认证中间件
        token: 使用自定义 Token
        files: 文件上传（multipart/form-data）
        **kwargs: 其他请求参数
    """
    # 自动处理 Pydantic 模型序列化
    if "json" in kwargs and isinstance(kwargs["json"], BaseModel):
        kwargs["json"] = kwargs["json"].model_dump(mode="json", by_alias=True)

    # v3.19.0: 传递认证控制参数
    if skip_auth:
        kwargs["skip_auth"] = True
    if token:
        kwargs["token"] = token

    # 🆕 v3.20.0: 传递 files 参数
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
    files: FilesTypes | None = None,  # 🆕 v3.20.0
    **kwargs,
) -> T | dict[str, Any]:
    """发送PUT请求（v3.20.0 新增 files 支持）"""
    if "json" in kwargs and isinstance(kwargs["json"], BaseModel):
        kwargs["json"] = kwargs["json"].model_dump(mode="json", by_alias=True)

    if skip_auth:
        kwargs["skip_auth"] = True
    if token:
        kwargs["token"] = token
    if files is not None:
        kwargs["files"] = files

    url = self._build_url(endpoint)
    response = self.http_client.put(url, **kwargs)
    return self._parse_response(response, model)


def patch(
    self,
    endpoint: str,
    model: type[T] | None = None,
    skip_auth: bool = False,
    token: str | None = None,
    files: FilesTypes | None = None,  # 🆕 v3.20.0
    **kwargs,
) -> T | dict[str, Any]:
    """发送PATCH请求（v3.20.0 新增 files 支持）"""
    if "json" in kwargs and isinstance(kwargs["json"], BaseModel):
        kwargs["json"] = kwargs["json"].model_dump(mode="json", by_alias=True)

    if skip_auth:
        kwargs["skip_auth"] = True
    if token:
        kwargs["token"] = token
    if files is not None:
        kwargs["files"] = files

    url = self._build_url(endpoint)
    response = self.http_client.patch(url, **kwargs)
    return self._parse_response(response, model)
```

## 4. 签名中间件修改（可选）

**文件**: `src/df_test_framework/capabilities/clients/http/middleware/signature.py`

如果签名需要包含表单字段：

```python
class SignatureMiddleware(Middleware[Request, Response]):

    async def __call__(self, request: Request, next_handler) -> Response:
        # 收集需要签名的参数
        sign_params = dict(request.params) if request.params else {}

        # 🆕 v3.20.0: 如果有 files，提取表单字段（非文件）
        if request.files and isinstance(request.files, dict):
            for name, value in request.files.items():
                # 表单字段格式: (None, value_bytes, None)
                if isinstance(value, tuple) and len(value) >= 2:
                    filename = value[0]
                    if filename is None:  # 这是表单字段，不是文件
                        field_value = value[1]
                        if isinstance(field_value, bytes):
                            sign_params[name] = field_value.decode("utf-8")
                        elif isinstance(field_value, str):
                            sign_params[name] = field_value

        # 计算签名
        signature = self._calculate_signature(sign_params)
        request = request.with_param("sign", signature)

        return await next_handler(request)
```

## 5. 导出类型

**文件**: `src/df_test_framework/capabilities/clients/http/core/__init__.py`

```python
from .request import Request, FileTypes, FilesTypes
from .response import Response

__all__ = [
    "Request",
    "Response",
    "FileTypes",
    "FilesTypes",
]
```

**文件**: `src/df_test_framework/__init__.py`

在顶层导出中添加：

```python
from df_test_framework.capabilities.clients.http.core import FileTypes, FilesTypes

__all__ = [
    # ... 现有导出 ...
    "FileTypes",
    "FilesTypes",
]
```

## 6. 单元测试示例

**文件**: `tests/unit/capabilities/clients/http/core/test_request.py`

```python
import pytest
from df_test_framework.capabilities.clients.http.core import Request


class TestRequestFiles:
    """Request files 字段测试"""

    def test_with_file_bytes(self):
        """测试添加简单字节文件"""
        request = Request(method="POST", url="/upload")
        request = request.with_file("image", b"image_bytes")

        assert request.files == {"image": b"image_bytes"}

    def test_with_file_tuple(self):
        """测试添加带元数据的文件"""
        request = Request(method="POST", url="/upload")
        file_tuple = ("photo.jpg", b"image_bytes", "image/jpeg")
        request = request.with_file("image", file_tuple)

        assert request.files == {"image": file_tuple}

    def test_with_files(self):
        """测试设置多个文件"""
        files = {
            "name": (None, b"test", None),
            "image": ("photo.jpg", b"bytes", "image/jpeg"),
        }
        request = Request(method="POST", url="/upload", files=files)

        assert request.files == files

    def test_with_form_field(self):
        """测试添加表单字段"""
        request = Request(method="POST", url="/upload")
        request = request.with_form_field("name", "测试")

        assert request.files is not None
        assert request.files["name"][0] is None  # filename 为 None
        assert request.files["name"][1] == "测试".encode("utf-8")

    def test_with_form_fields(self):
        """测试批量添加表单字段"""
        request = Request(method="POST", url="/upload")
        request = request.with_form_fields({
            "name": "测试",
            "price": "100.00",
        })

        assert "name" in request.files
        assert "price" in request.files

    def test_immutability(self):
        """测试不可变性"""
        request1 = Request(method="POST", url="/upload")
        request2 = request1.with_file("image", b"bytes")

        assert request1.files is None
        assert request2.files is not None
```

## 7. 集成测试示例

**文件**: `tests/integration/capabilities/clients/http/test_multipart.py`

```python
import pytest
from df_test_framework import HttpClient


class TestMultipartUpload:
    """Multipart/form-data 集成测试"""

    def test_post_with_files(self, http_client: HttpClient, httpbin_url: str):
        """测试 POST 文件上传"""
        files = {
            "file": ("test.txt", b"Hello World", "text/plain"),
        }
        response = http_client.post(f"{httpbin_url}/post", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert "test.txt" in str(data["files"])

    def test_post_with_form_fields_and_file(self, http_client: HttpClient, httpbin_url: str):
        """测试表单字段 + 文件上传"""
        files = {
            "name": (None, "测试名称"),
            "price": (None, "100.00"),
            "image": ("photo.jpg", b"fake_image_bytes", "image/jpeg"),
        }
        response = http_client.post(f"{httpbin_url}/post", files=files)

        assert response.status_code == 200
        data = response.json()
        # httpbin 会将表单字段放在 form 中，文件放在 files 中
        assert data["form"]["name"] == "测试名称"
        assert data["form"]["price"] == "100.00"
        assert "photo.jpg" in str(data["files"])

    def test_middleware_works_with_files(
        self,
        http_client_with_auth: HttpClient,
        mock_server,
    ):
        """测试中间件在文件上传时正常工作"""
        files = {"file": ("test.txt", b"content", "text/plain")}
        response = http_client_with_auth.post("/upload", files=files)

        # 验证认证中间件生效
        assert "Authorization" in mock_server.last_request_headers
```

---

## 检查清单

实现完成后，请确认以下事项：

- [ ] `Request` 类添加了 `files` 字段和相关方法
- [ ] `HttpClient._send_request_async` 处理 `files` 参数
- [ ] `HttpClient._prepare_request_object` 处理 `files` 参数
- [ ] `HttpClient.post/put/patch` 方法签名添加 `files` 参数
- [ ] `BaseAPI.post/put/patch` 方法签名添加 `files` 参数
- [ ] 类型定义已导出到顶层
- [ ] 单元测试覆盖新功能
- [ ] 集成测试验证 multipart 上传
- [ ] 中间件（签名、日志）兼容 files 参数
- [ ] CHANGELOG 更新
- [ ] 用户指南更新
