"""
Cargo.toml synchronization functionality for init command.
"""

import re
from pathlib import Path
from typing import Any, cast

# Try to import TOML libraries
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        # If neither library is available, we'll handle it when needed
        tomllib = None  # type: ignore

# --- Constants for Cargo sync ---
PYO3_VERSION = "0.21"
PYO3_FEATURES = ["extension-module"]


def load_toml(path: Path) -> dict[str, Any]:
    """Loads a TOML file, handling errors."""
    if tomllib is None:
        raise RuntimeError("错误: 需要 Python 3.11+ 或安装 tomli/toml 包")

    try:
        with open(path, "rb") as f:
            return cast(dict[str, Any], tomllib.load(f))
    except FileNotFoundError:
        raise FileNotFoundError(f"错误: {path} 未找到。")
    except Exception as e:
        raise RuntimeError(f"错误: 解析 {path} 失败: {e}")


def _format_complex_value(value: Any) -> str:
    """Format complex values like dicts and mixed lists."""
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            if isinstance(v, str):
                parts.append(f'{k} = "{v}"')
            elif isinstance(v, bool):
                parts.append(f"{k} = {str(v).lower()}")
            elif isinstance(v, list):
                formatted_list = "[" + ", ".join(f'"{item}"' for item in v) + "]"
                parts.append(f"{k} = {formatted_list}")
            else:
                parts.append(f"{k} = {v}")
        return "{ " + ", ".join(parts) + " }"
    elif isinstance(value, bool):
        return str(value).lower()
    else:
        return str(value)


def _write_toml_value(f, key: str, value: Any) -> None:
    """Write a single TOML key-value pair."""
    if isinstance(value, str):
        f.write(f'{key} = "{value}"\n')
    elif isinstance(value, bool):
        f.write(f"{key} = {str(value).lower()}\n")
    elif isinstance(value, list):
        if all(isinstance(item, str) for item in value):
            formatted_list = "[" + ", ".join(f'"{item}"' for item in value) + "]"
            f.write(f"{key} = {formatted_list}\n")
        else:
            # For complex lists like pyo3 dependency
            f.write(f"{key} = {_format_complex_value(value)}\n")
    elif isinstance(value, dict):
        f.write(f"{key} = {_format_complex_value(value)}\n")
    else:
        f.write(f"{key} = {value}\n")


def _write_toml_dict(data: dict[str, Any], f, depth: int = 0) -> None:
    """Simple TOML writer for basic data structures."""
    for key, value in data.items():
        if isinstance(value, dict):
            f.write(f"\n[{key}]\n")
            for subkey, subvalue in value.items():
                _write_toml_value(f, subkey, subvalue)
        else:
            _write_toml_value(f, key, value)


def write_toml(data: dict[str, Any], path: Path) -> None:
    """Writes data to a TOML file, handling errors."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            _write_toml_dict(data, f)
    except OSError as e:
        raise RuntimeError(f"错误: 写入 {path} 失败: {e}")


def clean_cargo_name(name: str) -> str:
    """Cleans a string to be a valid Cargo package name.
    - Replaces invalid characters (anything not letter, number, _, -) with underscore.
    - Ensures it doesn't start/end with invalid chars like _ or -.
    """
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", name.replace("-", "_"))
    cleaned = cleaned.strip("_")
    if not cleaned:
        return "rust_package"
    if cleaned[0].isdigit():
        cleaned = "_" + cleaned
    return cleaned


def extract_rust_crate_name(pyproject_data: dict[str, Any]) -> str | None:
    """Extracts and cleans the Rust crate name from pyproject data."""
    try:
        maturin_config = pyproject_data["tool"]["maturin"]
        module_name = maturin_config.get("module-name")
        if module_name and "." in module_name:
            raw_name = module_name.split(".")[-1]
            return clean_cargo_name(raw_name)
        else:
            return None
    except KeyError:
        return None


def format_authors(authors_list: list[dict[str, str]]) -> list[str]:
    """Formats pyproject authors for Cargo.toml."""
    formatted = []
    for author in authors_list:
        name = author.get("name")
        email = author.get("email")
        if name and email:
            formatted.append(f"{name} <{email}>")
        elif name:
            formatted.append(name)
    return formatted


def extract_pyproject_metadata(pyproject_data: dict[str, Any]) -> dict[str, Any]:
    """Extracts relevant metadata from pyproject data."""
    project_info = pyproject_data.get("project", {})
    return {
        "version": project_info.get("version"),
        "description": project_info.get("description"),
        "authors": project_info.get("authors"),
        "license": project_info.get("license"),
    }


def update_cargo_package_section(
    cargo_data: dict[str, Any],
    metadata: dict[str, Any],
    rust_crate_name: str | None,
    cargo_path: Path,
) -> None:
    """Updates the [package] section of Cargo data."""
    package_info = cargo_data.setdefault("package", {})

    # Update name
    if rust_crate_name:
        package_info["name"] = rust_crate_name
    elif "name" not in package_info:
        raise RuntimeError(
            "错误: 无法确定 Cargo 包名，且 Cargo.toml 中未设置 [package].name"
        )

    # Update other metadata
    if metadata["version"]:
        package_info["version"] = metadata["version"]
    if metadata["description"]:
        package_info["description"] = metadata["description"]
    if metadata["authors"]:
        package_info["authors"] = format_authors(metadata["authors"])
    if metadata["license"]:
        # Handle license format from pyproject.toml
        if isinstance(metadata["license"], dict) and "file" in metadata["license"]:
            # If license is in format {"file": "LICENSE"}, use license-file field
            # Calculate the relative path from Cargo.toml to the license file
            license_file = metadata["license"]["file"]
            # Get the parent directory of Cargo.toml
            cargo_dir = cargo_path.parent
            # Calculate the relative path from Cargo.toml's directory to the license file
            # The license file is usually in the project root, so we need to go up one level
            # if Cargo.toml is in a subdirectory like rust/
            relative_path = Path(license_file)
            if not relative_path.is_absolute():
                # If the license file path is relative in pyproject.toml, it's relative to the project root
                # So we need to calculate the relative path from Cargo.toml's directory
                project_root = (
                    cargo_path.parent.parent
                )  # Assuming Cargo.toml is in rust/ directory
                relative_path = Path("../") / license_file
            # Always use forward slashes in Cargo.toml paths, regardless of platform
            package_info["license-file"] = str(relative_path).replace("\\", "/")
        else:
            # Otherwise use regular license field
            package_info["license"] = metadata["license"]


def update_cargo_dependencies(cargo_data: dict[str, Any]) -> None:
    """Updates the [dependencies] section, adding pyo3 if missing."""
    dependencies = cargo_data.setdefault("dependencies", {})
    if "pyo3" not in dependencies:
        dependencies["pyo3"] = {"version": PYO3_VERSION, "features": PYO3_FEATURES}


def update_cargo_lib_section(cargo_data: dict[str, Any]) -> None:
    """Updates the [lib] section, ensuring crate-type is set."""
    if "lib" not in cargo_data:
        cargo_data["lib"] = {"crate-type": ["cdylib"]}
    elif "crate-type" not in cargo_data.get("lib", {}):
        cargo_data.setdefault("lib", {})["crate-type"] = ["cdylib"]


def sync_toml_files(pyproject_path: Path, cargo_path: Path) -> None:
    """Loads pyproject.toml and Cargo.toml, syncs metadata, and saves Cargo.toml."""
    # Load files
    pyproject_data = load_toml(pyproject_path)
    cargo_data = load_toml(cargo_path)

    # Extract info
    rust_crate_name = extract_rust_crate_name(pyproject_data)
    pyproject_metadata = extract_pyproject_metadata(pyproject_data)

    # Update Cargo data
    update_cargo_package_section(
        cargo_data, pyproject_metadata, rust_crate_name, cargo_path
    )
    update_cargo_dependencies(cargo_data)
    update_cargo_lib_section(cargo_data)

    # Write back Cargo.toml
    write_toml(cargo_data, cargo_path)
