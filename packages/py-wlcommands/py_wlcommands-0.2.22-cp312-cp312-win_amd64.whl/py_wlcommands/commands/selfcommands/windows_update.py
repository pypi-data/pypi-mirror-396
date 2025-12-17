"""
Windows update functionality for self update command.
"""

# Import directly since we don't mock os in tests
import os
import tempfile
import time

# Import from self.py to ensure mocks work correctly
from ..self import subprocess, sys


class WindowsUpdate:
    """Windows-specific update functionality for the wl command."""

    def handle_access_error(self, uv_path: str = None) -> None:
        """
        Handle Windows access denied errors with either delayed update or manual instructions.
        """
        from py_wlcommands.utils.logging import log_info

        # Try delayed update mechanism first
        if sys.platform.startswith("win"):
            log_info(
                "Detected file in use error on Windows. Trying delayed update mechanism..."
            )
            log_info(
                "在Windows上检测到文件被占用错误。尝试延迟更新机制...",
                lang="zh",
            )
            # Find uv executable path if not already found
            if uv_path is None:
                from ..self import shutil

                uv_path = shutil.which("uv")
            if uv_path:
                env = os.environ.copy()
                # Set Windows encoding variables
                env["PYTHONIOENCODING"] = "utf-8"
                env["PYTHONLEGACYWINDOWSFSENCODING"] = "1"
                self._run_delayed_update(uv_path, env)
                return
            else:
                log_info("Failed to find uv executable for delayed update.")
                log_info("无法找到uv可执行文件进行延迟更新。", lang="zh")

        # Fallback to manual instructions if delayed update fails
        log_info(
            "Error updating wl command: Access denied. This is a common issue on Windows when trying to update a running tool.",
            lang="en",
        )
        log_info(
            "错误：更新wl命令失败: 权限被拒绝。这是在Windows上尝试更新正在运行的工具时的常见问题。",
            lang="zh",
        )
        log_info("Please try one of the following solutions:", lang="en")
        log_info("请尝试以下解决方案之一：", lang="zh")
        log_info(
            "1. Close all wl command windows and run 'wl self update' again",
            lang="en",
        )
        log_info("   关闭所有wl命令窗口，然后再次运行'wl self update'", lang="zh")
        log_info("2. Run the command as administrator", lang="en")
        log_info("   以管理员身份运行命令", lang="zh")
        log_info("3. Use 'uv tool install --editable .' directly", lang="en")
        log_info("   直接使用'uv tool install --editable .'命令", lang="zh")
        sys.exit(1)

    def _run_delayed_update(self, uv_path: str, env: dict) -> None:
        """
        Run delayed update on Windows by creating a separate script that executes after the main process exits.
        在Windows上运行延迟更新，通过创建一个独立脚本，在主进程退出后执行。

        Args:
            uv_path (str): Path to the uv executable.
            env (dict): Environment variables to use for the update.
        """
        # Create a temporary update script
        import tempfile
        import time

        from py_wlcommands.utils.logging import log_info

        # 使用简单的字符串拼接而非f-string，避免变量作用域问题
        script_content = """
import subprocess
import time
import sys
import os

# Wait for the main process to exit
print("Waiting for main process to exit...")
print("等待主进程退出...")
time.sleep(3)

# Set environment variables
os.environ.update(" + repr(env) + ")

# Execute update commands
try:
    print("Uninstalling existing py_wlcommands...")
    print("正在卸载现有py_wlcommands...")
    # Run uninstall (ignore failure if not installed)
    subprocess.run([\"" + uv_path + "\", \"tool\", \"uninstall\", \"py_wlcommands\"], check=False, capture_output=True, text=True, encoding=\"utf-8\")

    print("Installing py_wlcommands...")
    print("正在安装py_wlcommands...")
    # Try primary installation method
    primary_cmd = [\"" + uv_path + "\", \"tool\", \"install\", \"--editable\", \\".\"]
    subprocess.run(primary_cmd, check=True, capture_output=False, text=True, encoding=\"utf-8\")

    print("\nWL command updated successfully!")
    print("wl命令更新成功！")
    print("You can close this window now.")
    print("现在可以关闭此窗口。")
except subprocess.CalledProcessError as e:
    print("\nError updating wl command: " + str(e))
    print("更新wl命令失败: " + str(e))
    try:
        # Try alternative installation method
        print("\nTrying alternative installation method...")
        print("尝试备选安装方法...")
        alternative_cmd = [\"" + uv_path + "\", \"tool\", \"install\", \"--editable\", \\".\", \"--python-preference\", \"only-system\"]
        subprocess.run(alternative_cmd, check=True, capture_output=False, text=True, encoding=\"utf-8\")
        print("\nWL command updated successfully with alternative method!")
        print("使用备选方法成功更新wl命令！")
        print("You can close this window now.")
        print("现在可以关闭此窗口。")
    except subprocess.CalledProcessError as alt_e:
        print("\nAlternative installation also failed: " + str(alt_e))
        print("备选安装方法也失败: " + str(alt_e))
        print("Please try manual installation:")
        print("请尝试手动安装：")
        print("uv tool install --editable .")
        print("Press Enter to exit...")
        input()
except Exception as e:
    print("\nUnexpected error: " + str(e))
    print("意外错误: " + str(e))
    print("Press Enter to exit...")
    input()
"""

        # Write the script to a temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(script_content)
            temp_script_path = f.name

        # Run the script in a new console window
        log_info(f"Running delayed update script: {temp_script_path}")
        log_info(f"正在运行延迟更新脚本: {temp_script_path}", lang="zh")

        try:
            # Use start command to run in a new window
            subprocess.Popen(
                [sys.executable, temp_script_path],
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            log_info(
                "Delayed update started. The update will continue in a new window."
            )
            log_info("延迟更新已启动。更新将在新窗口中继续进行。", lang="zh")
            sys.exit(0)
        except Exception as e:
            log_info(f"Failed to start delayed update: {e}")
            log_info(f"启动延迟更新失败: {e}", lang="zh")
            # Fall back to manual instructions
            self._show_manual_instructions()

    def _show_manual_instructions(self) -> None:
        """
        Show manual installation instructions to the user.
        """
        from py_wlcommands.utils.logging import log_info

        log_info(
            "Error updating wl command: Access denied. This is a common issue on Windows when trying to update a running tool.",
            lang="en",
        )
        log_info(
            "错误：更新wl命令失败: 权限被拒绝。这是在Windows上尝试更新正在运行的工具时的常见问题。",
            lang="zh",
        )
        log_info("Please try one of the following solutions:", lang="en")
        log_info("请尝试以下解决方案之一：", lang="zh")
        log_info(
            "1. Close all wl command windows and run 'wl self update' again",
            lang="en",
        )
        log_info("   关闭所有wl命令窗口，然后再次运行'wl self update'", lang="zh")
        log_info("2. Run the command as administrator", lang="en")
        log_info("   以管理员身份运行命令", lang="zh")
        log_info("3. Use 'uv tool install --editable .' directly", lang="en")
        log_info("   直接使用'uv tool install --editable .'命令", lang="zh")
        sys.exit(1)
