import asyncio

import click
from nb_cli.cli import CLI_DEFAULT_STYLE
from noneprompt import (
    Choice,
    ListPrompt,
)


class GitInstallHelp:
    @classmethod
    async def check_git(cls) -> bool:
        """
        检查环境变量中是否存在 git
        """
        process = await asyncio.create_subprocess_shell(
            "git --version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()
        return bool(stdout)

    @classmethod
    async def __clone_zhenxun(cls, git_url: str, dir_name: str = "zhenxun_bot"):
        """克隆项目

        参数:
            git_url: git仓库地址
            dir_name: 要存放的文件夹名
        """
        return await asyncio.create_subprocess_exec(
            "git",
            "clone",
            "--depth=1",
            "--single-branch",
            git_url,
            dir_name,
        )

    @classmethod
    async def start_clone(cls, ctx: click.Context, project_name: str):
        """克隆项目

        参数:
            ctx: ctx
            project_name: 项目文件夹名称
        """
        git_url = await ListPrompt(
            "要使用的克隆源?",
            [
                Choice(
                    "github官方源(国外推荐)",
                    "https://github.com/HibiKier/zhenxun_bot",
                ),
                Choice(
                    "cherishmoon镜像源(国内推荐)",
                    "https://github.cherishmoon.fun/https://github.com/HibiKier/zhenxun_bot",
                ),
                Choice(
                    "ghproxy镜像源(国内备选1)",
                    "https://ghproxy.com/https://github.com/HibiKier/zhenxun_bot",
                ),
            ],
            default_select=1,
        ).prompt_async(style=CLI_DEFAULT_STYLE)
        click.secho(f"在 {project_name} 文件夹克隆源码...", fg="yellow")
        clone_result = await cls.__clone_zhenxun(git_url.data, project_name)
        await clone_result.wait()
        click.secho(f"{project_name} 克隆完成！", fg="yellow")
