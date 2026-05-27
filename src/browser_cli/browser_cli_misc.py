"""其余浏览器命令。

这里放不属于读取、交互、标签页、弹窗分组的命令，
比如导航、截图、网络、Cookie、CDP 等。
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

import click

from browser_actions import bind, cdp, close_window, cookies, frames, navigate, screenshot
from browser_runner import get_browser_context, print_result, request_bridge_sync, run_browser_command, run_browser_js_command
from browser_js import js_analyze, js_console, js_extract, js_find, js_network, js_state


def register_misc_commands(browser_group: click.Group) -> None:
    """注册不适合单独再开文件夹的一般命令。"""

    @browser_group.command("open")
    @click.argument("url")
    @click.pass_context
    def browser_open(ctx: click.Context, url: str) -> None:
        run_browser_command(ctx, navigate(get_browser_context(ctx).session, url))

    @browser_group.command("state")
    @click.pass_context
    def browser_state(ctx: click.Context) -> None:
        run_browser_js_command(ctx, js_state())

    @browser_group.command("find")
    @click.option("--css", required=True)
    @click.option("--limit", default=50, type=int, show_default=True)
    @click.pass_context
    def browser_find(ctx: click.Context, css: str, limit: int) -> None:
        run_browser_js_command(ctx, js_find(css, limit))

    @browser_group.command("extract")
    @click.option("--css")
    @click.pass_context
    def browser_extract(ctx: click.Context, css: str | None) -> None:
        run_browser_js_command(ctx, js_extract(css))

    @browser_group.command("frames")
    @click.pass_context
    def browser_frames(ctx: click.Context) -> None:
        run_browser_command(ctx, frames(get_browser_context(ctx).session))

    @browser_group.command("screenshot")
    @click.argument("path", required=False)
    @click.option("--full-page", is_flag=True)
    @click.option("--width", type=int)
    @click.option("--height", type=int)
    @click.pass_context
    def browser_screenshot(ctx: click.Context, path: str | None, full_page: bool, width: int | None, height: int | None) -> None:
        context = get_browser_context(ctx)
        command, output = screenshot(context.session, path, full_page=full_page, width=width, height=height)
        result = request_bridge_sync(context, command)
        if result.ok and output and isinstance(result.data, str):
            # 扩展回传的是 base64 图片，CLI 负责决定是否保存到文件。
            Path(output).write_bytes(base64.b64decode(result.data))
            click.echo(json.dumps({"saved": output}, ensure_ascii=False, indent=2))
            return
        print_result(result)

    @browser_group.command("back")
    @click.pass_context
    def browser_back(ctx: click.Context) -> None:
        run_browser_js_command(ctx, "history.back(); true")

    @browser_group.command("eval")
    @click.argument("js")
    @click.pass_context
    def browser_eval(ctx: click.Context, js: str) -> None:
        run_browser_js_command(ctx, js)

    @browser_group.command("network")
    @click.pass_context
    def browser_network(ctx: click.Context) -> None:
        run_browser_js_command(ctx, js_network())

    @browser_group.command("close")
    @click.pass_context
    def browser_close(ctx: click.Context) -> None:
        run_browser_command(ctx, close_window(get_browser_context(ctx).session))

    @browser_group.command("bind")
    @click.pass_context
    def browser_bind(ctx: click.Context) -> None:
        run_browser_command(ctx, bind(get_browser_context(ctx).session))

    @browser_group.command("unbind")
    @click.pass_context
    def browser_unbind(ctx: click.Context) -> None:
        run_browser_command(ctx, close_window(get_browser_context(ctx).session))

    @browser_group.command("console")
    @click.pass_context
    def browser_console(ctx: click.Context) -> None:
        run_browser_js_command(ctx, js_console())

    @browser_group.command("analyze")
    @click.pass_context
    def browser_analyze(ctx: click.Context) -> None:
        run_browser_js_command(ctx, js_analyze())

    @browser_group.command("cookies")
    @click.option("--domain")
    @click.pass_context
    def browser_cookies(ctx: click.Context, domain: str | None) -> None:
        run_browser_command(ctx, cookies(get_browser_context(ctx).session, domain=domain))

    @browser_group.command("cdp")
    @click.argument("method")
    @click.option("--params", default="{}", show_default=True)
    @click.pass_context
    def browser_cdp(ctx: click.Context, method: str, params: str) -> None:
        run_browser_command(ctx, cdp(get_browser_context(ctx).session, method, json.loads(params)))

    @browser_group.command("init")
    @click.argument("name")
    def browser_init(name: str) -> None:
        click.echo(json.dumps({"todo": "当前版本只聚焦浏览器能力，未包含适配器脚手架", "name": name}, ensure_ascii=False, indent=2))

    @browser_group.command("verify")
    @click.argument("name")
    def browser_verify(name: str) -> None:
        click.echo(json.dumps({"todo": "当前版本只聚焦浏览器能力，未包含适配器校验", "name": name}, ensure_ascii=False, indent=2))
