"""现代化控制台调试器

v3.22.0 新增
v3.22.1 扩展：支持数据库调试

基于 EventBus 的事件驱动调试器，提供彩色、结构化的控制台输出。

特性：
- 事件驱动：自动订阅 EventBus，无需手动调用
- 彩色输出：使用 ANSI 颜色代码
- 结构化：清晰的请求/响应分隔
- 脱敏：自动隐藏敏感信息（Token、密码等）
- 多类型支持：HTTP 请求、数据库查询
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from loguru import logger

from df_test_framework.core.events.types import (
    DatabaseQueryEndEvent,
    DatabaseQueryErrorEvent,
    DatabaseQueryStartEvent,
    HttpRequestEndEvent,
    HttpRequestErrorEvent,
    HttpRequestStartEvent,
)


# ANSI 颜色代码
class Colors:
    """ANSI 颜色代码"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # 前景色
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    # 背景色
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


def _supports_color() -> bool:
    """检查终端是否支持颜色"""
    # Windows 终端、VS Code、大多数现代终端都支持
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _colorize(text: str, color: str) -> str:
    """添加颜色（如果支持）"""
    if _supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


@dataclass
class RequestRecord:
    """HTTP 请求记录"""

    correlation_id: str
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    body: str | None = None
    start_time: datetime = field(default_factory=datetime.now)


@dataclass
class QueryRecord:
    """数据库查询记录（v3.22.1 新增）"""

    correlation_id: str
    operation: str  # SELECT, INSERT, UPDATE, DELETE
    table: str
    sql: str
    params: dict[str, Any] = field(default_factory=dict)
    database: str | None = None
    start_time: datetime = field(default_factory=datetime.now)


class ConsoleDebugObserver:
    """现代化控制台调试器

    v3.22.0 新增
    v3.22.1 扩展：支持数据库调试

    基于 EventBus 的事件驱动调试器，自动订阅事件并输出调试信息。

    特性：
    - 事件驱动：自动订阅 EventBus
    - 彩色输出：请求/响应使用不同颜色
    - 结构化：清晰的分隔线和缩进
    - 脱敏：自动隐藏 Token、密码等敏感信息
    - 可配置：控制是否显示 headers、body、SQL 等
    - 多类型支持：HTTP 请求、数据库查询（v3.22.1）

    使用方式：
        # 方式1：通过 fixture（推荐）
        def test_api(http_client, console_debugger):
            response = http_client.get("/users")
            # 控制台自动输出调试信息

        # 方式2：手动创建
        from df_test_framework.infrastructure.events import get_event_bus

        observer = ConsoleDebugObserver()
        observer.subscribe(get_event_bus())

        # 执行请求...

        observer.unsubscribe()

        # v3.22.1: 启用数据库调试
        observer = ConsoleDebugObserver(show_database=True)
        observer.subscribe(get_event_bus())
    """

    # 敏感字段名（自动脱敏）
    SENSITIVE_FIELDS = {
        "authorization",
        "x-token",
        "x-api-key",
        "x-sign",
        "token",
        "password",
        "secret",
        "api_key",
        "access_token",
        "refresh_token",
    }

    def __init__(
        self,
        show_headers: bool = True,
        show_body: bool = True,
        show_params: bool = True,
        max_body_length: int = 500,
        use_colors: bool = True,
        output_to_logger: bool = False,
        # v3.22.1: 数据库调试选项
        show_database: bool = True,
        show_sql: bool = True,
        show_sql_params: bool = True,
        max_sql_length: int = 500,
    ):
        """初始化控制台调试器

        Args:
            show_headers: 是否显示请求/响应头
            show_body: 是否显示请求/响应体
            show_params: 是否显示 GET 参数
            max_body_length: 最大 body 显示长度
            use_colors: 是否使用颜色（自动检测终端支持）
            output_to_logger: 是否同时输出到 logger
            show_database: 是否显示数据库查询（v3.22.1 新增）
            show_sql: 是否显示 SQL 语句（v3.22.1 新增）
            show_sql_params: 是否显示 SQL 参数（v3.22.1 新增）
            max_sql_length: 最大 SQL 显示长度（v3.22.1 新增）
        """
        # HTTP 选项
        self.show_headers = show_headers
        self.show_body = show_body
        self.show_params = show_params
        self.max_body_length = max_body_length
        self.use_colors = use_colors and _supports_color()
        self.output_to_logger = output_to_logger

        # 数据库选项（v3.22.1）
        self.show_database = show_database
        self.show_sql = show_sql
        self.show_sql_params = show_sql_params
        self.max_sql_length = max_sql_length

        # 存储进行中的请求/查询（用于关联 Start/End 事件）
        self._pending_requests: dict[str, RequestRecord] = {}
        self._pending_queries: dict[str, QueryRecord] = {}  # v3.22.1
        self._event_bus = None

    def subscribe(self, event_bus) -> None:
        """订阅 EventBus 事件

        Args:
            event_bus: EventBus 实例
        """
        self._event_bus = event_bus

        # 订阅 HTTP 事件（使用事件类型类，保持类型安全）
        event_bus.subscribe(HttpRequestStartEvent, self._handle_request_start)
        event_bus.subscribe(HttpRequestEndEvent, self._handle_request_end)
        event_bus.subscribe(HttpRequestErrorEvent, self._handle_request_error)

        # v3.22.1: 订阅数据库事件
        if self.show_database:
            event_bus.subscribe(DatabaseQueryStartEvent, self._handle_query_start)
            event_bus.subscribe(DatabaseQueryEndEvent, self._handle_query_end)
            event_bus.subscribe(DatabaseQueryErrorEvent, self._handle_query_error)

    def unsubscribe(self) -> None:
        """取消订阅"""
        if self._event_bus:
            # 取消 HTTP 事件订阅
            self._event_bus.unsubscribe(HttpRequestStartEvent, self._handle_request_start)
            self._event_bus.unsubscribe(HttpRequestEndEvent, self._handle_request_end)
            self._event_bus.unsubscribe(HttpRequestErrorEvent, self._handle_request_error)

            # 取消数据库事件订阅
            if self.show_database:
                self._event_bus.unsubscribe(DatabaseQueryStartEvent, self._handle_query_start)
                self._event_bus.unsubscribe(DatabaseQueryEndEvent, self._handle_query_end)
                self._event_bus.unsubscribe(DatabaseQueryErrorEvent, self._handle_query_error)

            self._event_bus = None

    def _handle_request_start(self, event) -> None:
        """处理请求开始事件"""
        correlation_id = getattr(event, "correlation_id", "")

        # 记录请求信息
        record = RequestRecord(
            correlation_id=correlation_id,
            method=getattr(event, "method", ""),
            url=getattr(event, "url", ""),
            headers=dict(event.headers) if getattr(event, "headers", None) else {},
            params=dict(event.params) if getattr(event, "params", None) else {},
            body=getattr(event, "body", None),
        )
        self._pending_requests[correlation_id] = record

        # 输出请求信息
        self._print_request(record)

    def _handle_request_end(self, event) -> None:
        """处理请求结束事件"""
        correlation_id = getattr(event, "correlation_id", "")
        request = self._pending_requests.pop(correlation_id, None)

        status_code = getattr(event, "status_code", 0)
        duration = getattr(event, "duration", 0)
        headers = dict(event.headers) if getattr(event, "headers", None) else {}
        body = getattr(event, "body", None)

        # 输出响应信息
        self._print_response(
            method=request.method if request else "???",
            url=request.url if request else "???",
            status_code=status_code,
            duration_ms=duration * 1000,
            headers=headers,
            body=body,
        )

    def _handle_request_error(self, event) -> None:
        """处理请求错误事件"""
        correlation_id = getattr(event, "correlation_id", "")
        request = self._pending_requests.pop(correlation_id, None)

        error_type = getattr(event, "error_type", "UnknownError")
        error_message = getattr(event, "error_message", "")
        duration = getattr(event, "duration", 0)

        # 输出错误信息
        self._print_error(
            method=request.method if request else "???",
            url=request.url if request else "???",
            error_type=error_type,
            error_message=error_message,
            duration_ms=duration * 1000,
        )

    def _print_request(self, record: RequestRecord) -> None:
        """打印请求信息"""
        lines = []

        # 分隔线和标题
        separator = "─" * 60
        lines.append("")
        lines.append(self._color(separator, Colors.DIM))
        lines.append(
            self._color(f"🌐 {record.method} ", Colors.BOLD + Colors.CYAN)
            + self._color(record.url, Colors.CYAN)
        )

        # Headers
        if self.show_headers and record.headers:
            lines.append(self._color("  Headers:", Colors.GRAY))
            for key, value in record.headers.items():
                safe_value = self._sanitize_value(key, value)
                lines.append(f"    {self._color(key, Colors.BLUE)}: {safe_value}")

        # Params
        if self.show_params and record.params:
            lines.append(self._color("  Params:", Colors.GRAY))
            for key, value in record.params.items():
                lines.append(f"    {self._color(key, Colors.MAGENTA)}: {value}")

        # Body
        if self.show_body and record.body:
            lines.append(self._color("  Body:", Colors.GRAY))
            body_str = self._format_body(record.body)
            for line in body_str.split("\n"):
                lines.append(f"    {line}")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_response(
        self,
        method: str,
        url: str,
        status_code: int,
        duration_ms: float,
        headers: dict[str, str],
        body: str | None,
    ) -> None:
        """打印响应信息"""
        lines = []

        # 状态颜色
        if 200 <= status_code < 300:
            status_color = Colors.GREEN
            status_icon = "✅"
        elif 300 <= status_code < 400:
            status_color = Colors.YELLOW
            status_icon = "↩️"
        elif 400 <= status_code < 500:
            status_color = Colors.YELLOW
            status_icon = "⚠️"
        else:
            status_color = Colors.RED
            status_icon = "❌"

        # 响应行
        lines.append(
            f"  {status_icon} "
            + self._color(f"{status_code}", Colors.BOLD + status_color)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )

        # Headers
        if self.show_headers and headers:
            # 只显示关键响应头
            key_headers = ["content-type", "content-length", "x-request-id"]
            for key in key_headers:
                for h_key, h_value in headers.items():
                    if h_key.lower() == key:
                        lines.append(f"    {self._color(h_key, Colors.BLUE)}: {h_value}")

        # Body
        if self.show_body and body:
            lines.append(self._color("  Response:", Colors.GRAY))
            body_str = self._format_body(body)
            for line in body_str.split("\n")[:10]:  # 最多显示10行
                lines.append(f"    {line}")
            if body_str.count("\n") > 10:
                lines.append(self._color("    ... (truncated)", Colors.DIM))

        # 分隔线
        separator = "─" * 60
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_error(
        self,
        method: str,
        url: str,
        error_type: str,
        error_message: str,
        duration_ms: float,
    ) -> None:
        """打印错误信息"""
        lines = []

        # 错误行
        lines.append(
            "  💥 "
            + self._color(f"{error_type}", Colors.BOLD + Colors.RED)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )
        lines.append(f"    {self._color(error_message, Colors.RED)}")

        # 分隔线
        separator = "─" * 60
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    # =========================================================================
    # 数据库事件处理（v3.22.1 新增）
    # =========================================================================

    def _handle_query_start(self, event) -> None:
        """处理数据库查询开始事件"""
        if not self.show_database:
            return

        correlation_id = getattr(event, "correlation_id", "")

        # 记录查询信息
        record = QueryRecord(
            correlation_id=correlation_id,
            operation=getattr(event, "operation", ""),
            table=getattr(event, "table", ""),
            sql=getattr(event, "sql", ""),
            params=dict(event.params) if getattr(event, "params", None) else {},
            database=getattr(event, "database", None),
        )
        self._pending_queries[correlation_id] = record

        # 输出查询信息
        self._print_query(record)

    def _handle_query_end(self, event) -> None:
        """处理数据库查询结束事件"""
        if not self.show_database:
            return

        correlation_id = getattr(event, "correlation_id", "")
        query = self._pending_queries.pop(correlation_id, None)

        duration_ms = getattr(event, "duration_ms", 0)
        row_count = getattr(event, "row_count", 0)

        # 输出查询结果
        self._print_query_result(
            operation=query.operation if query else "???",
            table=query.table if query else "???",
            duration_ms=duration_ms,
            row_count=row_count,
        )

    def _handle_query_error(self, event) -> None:
        """处理数据库查询错误事件"""
        if not self.show_database:
            return

        correlation_id = getattr(event, "correlation_id", "")
        query = self._pending_queries.pop(correlation_id, None)

        error_type = getattr(event, "error_type", "UnknownError")
        error_message = getattr(event, "error_message", "")
        duration_ms = getattr(event, "duration_ms", 0)

        # 输出错误信息
        self._print_query_error(
            operation=query.operation if query else "???",
            table=query.table if query else "???",
            error_type=error_type,
            error_message=error_message,
            duration_ms=duration_ms,
        )

    def _print_query(self, record: QueryRecord) -> None:
        """打印数据库查询信息"""
        lines = []

        # 分隔线和标题
        separator = "─" * 60
        lines.append("")
        lines.append(self._color(separator, Colors.DIM))

        # 操作类型图标
        op_icons = {
            "SELECT": "🔍",
            "INSERT": "➕",
            "UPDATE": "✏️",
            "DELETE": "🗑️",
        }
        icon = op_icons.get(record.operation.upper(), "📊")

        # 数据库名（如果有）
        db_info = f" [{record.database}]" if record.database else ""

        lines.append(
            self._color(f"{icon} {record.operation} ", Colors.BOLD + Colors.YELLOW)
            + self._color(record.table, Colors.YELLOW)
            + self._color(db_info, Colors.DIM)
        )

        # SQL
        if self.show_sql and record.sql:
            lines.append(self._color("  SQL:", Colors.GRAY))
            sql_str = self._format_sql(record.sql)
            for line in sql_str.split("\n"):
                lines.append(f"    {self._color(line, Colors.WHITE)}")

        # Params
        if self.show_sql_params and record.params:
            lines.append(self._color("  Params:", Colors.GRAY))
            for key, value in record.params.items():
                lines.append(f"    {self._color(str(key), Colors.MAGENTA)}: {value}")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_query_result(
        self,
        operation: str,
        table: str,
        duration_ms: float,
        row_count: int,
    ) -> None:
        """打印数据库查询结果"""
        lines = []

        # 结果行
        lines.append(
            "  ✅ "
            + self._color(f"{row_count} rows", Colors.BOLD + Colors.GREEN)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )

        # 分隔线
        separator = "─" * 60
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_query_error(
        self,
        operation: str,
        table: str,
        error_type: str,
        error_message: str,
        duration_ms: float,
    ) -> None:
        """打印数据库查询错误"""
        lines = []

        # 错误行
        lines.append(
            "  💥 "
            + self._color(f"{error_type}", Colors.BOLD + Colors.RED)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )
        lines.append(f"    {self._color(error_message, Colors.RED)}")

        # 分隔线
        separator = "─" * 60
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _format_sql(self, sql: str) -> str:
        """格式化 SQL 语句"""
        # 简单格式化：去除多余空白
        sql_str = " ".join(sql.split())

        # 截断
        if len(sql_str) > self.max_sql_length:
            sql_str = sql_str[: self.max_sql_length] + " ... (truncated)"

        return sql_str

    # =========================================================================
    # 通用辅助方法
    # =========================================================================

    def _color(self, text: str, color: str) -> str:
        """添加颜色"""
        if self.use_colors:
            return f"{color}{text}{Colors.RESET}"
        return text

    def _sanitize_value(self, key: str, value: str) -> str:
        """脱敏敏感值"""
        if key.lower() in self.SENSITIVE_FIELDS:
            if len(value) > 20:
                return value[:8] + "****" + value[-4:]
            return "****"
        return value

    def _format_body(self, body: str | dict | Any) -> str:
        """格式化 body"""
        if isinstance(body, dict):
            body_str = json.dumps(body, indent=2, ensure_ascii=False, default=str)
        elif isinstance(body, str):
            # 尝试格式化 JSON
            try:
                parsed = json.loads(body)
                body_str = json.dumps(parsed, indent=2, ensure_ascii=False, default=str)
            except (json.JSONDecodeError, TypeError):
                body_str = body
        else:
            body_str = str(body)

        # 截断
        if len(body_str) > self.max_body_length:
            body_str = body_str[: self.max_body_length] + "\n... (truncated)"

        return body_str

    def _output(self, text: str) -> None:
        """输出到控制台

        v3.28.0: 调试输出始终直接输出到 stderr，不走 pytest 桥接。
        原因：调试输出有自己的格式化（彩色、分隔线），不应被 pytest log_cli_format 破坏。
        """
        # 直接输出到 stderr，保持调试输出的完整格式
        print(text, file=sys.stderr)
        if self.output_to_logger:
            logger.debug(text)


# 创建默认实例的便捷函数
def create_console_debugger(
    show_headers: bool = True,
    show_body: bool = True,
    show_params: bool = True,
    max_body_length: int = 500,
    # v3.22.1: 数据库调试选项
    show_database: bool = True,
    show_sql: bool = True,
    show_sql_params: bool = True,
    max_sql_length: int = 500,
) -> ConsoleDebugObserver:
    """创建控制台调试器

    Args:
        show_headers: 是否显示请求/响应头
        show_body: 是否显示请求/响应体
        show_params: 是否显示 GET 参数
        max_body_length: 最大 body 显示长度
        show_database: 是否显示数据库查询（v3.22.1 新增）
        show_sql: 是否显示 SQL 语句（v3.22.1 新增）
        show_sql_params: 是否显示 SQL 参数（v3.22.1 新增）
        max_sql_length: 最大 SQL 显示长度（v3.22.1 新增）

    Returns:
        ConsoleDebugObserver 实例
    """
    return ConsoleDebugObserver(
        show_headers=show_headers,
        show_body=show_body,
        show_params=show_params,
        max_body_length=max_body_length,
        show_database=show_database,
        show_sql=show_sql,
        show_sql_params=show_sql_params,
        max_sql_length=max_sql_length,
    )


__all__ = [
    "ConsoleDebugObserver",
    "create_console_debugger",
    "Colors",
    "QueryRecord",
]
