"""Multipart/form-data 集成测试（v3.20.0）

测试覆盖:
- Request files/content 字段构建
- LoggingMiddleware 与 files/content 兼容性
- Request 不可变性验证
"""

import logging
from unittest.mock import AsyncMock, Mock

import pytest

from df_test_framework.capabilities.clients.http.core import Request
from df_test_framework.capabilities.clients.http.middleware.logging import LoggingMiddleware


class TestRequestFilesConstruction:
    """测试 Request files 字段构建"""

    def test_create_request_with_files_dict(self):
        """测试创建带 files 字典的 Request"""
        files = {"image": b"fake_image_bytes"}
        request = Request(method="POST", url="/upload", files=files)

        assert request.files == files
        assert request.method == "POST"

    def test_create_request_with_files_tuple(self):
        """测试创建带完整文件元组的 Request"""
        files = {"image": ("photo.jpg", b"image_bytes", "image/jpeg")}
        request = Request(method="POST", url="/upload", files=files)

        assert request.files["image"][0] == "photo.jpg"
        assert request.files["image"][2] == "image/jpeg"

    def test_create_request_with_files_list(self):
        """测试创建带文件列表的 Request（同名字段）"""
        files = [
            ("files", ("doc1.pdf", b"pdf1", "application/pdf")),
            ("files", ("doc2.pdf", b"pdf2", "application/pdf")),
        ]
        request = Request(method="POST", url="/batch-upload", files=files)

        assert len(request.files) == 2
        assert request.files[0][0] == "files"
        assert request.files[1][0] == "files"

    def test_create_request_with_mixed_form(self):
        """测试创建混合表单的 Request"""
        files = {
            "name": (None, "测试名称".encode(), None),
            "price": (None, b"100.00", None),
            "image": ("cover.jpg", b"image_bytes", "image/jpeg"),
        }
        request = Request(method="POST", url="/templates", files=files)

        # 表单字段
        assert request.files["name"][0] is None
        # 文件字段
        assert request.files["image"][0] == "cover.jpg"

    def test_with_file_method(self):
        """测试 with_file 方法"""
        request = Request(method="POST", url="/upload")
        request = request.with_file("image", b"bytes")

        assert request.files == {"image": b"bytes"}

    def test_with_file_tuple(self):
        """测试 with_file 方法带元组"""
        request = Request(method="POST", url="/upload")
        request = request.with_file("image", ("photo.jpg", b"bytes", "image/jpeg"))

        assert request.files["image"] == ("photo.jpg", b"bytes", "image/jpeg")

    def test_with_files_method(self):
        """测试 with_files 方法"""
        files = {"a": b"1", "b": b"2"}
        request = Request(method="POST", url="/upload")
        request = request.with_files(files)

        assert request.files == files

    def test_with_form_field_method(self):
        """测试 with_form_field 方法"""
        request = Request(method="POST", url="/upload")
        request = request.with_form_field("name", "测试")

        assert request.files["name"][0] is None  # filename
        assert request.files["name"][1] == "测试".encode()  # content
        assert request.files["name"][2] is None  # mime

    def test_with_form_fields_method(self):
        """测试 with_form_fields 方法"""
        request = Request(method="POST", url="/upload")
        request = request.with_form_fields({"name": "测试", "price": "100"})

        assert "name" in request.files
        assert "price" in request.files


class TestRequestContentConstruction:
    """测试 Request content 字段构建"""

    def test_create_request_with_content_bytes(self):
        """测试创建带 bytes content 的 Request"""
        binary_data = b"\x00\x01\x02\x03\x04"
        request = Request(method="POST", url="/binary", content=binary_data)

        assert request.content == binary_data

    def test_create_request_with_content_string(self):
        """测试创建带 string content 的 Request"""
        text_data = "plain text payload"
        request = Request(method="POST", url="/text", content=text_data)

        assert request.content == text_data

    def test_with_content_method_bytes(self):
        """测试 with_content 方法（bytes）"""
        request = Request(method="POST", url="/upload")
        request = request.with_content(b"binary_data")

        assert request.content == b"binary_data"

    def test_with_content_method_string(self):
        """测试 with_content 方法（string）"""
        request = Request(method="POST", url="/upload")
        request = request.with_content("text_data")

        assert request.content == "text_data"


class TestRequestHeadOptionsMethod:
    """测试 Request HEAD/OPTIONS 方法构建"""

    def test_create_head_request(self):
        """测试创建 HEAD 请求"""
        request = Request(method="HEAD", url="/files/123")

        assert request.method == "HEAD"
        assert request.url == "/files/123"

    def test_create_options_request(self):
        """测试创建 OPTIONS 请求"""
        request = Request(method="OPTIONS", url="/api/users")

        assert request.method == "OPTIONS"
        assert request.url == "/api/users"


class TestMiddlewareFilesCompatibility:
    """测试中间件与 files 参数兼容性"""

    @pytest.fixture
    def logging_middleware(self):
        """日志中间件"""
        return LoggingMiddleware()

    @pytest.mark.asyncio
    async def test_logging_middleware_with_files(self, logging_middleware, caplog):
        """测试 LoggingMiddleware 处理 files 请求"""
        # 创建带 files 的请求
        request = Request(
            method="POST",
            url="/upload",
            files={"image": ("photo.jpg", b"image_bytes", "image/jpeg")},
        )

        # 模拟 call_next
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.headers = {}
        mock_response.text = "{}"
        call_next = AsyncMock(return_value=mock_response)

        with caplog.at_level(logging.DEBUG):
            await logging_middleware(request, call_next)

        # 验证日志包含文件信息
        assert "Files:" in caplog.text
        assert "photo.jpg" in caplog.text

    @pytest.mark.asyncio
    async def test_logging_middleware_with_content(self, logging_middleware, caplog):
        """测试 LoggingMiddleware 处理 content 请求"""
        request = Request(
            method="POST",
            url="/binary",
            content=b"\x00\x01\x02\x03",
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.headers = {}
        mock_response.text = "OK"
        call_next = AsyncMock(return_value=mock_response)

        with caplog.at_level(logging.DEBUG):
            await logging_middleware(request, call_next)

        # 验证日志包含 content 信息
        assert "Content:" in caplog.text
        assert "<bytes>" in caplog.text

    @pytest.mark.asyncio
    async def test_logging_middleware_with_mixed_form(self, logging_middleware, caplog):
        """测试 LoggingMiddleware 处理混合表单"""
        request = (
            Request(method="POST", url="/templates")
            .with_form_field("name", "测试模板")
            .with_file("image", ("cover.jpg", b"image_bytes", "image/jpeg"))
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.headers = {}
        mock_response.text = "{}"
        call_next = AsyncMock(return_value=mock_response)

        with caplog.at_level(logging.DEBUG):
            await logging_middleware(request, call_next)

        # 验证日志包含表单字段和文件
        assert "Files:" in caplog.text
        assert "name" in caplog.text
        assert "cover.jpg" in caplog.text


class TestRequestImmutability:
    """测试 Request 不可变性"""

    def test_with_file_creates_new_request(self):
        """测试 with_file 创建新请求"""
        request1 = Request(method="POST", url="/upload")
        request2 = request1.with_file("image", b"bytes")

        assert request1.files is None
        assert request2.files is not None
        assert request1 is not request2

    def test_with_files_creates_new_request(self):
        """测试 with_files 创建新请求"""
        request1 = Request(method="POST", url="/upload")
        request2 = request1.with_files({"image": b"bytes"})

        assert request1.files is None
        assert request2.files is not None

    def test_with_content_creates_new_request(self):
        """测试 with_content 创建新请求"""
        request1 = Request(method="POST", url="/upload")
        request2 = request1.with_content(b"binary_data")

        assert request1.content is None
        assert request2.content == b"binary_data"

    def test_chained_with_methods(self):
        """测试链式调用"""
        request = (
            Request(method="POST", url="/templates")
            .with_form_field("name", "测试")
            .with_form_field("price", "100")
            .with_file("image", ("photo.jpg", b"bytes", "image/jpeg"))
            .with_header("X-Custom", "value")
        )

        assert "name" in request.files
        assert "price" in request.files
        assert "image" in request.files
        assert request.headers["X-Custom"] == "value"

    def test_multiple_files_immutability(self):
        """测试多次添加文件的不可变性"""
        request1 = Request(method="POST", url="/upload")
        request2 = request1.with_file("file1", b"data1")
        request3 = request2.with_file("file2", b"data2")

        # 每个请求都是独立的
        assert request1.files is None
        assert "file1" in request2.files
        assert "file2" not in request2.files
        assert "file1" in request3.files
        assert "file2" in request3.files
