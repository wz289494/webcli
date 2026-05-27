"""CLI 侧桥接客户端。

这里封装 WebSocket 请求、结果输出和同步运行辅助函数，
让 Click 命令处理函数只关心“调用什么动作”。
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass

import click
import websockets

from protocol import Command, Result
from browser_actions import exec_js


@dataclass(slots=True)
class BridgeContext:
    """浏览器命令执行时共享的上下文。"""

    session: str
    host: str
    port: int


def print_result(result: Result) -> None:
    """统一输出结果结构，方便终端和脚本消费。"""
    payload = {"id": result.id, "ok": result.ok, "page": result.page}
    if result.ok:
        payload["data"] = result.data
    else:
        payload["error"] = result.error
        payload["errorCode"] = result.errorCode
        payload["errorHint"] = result.errorHint
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2))


async def request_bridge(host: str, port: int, command: Command, timeout: float = 30.0) -> Result:
    """向桥接服务发送一条命令并等待单次返回。"""
    uri = f"ws://{host}:{port}"
    envelope = {
        "type": "command",
        "timeout": timeout,
        "command": command.to_payload(),
    }
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(envelope, ensure_ascii=False))
        raw = await asyncio.wait_for(websocket.recv(), timeout=timeout + 1)
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        payload = json.loads(raw)
        return Result.from_payload(payload.get("result") or {})


async def run_js(host: str, port: int, session: str, js: str, timeout: float = 30.0) -> Result:
    """通过通用 exec 动作在页面上下文执行 JS。"""
    return await request_bridge(host, port, exec_js(session, js), timeout=timeout)


def request_bridge_sync(context: BridgeContext, command: Command, timeout: float = 30.0) -> Result:
    """给 Click 命令使用的同步封装。"""
    return asyncio.run(request_bridge(context.host, context.port, command, timeout=timeout))


def run_js_sync(context: BridgeContext, js: str, timeout: float = 30.0) -> Result:
    """同步执行页面 JS，避免在每个命令函数里重复 asyncio.run。"""
    return asyncio.run(run_js(context.host, context.port, context.session, js, timeout=timeout))
