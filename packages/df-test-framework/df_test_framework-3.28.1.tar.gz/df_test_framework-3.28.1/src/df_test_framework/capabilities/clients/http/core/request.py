"""HTTP请求对象（不可变）

设计理念:
- 不可变对象，避免拦截器互相影响
- 易于调试（每个拦截器的输入输出都清晰）
- 支持并发（未来）

v3.19.0:
- 新增 metadata 字段，用于中间件控制（skip_auth, custom_token 等）

v3.20.0:
- 新增 files 字段，支持 multipart/form-data 文件上传
- 新增 content 字段，支持 raw body（binary/text）
"""

from dataclasses import dataclass, field, replace
from typing import Any, BinaryIO

# v3.20.0: 文件类型定义
FileContent = bytes | BinaryIO
FileTypes = (
    # 简单文件: bytes
    bytes
    # 带文件名: ("filename", bytes)
    | tuple[str, FileContent]
    # 带 MIME: ("filename", bytes, "mime/type") 或 (None, bytes, None) 表示表单字段
    | tuple[str | None, FileContent, str | None]
    # 带 headers: ("filename", bytes, "mime/type", {"X-Custom": "value"})
    | tuple[str | None, FileContent, str | None, dict[str, str]]
)

# files 参数类型：字典或列表（支持同名字段）
FilesTypes = dict[str, FileTypes] | list[tuple[str, FileTypes]]


@dataclass(frozen=True)
class Request:
    """HTTP请求对象（不可变）

    使用dataclass(frozen=True)实现不可变性
    拦截器通过返回新对象来修改请求

    v3.19.0 新增 metadata 字段:
    - skip_auth: 跳过认证中间件
    - custom_token: 使用自定义 Token（绕过中间件缓存）

    v3.20.0 新增:
    - files: 支持 multipart/form-data 文件上传
    - content: 支持 raw body（binary/text）

    Example:
        >>> request = Request(method="GET", url="/users")
        >>> # 添加header（返回新对象）
        >>> new_request = request.with_header("X-Token", "abc123")
        >>> # 原对象不变
        >>> assert "X-Token" not in request.headers
        >>> assert "X-Token" in new_request.headers

        >>> # 跳过认证中间件
        >>> request = Request(method="GET", url="/users", metadata={"skip_auth": True})

        >>> # 使用自定义 Token
        >>> request = Request(method="GET", url="/users", metadata={"custom_token": "my_token"})

        >>> # v3.20.0: 文件上传
        >>> request = Request(method="POST", url="/upload", files={"file": image_bytes})

        >>> # v3.20.0: 二进制数据
        >>> request = Request(method="POST", url="/binary", content=binary_data)
    """

    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    json: dict[str, Any] | None = None
    data: Any | None = None

    # v3.20.0: multipart/form-data 文件上传
    files: FilesTypes | None = None

    # v3.20.0: raw body（binary/text）
    content: bytes | str | None = None

    # 上下文（拦截器间传递数据）
    context: dict[str, Any] = field(default_factory=dict)

    # v3.19.0: 元数据（用于中间件控制）
    # - skip_auth: bool - 跳过认证中间件
    # - custom_token: str - 使用自定义 Token
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def path(self) -> str:
        """获取请求路径（用于路径匹配）

        从url中提取路径部分（去除query参数）

        Returns:
            请求路径

        Example:
            >>> Request(method="GET", url="/api/users?id=1").path
            '/api/users'
            >>> Request(method="GET", url="/api/users").path
            '/api/users'
        """
        # 如果url包含query参数，去除它
        if "?" in self.url:
            return self.url.split("?")[0]
        return self.url

    def with_header(self, key: str, value: str) -> "Request":
        """返回添加了新header的Request对象

        Args:
            key: Header键
            value: Header值

        Returns:
            新的Request对象
        """
        new_headers = {**self.headers, key: value}
        return replace(self, headers=new_headers)

    def with_headers(self, headers: dict[str, str]) -> "Request":
        """返回合并了headers的Request对象

        Args:
            headers: 要合并的headers字典

        Returns:
            新的Request对象
        """
        new_headers = {**self.headers, **headers}
        return replace(self, headers=new_headers)

    def with_param(self, key: str, value: Any) -> "Request":
        """返回添加了新参数的Request对象

        Args:
            key: 参数键
            value: 参数值

        Returns:
            新的Request对象
        """
        new_params = {**self.params, key: value}
        return replace(self, params=new_params)

    def with_params(self, params: dict[str, Any]) -> "Request":
        """返回合并了params的Request对象

        Args:
            params: 要合并的params字典

        Returns:
            新的Request对象
        """
        new_params = {**self.params, **params}
        return replace(self, params=new_params)

    def with_json(self, json_data: dict[str, Any]) -> "Request":
        """返回设置了json的Request对象

        Args:
            json_data: JSON数据

        Returns:
            新的Request对象
        """
        return replace(self, json=json_data)

    def with_context(self, key: str, value: Any) -> "Request":
        """在context中设置值

        Args:
            key: 上下文键
            value: 上下文值

        Returns:
            新的Request对象
        """
        new_context = {**self.context, key: value}
        return replace(self, context=new_context)

    def get_context(self, key: str, default: Any = None) -> Any:
        """从context中获取值

        Args:
            key: 上下文键
            default: 默认值

        Returns:
            上下文值
        """
        return self.context.get(key, default)

    def with_metadata(self, key: str, value: Any) -> "Request":
        """在 metadata 中设置值（v3.19.0）

        用于控制中间件行为，如跳过认证、使用自定义 Token 等。

        Args:
            key: 元数据键（如 'skip_auth', 'custom_token'）
            value: 元数据值

        Returns:
            新的 Request 对象

        Example:
            >>> request = Request(method="GET", url="/users")
            >>> # 跳过认证
            >>> request = request.with_metadata("skip_auth", True)
            >>> # 使用自定义 Token
            >>> request = request.with_metadata("custom_token", "my_token")
        """
        new_metadata = {**self.metadata, key: value}
        return replace(self, metadata=new_metadata)

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """从 metadata 中获取值（v3.19.0）

        Args:
            key: 元数据键
            default: 默认值

        Returns:
            元数据值
        """
        return self.metadata.get(key, default)

    # ==================== v3.20.0: 文件/内容相关方法 ====================

    def with_file(self, name: str, file: FileTypes) -> "Request":
        """添加单个文件（v3.20.0）

        Args:
            name: 字段名
            file: 文件数据（bytes 或 tuple）

        Returns:
            新的 Request 对象

        Example:
            >>> request = request.with_file("image", image_bytes)
            >>> request = request.with_file("image", ("photo.jpg", image_bytes, "image/jpeg"))
        """
        current_files = dict(self.files) if isinstance(self.files, dict) else {}
        current_files[name] = file
        return replace(self, files=current_files)

    def with_files(self, files: FilesTypes) -> "Request":
        """设置多个文件/表单字段（v3.20.0）

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
        """添加 multipart 表单字段（v3.20.0）

        便捷方法，等价于 with_file(name, (None, value.encode(), None))

        Args:
            name: 字段名
            value: 字段值

        Returns:
            新的 Request 对象

        Example:
            >>> request = request.with_form_field("name", "模板名称")
            >>> request = request.with_form_field("price", "100.00")
        """
        value_bytes = value.encode("utf-8") if isinstance(value, str) else value
        return self.with_file(name, (None, value_bytes, None))

    def with_form_fields(self, fields: dict[str, str]) -> "Request":
        """批量添加 multipart 表单字段（v3.20.0）

        Args:
            fields: 字段字典

        Returns:
            新的 Request 对象

        Example:
            >>> request = request.with_form_fields({
            ...     "name": "模板名称",
            ...     "price": "100.00",
            ... })
        """
        result = self
        for name, value in fields.items():
            result = result.with_form_field(name, value)
        return result

    def with_content(self, content: bytes | str) -> "Request":
        """设置原始请求体（v3.20.0）

        用于发送二进制数据或纯文本。

        Args:
            content: 请求体内容（bytes 或 str）

        Returns:
            新的 Request 对象

        Example:
            >>> # 二进制数据
            >>> request = request.with_content(binary_data)
            >>> # 纯文本
            >>> request = request.with_content("Hello World")
        """
        return replace(self, content=content)
