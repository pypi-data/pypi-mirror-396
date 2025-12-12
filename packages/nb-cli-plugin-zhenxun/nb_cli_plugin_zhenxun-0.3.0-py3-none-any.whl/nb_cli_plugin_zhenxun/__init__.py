import sys

if sys.version_info < (3, 10):  # noqa: UP036
    from importlib_metadata import version
else:
    from importlib.metadata import version
try:
    __version__ = version("nb-cli-plugin-zhenxun")
except Exception:
    __version__ = None
