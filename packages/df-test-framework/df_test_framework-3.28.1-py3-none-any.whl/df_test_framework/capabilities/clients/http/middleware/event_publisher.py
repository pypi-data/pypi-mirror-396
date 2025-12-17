"""
HTTP 事件发布中间件

v3.22.0 新增

在中间件链的最内层发布 HTTP 事件，确保能记录到所有中间件修改后的完整请求信息。
"""

import time
from typing import Any

from df_test_framework.capabilities.clients.http.core.request import Request
from df_test_framework.capabilities.clients.http.core.response import Response
from df_test_framework.core.events import (
    HttpRequestEndEvent,
    HttpRequestErrorEvent,
    HttpRequestStartEvent,
)
from df_test_framework.core.middleware import BaseMiddleware
from df_test_framework.infrastructure.events import EventBus, get_event_bus


class HttpEventPublisherMiddleware(BaseMiddleware[Request, Response]):
    """HTTP 事件发布中间件

    v3.22.0 新增

    关键特性：
    - priority=999: 在所有业务中间件之后执行（洋葱模型最内层）
    - 能记录到所有中间件修改后的完整 headers
    - 记录 params（GET 请求参数）
    - 使用 correlation_id 关联 Start/End 事件

    执行流程（洋葱模型）：
        BearerTokenMiddleware.before  →  SignatureMiddleware.before  →  EventPublisher.before
                                                    ↓
                                              发布 StartEvent
                                                    ↓
                                               send_request
                                                    ↓
                                              发布 EndEvent
                                                    ↓
        BearerTokenMiddleware.after  ←  SignatureMiddleware.after  ←  EventPublisher.after

    示例:
        # 自动添加（HttpClient 默认行为）
        client = HttpClient(base_url="...")

        # 或手动添加
        client.use(HttpEventPublisherMiddleware())
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        enabled: bool = True,
    ):
        """初始化事件发布中间件

        Args:
            event_bus: EventBus 实例（可选，默认使用全局 EventBus）
            enabled: 是否启用事件发布（默认 True）
        """
        # priority=999: 最后执行 before，能看到所有中间件的修改
        super().__init__(name="HttpEventPublisherMiddleware", priority=999)
        self._event_bus = event_bus
        self._enabled = enabled

    def _get_event_bus(self) -> EventBus | None:
        """获取 EventBus（优先使用注入的，否则获取全局的）"""
        if self._event_bus:
            return self._event_bus
        return get_event_bus()

    async def __call__(
        self,
        request: Request,
        call_next,
    ) -> Response:
        """发布 HTTP 事件

        在发送请求前发布 StartEvent，在收到响应后发布 EndEvent。
        此时 request 已经被所有中间件处理过，包含完整的 headers。
        """
        if not self._enabled:
            return await call_next(request)

        event_bus = self._get_event_bus()
        if not event_bus:
            return await call_next(request)

        # 提取完整的请求信息（此时已包含所有中间件添加的 headers）
        full_url = self._build_full_url(request)
        headers = dict(request.headers) if request.headers else {}
        params = self._extract_params(request)
        body = self._extract_body(request)

        # 发布请求开始事件（异步发布，因为我们在 async 上下文中）
        start_event, correlation_id = HttpRequestStartEvent.create(
            method=request.method,
            url=full_url,
            headers=headers,
            params=params,
            body=body,
        )
        await event_bus.publish(start_event)

        start_time = time.time()

        try:
            # 调用下一个中间件或发送请求
            response = await call_next(request)
            duration = time.time() - start_time

            # 发布请求结束事件
            end_event = HttpRequestEndEvent.create(
                correlation_id=correlation_id,
                method=request.method,
                url=full_url,
                status_code=response.status_code,
                duration=duration,
                headers=dict(response.headers) if response.headers else None,
                body=response.body,
            )
            await event_bus.publish(end_event)

            return response

        except Exception as e:
            duration = time.time() - start_time

            # 发布请求错误事件
            error_event = HttpRequestErrorEvent.create(
                correlation_id=correlation_id,
                method=request.method,
                url=full_url,
                error=e,
                duration=duration,
            )
            await event_bus.publish(error_event)

            raise

    def _build_full_url(self, request: Request) -> str:
        """构建完整 URL（包含 base_url）

        Args:
            request: HTTP 请求

        Returns:
            完整 URL 或相对路径
        """
        # 尝试从 context 获取 base_url
        base_url = ""
        if request.context and "base_url" in request.context:
            base_url = request.context["base_url"].rstrip("/")

        path = request.url or request.path or ""

        if base_url and not path.startswith("http"):
            return f"{base_url}/{path.lstrip('/')}"
        return path

    def _extract_params(self, request: Request) -> dict[str, Any]:
        """提取请求参数

        Args:
            request: HTTP 请求

        Returns:
            参数字典
        """
        if request.params:
            # 确保值是可序列化的
            params = {}
            for key, value in request.params.items():
                if isinstance(value, (str, int, float, bool, type(None))):
                    params[key] = value
                elif isinstance(value, (list, tuple)):
                    params[key] = list(value)
                else:
                    params[key] = str(value)
            return params
        return {}

    def _extract_body(self, request: Request) -> str | None:
        """提取请求体

        Args:
            request: HTTP 请求

        Returns:
            请求体字符串或 None
        """
        if request.json:
            import json

            try:
                return json.dumps(request.json, ensure_ascii=False, default=str)
            except Exception:
                return str(request.json)
        elif request.data:
            return str(request.data)
        elif request.content:
            if isinstance(request.content, bytes):
                return f"<binary: {len(request.content)} bytes>"
            return str(request.content)
        elif request.files:
            # 记录文件上传信息，不记录内容
            file_info = []
            for name, file_data in request.files.items():
                if isinstance(file_data, tuple):
                    filename = file_data[0] if len(file_data) > 0 else "unknown"
                    file_info.append(f"{name}: {filename}")
                else:
                    file_info.append(f"{name}: <file>")
            return f"<multipart: {', '.join(file_info)}>"
        return None
