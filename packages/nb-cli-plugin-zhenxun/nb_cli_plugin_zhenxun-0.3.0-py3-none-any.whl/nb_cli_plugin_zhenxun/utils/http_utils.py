import asyncio
from asyncio.exceptions import TimeoutError
from pathlib import Path
import time
from typing import Any

import httpx
from httpx import ConnectTimeout, HTTPStatusError, Response
import rich

# from .browser import get_browser


class AsyncHttpx:
    @classmethod
    async def get(
        cls,
        url: str | list[str],
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        verify: bool = True,
        use_proxy: bool = True,
        proxy: dict[str, str] | None = None,
        timeout: int = 30,
        **kwargs,
    ) -> Response:
        """Get

        参数:
            url: url
            params: params
            headers: 请求头
            cookies: cookies
            verify: verify
            use_proxy: 使用默认代理
            proxy: 指定代理
            timeout: 超时时间
        """
        urls = [url] if isinstance(url, str) else url
        return await cls._get_first_successful(
            urls,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            use_proxy=use_proxy,
            proxy=proxy,
            timeout=timeout,
            **kwargs,
        )

    @classmethod
    async def _get_first_successful(
        cls,
        urls: list[str],
        **kwargs,
    ) -> Response:
        last_exception = None
        for url in urls:
            try:
                return await cls._get_single(url, **kwargs)
            except Exception as e:
                last_exception = e
                if url != urls[-1]:
                    print(f"获取 {url} 失败, 尝试下一个")
        raise last_exception or Exception("All URLs failed")

    @classmethod
    async def _get_single(
        cls,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        verify: bool = True,
        use_proxy: bool = True,
        proxy: dict[str, str] | None = None,
        timeout: int = 30,
        **kwargs,
    ) -> Response:
        async with httpx.AsyncClient(verify=verify) as client:  # type: ignore
            return await client.get(
                url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
                **kwargs,
            )

    @classmethod
    async def head(
        cls,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        verify: bool = True,
        use_proxy: bool = True,
        proxy: dict[str, str] | None = None,
        timeout: int = 30,
        **kwargs,
    ) -> Response:
        """Get

        参数:
            url: url
            params: params
            headers: 请求头
            cookies: cookies
            verify: verify
            use_proxy: 使用默认代理
            proxy: 指定代理
            timeout: 超时时间
        """
        async with httpx.AsyncClient(verify=verify) as client:  # type: ignore
            return await client.head(
                url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
                **kwargs,
            )

    @classmethod
    async def download_file(
        cls,
        url: str | list[str],
        path: str | Path,
        *,
        params: dict[str, str] | None = None,
        verify: bool = True,
        use_proxy: bool = True,
        proxy: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        timeout: int = 30,
        stream: bool = False,
        follow_redirects: bool = True,
        **kwargs,
    ) -> bool:
        """下载文件

        参数:
            url: url
            path: 存储路径
            params: params
            verify: verify
            use_proxy: 使用代理
            proxy: 指定代理
            headers: 请求头
            cookies: cookies
            timeout: 超时时间
            stream: 是否使用流式下载（流式写入+进度条，适用于下载大文件）
        """
        if isinstance(path, str):
            path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            for _ in range(3):
                if not isinstance(url, list):
                    url = [url]
                for u in url:
                    try:
                        if not stream:
                            response = await cls.get(
                                u,
                                params=params,
                                headers=headers,
                                cookies=cookies,
                                use_proxy=use_proxy,
                                proxy=proxy,
                                timeout=timeout,
                                follow_redirects=follow_redirects,
                                **kwargs,
                            )
                            response.raise_for_status()
                            content = response.content
                            with open(path, "wb") as wf:  # noqa: ASYNC230
                                wf.write(content)
                                print(f"下载 {u} 成功.. Path：{path.absolute()}")
                        else:
                            async with httpx.AsyncClient(verify=verify) as client:
                                async with client.stream(
                                    "GET",
                                    u,
                                    params=params,
                                    headers=headers,
                                    cookies=cookies,
                                    timeout=timeout,
                                    follow_redirects=True,
                                    **kwargs,
                                ) as response:
                                    response.raise_for_status()
                                    print(
                                        f"开始下载 {path.name}.. "
                                        f"Url: {u}.. "
                                        f"Path: {path.absolute()}"
                                    )
                                    with open(path, "wb") as wf:  # noqa: ASYNC230
                                        total = int(
                                            response.headers.get("Content-Length", 0)
                                        )
                                        with rich.progress.Progress(  # type: ignore
                                            rich.progress.TextColumn(path.name),  # type: ignore
                                            "[progress.percentage]{task.percentage:>3.0f}%",  # type: ignore
                                            rich.progress.BarColumn(bar_width=None),  # type: ignore
                                            rich.progress.DownloadColumn(),  # type: ignore
                                            rich.progress.TransferSpeedColumn(),  # type: ignore
                                        ) as progress:
                                            download_task = progress.add_task(
                                                "Download",
                                                total=total or None,
                                            )
                                            async for chunk in response.aiter_bytes():
                                                wf.write(chunk)
                                                wf.flush()
                                                progress.update(
                                                    download_task,
                                                    completed=response.num_bytes_downloaded,
                                                )
                                        print(
                                            f"下载 {u} 成功.. Path：{path.absolute()}"
                                        )
                        return True
                    except (TimeoutError, ConnectTimeout, HTTPStatusError):
                        print(f"下载 {u} 失败.. 尝试下一个地址..")
            print(f"下载 {url} 下载超时.. Path：{path.absolute()}")
        except Exception:
            print(f"下载 {url} 错误 Path：{path.absolute()}")
        return False

    @classmethod
    async def get_fastest_mirror(cls, url_list: list[str]) -> list[str]:
        assert url_list

        async def head_mirror(client: type[AsyncHttpx], url: str) -> dict[str, Any]:
            begin_time = time.time()

            response = await client.head(url=url, timeout=6)

            elapsed_time = (time.time() - begin_time) * 1000
            content_length = int(response.headers.get("content-length", 0))

            return {
                "url": url,
                "elapsed_time": elapsed_time,
                "content_length": content_length,
            }

        print(f"开始获取最快镜像，可能需要一段时间... | URL列表：{url_list}")
        results = await asyncio.gather(
            *(head_mirror(cls, url) for url in url_list),
            return_exceptions=True,
        )
        _results: list[dict[str, Any]] = []
        for result in results:
            if isinstance(result, BaseException):
                print(f"获取镜像失败，错误：{result}")
            else:
                print(f"获取镜像成功，结果：{result}")
                _results.append(result)
        _results = sorted(iter(_results), key=lambda r: r["elapsed_time"])
        return [result["url"] for result in _results]
