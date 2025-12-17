# httpx 高级用法参考

本文档记录 httpx 底层客户端的各种用法，供参考和学习。

> **注意**: v3.20.0 起，框架已原生支持这些功能，推荐使用框架封装的方式。本文档仅作为底层原理参考。

---

## 目录

- [1. multipart/form-data 文件上传](#1-multipartform-data-文件上传)
- [2. 混合表单（文字+文件）](#2-混合表单文字文件)
- [3. 同名字段多文件上传](#3-同名字段多文件上传)
- [4. 二进制数据 (raw body)](#4-二进制数据-raw-body)
- [5. 流式上传](#5-流式上传)
- [6. HEAD/OPTIONS 请求](#6-headoptions-请求)
- [7. 框架封装对比](#7-框架封装对比)

---

## 1. multipart/form-data 文件上传

### 基本用法

```python
import httpx

# 方式1: 简单 bytes
files = {"file": b"file_content"}

# 方式2: 带文件名
files = {"file": ("filename.txt", b"file_content")}

# 方式3: 带文件名和 MIME 类型
files = {"file": ("image.jpg", image_bytes, "image/jpeg")}

# 方式4: 带自定义 headers
files = {"file": ("doc.pdf", pdf_bytes, "application/pdf", {"X-Custom": "value"})}

# 发送请求
response = httpx.post("https://api.example.com/upload", files=files)
```

### 从文件读取

```python
from pathlib import Path

# 方式1: 读取到内存
with open("photo.jpg", "rb") as f:
    files = {"image": ("photo.jpg", f.read(), "image/jpeg")}
    response = httpx.post("/upload", files=files)

# 方式2: 流式读取（大文件推荐）
with open("large_file.zip", "rb") as f:
    files = {"file": ("large_file.zip", f, "application/zip")}
    response = httpx.post("/upload", files=files)
```

---

## 2. 混合表单（文字+文件）

当需要同时发送表单字段和文件时：

```python
# 表单字段：filename 设为 None
# 文件字段：filename 为实际文件名

files = {
    # 表单字段（filename=None 表示这是普通字段，不是文件）
    "name": (None, "测试模板"),
    "description": (None, "这是模板描述"),
    "price": (None, "99.99"),

    # 文件字段
    "cover_image": ("cover.jpg", image_bytes, "image/jpeg"),
    "attachment": ("doc.pdf", pdf_bytes, "application/pdf"),
}

response = httpx.post("https://api.example.com/templates", files=files)
```

### 编码注意事项

```python
# 中文字段需要编码为 bytes
files = {
    "name": (None, "测试名称".encode("utf-8"), None),
    "price": (None, b"100.00", None),  # 数字也需要是 bytes
    "image": ("photo.jpg", image_bytes, "image/jpeg"),
}
```

---

## 3. 同名字段多文件上传

当 API 需要同一个字段名上传多个文件时，使用 list 格式：

```python
# 使用 list 格式（而非 dict）支持重复的字段名
files = [
    ("files", ("doc1.pdf", pdf1_bytes, "application/pdf")),
    ("files", ("doc2.pdf", pdf2_bytes, "application/pdf")),
    ("files", ("doc3.pdf", pdf3_bytes, "application/pdf")),
]

response = httpx.post("https://api.example.com/batch-upload", files=files)
```

### 混合使用

```python
# 可以混合不同字段
files = [
    ("title", (None, b"Batch Upload", None)),
    ("files", ("doc1.pdf", pdf1_bytes, "application/pdf")),
    ("files", ("doc2.pdf", pdf2_bytes, "application/pdf")),
    ("tags", (None, b"tag1", None)),
    ("tags", (None, b"tag2", None)),
]
```

---

## 4. 二进制数据 (raw body)

当需要发送原始二进制数据（非 multipart）时，使用 `content` 参数：

### application/octet-stream

```python
binary_data = b"\x00\x01\x02\x03\x04\x05"

response = httpx.post(
    "https://api.example.com/upload/binary",
    content=binary_data,
    headers={"Content-Type": "application/octet-stream"}
)
```

### text/plain

```python
text_data = "plain text content"

response = httpx.post(
    "https://api.example.com/webhook",
    content=text_data,
    headers={"Content-Type": "text/plain; charset=utf-8"}
)
```

### 自定义 Content-Type

```python
# XML
xml_data = '<?xml version="1.0"?><root><item>value</item></root>'
response = httpx.post(
    "/api/xml",
    content=xml_data,
    headers={"Content-Type": "application/xml"}
)

# GraphQL（非 JSON 格式）
graphql_query = 'query { users { id name } }'
response = httpx.post(
    "/graphql",
    content=graphql_query,
    headers={"Content-Type": "application/graphql"}
)
```

---

## 5. 流式上传

对于大文件，避免一次性加载到内存：

```python
def file_generator():
    """生成器函数，逐块读取文件"""
    with open("large_file.zip", "rb") as f:
        while chunk := f.read(8192):  # 8KB 块
            yield chunk

# 流式上传
response = httpx.post(
    "https://api.example.com/upload/stream",
    content=file_generator(),
    headers={
        "Content-Type": "application/octet-stream",
        "Transfer-Encoding": "chunked",
    }
)
```

### 异步流式上传

```python
import httpx

async def async_file_generator():
    async with aiofiles.open("large_file.zip", "rb") as f:
        while chunk := await f.read(8192):
            yield chunk

async with httpx.AsyncClient() as client:
    response = await client.post(
        "/upload/stream",
        content=async_file_generator(),
    )
```

---

## 6. HEAD/OPTIONS 请求

### HEAD - 获取资源元信息

```python
# 检查文件是否存在，获取大小
response = httpx.head("https://api.example.com/files/123")

if response.status_code == 200:
    content_length = response.headers.get("Content-Length")
    content_type = response.headers.get("Content-Type")
    last_modified = response.headers.get("Last-Modified")
    print(f"文件大小: {content_length} bytes")
    print(f"类型: {content_type}")
    print(f"最后修改: {last_modified}")
elif response.status_code == 404:
    print("文件不存在")
```

### OPTIONS - CORS 预检/API 发现

```python
# 获取 API 支持的方法
response = httpx.options("https://api.example.com/users")

allowed_methods = response.headers.get("Allow")
print(f"支持的方法: {allowed_methods}")  # GET, POST, PUT, DELETE

# CORS 相关
access_control_methods = response.headers.get("Access-Control-Allow-Methods")
access_control_origin = response.headers.get("Access-Control-Allow-Origin")
```

---

## 7. 框架封装对比

### 底层 httpx 方式

```python
import httpx

client = httpx.Client(base_url="https://api.example.com")

# 文件上传
files = {
    "name": (None, "测试".encode("utf-8"), None),
    "image": ("photo.jpg", image_bytes, "image/jpeg"),
}
response = client.post("/templates", files=files)

# 二进制上传
response = client.post(
    "/upload/binary",
    content=binary_data,
    headers={"Content-Type": "application/octet-stream"}
)

# HEAD 请求
response = client.head("/files/123")
```

### 框架封装方式（v3.20.0 推荐）

```python
from df_test_framework import BaseAPI, Request

class TemplateAPI(BaseAPI):
    def create(self, name: str, image_bytes: bytes) -> dict:
        return self.post(
            "/templates",
            files={
                "name": (None, name.encode("utf-8"), None),
                "image": ("photo.jpg", image_bytes, "image/jpeg"),
            }
        )

    def upload_binary(self, data: bytes) -> dict:
        return self.client.post(
            "/upload/binary",
            content=data,
            headers={"Content-Type": "application/octet-stream"}
        )

    def check_file_exists(self, file_id: str) -> bool:
        response = self.head(f"/files/{file_id}")
        return response.status_code == 200
```

### Request 链式构建（v3.20.0）

```python
from df_test_framework import Request

# 链式构建混合表单
request = (
    Request(method="POST", url="/templates")
    .with_form_field("name", "测试模板")
    .with_form_field("price", "99.99")
    .with_file("image", ("cover.jpg", image_bytes, "image/jpeg"))
    .with_header("X-Custom", "value")
)

# 构建二进制请求
request = (
    Request(method="POST", url="/upload/binary")
    .with_content(binary_data)
    .with_header("Content-Type", "application/octet-stream")
)
```

---

## 参考链接

- [httpx 官方文档 - 文件上传](https://www.python-httpx.org/quickstart/#sending-multipart-file-uploads)
- [httpx 官方文档 - 请求内容](https://www.python-httpx.org/quickstart/#request-content)
- [v3.20.0 发布说明](../releases/v3.20.0.md)
