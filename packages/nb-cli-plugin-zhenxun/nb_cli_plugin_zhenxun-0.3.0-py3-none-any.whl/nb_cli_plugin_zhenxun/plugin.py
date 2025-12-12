from typing import cast

from nb_cli.cli import CLIMainGroup, cli

from .cli import zhenxun


def main():
    cli_ = cast(CLIMainGroup, cli)
    cli_.add_command(zhenxun)
    cli_.add_aliases("zhenxun", ["zx"])


if __name__ == "main":
    main()
