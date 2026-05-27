"""弹窗相关命令。"""

from __future__ import annotations

import click

from browser_runner import run_browser_js_command


def register_dialog_commands(browser_group: click.Group) -> None:
    """注册 `browser dialog` 子命令组。"""

    @browser_group.group("dialog")
    def browser_dialog() -> None:
        """浏览器弹窗相关操作。"""

    @browser_dialog.command("accept")
    @click.option("--text")
    @click.pass_context
    def browser_dialog_accept(ctx: click.Context, text: str | None) -> None:
        js_code = f"(() => {{ if (window.__opencli_handle_dialog) window.__opencli_handle_dialog('accept', {text!r}); return true; }})()"
        run_browser_js_command(ctx, js_code)

    @browser_dialog.command("dismiss")
    @click.pass_context
    def browser_dialog_dismiss(ctx: click.Context) -> None:
        js_code = "(() => { if (window.__opencli_handle_dialog) window.__opencli_handle_dialog('dismiss'); return true; })()"
        run_browser_js_command(ctx, js_code)
