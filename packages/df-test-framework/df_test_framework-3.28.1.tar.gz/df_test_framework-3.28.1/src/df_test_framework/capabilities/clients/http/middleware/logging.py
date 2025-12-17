"""
日志中间件

记录 HTTP 请求和响应日志。
"""

import logging
import time

from df_test_framework.capabilities.clients.http.core.request import Request
from df_test_framework.capabilities.clients.http.core.response import Response
from df_test_framework.core.middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware[Request, Response]):
    """日志中间件

    记录 HTTP 请求和响应的详细信息。

    可配置日志级别和输出内容。

    示例:
        middleware = LoggingMiddleware(
            level="DEBUG",
            log_request=True,
            log_response=True,
            log_body=True,
        )
    """

    def __init__(
        self,
        logger: logging.Logger | None = None,
        level: str = "DEBUG",
        log_request: bool = True,
        log_response: bool = True,
        log_headers: bool = False,
        log_body: bool = True,
        mask_fields: list[str] | None = None,
        max_body_length: int = 1000,
        priority: int = 100,
    ):
        """初始化日志中间件

        Args:
            logger: 日志对象
            level: 日志级别
            log_request: 是否记录请求
            log_response: 是否记录响应
            log_headers: 是否记录 Headers
            log_body: 是否记录 Body
            mask_fields: 需要脱敏的字段
            max_body_length: 最大记录体长度
            priority: 优先级（应该较大，最后执行）
        """
        super().__init__(name="LoggingMiddleware", priority=priority)
        self._logger = logger or logging.getLogger(__name__)
        self._level = getattr(logging, level.upper(), logging.DEBUG)
        self.log_request = log_request
        self.log_response = log_response
        self.log_headers = log_headers
        self.log_body = log_body
        self.mask_fields = mask_fields or ["password", "token", "secret"]
        self.max_body_length = max_body_length

    async def __call__(
        self,
        request: Request,
        call_next,
    ) -> Response:
        """记录请求和响应"""
        # 记录请求
        if self.log_request:
            self._log_request(request)

        start = time.monotonic()

        try:
            response = await call_next(request)
            duration = time.monotonic() - start

            # 记录响应
            if self.log_response:
                self._log_response(request, response, duration)

            return response

        except Exception as e:
            duration = time.monotonic() - start
            self._log_error(request, e, duration)
            raise

    def _log_request(self, request: Request) -> None:
        """记录请求"""
        parts = [f"→ {request.method} {request.path}"]

        if self.log_headers and request.headers:
            headers_str = ", ".join(f"{k}={v}" for k, v in request.headers.items())
            parts.append(f"  Headers: {headers_str}")

        if self.log_body:
            # JSON body
            if request.json:
                body_str = str(request.json)
                if len(body_str) > self.max_body_length:
                    body_str = body_str[: self.max_body_length] + "..."
                parts.append(f"  Body: {body_str}")

            # v3.20.0: 记录文件元信息（不记录文件内容）
            if request.files:
                files_info = self._format_files_info(request.files)
                parts.append(f"  Files: {files_info}")

            # v3.20.0: 记录 content 元信息
            if request.content is not None:
                content_info = self._format_content_info(request.content)
                parts.append(f"  Content: {content_info}")

        self._logger.log(self._level, "\n".join(parts))

    def _format_files_info(self, files) -> str:
        """格式化文件信息（只记录元数据，不记录内容）

        Args:
            files: FilesTypes - dict 或 list 格式的文件数据

        Returns:
            格式化的文件信息字符串
        """
        file_infos = []

        # 处理 dict 格式: {"field": file_data}
        if isinstance(files, dict):
            for field_name, file_data in files.items():
                info = self._extract_file_info(field_name, file_data)
                file_infos.append(info)
        # 处理 list 格式: [("field", file_data), ...]
        elif isinstance(files, list):
            for field_name, file_data in files:
                info = self._extract_file_info(field_name, file_data)
                file_infos.append(info)

        return ", ".join(file_infos)

    def _extract_file_info(self, field_name: str, file_data) -> str:
        """提取单个文件的元信息

        Args:
            field_name: 表单字段名
            file_data: FileTypes - bytes 或 tuple 格式

        Returns:
            格式化的文件信息
        """
        # 简单 bytes 格式
        if isinstance(file_data, bytes):
            return f"{field_name}(<bytes>, {len(file_data)} bytes)"

        # tuple 格式: (filename, content, mime?, headers?)
        if isinstance(file_data, tuple):
            filename = file_data[0] if len(file_data) > 0 else None
            content = file_data[1] if len(file_data) > 1 else None
            mime = file_data[2] if len(file_data) > 2 else None

            # 计算内容大小
            size = 0
            if content is not None:
                if isinstance(content, bytes):
                    size = len(content)
                elif hasattr(content, "read"):
                    # BinaryIO - 无法直接获取大小
                    size = -1  # 表示未知大小

            # 格式化输出
            if filename:
                size_str = f"{size} bytes" if size >= 0 else "stream"
                mime_str = f", {mime}" if mime else ""
                return f"{field_name}({filename}, {size_str}{mime_str})"
            else:
                # 表单字段（filename 为 None）
                return f"{field_name}(<form field>, {size} bytes)"

        return f"{field_name}(<unknown>)"

    def _format_content_info(self, content: bytes | str) -> str:
        """格式化 content 信息

        Args:
            content: bytes 或 str 类型的原始内容

        Returns:
            格式化的 content 信息
        """
        if isinstance(content, bytes):
            return f"<bytes>, {len(content)} bytes"
        elif isinstance(content, str):
            length = len(content)
            if length <= 50:
                return f'"{content}"'
            else:
                return f'"{content[:50]}...", {length} chars'
        return "<unknown>"

    def _log_response(
        self,
        request: Request,
        response: Response,
        duration: float,
    ) -> None:
        """记录响应"""
        status_emoji = "✓" if response.is_success else "✗"
        parts = [
            f"← {request.method} {request.path} "
            f"{status_emoji} {response.status_code} ({duration:.3f}s)"
        ]

        if self.log_headers and response.headers:
            headers_str = ", ".join(f"{k}={v}" for k, v in response.headers.items())
            parts.append(f"  Headers: {headers_str}")

        if self.log_body:
            body_str = response.text
            if len(body_str) > self.max_body_length:
                body_str = body_str[: self.max_body_length] + "..."
            parts.append(f"  Body: {body_str}")

        self._logger.log(self._level, "\n".join(parts))

    def _log_error(
        self,
        request: Request,
        error: Exception,
        duration: float,
    ) -> None:
        """记录错误"""
        self._logger.error(f"← {request.method} {request.path} ✗ ERROR ({duration:.3f}s): {error}")
