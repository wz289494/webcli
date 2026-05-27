"""标签页相关命令。"""

from __future__ import annotations

import click

from browser_actions import tabs
from browser_runner import get_browser_context, run_browser_command


def register_tab_commands(browser_group: click.Group) -> None:
    """注册 `browser tab` 子命令组。"""

    @browser_group.group("tab")
    def browser_tab() -> None:
        """标签页管理。"""

    @browser_tab.command("list")
    @click.pass_context
    def browser_tab_list(ctx: click.Context) -> None:
        run_browser_command(ctx, tabs(get_browser_context(ctx).session, "list"))

    @browser_tab.command("new")
    @click.argument("url", required=False)
    @click.pass_context
    def browser_tab_new(ctx: click.Context, url: str | None) -> None:
        run_browser_command(ctx, tabs(get_browser_context(ctx).session, "new", url=url))

    @browser_tab.command("select")
    @click.option("--page")
    @click.option("--index", type=int)
    @click.pass_context
    def browser_tab_select(ctx: click.Context, page: str | None, index: int | None) -> None:
        run_browser_command(ctx, tabs(get_browser_context(ctx).session, "select", page=page, index=index))

    @browser_tab.command("close")
    @click.option("--page")
    @click.option("--index", type=int)
    @click.pass_context
    def browser_tab_close(ctx: click.Context, page: str | None, index: int | None) -> None:
        run_browser_command(ctx, tabs(get_browser_context(ctx).session, "close", page=page, index=index))
