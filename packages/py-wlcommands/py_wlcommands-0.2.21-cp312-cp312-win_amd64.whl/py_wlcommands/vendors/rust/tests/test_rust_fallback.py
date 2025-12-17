import sys
from unittest.mock import patch

import pytest

from py_wlcommands.lib import HAS_RUST_EXTENSION, sum_as_string


def test_sum_as_string():
    """测试 sum_as_string 函数基本功能"""
    assert sum_as_string(1, 2) == "3"
    assert sum_as_string(0, 0) == "0"
    assert sum_as_string(100, 200) == "300"


def test_sum_as_string_rust_available():
    """测试 Rust 扩展可用时的功能"""
    if HAS_RUST_EXTENSION:
        # 确保使用的是 Rust 实现
        result = sum_as_string(1, 2)
        assert result == "3"


def test_sum_as_string_fallback():
    """测试 Rust 扩展不可用时的回落功能"""
    # 模拟 Rust 扩展不可用
    with patch.dict("sys.modules", {"py_wlcommands_native": None}):
        # 重新导入模块以应用模拟
        if "py_wlcommands.lib.rust_utils" in sys.modules:
            del sys.modules["py_wlcommands.lib.rust_utils"]
        if "py_wlcommands.lib" in sys.modules:
            del sys.modules["py_wlcommands.lib"]

        from py_wlcommands.lib import HAS_RUST_EXTENSION, sum_as_string

        # 验证已切换到 Python 实现
        assert not HAS_RUST_EXTENSION

        # 测试 Python 回落实现
        assert sum_as_string(1, 2) == "3"
        assert sum_as_string(0, 0) == "0"
        assert sum_as_string(100, 200) == "300"
