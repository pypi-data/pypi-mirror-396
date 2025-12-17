"""
使用 Fixture 进行测试示例 (v3.28.0)

演示如何使用框架提供的各种 fixture。
"""

import pytest


class TestWithRuntime:
    """使用 runtime fixture 的测试"""

    def test_access_settings(self, runtime):
        """测试访问配置"""
        assert runtime.settings is not None
        assert runtime.settings.http.base_url is not None

    def test_get_http_client(self, runtime):
        """测试获取 HTTP 客户端"""
        http_client = runtime.http_client()
        assert http_client is not None


class TestWithHttpClient:
    """使用 http_client fixture 的测试"""

    def test_http_client_get(self, http_client):
        """测试 HTTP GET 请求"""
        response = http_client.get("/users/1")

        assert response.status_code == 200
        assert response.json()["id"] == 1

    def test_http_client_post(self, http_client, sample_user_data):
        """测试 HTTP POST 请求"""
        response = http_client.post("/users", json=sample_user_data)

        assert response.status_code == 201
        assert response.json()["name"] == sample_user_data["name"]


class TestWithMultipleFixtures:
    """使用多个 fixture 的测试"""

    def test_with_runtime_and_http_client(self, runtime, http_client):
        """测试同时使用 runtime 和 http_client"""
        # 使用 runtime
        settings = runtime.settings

        # 使用 http_client
        response = http_client.get("/users/1")

        assert response.status_code == 200
        assert settings is not None


class TestWithSampleData:
    """使用测试数据 fixture 的测试"""

    def test_with_sample_user_data(self, sample_user_data):
        """测试使用示例用户数据"""
        assert "name" in sample_user_data
        assert "email" in sample_user_data
        assert sample_user_data["name"] == "张三"

    def test_with_sample_post_data(self, sample_post_data):
        """测试使用示例文章数据"""
        assert "title" in sample_post_data
        assert "body" in sample_post_data
        assert sample_post_data["userId"] == 1

    def test_create_user_with_sample_data(self, http_client, sample_user_data):
        """测试使用示例数据创建用户"""
        response = http_client.post("/users", json=sample_user_data)

        assert response.status_code == 201
        assert response.json()["name"] == sample_user_data["name"]


@pytest.fixture
def custom_fixture():
    """自定义 fixture 示例"""
    print("\n设置自定义fixture")
    yield "自定义数据"
    print("\n清理自定义fixture")


class TestWithCustomFixture:
    """使用自定义 fixture 的测试"""

    def test_custom_fixture(self, custom_fixture):
        """测试自定义 fixture"""
        assert custom_fixture == "自定义数据"


# Fixture scope 示例
@pytest.fixture(scope="module")
def module_fixture():
    """模块级别的 fixture（整个模块只执行一次）"""
    return "模块级别数据"


@pytest.fixture(scope="function")
def function_fixture():
    """函数级别的 fixture（每个测试函数都执行一次）"""
    return "函数级别数据"


class TestFixtureScope:
    """Fixture 作用域测试"""

    def test_module_fixture_1(self, module_fixture):
        """第一次使用模块 fixture"""
        assert module_fixture == "模块级别数据"

    def test_module_fixture_2(self, module_fixture):
        """第二次使用模块 fixture（不会重新创建）"""
        assert module_fixture == "模块级别数据"

    def test_function_fixture_1(self, function_fixture):
        """第一次使用函数 fixture"""
        assert function_fixture == "函数级别数据"

    def test_function_fixture_2(self, function_fixture):
        """第二次使用函数 fixture（会重新创建）"""
        assert function_fixture == "函数级别数据"


# ============================================================
# 调试 Fixture 示例 (v3.28.0)
# ============================================================


class TestWithDebugFixtures:
    """调试 fixture 示例

    运行方式:
        pytest examples/03-testing/test_with_fixtures.py::TestWithDebugFixtures -v -s
    """

    def test_with_console_debugger(self, http_client, console_debugger):
        """使用 console_debugger fixture

        控制台会输出彩色的请求/响应调试信息。
        """
        response = http_client.get("/users/1")
        assert response.status_code == 200

    @pytest.mark.usefixtures("debug_mode")
    def test_with_debug_mode(self, http_client):
        """使用 debug_mode fixture

        等效于使用 console_debugger，但语法更简洁。
        """
        response = http_client.get("/posts/1")
        assert response.status_code == 200
