import asyncio
from pathlib import Path

import click
from nb_cli.cli import ClickAliasedCommand, run_async
from nb_cli.handlers import (
    get_default_python,
    register_signal_handler,
    remove_signal_handler,
    terminate_process,
)


@click.command(
    cls=ClickAliasedCommand,
    aliases=["start"],
    context_settings={"ignore_unknown_options": True},
    help="启动小真寻.",
)
@click.option("-d", "--cwd", default=".", help="指定工作目录.")
@click.option(
    "-p",
    "--python-interpreter",
    default=None,
    help="指定Python解释器的路径",
)
@click.pass_context
@run_async
async def run(ctx: click.Context, cwd: str, python_interpreter: str | None):
    project_path = Path(cwd)
    if not (
        (project_path / "zhenxun").is_dir() and (project_path / "bot.py").is_file()
    ):
        click.secho("未检测到该目录下有小真寻，请确保目录无误", fg="red")
        ctx.exit()

    should_exit = asyncio.Event()

    def shutdown(signum, frame):
        should_exit.set()

    register_signal_handler(shutdown)

    async def wait_for_exit():
        await should_exit.wait()
        await terminate_process(proc)

    python_path = python_interpreter or await get_default_python()

    proc = await asyncio.create_subprocess_exec(
        python_path,
        "-m",
        *["poetry", "run", "python", "bot.py"],
        cwd=cwd,
    )
    task = asyncio.create_task(wait_for_exit())
    await proc.wait()
    should_exit.set()
    await task
    remove_signal_handler(shutdown)
