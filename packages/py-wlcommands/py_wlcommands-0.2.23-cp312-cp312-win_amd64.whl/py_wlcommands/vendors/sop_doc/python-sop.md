# Python 引入 Rust 扩展 SOP

本文档详细说明如何从 Python 代码中引入和使用 Rust 扩展，包括导入方式、使用示例、类型转换和错误处理。

## 1. 概述

py_wlcommands 项目使用 PyO3 库将 Rust 代码集成到 Python 中，提供高性能的底层功能。Rust 扩展以动态链接库的形式提供，可直接从 Python 代码中导入使用。

## 2. 导入方式

### 2.1 直接导入

如果 Rust 扩展已经安装在 Python 路径中，可以直接导入：

```python
from py_wlcommands_native import sum_as_string
```

### 2.2 从包中导入

在 py_wlcommands 项目中，Rust 扩展通常通过包结构导入：

```python
from py_wlcommands.lib.py_wlcommands_native import sum_as_string
```

### 2.3 延迟导入

对于可选依赖或大型扩展，可以使用延迟导入：

```python
def get_rust_function():
    from py_wlcommands_native import sum_as_string
    return sum_as_string
```

## 3. 使用示例

### 3.1 基本函数调用

```python
from py_wlcommands_native import sum_as_string

# 调用 Rust 函数
result = sum_as_string(1, 2)
print(result)  # 输出: "3"
```

### 3.2 传递复杂数据类型

```python
from py_wlcommands_native import process_list

# 传递列表给 Rust 函数
data = [1, 2, 3, 4, 5]
result = process_list(data)
print(result)  # 输出处理后的结果
```

### 3.3 使用 Rust 类

```python
from py_wlcommands_native import RustCalculator

# 创建 Rust 类实例
calc = RustCalculator()

# 调用类方法
result = calc.add(10, 20)
print(result)  # 输出: 30

# 访问属性
calc.multiplier = 2
result = calc.multiply(5)
print(result)  # 输出: 10
```

## 4. 类型转换

### 4.1 基本类型转换

| Python 类型       | Rust 类型               |
|-------------------|-------------------------|
| `bool`            | `bool`                  |
| `int`             | `i64` 或 `u64`（根据大小）|
| `float`           | `f64`                   |
| `str`             | `String` 或 `&str`       |
| `list`            | `Vec<T>`                |
| `dict`            | `HashMap<K, V>`         |
| `None`            | `Option::None`          |
| `Exception`       | `Result::Err`           |

### 4.2 自定义类型转换

对于自定义类型，可以使用 PyO3 的 `FromPyObject` 和 `ToPyObject` traits 实现转换：

```rust
use pyo3::prelude::*;
use pyo3::types::PyDict;

#[derive(Debug)]
struct Person {
    name: String,
    age: u32,
}

#[pyclass]
struct PyPerson {
    inner: Person,
}

#[pymethods]
impl PyPerson {
    #[new]
    fn new(name: &str, age: u32) -> Self {
        PyPerson {
            inner: Person { name: name.into(), age },
        }
    }

    #[getter]
    fn name(&self) -> &str {
        &self.inner.name
    }

    #[getter]
    fn age(&self) -> u32 {
        self.inner.age
    }
}
```

## 5. 错误处理

### 5.1 捕获 Rust 异常

Rust 函数返回的错误会被转换为 Python 异常，可以使用 try-except 块捕获：

```python
from py_wlcommands_native import divide

try:
    result = divide(10, 0)
except ZeroDivisionError as e:
    print(f"捕获到异常: {e}")
```

### 5.2 常见异常类型

| Rust 错误类型       | Python 异常类型        |
|---------------------|------------------------|
| `PyZeroDivisionError` | `ZeroDivisionError`    |
| `PyTypeError`        | `TypeError`            |
| `PyValueError`       | `ValueError`           |
| `PyIOError`          | `IOError`              |
| `PyRuntimeError`     | `RuntimeError`         |

## 6. 调试技巧

### 6.1 查看导入路径

如果遇到导入错误，可以检查 Python 路径：

```python
import sys
print(sys.path)
```

### 6.2 检查扩展是否存在

```python
import os
from py_wlcommands.utils.platform_adapter import PlatformAdapter

# 检查扩展文件是否存在
extension_path = PlatformAdapter.get_native_extension_path("py_wlcommands_native")
print(f"扩展路径: {extension_path}")
print(f"扩展是否存在: {os.path.exists(extension_path)}")
```

### 6.3 启用调试输出

在 Rust 代码中，可以使用 `eprintln!` 输出调试信息，这些信息会显示在 Python 运行的控制台中：

```rust
#[pyfunction]
fn debug_function() -> PyResult<()> {
    eprintln!("Rust 调试信息: 函数被调用");
    Ok(())
}
```

### 6.4 使用 Python 调试器

可以使用 Python 调试器（如 `pdb` 或 `ipdb`）调试调用 Rust 函数的 Python 代码：

```python
import pdb
from py_wlcommands_native import sum_as_string

pdb.set_trace()
result = sum_as_string(1, 2)
```

## 7. 性能优化

### 7.1 减少类型转换

尽量减少 Python 和 Rust 之间的类型转换，特别是对于大型数据结构：

```python
# 不推荐：多次转换
total = 0
for i in range(1000):
    total += int(sum_as_string(i, 0))

# 推荐：一次性转换
results = process_batch(range(1000))
total = sum(results)
```

### 7.2 使用批量处理

对于大量数据，使用批量处理函数减少函数调用开销：

```python
# 不推荐：多次调用
data = [1, 2, 3, 4, 5]
results = []
for item in data:
    results.append(process_item(item))

# 推荐：批量调用
results = process_batch(data)
```

### 7.3 避免频繁内存分配

在 Rust 代码中，尽量重用内存，减少 Python 和 Rust 之间的内存分配：

```rust
#[pyfunction]
fn process_large_data(data: Vec<u8>) -> PyResult<Vec<u8>> {
    // 在 Rust 中直接处理数据，避免额外内存分配
    let mut result = Vec::with_capacity(data.len());
    // 处理数据...
    Ok(result)
}
```

## 8. 最佳实践

1. **明确的类型注解**: 为 Rust 函数添加明确的类型注解，便于 Python 开发者理解
2. **详细的文档字符串**: 为每个暴露的函数和类型编写详细的文档字符串
3. **合理的错误信息**: 提供清晰、有用的错误信息，便于调试
4. **充分的测试**: 编写 Python 集成测试，确保 Rust 扩展正常工作
5. **版本兼容性**: 确保 Rust 扩展与 Python 版本兼容
6. **性能测试**: 对关键路径进行性能测试，确保达到预期性能

## 9. 示例：完整的使用流程

### 9.1 编写 Rust 函数

```rust
// rust/src/lib.rs
use pyo3::prelude::*;

#[pymodule]
fn py_wlcommands_native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(calculate_fibonacci, m)?)?;
    Ok(())
}

#[pyfunction]
fn calculate_fibonacci(n: usize) -> PyResult<Vec<u64>> {
    if n == 0 {
        return Ok(Vec::new());
    }
    if n == 1 {
        return Ok(vec![0]);
    }

    let mut fib = Vec::with_capacity(n);
    fib.push(0);
    fib.push(1);

    for i in 2..n {
        let next = fib[i-1] + fib[i-2];
        fib.push(next);
    }

    Ok(fib)
}
```

### 9.2 构建 Rust 扩展

```bash
cd rust
cargo build --release
```

### 9.3 在 Python 中使用

```python
from py_wlcommands_native import calculate_fibonacci

# 调用 Rust 函数计算斐波那契数列
fib_sequence = calculate_fibonacci(10)
print(fib_sequence)  # 输出: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

## 10. 故障排除

### 10.1 导入错误

如果遇到 `ImportError: No module named 'py_wlcommands_native'`：

1. 检查 Rust 扩展是否已正确构建
2. 检查扩展文件是否在 Python 路径中
3. 检查 Python 版本是否与扩展兼容
4. 检查操作系统架构是否匹配（32位/64位）

### 10.2 类型错误

如果遇到 `TypeError: Expected int for parameter 'n'`：

1. 检查传递给 Rust 函数的参数类型
2. 确保参数类型与 Rust 函数签名匹配
3. 考虑添加类型转换：`calculate_fibonacci(int(n))`

### 10.3 运行时错误

如果遇到 `RuntimeError: Rust function failed`：

1. 检查 Rust 函数中的错误处理
2. 添加调试输出查看具体错误
3. 检查输入数据是否符合预期
4. 考虑添加更详细的错误信息

## 11. 结论

通过遵循本 SOP，开发者可以轻松地从 Python 代码中引入和使用 Rust 扩展，充分利用 Rust 的高性能和 Python 的易用性。在实际开发中，应根据具体需求选择合适的导入方式和使用模式，并遵循最佳实践确保代码的可维护性和性能。
