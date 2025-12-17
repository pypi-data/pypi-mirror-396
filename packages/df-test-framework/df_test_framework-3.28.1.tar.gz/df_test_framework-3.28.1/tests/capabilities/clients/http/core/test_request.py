"""Request 对象测试

v3.20.0 新增:
- files 字段测试
- content 字段测试
- with_file/with_files/with_form_field/with_form_fields/with_content 方法测试
"""

from df_test_framework.capabilities.clients.http.core import (
    FilesTypes,
    FileTypes,
    Request,
)


class TestRequestBasic:
    """Request 基本功能测试"""

    def test_create_request(self):
        """测试创建 Request 对象"""
        request = Request(method="GET", url="/users")

        assert request.method == "GET"
        assert request.url == "/users"
        assert request.headers == {}
        assert request.params == {}
        assert request.json is None
        assert request.data is None
        assert request.files is None
        assert request.content is None

    def test_request_path_property(self):
        """测试 path 属性"""
        request = Request(method="GET", url="/api/users?id=1")
        assert request.path == "/api/users"

        request2 = Request(method="GET", url="/api/users")
        assert request2.path == "/api/users"

    def test_request_immutability(self):
        """测试 Request 不可变性"""
        request1 = Request(method="GET", url="/users")
        request2 = request1.with_header("X-Token", "abc")

        # 原对象不变
        assert "X-Token" not in request1.headers
        # 新对象有新的 header
        assert request2.headers["X-Token"] == "abc"


class TestRequestFiles:
    """Request files 字段测试（v3.20.0）"""

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

    def test_with_files_dict(self):
        """测试设置多个文件（字典）"""
        files: FilesTypes = {
            "name": (None, b"test", None),
            "image": ("photo.jpg", b"bytes", "image/jpeg"),
        }
        request = Request(method="POST", url="/upload")
        request = request.with_files(files)

        assert request.files == files

    def test_with_files_list(self):
        """测试设置多个文件（列表，支持同名字段）"""
        files: FilesTypes = [
            ("files", ("file1.jpg", b"bytes1", "image/jpeg")),
            ("files", ("file2.jpg", b"bytes2", "image/jpeg")),
        ]
        request = Request(method="POST", url="/upload")
        request = request.with_files(files)

        assert request.files == files

    def test_with_form_field(self):
        """测试添加表单字段"""
        request = Request(method="POST", url="/upload")
        request = request.with_form_field("name", "测试")

        assert request.files is not None
        assert request.files["name"][0] is None  # filename 为 None
        assert request.files["name"][1] == "测试".encode()
        assert request.files["name"][2] is None  # mime 为 None

    def test_with_form_fields(self):
        """测试批量添加表单字段"""
        request = Request(method="POST", url="/upload")
        request = request.with_form_fields(
            {
                "name": "测试",
                "price": "100.00",
            }
        )

        assert "name" in request.files
        assert "price" in request.files
        assert request.files["name"][1] == "测试".encode()
        assert request.files["price"][1] == b"100.00"

    def test_files_immutability(self):
        """测试 files 不可变性"""
        request1 = Request(method="POST", url="/upload")
        request2 = request1.with_file("image", b"bytes")

        assert request1.files is None
        assert request2.files is not None

    def test_add_multiple_files(self):
        """测试链式添加多个文件"""
        request = (
            Request(method="POST", url="/upload")
            .with_form_field("name", "模板名称")
            .with_form_field("price", "100.00")
            .with_file("image", ("photo.jpg", b"image_bytes", "image/jpeg"))
        )

        assert "name" in request.files
        assert "price" in request.files
        assert "image" in request.files


class TestRequestContent:
    """Request content 字段测试（v3.20.0）"""

    def test_with_content_bytes(self):
        """测试设置二进制内容"""
        binary_data = b"\x00\x01\x02\x03"
        request = Request(method="POST", url="/upload")
        request = request.with_content(binary_data)

        assert request.content == binary_data

    def test_with_content_string(self):
        """测试设置字符串内容"""
        text = "Hello World"
        request = Request(method="POST", url="/text")
        request = request.with_content(text)

        assert request.content == text

    def test_content_immutability(self):
        """测试 content 不可变性"""
        request1 = Request(method="POST", url="/upload")
        request2 = request1.with_content(b"bytes")

        assert request1.content is None
        assert request2.content == b"bytes"

    def test_create_request_with_content(self):
        """测试直接创建带 content 的 Request"""
        request = Request(
            method="POST",
            url="/upload",
            content=b"binary_data",
        )

        assert request.content == b"binary_data"


class TestRequestMetadata:
    """Request metadata 字段测试（v3.19.0）"""

    def test_with_metadata(self):
        """测试设置 metadata"""
        request = Request(method="GET", url="/users")
        request = request.with_metadata("skip_auth", True)

        assert request.get_metadata("skip_auth") is True

    def test_get_metadata_default(self):
        """测试获取不存在的 metadata（使用默认值）"""
        request = Request(method="GET", url="/users")

        assert request.get_metadata("skip_auth", False) is False
        assert request.get_metadata("nonexistent") is None


class TestTypeAnnotations:
    """类型注解测试"""

    def test_file_types(self):
        """测试 FileTypes 类型"""
        # 简单 bytes
        file1: FileTypes = b"bytes"
        assert isinstance(file1, bytes)

        # 带文件名
        file2: FileTypes = ("filename", b"bytes")
        assert file2[0] == "filename"

        # 带 MIME
        file3: FileTypes = ("filename", b"bytes", "text/plain")
        assert file3[2] == "text/plain"

        # 表单字段（filename 为 None）
        file4: FileTypes = (None, b"value", None)
        assert file4[0] is None

    def test_files_types(self):
        """测试 FilesTypes 类型"""
        # 字典形式
        files1: FilesTypes = {"file": b"bytes"}
        assert "file" in files1

        # 列表形式（支持同名字段）
        files2: FilesTypes = [
            ("file", b"bytes1"),
            ("file", b"bytes2"),
        ]
        assert len(files2) == 2
