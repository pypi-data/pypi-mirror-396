from pathlib import Path

import click
from nb_cli.cli import CLI_DEFAULT_STYLE, ClickAliasedCommand, run_async
from noneprompt import (
    CancelledError,
    Choice,
    ConfirmPrompt,
    ListPrompt,
)

from ..handlers.create import (
    GitInstallHelp,
    check_path,
    check_python_version,
    install_dependencies,
    run_download_install,
    run_git_install,
    setting_env,
)


@click.command(
    cls=ClickAliasedCommand,
    aliases=["new", "init"],
    context_settings={"ignore_unknown_options": True},
    help="在当前目录下安装小真寻.",
)
@click.option(
    "-p",
    "--python-interpreter",
    default=None,
    help="指定Python解释器的路径",
)
@click.option(
    "-i",
    "--index-url",
    "index_url",
    default="https://mirrors.aliyun.com/pypi/simple/",
    help="pip下载所使用的镜像源",
)
@click.pass_context
@run_async
async def create(
    ctx: click.Context,
    python_interpreter: str | None,
    index_url: str,
):
    """在当前目录下安装小真寻."""
    try:
        click.clear()
        click.secho("正在检测python版本...", fg="yellow")
        if not check_python_version():
            click.secho(
                "当前python版本过低，python版本至少需要3.10及以上！", fg="yellow"
            )
            ctx.exit()
        install_choice = await ListPrompt(
            "需要使用哪种安装方式?",
            [
                Choice("git安装", "git"),
                Choice("下载安装", "download"),
            ],
            default_select=0,
        ).prompt_async(style=CLI_DEFAULT_STYLE)
        if install_choice.data == "git" and not await GitInstallHelp.check_git():
            click.secho("未检测到git，请先安装git...", fg="yellow")
            ctx.exit()
        project_name = await check_path(ctx)
        if not project_name:
            click.secho("获取项目名称...", fg="yellow")
            ctx.exit()
        if not project_name.endswith("[use]"):
            click.secho(f"开始安装({install_choice.name})小真寻...", fg="yellow")
            if install_choice.data == "download":
                await run_download_install(ctx, project_name)
            else:
                await run_git_install(ctx, project_name)
        project_name = project_name.replace("[use]", "")
        await setting_env(ctx, project_name)
        is_install_dependencies = await ConfirmPrompt(
            "是否立刻安装依赖?",
            default_choice=True,
        ).prompt_async(style=CLI_DEFAULT_STYLE)
        if is_install_dependencies:
            proc = await install_dependencies(
                project_name, python_interpreter, ["-i", index_url]
            )
            await proc.wait()
            click.secho("安装小真寻依赖完成！", fg="yellow")
        if not (Path() / project_name).is_dir():
            ctx.exit()

        if is_install_dependencies:
            click.secho(
                f"一切准备就绪，请使用命令\ncd {project_name}(安装的项目名称)\n"
                "poetry run python bot.py\n"
                "或\n"
                "nb zx start\n"
                "启动小真寻吧！",
                fg="yellow",
            )
        else:
            click.secho(
                "请在手动安装环境（项目根目录，命令: poetry install）后\n"
                f"cd {project_name}(安装的项目名称)\n"
                "poetry run python bot.py\n"
                "或\n"
                "nb zx start\n"
                "启动小真寻吧！",
                fg="yellow",
            )

    except CancelledError:
        ctx.exit()
