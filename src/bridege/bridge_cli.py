"""桥接服务命令。"""

from __future__ import annotations

import asyncio

import click

from .bridge_server import BridgeServer


@click.group(name="bridge")
def bridge_group() -> None:
    """桥接服务相关命令。"""


@bridge_group.command("serve")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8765, type=int, show_default=True)
def bridge_serve(host: str, port: int) -> None:
    """启动本地桥接服务。"""
    asyncio.run(BridgeServer().serve_forever(host, port))
