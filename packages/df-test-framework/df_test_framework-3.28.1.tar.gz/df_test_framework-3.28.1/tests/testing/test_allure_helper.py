"""测试 Allure 辅助工具 - attach_json 自动处理 Pydantic 模型

v3.18.x 新特性:
- attach_json() 自动识别并处理 Pydantic 模型
- 向后兼容：仍然支持手动调用 .model_dump()
"""

import pytest
from pydantic import BaseModel

from df_test_framework.testing.reporting.allure import attach_json


class SampleResponse(BaseModel):
    """测试用 Pydantic 响应模型"""

    code: int
    message: str
    data: dict | None = None


class SampleResponseV1(BaseModel):
    """Pydantic v2 测试模型（已更新为 ConfigDict 语法）"""

    code: int
    message: str

    model_config = {"extra": "allow"}  # Pydantic v2 ConfigDict 语法


@pytest.mark.unit
class TestAttachJson:
    """测试 attach_json 功能"""

    def test_attach_json_with_dict(self):
        """测试 attach_json 处理字典类型"""
        # Arrange
        data = {"code": 200, "message": "成功"}

        # Act & Assert - 不应抛出异常
        attach_json(data, "字典数据")

    def test_attach_json_with_pydantic_v2_model(self):
        """测试 attach_json 自动处理 Pydantic v2 模型"""
        # Arrange
        response = SampleResponse(code=200, message="成功", data={"user_id": "test_001"})

        # Act & Assert - 应该自动调用 .model_dump()
        attach_json(response, "Pydantic V2 模型")

    def test_attach_json_with_model_dump_manual(self):
        """测试向后兼容：手动调用 .model_dump() 仍然有效"""
        # Arrange
        response = SampleResponse(code=200, message="成功")

        # Act & Assert - 向后兼容
        attach_json(response.model_dump(), "手动调用 model_dump")

    def test_attach_json_with_nested_pydantic_model(self):
        """测试 attach_json 处理嵌套 Pydantic 模型"""

        # Arrange
        class NestedData(BaseModel):
            """嵌套数据模型"""

            user_id: str
            username: str

        class NestedResponse(BaseModel):
            """包含嵌套模型的响应"""

            code: int
            data: NestedData

        response = NestedResponse(code=200, data=NestedData(user_id="user_001", username="Alice"))

        # Act & Assert - 应该自动处理嵌套模型
        attach_json(response, "嵌套 Pydantic 模型")

    def test_attach_json_with_list_of_models(self):
        """测试 attach_json 处理 Pydantic 模型列表"""

        # Arrange
        class Item(BaseModel):
            """项目模型"""

            id: str
            name: str

        class ListResponse(BaseModel):
            """包含列表的响应"""

            code: int
            items: list[Item]

        response = ListResponse(
            code=200,
            items=[Item(id="1", name="Item 1"), Item(id="2", name="Item 2")],
        )

        # Act & Assert
        attach_json(response, "包含 Pydantic 模型列表")

    def test_attach_json_with_none_values(self):
        """测试 attach_json 处理包含 None 值的模型"""
        # Arrange
        response = SampleResponse(code=200, message="成功", data=None)

        # Act & Assert
        attach_json(response, "包含 None 值的模型")

    def test_attach_json_backward_compatibility(self):
        """测试向后兼容性：所有旧的调用方式仍然有效"""
        # Arrange
        response = SampleResponse(code=200, message="成功")

        # Act & Assert - 多种调用方式都应该有效
        # 方式1: 直接传递模型（新特性）
        attach_json(response, "方式1")

        # 方式2: 手动调用 model_dump()（向后兼容）
        attach_json(response.model_dump(), "方式2")

        # 方式3: 传递字典（原有功能）
        attach_json({"code": 200, "message": "成功"}, "方式3")
