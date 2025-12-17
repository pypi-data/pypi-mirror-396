# RFC: HTTP 能力完善 (v3.20.0)

> **版本**: v3.20.0 (提议)
> **状态**: Draft
> **作者**: QA Team
> **创建日期**: 2024-12-12
> **最后更新**: 2024-12-12

## 1. 概述

### 1.1 背景

当前框架的 HTTP 客户端存在以下能力缺失：

1. **Content-Type 支持不完整**：
   - ❌ `multipart/form-data` - 文件上传场景需要绕过中间件
   - ❌ `application/octet-stream` - 二进制数据传输无原生支持

2. **HTTP 方法不完整**：
   - ❌ `HEAD` - 检查资源存在/获取元信息
   - ❌ `OPTIONS` - CORS 预检/API 发现

本 RFC 旨在一次性补齐这些能力，使框架 HTTP 客户端功能完整。

### 1.2 问题描述（multipart/form-data）

在 `gift-card-test` 项目中，Admin 模板管理 API 的创建和更新接口使用 `@ModelAttribute + MultipartFile` 接收数据，需要 `multipart/form-data` 格式：

```java
// 后端 Controller
@PostMapping
public Result<String> createTemplate(
    @ModelAttribute CardTemplateDTO dto,
    @RequestParam(required = false) MultipartFile image
) { ... }
```

**当前的绕过方式：**

```python
# admin_template_api.py - 绕过中间件直接使用 httpx
def _post_multipart(self, endpoint: str, files: dict, model: type) -> Any:
    url = f"{self.http_client.base_url}{endpoint}"
    token = self._get_token()  # 手动获取 token
    headers = {"Authorization": f"Bearer {token}"}

    # 直接使用底层 httpx 客户端
    response = self.http_client.client.post(url, files=files, headers=headers)
    # ...
```

**问题：**
- ❌ 中间件不生效（认证、签名、日志、重试等）
- ❌ 代码重复（每个需要文件上传的 API 都要写类似逻辑）
- ❌ 难以维护和测试
- ❌ 无法使用框架的统一错误处理

### 1.3 目标

- 在框架层面原生支持 `multipart/form-data` 请求
- 保持中间件系统正常工作
- 提供简洁一致的 API
- 向后兼容，不破坏现有代码

## 2. 需求分析

### 2.1 HTTP Content-Type 支持矩阵

| Content-Type | 当前支持 | v3.20.0 | httpx 参数 | 使用场景 |
|-------------|---------|---------|-----------|---------|
| `application/json` | ✅ | ✅ | `json=` | JSON API |
| `application/x-www-form-urlencoded` | ✅ | ✅ | `data=` | 表单提交 |
| `multipart/form-data` | ❌ | ✅ | `files=` | 文件上传、混合表单 |
| `text/plain` | ❌ | ✅ | `content=` | 纯文本 |
| `application/octet-stream` | ❌ | ✅ | `content=` | 二进制数据 |

### 2.2 HTTP 方法支持矩阵

| 方法 | 当前支持 | v3.20.0 | 使用场景 |
|------|---------|---------|---------|
| GET | ✅ | ✅ | 获取资源 |
| POST | ✅ | ✅ | 创建资源 |
| PUT | ✅ | ✅ | 更新资源（全量） |
| PATCH | ✅ | ✅ | 更新资源（部分） |
| DELETE | ✅ | ✅ | 删除资源 |
| HEAD | ❌ | ✅ | 检查资源存在/获取元信息 |
| OPTIONS | ❌ | ✅ | CORS 预检/API 发现 |

### 2.3 Multipart/Form-Data 使用场景

1. **纯文件上传**
   ```python
   files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
   ```

2. **表单字段 + 文件上传**（最常见）
   ```python
   files = {
       "name": (None, "模板名称"),           # 普通字段
       "faceValue": (None, "100.00"),        # 普通字段
       "image": ("image.jpg", image_bytes, "image/jpeg"),  # 文件
   }
   ```

3. **多文件上传**
   ```python
   files = [
       ("files", ("file1.jpg", bytes1, "image/jpeg")),
       ("files", ("file2.jpg", bytes2, "image/jpeg")),
   ]
   ```

### 2.4 Binary/Raw Content 使用场景

1. **二进制数据传输**
   ```python
   # 上传二进制文件（非 multipart）
   client.post("/api/upload", content=binary_data, headers={"Content-Type": "application/octet-stream"})
   ```

2. **纯文本传输**
   ```python
   # 发送纯文本
   client.post("/api/text", content="Hello World", headers={"Content-Type": "text/plain"})
   ```

3. **XML 数据**
   ```python
   # 发送 XML
   client.post("/api/xml", content=xml_string, headers={"Content-Type": "application/xml"})
   ```

### 2.5 HEAD/OPTIONS 使用场景

1. **HEAD - 检查资源存在**
   ```python
   # 检查文件是否存在（不下载内容）
   response = client.head("/api/files/123")
   if response.status_code == 200:
       file_size = response.headers.get("Content-Length")
   ```

2. **OPTIONS - CORS 预检**
   ```python
   # 检查 API 支持的方法
   response = client.options("/api/users")
   allowed_methods = response.headers.get("Allow")  # "GET, POST, PUT, DELETE"
   ```

### 2.6 httpx 的 files 参数格式

```python
# 格式1: 简单文件
files = {"upload-file": open("report.xls", "rb")}

# 格式2: 带文件名和 MIME 类型
files = {"upload-file": ("report.xls", file_bytes, "application/vnd.ms-excel")}

# 格式3: 表单字段（值为 tuple，第一个元素为 None）
files = {"field_name": (None, "field_value")}

# 格式4: 混合
files = {
    "name": (None, "test"),
    "file": ("image.jpg", image_bytes, "image/jpeg"),
}
```

## 3. 设计方案

### 3.1 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|-----|------|------|-------|
| A: 扩展 Request 对象 | 完整支持、中间件正常工作、API 一致 | 需要修改核心类 | ⭐⭐⭐⭐⭐ |
| B: 添加 upload() 方法 | 改动小、专门优化 | 增加 API 表面积、代码重复 | ⭐⭐⭐ |
| C: 透传 httpx 参数 | 最小改动 | 无法使用中间件 | ⭐⭐ |

**推荐方案 A**：扩展 Request 对象，提供完整的 multipart/form-data 支持。

### 3.2 详细设计

#### 3.2.1 Request 对象扩展

**文件**: `src/df_test_framework/capabilities/clients/http/core/request.py`

```python
from typing import Any, BinaryIO

# 文件类型定义
FileTypes = (
    # 简单文件: {"file": file_bytes}
    bytes |
    # 带元数据: {"file": ("filename", file_bytes, "mime/type")}
    tuple[str | None, bytes | BinaryIO, str | None] |
    # 带额外 headers: {"file": ("filename", file_bytes, "mime/type", {"X-Custom": "value"})}
    tuple[str | None, bytes | BinaryIO, str | None, dict[str, str]]
)

FilesTypes = dict[str, FileTypes] | list[tuple[str, FileTypes]]


@dataclass(frozen=True)
class Request:
    """HTTP请求对象（不可变）

    v3.20.0 新增:
    - files: 支持 multipart/form-data 文件上传
    - content: 支持 raw body（binary/text）
    """

    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    json: dict[str, Any] | None = None
    data: Any | None = None
    files: FilesTypes | None = None  # 🆕 v3.20.0: multipart/form-data
    content: bytes | str | None = None  # 🆕 v3.20.0: raw body
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def with_file(self, name: str, file: FileTypes) -> "Request":
        """添加单个文件

        Args:
            name: 字段名
            file: 文件数据（bytes 或 tuple）

        Returns:
            新的 Request 对象

        Example:
            >>> request = request.with_file("image", image_bytes)
            >>> request = request.with_file("image", ("photo.jpg", image_bytes, "image/jpeg"))
        """
        new_files = dict(self.files) if self.files else {}
        new_files[name] = file
        return replace(self, files=new_files)

    def with_files(self, files: FilesTypes) -> "Request":
        """设置多个文件/表单字段

        Args:
            files: 文件字典或列表

        Returns:
            新的 Request 对象

        Example:
            >>> files = {
            ...     "name": (None, "模板名称"),
            ...     "image": ("photo.jpg", image_bytes, "image/jpeg"),
            ... }
            >>> request = request.with_files(files)
        """
        return replace(self, files=files)

    def with_form_field(self, name: str, value: str) -> "Request":
        """添加表单字段（用于 multipart/form-data）

        这是 with_file(name, (None, value)) 的便捷方法。

        Args:
            name: 字段名
            value: 字段值（字符串）

        Returns:
            新的 Request 对象

        Example:
            >>> request = request.with_form_field("name", "测试模板")
            >>> request = request.with_form_field("price", "100.00")
        """
        return self.with_file(name, (None, value.encode() if isinstance(value, str) else value, None))
```

#### 3.2.2 HttpClient 扩展

**文件**: `src/df_test_framework/capabilities/clients/http/rest/httpx/client.py`

```python
class HttpClient:

    async def _send_request_async(self, request: Request) -> Response:
        """异步发送 HTTP 请求（中间件链的最终处理器）"""
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
        # 🆕 v3.20.0: 支持 content 参数（raw body）
        if request.content is not None:
            params["content"] = request.content

        # ... 发送请求 ...

    def _prepare_request_object(self, method: str, url: str, **kwargs) -> Request:
        """准备 Request 对象"""
        # ... 现有代码 ...

        return Request(
            method=method,
            url=url,
            headers=kwargs.get("headers", {}),
            params=kwargs.get("params"),
            json=kwargs.get("json"),
            data=kwargs.get("data"),
            files=kwargs.get("files"),  # 🆕 v3.20.0
            content=kwargs.get("content"),  # 🆕 v3.20.0
            context={"base_url": self.base_url},
            metadata=metadata,
        )

    def post(
        self,
        url: str,
        json: dict[str, Any] | BaseModel | None = None,
        data: dict[str, Any] | None = None,
        files: FilesTypes | None = None,  # 🆕 v3.20.0
        content: bytes | str | None = None,  # 🆕 v3.20.0
        **kwargs,
    ) -> httpx.Response:
        """POST请求

        v3.20.0 新增: 支持 files 和 content 参数

        Args:
            url: 请求路径
            json: JSON 请求体
            data: 表单数据
            files: 文件上传（multipart/form-data）
            content: 原始请求体（binary/text）
            **kwargs: 其他请求参数

        Example:
            >>> # 纯 JSON
            >>> client.post("/api/users", json={"name": "Alice"})
            >>>
            >>> # 文件上传
            >>> client.post("/api/upload", files={"file": image_bytes})
            >>>
            >>> # 二进制数据
            >>> client.post("/api/binary", content=binary_data,
            ...     headers={"Content-Type": "application/octet-stream"})
        """
        return self.request("POST", url, json=json, data=data, files=files, content=content, **kwargs)

    def put(
        self,
        url: str,
        json: dict[str, Any] | BaseModel | None = None,
        files: FilesTypes | None = None,  # 🆕 v3.20.0
        content: bytes | str | None = None,  # 🆕 v3.20.0
        **kwargs,
    ) -> httpx.Response:
        """PUT请求（v3.20.0 新增 files/content 支持）"""
        return self.request("PUT", url, json=json, files=files, content=content, **kwargs)

    # 🆕 v3.20.0: HEAD 方法
    def head(
        self,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        """HEAD请求（v3.20.0 新增）

        获取资源元信息，不返回响应体。

        Args:
            url: 请求路径
            **kwargs: 其他请求参数

        Example:
            >>> response = client.head("/api/files/123")
            >>> file_size = response.headers.get("Content-Length")
        """
        return self.request("HEAD", url, **kwargs)

    # 🆕 v3.20.0: OPTIONS 方法
    def options(
        self,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        """OPTIONS请求（v3.20.0 新增）

        获取资源支持的 HTTP 方法。

        Args:
            url: 请求路径
            **kwargs: 其他请求参数

        Example:
            >>> response = client.options("/api/users")
            >>> allowed = response.headers.get("Allow")  # "GET, POST, PUT, DELETE"
        """
        return self.request("OPTIONS", url, **kwargs)
```

#### 3.2.3 BaseAPI 扩展

**文件**: `src/df_test_framework/capabilities/clients/http/rest/httpx/base_api.py`

```python
class BaseAPI:

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

        Example:
            >>> # JSON 请求
            >>> api.post("/users", json={"name": "Alice"}, model=UserResponse)
            >>>
            >>> # 文件上传
            >>> api.post("/templates", files={
            ...     "name": (None, "模板"),
            ...     "image": ("img.jpg", img_bytes, "image/jpeg"),
            ... }, model=TemplateResponse)
        """
        # 自动处理 Pydantic 模型序列化
        if "json" in kwargs and isinstance(kwargs["json"], BaseModel):
            kwargs["json"] = kwargs["json"].model_dump(mode="json", by_alias=True)

        # v3.20.0: 传递 files 参数
        if files is not None:
            kwargs["files"] = files

        if skip_auth:
            kwargs["skip_auth"] = True
        if token:
            kwargs["token"] = token

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
        # ... 类似 post ...

    # 🆕 v3.20.0: HEAD 方法
    def head(
        self,
        endpoint: str,
        skip_auth: bool = False,
        token: str | None = None,
        **kwargs,
    ) -> httpx.Response:
        """发送HEAD请求（v3.20.0 新增）

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
        if skip_auth:
            kwargs["skip_auth"] = True
        if token:
            kwargs["token"] = token

        url = self._build_url(endpoint)
        return self.http_client.head(url, **kwargs)

    # 🆕 v3.20.0: OPTIONS 方法
    def options(
        self,
        endpoint: str,
        skip_auth: bool = False,
        token: str | None = None,
        **kwargs,
    ) -> httpx.Response:
        """发送OPTIONS请求（v3.20.0 新增）

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
        if skip_auth:
            kwargs["skip_auth"] = True
        if token:
            kwargs["token"] = token

        url = self._build_url(endpoint)
        return self.http_client.options(url, **kwargs)
```

### 3.3 中间件兼容性

#### 3.3.1 签名中间件

签名中间件需要处理 `files` 参数：

```python
class SignatureMiddleware(Middleware[Request, Response]):

    async def __call__(self, request: Request, next_handler) -> Response:
        # 计算签名时需要考虑 files 中的表单字段
        sign_params = dict(request.params) if request.params else {}

        # 如果有 files，提取表单字段（非文件）加入签名
        if request.files:
            for name, value in request.files.items():
                if isinstance(value, tuple) and value[0] is None:
                    # 这是表单字段，不是文件
                    sign_params[name] = value[1] if isinstance(value[1], str) else value[1].decode()

        # 计算签名
        signature = self._calculate_signature(sign_params)
        request = request.with_param("sign", signature)

        return await next_handler(request)
```

#### 3.3.2 日志中间件

日志中间件需要正确记录 multipart 请求：

```python
class LoggingMiddleware(Middleware[Request, Response]):

    async def __call__(self, request: Request, next_handler) -> Response:
        # 记录请求
        body_info = ""
        if request.json:
            body_info = f"json={request.json}"
        elif request.data:
            body_info = f"data={request.data}"
        elif request.files:
            # 不记录文件内容，只记录字段名
            file_names = list(request.files.keys())
            body_info = f"files={file_names}"

        logger.info(f"HTTP Request: {request.method} {request.url} {body_info}")

        return await next_handler(request)
```

## 4. 使用示例

### 4.1 改进后的 API 客户端代码

```python
# admin_template_api.py - 改进后（使用框架原生支持）
class AdminTemplateAPI(GiftCardBaseAPI):

    def create_template(
        self,
        request: AdminTemplateCreateRequest,
        image: bytes | None = None
    ) -> AdminTemplateCreateResponse:
        """创建卡片模板

        使用框架原生 multipart/form-data 支持，中间件正常工作。
        """
        # 转换为 multipart 字段
        files = request.to_multipart_fields()

        # 如果有图片，添加到字段
        if image is not None:
            files["image"] = ("image.jpg", image, "image/jpeg")

        # ✅ 使用框架原生支持，中间件正常工作
        return self.post(
            endpoint=self.base_path,
            model=AdminTemplateCreateResponse,
            files=files,
        )

    def update_template(
        self,
        template_id: int,
        request: AdminTemplateUpdateRequest,
        image: bytes | None = None,
    ) -> AdminTemplateUpdateResponse:
        """更新卡片模板"""
        files = request.to_multipart_fields()

        if image is not None:
            files["image"] = ("image.jpg", image, "image/jpeg")

        # ✅ 使用框架原生支持
        return self.put(
            endpoint=f"{self.base_path}/{template_id}",
            model=AdminTemplateUpdateResponse,
            files=files,
        )
```

### 4.2 请求模型的辅助方法

```python
# admin_template.py - 请求模型
class AdminTemplateCreateRequest(BaseModel):
    name: str
    face_value: Decimal
    activated_validity: int
    status: int
    # ...

    def to_multipart_fields(self) -> dict[str, tuple[None, str]]:
        """转换为 multipart/form-data 字段

        Returns:
            适用于 httpx files 参数的字典
        """
        fields: dict[str, tuple[None, str]] = {}
        fields["name"] = (None, self.name)
        fields["faceValue"] = (None, str(self.face_value))
        fields["activatedValidity"] = (None, str(self.activated_validity))
        fields["status"] = (None, str(self.status))
        # ... 其他字段
        return fields
```

## 5. 迁移指南

### 5.1 从绕过方式迁移

**改进前（绕过中间件）：**

```python
def create_template(self, request, image=None):
    url = f"{self.http_client.base_url}{self.base_path}"
    token = self._get_token()  # 手动获取
    headers = {"Authorization": f"Bearer {token}"}

    files = request.to_multipart_fields()
    if image:
        files["image"] = ("image.jpg", image, "image/jpeg")

    # 直接使用 httpx，绕过中间件
    response = self.http_client.client.post(url, files=files, headers=headers)
    return AdminTemplateCreateResponse.model_validate(response.json())
```

**改进后（使用框架支持）：**

```python
def create_template(self, request, image=None):
    files = request.to_multipart_fields()
    if image:
        files["image"] = ("image.jpg", image, "image/jpeg")

    # 使用框架原生支持，中间件自动工作
    return self.post(
        endpoint=self.base_path,
        model=AdminTemplateCreateResponse,
        files=files,
    )
```

### 5.2 向后兼容

- 现有使用 `json=` 和 `data=` 的代码无需修改
- `files=` 是新增参数，不影响现有代码
- 中间件默认支持 files 参数，无需额外配置

## 6. 测试计划

### 6.1 单元测试

```python
# test_request.py
def test_request_with_file():
    request = Request(method="POST", url="/upload")
    request = request.with_file("image", b"image_bytes")
    assert request.files == {"image": b"image_bytes"}

def test_request_with_files():
    files = {
        "name": (None, "test"),
        "image": ("photo.jpg", b"bytes", "image/jpeg"),
    }
    request = Request(method="POST", url="/upload", files=files)
    assert request.files == files

def test_request_with_form_field():
    request = Request(method="POST", url="/upload")
    request = request.with_form_field("name", "test")
    assert request.files["name"][0] is None
```

### 6.2 集成测试

```python
# test_http_client.py
def test_post_with_files(http_client, mock_server):
    """测试 POST 文件上传"""
    files = {
        "name": (None, "test"),
        "file": ("test.txt", b"content", "text/plain"),
    }
    response = http_client.post("/upload", files=files)
    assert response.status_code == 200

def test_middleware_works_with_files(http_client_with_auth, mock_server):
    """测试中间件在文件上传时正常工作"""
    files = {"file": ("test.txt", b"content", "text/plain")}
    response = http_client_with_auth.post("/upload", files=files)
    # 验证认证头被添加
    assert "Authorization" in mock_server.last_request.headers
```

## 7. 实施计划

### 7.1 v3.20.0 完整功能清单

| 功能 | 类型 | 状态 |
|-----|------|------|
| `files` 参数（multipart/form-data） | Content-Type | 🔲 待实现 |
| `content` 参数（raw body） | Content-Type | 🔲 待实现 |
| `HEAD` 方法 | HTTP Method | 🔲 待实现 |
| `OPTIONS` 方法 | HTTP Method | 🔲 待实现 |

### 7.2 版本规划

- **v3.20.0**: HTTP 能力完善
  - ✅ multipart/form-data 支持（files 参数）
  - ✅ raw body 支持（content 参数）
  - ✅ HEAD/OPTIONS 方法
  - 更新 CHANGELOG
  - 更新用户指南

## 8. 附录

### 8.1 相关文件清单

需要修改的文件：

```
src/df_test_framework/
├── capabilities/
│   └── clients/
│       └── http/
│           ├── core/
│           │   ├── __init__.py       # 导出 FileTypes, FilesTypes
│           │   └── request.py        # 添加 files, content 字段
│           ├── rest/
│           │   └── httpx/
│           │       ├── client.py     # files/content 参数, head/options 方法
│           │       └── base_api.py   # files 参数, head/options 方法
│           └── middleware/
│               ├── signature.py      # 签名时处理 files
│               └── logging.py        # 日志记录 files/content
├── __init__.py                       # 顶层导出

tests/
├── capabilities/clients/http/
│   ├── core/
│   │   └── test_request.py           # Request 新字段测试
│   └── rest/httpx/
│       └── test_client.py            # HttpClient 新功能测试
```

### 8.2 参考资料

- [httpx 文件上传文档](https://www.python-httpx.org/advanced/#multipart-file-encoding)
- [RFC 7578 - multipart/form-data](https://tools.ietf.org/html/rfc7578)
- [Spring @ModelAttribute 文档](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-methods/modelattrib-method-args.html)

---

## 审批

| 角色 | 姓名 | 日期 | 意见 |
|-----|------|------|------|
| 提案人 | | | |
| 技术评审 | | | |
| 最终批准 | | | |
