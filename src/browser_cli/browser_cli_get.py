"""页面读取类命令。"""

from __future__ import annotations

import click

from browser_runner import run_browser_js_command
from browser_js import js_attributes, js_html, js_text, js_value


def register_get_commands(browser_group: click.Group) -> None:
    """注册 `browser get` 子命令组。"""

    @browser_group.group("get")
    def browser_get() -> None:
        """读取页面属性。"""

    @browser_get.command("title")
    @click.pass_context
    def browser_get_title(ctx: click.Context) -> None:
        run_browser_js_command(ctx, "document.title")

    @browser_get.command("url")
    @click.pass_context
    def browser_get_url(ctx: click.Context) -> None:
        run_browser_js_command(ctx, "location.href")

    @browser_get.command("text")
    @click.option("--css", required=True)
    @click.pass_context
    def browser_get_text(ctx: click.Context, css: str) -> None:
        run_browser_js_command(ctx, js_text(css))

    @browser_get.command("value")
    @click.option("--css", required=True)
    @click.pass_context
    def browser_get_value(ctx: click.Context, css: str) -> None:
        run_browser_js_command(ctx, js_value(css))

    @browser_get.command("attributes")
    @click.option("--css", required=True)
    @click.pass_context
    def browser_get_attributes(ctx: click.Context, css: str) -> None:
        run_browser_js_command(ctx, js_attributes(css))

    @browser_get.command("html")
    @click.option("--css")
    @click.pass_context
    def browser_get_html(ctx: click.Context, css: str | None) -> None:
        run_browser_js_command(ctx, js_html(css))
