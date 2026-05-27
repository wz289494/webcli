"""浏览器桥接协议模型。

这里定义 CLI 与浏览器扩展之间传输的命令和返回结果，
让 WebSocket 上传递的 JSON 结构集中在一个地方维护。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal
from uuid import uuid4

Action = Literal[
    "exec",
    "navigate",
    "tabs",
    "cookies",
    "screenshot",
    "close-window",
    "sessions",
    "set-file-input",
    "insert-text",
    "bind",
    "network-capture-start",
    "network-capture-read",
    "wait-download",
    "cdp",
    "frames",
]
TabOp = Literal["list", "new", "close", "select"]
WindowMode = Literal["foreground", "background"]
Surface = Literal["browser"]


@dataclass(slots=True)
class Command:
    """发给桥接层或扩展的命令模型。"""

    id: str
    action: Action
    page: str | None = None
    code: str | None = None
    session: str | None = None
    surface: Surface = "browser"
    url: str | None = None
    op: TabOp | None = None
    index: int | None = None
    domain: str | None = None
    format: Literal["png", "jpeg"] | None = None
    quality: int | None = None
    fullPage: bool | None = None
    width: int | None = None
    height: int | None = None
    files: list[str] | None = None
    selector: str | None = None
    text: str | None = None
    pattern: str | None = None
    timeoutMs: int | None = None
    cdpMethod: str | None = None
    cdpParams: dict[str, Any] | None = None
    windowMode: WindowMode | None = None
    idleTimeout: int | None = None
    frameIndex: int | None = None
    contextId: str | None = None

    def to_payload(self) -> dict[str, Any]:
        """去掉空字段，保持线上协议负载简洁稳定。"""
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass(slots=True)
class Result:
    """桥接层返回给 CLI 的统一结果模型。"""

    id: str
    ok: bool
    data: Any = None
    error: str | None = None
    errorCode: str | None = None
    errorHint: str | None = None
    page: str | None = None

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Result":
        """把任意 JSON 载荷规整成结果对象。"""
        return cls(
            id=str(payload.get("id", "")),
            ok=bool(payload.get("ok", False)),
            data=payload.get("data"),
            error=payload.get("error"),
            errorCode=payload.get("errorCode"),
            errorHint=payload.get("errorHint"),
            page=payload.get("page"),
        )


def make_command(action: Action, **kwargs: Any) -> Command:
    """创建带唯一请求 id 的命令对象。"""
    return Command(id=f"cmd_{uuid4().hex}", action=action, **kwargs)
