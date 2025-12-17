"""HTTP核心抽象

包含Request/Response等核心抽象

v3.16.0 更新:
- Interceptor/InterceptorChain 已完全移除
- 请使用 middleware.Middleware/MiddlewareChain

v3.20.0 更新:
- 新增 FileTypes, FilesTypes 类型（用于 multipart/form-data）
"""

from .request import FilesTypes, FileTypes, Request
from .response import Response

__all__ = [
    "Request",
    "Response",
    # v3.20.0: 文件类型
    "FileTypes",
    "FilesTypes",
]
