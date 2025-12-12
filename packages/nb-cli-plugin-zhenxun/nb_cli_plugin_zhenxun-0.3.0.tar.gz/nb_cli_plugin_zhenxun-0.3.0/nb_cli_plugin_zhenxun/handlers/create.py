import asyncio
import os
from pathlib import Path
import shutil
import stat
import sys

import click
from nb_cli.cli import CLI_DEFAULT_STYLE
from nb_cli.cli.commands.project import project_name_validator
from nb_cli.handlers import get_default_python
from noneprompt import Choice, InputPrompt, ListPrompt

from ..utils.download_help import DownloadInstallHelp
from ..utils.git_help import GitInstallHelp


def check_python_version():
    """
    检查 python 版本
    """
    return sys.version_info >= (3, 10)


async def check_path(ctx: click.Context) -> str:
    """路径检测

    参数:
        ctx: ctx

    返回:
        str: 项目名称
    """
    project_name = await InputPrompt(
        "项目名称:",
        default_text="zhenxun_bot",
        validator=project_name_validator,
    ).prompt_async(style=CLI_DEFAULT_STYLE)
    while True:
        project_path = Path() / project_name
        if project_path.is_dir():
            dir_choice = await ListPrompt(
                "当前目录下已存在同名项目文件夹，如何操作?",
                [
                    Choice("删除该文件夹并重新安装", "delete"),
                    Choice("使用该文件夹继续", "use"),
                    Choice("重新命名", "rename"),
                    Choice("取消安装", "exit"),
                ],
                default_select=0,
            ).prompt_async(style=CLI_DEFAULT_STYLE)
            if dir_choice.data == "rename":
                pass
            elif dir_choice.data == "use":
                return f"{project_name}[use]"
            elif dir_choice.data == "delete":

                def delete(func, path_, execinfo):
                    os.chmod(path_, stat.S_IWUSR)
                    func(path_)

                shutil.rmtree((project_path).absolute(), onerror=delete)
                await asyncio.sleep(0.2)
                return project_name
            else:
                ctx.exit()
        else:
            return project_name


async def run_git_install(ctx: click.Context, project_name: str):
    await GitInstallHelp.start_clone(ctx, project_name)


async def run_download_install(ctx: click.Context, project_name: str):
    await DownloadInstallHelp.download_install(ctx, project_name)


async def setting_env(ctx: click.Context, project_name: str):
    """设置配置文件

    参数:
        ctx: ctx
        project_name: 项目名称
    """
    project_path = Path() / project_name
    env_path = project_path / ".env.dev"
    if not env_path.is_file():
        example_env_path = project_path / ".env.example"
        if example_env_path.is_file():
            env_path.write_text(
                example_env_path.read_text(
                    encoding="utf-8",
                ),
                encoding="utf-8",
            )
        else:
            click.secho("未检测到.env.example文件，请手动创建.env.dev文件", fg="red")
            ctx.exit()

    env_file = env_path.read_text(
        encoding="utf-8",
    )
    superusers = await InputPrompt(
        "超级用户QQ(即你自己的QQ号，多个用空格隔开):",
        validator=lambda x: x.replace(" ", "").isdigit(),
    ).prompt_async(style=CLI_DEFAULT_STYLE)
    if superusers := superusers.replace(" ", '", "'):
        env_file = env_file.replace(
            'SUPERUSERS=[""]',
            f'SUPERUSERS=["{superusers}"]',
        )

    db_url = await InputPrompt(
        "请输入数据库连接地址（为空则使用sqlite）:",
    ).prompt_async(style=CLI_DEFAULT_STYLE)
    if not db_url:
        (project_path / "data" / "db").mkdir(parents=True, exist_ok=True)
        db_url = "sqlite:data/db/zhenxun.db"
        env_file = env_file.replace(
            'DB_URL = ""',
            f'DB_URL = "{db_url}"',
        )

    env_path.write_text(
        env_file,
        encoding="utf-8",
    )


async def install_poetry(
    project_path: Path,
    python_path: str,
    pip_args: list[str] | None = None,
):
    """
    安装包
    """
    if pip_args is None:
        pip_args = []
    return await asyncio.create_subprocess_exec(
        python_path,
        "-m",
        "pip",
        "install",
        "poetry",
        *pip_args,
        cwd=project_path.absolute(),
    )


async def install_package(
    project_path: Path,
    python_path: str,
    package: str,
    pip_args: list[str] | None = None,
):
    """
    安装包
    """
    if pip_args is None:
        pip_args = []
    return await asyncio.create_subprocess_exec(
        python_path,
        "-m",
        "poetry",
        "run",
        "pip",
        "install",
        package,
        *pip_args,
        cwd=project_path.absolute(),
    )


async def install_dependencies(
    project_name: str,
    python_path: str | None,
    pip_args: list[str] | None = None,
):
    if pip_args is None:
        pip_args = []
    if python_path is None:
        python_path = await get_default_python()
    project_path = Path() / project_name
    click.secho("开始安装Poetry包管理器...", fg="yellow")
    proc = await install_poetry(project_path, python_path, pip_args)
    await proc.wait()
    click.secho("Poetry包管理器安装完成！", fg="yellow")
    click.secho("开始在依赖环境中安装nb-cli...", fg="yellow")
    proc = await install_package(project_path, python_path, "nb-cli", pip_args)
    await proc.wait()
    click.secho("依赖环境中nb-cli安装完成！", fg="yellow")
    click.secho("开始在依赖环境中安装nb-cli-plugin-zhenxun...", fg="yellow")
    proc = await install_package(
        project_path, python_path, "nb-cli-plugin-zhenxun", pip_args
    )
    await proc.wait()
    click.secho("依赖环境中安装nb-cli-plugin-zhenxun安装完成！", fg="yellow")
    click.secho("开始在依赖环境中安poetry...", fg="yellow")
    proc = await install_package(project_path, python_path, "poetry", pip_args)
    await proc.wait()
    click.secho("依赖环境中poetry安装完成！", fg="yellow")
    click.secho("开始尝试安装小真寻依赖...", fg="yellow")
    return await asyncio.create_subprocess_exec(
        python_path,
        "-m",
        "poetry",
        "install",
        cwd=project_path.absolute(),
    )
