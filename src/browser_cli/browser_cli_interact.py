"""页面交互类命令。"""

from __future__ import annotations

import json
import time

import click

from browser_runner import get_browser_context, print_result, run_browser_js_command
from bridege.bridge_client import run_js_sync
from browser_js import (
    js_check,
    js_click,
    js_dblclick,
    js_focus,
    js_hover,
    js_scroll,
    js_select,
    js_set_value,
    js_wait_selector,
    js_wait_text,
)
from protocol import Result


def register_interact_commands(browser_group: click.Group) -> None:
    """注册点击、输入、拖拽等交互命令。"""

    @browser_group.command("click")
    @click.option("--css", required=True)
    @click.pass_context
    def browser_click(ctx: click.Context, css: str) -> None:
        run_browser_js_command(ctx, js_click(css))

    @browser_group.command("type")
    @click.option("--css", required=True)
    @click.argument("text")
    @click.pass_context
    def browser_type(ctx: click.Context, css: str, text: str) -> None:
        run_browser_js_command(ctx, js_set_value(css, text, mode="typed"))

    @browser_group.command("fill")
    @click.option("--css", required=True)
    @click.argument("text")
    @click.pass_context
    def browser_fill(ctx: click.Context, css: str, text: str) -> None:
        run_browser_js_command(ctx, js_set_value(css, text, mode="filled"))

    @browser_group.command("select")
    @click.option("--css", required=True)
    @click.argument("value")
    @click.pass_context
    def browser_select(ctx: click.Context, css: str, value: str) -> None:
        run_browser_js_command(ctx, js_select(css, value))

    @browser_group.command("keys")
    @click.argument("key")
    @click.pass_context
    def browser_keys(ctx: click.Context, key: str) -> None:
        js_code = (
            "(() => { document.dispatchEvent(new KeyboardEvent('keydown', "
            f"{{ key: {key!r}, bubbles: true }})); return {{ pressed: true, key: {key!r} }}; }})()"
        )
        run_browser_js_command(ctx, js_code)

    @browser_group.command("wait")
    @click.argument("kind", type=click.Choice(["time", "text", "selector"]))
    @click.argument("value")
    @click.option("--timeout", default=10.0, type=float, show_default=True)
    @click.pass_context
    def browser_wait(ctx: click.Context, kind: str, value: str, timeout: float) -> None:
        if kind == "time":
            seconds = float(value)
            time.sleep(seconds)
            click.echo(json.dumps({"waited": seconds}, ensure_ascii=False, indent=2))
            return

        deadline = time.time() + timeout
        while time.time() < deadline:
            # 暂时用轮询等待，保证实现简单；
            # 未来如果桥接层支持原生等待，这里可直接替换。
            js_code = js_wait_text(value) if kind == "text" else js_wait_selector(value)
            result = run_js_sync(get_browser_context(ctx), js_code)
            if result.ok and result.data is True:
                print_result(Result(id=result.id, ok=True, data={"matched": True, "kind": kind, "value": value}, page=result.page))
                return
            time.sleep(0.5)
        print_result(Result(id="wait-timeout", ok=False, error=f"{kind} not observed before timeout", errorCode="wait_timeout"))

    @browser_group.command("scroll")
    @click.argument("direction", type=click.Choice(["up", "down"]))
    @click.option("--amount", default=500, type=int, show_default=True)
    @click.pass_context
    def browser_scroll(ctx: click.Context, direction: str, amount: int) -> None:
        run_browser_js_command(ctx, js_scroll(direction, amount))

    @browser_group.command("hover")
    @click.option("--css", required=True)
    @click.pass_context
    def browser_hover(ctx: click.Context, css: str) -> None:
        run_browser_js_command(ctx, js_hover(css))

    @browser_group.command("focus")
    @click.option("--css", required=True)
    @click.pass_context
    def browser_focus(ctx: click.Context, css: str) -> None:
        run_browser_js_command(ctx, js_focus(css))

    @browser_group.command("dblclick")
    @click.option("--css", required=True)
    @click.pass_context
    def browser_dblclick(ctx: click.Context, css: str) -> None:
        run_browser_js_command(ctx, js_dblclick(css))

    @browser_group.command("check")
    @click.option("--css", required=True)
    @click.pass_context
    def browser_check(ctx: click.Context, css: str) -> None:
        run_browser_js_command(ctx, js_check(css, True))

    @browser_group.command("uncheck")
    @click.option("--css", required=True)
    @click.pass_context
    def browser_uncheck(ctx: click.Context, css: str) -> None:
        run_browser_js_command(ctx, js_check(css, False))

    @browser_group.command("upload")
    @click.option("--css", required=True)
    @click.argument("files", nargs=-1, type=click.Path(exists=True, dir_okay=False))
    @click.pass_context
    def browser_upload(ctx: click.Context, css: str, files: tuple[str, ...]) -> None:
        js_code = f"(() => {{ return {{ warning: 'set-file-input action should be implemented by the paired extension', selector: {css!r}, files: {list(files)!r} }}; }})()"
        run_browser_js_command(ctx, js_code)

    @browser_group.command("drag")
    @click.option("--from-css", required=True)
    @click.option("--to-css", required=True)
    @click.pass_context
    def browser_drag(ctx: click.Context, from_css: str, to_css: str) -> None:
        js_code = (
            "(() => { const from = document.querySelector(" + repr(from_css) + "); "
            "const to = document.querySelector(" + repr(to_css) + "); "
            "if (!from || !to) return { error: 'selector_not_found' }; "
            "to.dispatchEvent(new DragEvent('drop', { bubbles: true })); "
            "return { dragged: true, from: " + repr(from_css) + ", to: " + repr(to_css) + " }; })()"
        )
        run_browser_js_command(ctx, js_code)
