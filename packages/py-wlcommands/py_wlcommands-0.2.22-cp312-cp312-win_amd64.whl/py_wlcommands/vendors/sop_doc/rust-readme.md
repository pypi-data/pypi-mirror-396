# Rust-Python 集成标准操作流程 (SOP)

本文档详细说明如何将 Rust 代码集成到 Python 项目中，包括文件结构、命名规则、开发流程和最佳实践。

## 1. 文件结构

Rust 集成部分遵循以下文件结构：

```
rust/
├── src/
│   ├── lib.rs          # 主 Rust 库文件，定义 Python 模块
│   └── main.rs         # 可选的 Rust 可执行文件（用于测试或独立运行）
├── Cargo.toml          # Rust 项目配置文件
└── rust-analyzer.json  # Rust Analyzer 配置文件
```

### 1.1 目录职责

- **rust/src/lib.rs**: 定义 Python 模块，包含所有暴露给 Python 的函数和类型
- **rust/src/main.rs**: 可选，用于编写独立的 Rust 测试或工具
- **rust/Cargo.toml**: 配置 Rust 依赖、版本和构建选项

## 2. 命名规则

### 2.1 Rust 侧命名规则

- **模块名**: 使用蛇形命名法，与 Python 模块名保持一致
- **函数名**: 使用蛇形命名法，与 Python 函数命名习惯一致
- **类型名**: 使用驼峰命名法，遵循 Rust 传统
- **常量名**: 使用全大写加下划线，遵循 Rust 传统

### 2.2 Python 侧命名规则

- **导入名**: 使用与 Rust 模块名相同的名称
- **函数调用**: 使用与 Rust 函数名相同的名称
- **类名**: 使用与 Rust 类型名相同的名称

## 3. 开发流程

### 3.1 编写 Rust 代码

1. 在 `rust/src/lib.rs` 中定义 Python 模块
2. 使用 `#[pymodule]` 宏标记模块入口
3. 使用 `#[pyfunction]` 宏标记要暴露给 Python 的函数
4. 使用 `#[pyclass]` 宏标记要暴露给 Python 的类

### 3.2 配置 Cargo.toml

确保 Cargo.toml 包含以下配置：

```toml
[package]
name = "py_wlcommands_native"
version = "0.2.14"
edition = "2024"

[dependencies]
pyo3 = { version = "0.27.2", features = ["extension-module"] }

[lib]
name = "py_wlcommands_native"
crate-type = ["cdylib"]
path = "src/lib.rs"
```

### 3.3 构建 Rust 扩展

使用以下命令构建 Rust 扩展：

```bash
cd rust
cargo build --release
```

构建产物将生成在 `rust/target/release/` 目录中。

### 3.4 集成到 Python

将构建生成的 `.so`（Linux/macOS）或 `.pyd`（Windows）文件复制到 Python 项目的适当位置，或使用构建工具自动处理。

## 4. PyO3 使用指南

### 4.1 基本函数暴露

```rust
use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
fn py_wlcommands_native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}

#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}
```

### 4.2 类型转换

PyO3 自动处理大部分基本类型的转换：

| Rust 类型       | Python 类型       |
|-----------------|-------------------|
| `bool`          | `bool`            |
| `i8`, `i16`, `i32`, `i64`, `isize` | `int` |
| `u8`, `u16`, `u32`, `u64`, `usize` | `int` |
| `f32`, `f64`    | `float`           |
| `String`, `&str`| `str`             |
| `Vec<T>`        | `list`            |
| `HashMap<K, V>` | `dict`            |
| `Option<T>`     | `T` 或 `None`     |
| `Result<T, E>`  | `T` 或 `Exception`|

### 4.3 错误处理

使用 `PyResult<T>` 类型处理错误，PyO3 会自动将 Rust 错误转换为 Python 异常：

```rust
#[pyfunction]
fn divide(a: f64, b: f64) -> PyResult<f64> {
    if b == 0.0 {
        return Err(PyZeroDivisionError::new_err("division by zero"));
    }
    Ok(a / b)
}
```

## 5. 测试策略

### 5.1 Rust 单元测试

在 Rust 代码中编写单元测试，使用 `#[test]` 宏标记：

```rust
#[test]
fn test_sum_as_string() {
    assert_eq!(sum_as_string(1, 2).unwrap(), "3");
}
```

运行 Rust 单元测试：

```bash
cd rust
cargo test
```

### 5.2 Python 集成测试

在 Python 测试文件中测试 Rust 扩展：

```python
def test_rust_sum():
    from py_wlcommands_native import sum_as_string
    assert sum_as_string(1, 2) == "3"
```

运行 Python 集成测试：

```bash
pytest tests/test_rust_integration.py
```

## 6. 构建和部署

### 6.1 本地开发构建

```bash
cd rust
cargo build
```

### 6.2 发布构建

```bash
cd rust
cargo build --release
```

### 6.3 集成到 Python 包

在 Python 项目的构建脚本中，确保包含以下步骤：

1. 构建 Rust 扩展
2. 将构建产物复制到 Python 包目录
3. 更新 `__init__.py` 以导入 Rust 扩展

## 7. 最佳实践

1. **最小化暴露**: 只暴露必要的函数和类型给 Python
2. **清晰的文档**: 为所有暴露的函数和类型编写详细的文档字符串
3. **类型安全**: 充分利用 Rust 的类型系统确保安全性
4. **错误处理**: 提供清晰的错误信息，便于 Python 开发者调试
5. **性能考虑**: 避免不必要的类型转换和内存分配
6. **测试覆盖**: 确保 Rust 代码和 Python 集成都有充分的测试覆盖

## 8. 调试技巧

1. **使用 Rust 调试器**: 可以使用 `rust-gdb` 或 `rust-lldb` 调试 Rust 代码
2. **打印调试信息**: 使用 `println!` 或 `eprintln!` 在 Rust 代码中输出调试信息
3. **Python 调试器**: 可以使用 `pdb` 或 `ipdb` 调试 Python 代码，包括调用 Rust 函数的部分
4. **错误信息**: 确保 Rust 错误转换为有意义的 Python 异常

## 9. 版本管理

Rust 扩展的版本应与 Python 包的版本保持同步。在 `Cargo.toml` 中更新版本号时，确保同时更新 Python 包的版本号。

## 10. 依赖管理

Rust 依赖应在 `Cargo.toml` 中明确指定，并使用固定版本或版本范围，确保构建的可重复性。

---

遵循本 SOP 可以确保 Rust-Python 集成的一致性、可维护性和可靠性。
