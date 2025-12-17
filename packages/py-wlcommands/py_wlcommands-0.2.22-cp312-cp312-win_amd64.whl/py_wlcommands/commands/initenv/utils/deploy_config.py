"""
Deployment configuration for init command.
"""

# 白名单列表：只有这些文件或文件夹会被部署
DEPLOY_WHITELIST = [
    ".uv",
    # '.cursor',
    ".lingma",
    "tools",
    "Makefile",
    ".python-version",
    "project_vendors",
]


from typing import Any, Callable

# 定义一个类型别名
try:
    from packaging.version import parse as packaging_parse

    parse_version: Callable[[str], Any] = packaging_parse
except ImportError:
    # 如果没有安装 packaging 库，则回退到简单的字符串比较
    def _simple_parse_version(version: str) -> str:
        return version

    parse_version = _simple_parse_version
