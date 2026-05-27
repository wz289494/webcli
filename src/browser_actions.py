"""桥接层原生命令工厂。

这类函数生成的是给扩展/桥接服务识别的结构化命令，
与页面内直接执行的 JS 片段分开维护。
"""

from __future__ import annotations

from typing import Any

from protocol import Command, make_command


def navigate(session: str, url: str) -> Command:
    """导航到目标 URL。"""
    return make_command("navigate", session=session, url=url)


def bind(session: str) -> Command:
    """把当前活动页绑定到指定会话。"""
    return make_command("bind", session=session)


def close_window(session: str) -> Command:
    """关闭或解绑当前会话窗口。"""
    return make_command("close-window", session=session)


def frames(session: str) -> Command:
    """列出当前页面的 frame 信息。"""
    return make_command("frames", session=session)


def tabs(session: str, op: str, *, page: str | None = None, index: int | None = None, url: str | None = None) -> Command:
    """创建标签页管理相关命令。"""
    return make_command("tabs", session=session, op=op, page=page, index=index, url=url)


def screenshot(session: str, path: str | None, *, full_page: bool, width: int | None, height: int | None) -> tuple[Command, str | None]:
    """请求截图，并把本地输出路径一起返回给调用方。"""
    command = make_command(
        "screenshot",
        session=session,
        format="png",
        fullPage=full_page,
        width=width,
        height=height,
    )
    return command, path


def cookies(session: str, *, domain: str | None = None) -> Command:
    """读取 Cookie。"""
    return make_command("cookies", session=session, domain=domain)


def cdp(session: str, method: str, params: dict[str, Any]) -> Command:
    """透传 CDP 调用。"""
    return make_command("cdp", session=session, cdpMethod=method, cdpParams=params)


def exec_js(session: str, code: str, *, page: str | None = None) -> Command:
    """在页面上下文执行原始 JavaScript。"""
    return make_command("exec", session=session, page=page, code=code)
