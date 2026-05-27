"""浏览器命令执行入口。

这里集中放 Click 上下文读取、桥接命令执行、页面 JS 执行等公共逻辑，
避免每个命令模块都重复写同样的样板代码。
"""

from __future__ import annotations

import click

from bridege.bridge_client import BridgeContext, print_result, request_bridge_sync, run_js_sync


def get_browser_context(ctx: click.Context) -> BridgeContext:
    """从 Click 上下文中恢复当前浏览器会话信息。"""
    obj = ctx.obj or {}
    return BridgeContext(session=obj["session"], host=obj["host"], port=obj["port"])


def run_browser_command(ctx: click.Context, command: object) -> None:
    """执行结构化桥接命令并输出统一结果。"""
    print_result(request_bridge_sync(get_browser_context(ctx), command))


def run_browser_js_command(ctx: click.Context, js_code: str) -> None:
    """执行页面内 JS 代码并输出统一结果。"""
    print_result(run_js_sync(get_browser_context(ctx), js_code))
