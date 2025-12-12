from pathlib import Path
import shutil
import zipfile

import click

from ..utils.github_utils import GithubUtils
from ..utils.http_utils import AsyncHttpx

TMP_PATH = Path() / "tmp"
DOWNLOAD_ZIP_FILE_STRING = "download_latest_file.zip"


class DownloadInstallHelp:
    DEFAULT_GITHUB_URL = "https://github.com/HibiKier/zhenxun_bot/tree/main"

    @classmethod
    async def download_install(cls, ctx: click.Context, project_name: str) -> str:
        """下载文件

        参数:
            ctx: ctx
        """
        click.secho("开始下载小真寻项目...", fg="yellow")
        repo_info = GithubUtils.parse_github_url(cls.DEFAULT_GITHUB_URL)
        url = await repo_info.get_archive_download_urls()
        if not url:
            click.secho("获取下载链接失败...", fg="yellow")
            ctx.exit()
        if TMP_PATH.exists():
            shutil.rmtree(TMP_PATH)
        TMP_PATH.mkdir(parents=True, exist_ok=True)
        download_file = TMP_PATH / DOWNLOAD_ZIP_FILE_STRING
        if await AsyncHttpx.download_file(url, download_file, stream=True):
            click.secho("下载真寻最新版文件完成！", fg="yellow")
            await cls._unzip_handle(project_name)
        else:
            click.secho("下载真寻最新版文件失败...", fg="red")
            ctx.exit()
        return "zhenxun_bot"

    @classmethod
    async def _unzip_handle(cls, project_name: str):
        """解压文件

        参数:
            ctx: ctx
        """
        click.secho("开始解压下载文件...", fg="yellow")
        download_file = TMP_PATH / DOWNLOAD_ZIP_FILE_STRING
        tf = zipfile.ZipFile(download_file)
        tf.extractall(Path())
        if tf:
            tf.close()
        click.secho("解压下载完成！", fg="yellow")
        if download_file.exists():
            download_file.unlink()
        unzip_file = Path() / "zhenxun_bot-main"
        if unzip_file.exists():
            unzip_file.rename(project_name)
        if TMP_PATH.exists():
            shutil.rmtree(TMP_PATH)
