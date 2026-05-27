"""WebCLI 标准打包入口。"""

from __future__ import annotations

import click

from bridege.bridge_cli import bridge_group
from browser_cli import browser_group


@click.group()
def main() -> None:
    """轻量版 WebCLI 浏览器命令行工具。"""


main.add_command(bridge_group)
main.add_command(browser_group)


if __name__ == "__main__":
    main()
