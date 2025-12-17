"""PyProject.toml generator utility."""

import re
from pathlib import Path
from typing import Any

import toml  # type: ignore [import-untyped]

from ....utils.logging import log_info
from .config_manager import ConfigManager


def clean_cargo_name(name: str) -> str:
    """Cleans a string to be a valid Cargo package name.
    - Replaces invalid characters (anything not letter, number, _, -) with underscore.
    - Ensures it doesn't start/end with invalid chars like _ or -.
    """
    # Replace sequences of invalid characters (anything not alphanumeric or _) with a single underscore
    # Also replace hyphens with underscores as Cargo prefers underscores, though hyphens are technically allowed.
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", name.replace("-", "_"))
    # Remove leading/trailing underscores
    cleaned = cleaned.strip("_")
    # Handle potential empty string after cleaning
    if not cleaned:
        return "rust_package"  # Default fallback name
    # Ensure it doesn't start with a digit (invalid for Rust identifiers)
    if cleaned[0].isdigit():
        cleaned = "_" + cleaned
    return cleaned


def clean_python_package_name(name: str) -> str:
    """Cleans a string to be a valid Python package/module name.
    - Replaces invalid characters (like ., -, space) with underscore.
    - Ensures it follows Python identifier rules.
    """
    # Replace hyphens, dots, and spaces with underscores
    cleaned = name.replace("-", "_").replace(".", "_").replace(" ", "_")
    # Replace other sequences of invalid characters (anything not alphanumeric or _) with a single underscore
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", cleaned)
    # Remove leading/trailing underscores
    cleaned = cleaned.strip("_")
    # Handle potential empty string after cleaning
    if not cleaned:
        return "python_package"  # Default fallback name
    # Ensure it doesn't start with a digit (invalid for Python identifiers)
    if cleaned[0].isdigit():
        cleaned = "_" + cleaned
    return cleaned


def format_list(items: list[str]) -> list[str]:
    """格式化列表，确保每个元素独占一行"""
    return [item.strip() for item in items]


def dump_toml(data: dict[str, Any], file_path: str) -> None:
    """将数据以 TOML 格式写入文件"""
    with open(file_path, "w", encoding="utf-8") as f:
        toml.dump(data, f)


class PyProjectGenerator:
    """pyproject.toml 生成器类"""

    def __init__(self, project_name: str, version: str = "0.1.0") -> None:
        self.project_name_raw = project_name  # Store original name if needed later
        # Use the new cleaning functions
        self.cleaned_python_name = clean_python_package_name(project_name)
        # Generate the cleaned rust name based on the raw project name + suffix
        self.cleaned_rust_name = clean_cargo_name(f"{project_name}_native")
        self.version = version
        self.config: dict[str, Any] = {}
        self.config_manager = ConfigManager()

    def _load_default_config(self) -> dict[str, Any]:
        """加载默认配置"""
        return self.config_manager.load_vendor_config("config/pyproject_defaults.toml")

    def _load_tool_configs(self) -> dict[str, Any]:
        """加载工具配置"""
        return self.config_manager.load_vendor_config("config/tool_configs.toml")

    def _load_dependencies(self) -> list[str]:
        """加载依赖列表"""
        dependencies_config = self.config_manager.load_vendor_config(
            "config/dependencies.toml"
        )
        return dependencies_config.get("dependencies", {}).get("default", [])

    def set_project_info(
        self,
        description: str | None = None,
        authors: list[dict[str, str]] | None = None,
        python_version: str = ">=3.10",
        license_name: str = "MIT",
        dependencies: list[str] | None = None,
    ) -> None:
        """设置项目基本信息"""
        # Load default config
        default_config = self._load_default_config()
        default_project_config = default_config.get("project", {})

        # Load dependencies from config if not provided
        if not dependencies:
            dependencies = self._load_dependencies()

        # Use cleaned python name for URLs and description default
        project_urls = {
            "Homepage": f"https://github.com/example/{self.cleaned_python_name}",
            "Issues": f"https://github.com/example/{self.cleaned_python_name}/issues",
        }

        self.config["project"] = {
            "name": self.cleaned_python_name,
            "dynamic": ["version"],
            "description": description or f"{self.cleaned_python_name} - Python项目",
            "requires-python": python_version,
            "license": license_name,
            "readme": "README.md",
            "dependencies": dependencies,
            "authors": authors or [{"name": "Admin", "email": "admin@example.com"}],
            "urls": project_urls,
        }

    def set_build_system(self, is_rust: bool = False, is_qt: bool = False) -> None:
        """设置构建系统配置"""
        if not is_rust:
            # Handle non-rust build system if needed (currently assumes Maturin)
            print("Warning: Non-Rust build system not fully configured in generator.")
            # Set a basic setuptools build system or similar if required
            self.config["build-system"] = {
                "requires": ["setuptools>=61.0"],
                "build-backend": "setuptools.build_meta",
            }
            return  # Exit early if not using Rust/Maturin

        # --- Maturin Configuration ---
        self.config["build-system"] = {
            "requires": ["maturin>=1.0,<2.0"],
            "build-backend": "maturin",
        }

        # Maturin 特定配置
        maturin_config = {
            "manifest-path": "rust/Cargo.toml",
            # Use CLEANED Python and Rust names for module-name
            "module-name": f"{self.cleaned_python_name}.lib.{self.cleaned_rust_name}",
            "python-source": "src",
            # Use cleaned python name for include path
            "include": [f"src/{self.cleaned_python_name}/**/*"],
            "bindings": "pyo3",
            "features": ["pyo3/extension-module"],
            "sdist-include": ["src/**/*"],
            # Use cleaned python name for python-packages
            "python-packages": [self.cleaned_python_name],
        }

        self.config["tool"] = self.config.get("tool", {})
        self.config["tool"]["maturin"] = maturin_config

    def set_development_tools(self) -> None:
        """设置开发工具配置"""
        # Load tool configs from vendor
        tool_configs = self._load_tool_configs()

        # 更新工具配置
        self.config["tool"] = self.config.get("tool", {})
        self.config["tool"].update(tool_configs.get("tool", {}))

    def set_entry_points(self, entry_points: dict[str, Any]) -> None:
        """设置入口点"""
        if "project" not in self.config:
            self.config["project"] = {}

        if "scripts" in entry_points:
            self.config["project"]["scripts"] = entry_points["scripts"]
        if "gui_scripts" in entry_points:
            self.config["project"]["gui-scripts"] = entry_points["gui_scripts"]

    def generate(self, output_path: str = "pyproject.toml") -> None:
        """生成 pyproject.toml 文件"""
        # Get args passed to main (if any) to determine rust/qt flags
        is_rust = Path("rust").exists()
        # is_qt = "--qt" in sys.argv # This variable is assigned but never used

        # 确保配置完整性
        if "project" not in self.config:
            self.set_project_info()
        # Pass the actual rust flag to set_build_system
        if "build-system" not in self.config:
            self.set_build_system(is_rust=is_rust)
        if "tool" not in self.config or "ruff" not in self.config["tool"]:
            self.set_development_tools()

        # Set entry points if provided (example)
        # self.set_entry_points({"scripts": {"my-cli": f"{self.cleaned_python_name}.cli:main"}})

        # 写入文件，使用toml包保证格式正确
        dump_toml(self.config, output_path)
        log_info(f"✓ 已生成 {output_path}")
