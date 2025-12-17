# 尝试导入 Rust 扩展，如果失败则使用 Python 实现
try:
    from py_wlcommands_native import sum_as_string as rust_sum_as_string

    HAS_RUST_EXTENSION = True
except ImportError:
    HAS_RUST_EXTENSION = False


def sum_as_string(a: int, b: int) -> str:
    """
    计算两个整数的和并返回字符串表示。
    优先使用 Rust 扩展实现，不可用时回落至 Python 实现。

    Args:
        a: 第一个整数
        b: 第二个整数

    Returns:
        两个整数和的字符串表示
    """
    if HAS_RUST_EXTENSION:
        return rust_sum_as_string(a, b)
    else:
        # Python 实现作为回落
        return str(a + b)
