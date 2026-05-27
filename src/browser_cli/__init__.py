"""浏览器命令包入口。

这个包负责组织 `browser` 命令组，并按模块注册具体子命令。
"""

from __future__ import annotations

import click

from .browser_cli_dialog import register_dialog_commands
from .browser_cli_get import register_get_commands
from .browser_cli_interact import register_interact_commands
from .browser_cli_misc import register_misc_commands
from .browser_cli_tab import register_tab_commands


@click.group(name="browser")
@click.argument("session")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8765, type=int, show_default=True)
@click.pass_context
def browser_group(ctx: click.Context, session: str, host: str, port: int) -> None:
    """浏览器命令，所有操作都绑定到一个命名会话。"""
    ctx.obj = {"session": session, "host": host, "port": port}


# 按职责逐块注册命令，后续新增能力时只改对应模块即可。
register_misc_commands(browser_group)
register_get_commands(browser_group)
register_interact_commands(browser_group)
register_tab_commands(browser_group)
register_dialog_commands(browser_group)
