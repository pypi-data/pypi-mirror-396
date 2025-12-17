"""
Local installer for self update command.
"""


class LocalInstaller:
    """Installer for local installation of the wl command."""

    def install(self, uv_path: str, env: dict) -> None:
        """
        Install the current local code (replicates reinstall.bat functionality).

        Args:
            uv_path (str): Path to the uv executable.
            env (dict): Environment variables to use for the installation.
        """
        from py_wlcommands.utils.logging import log_info

        from ..self import subprocess, sys

        log_info("Installing local py_wlcommands...")
        log_info("正在安装本地py_wlcommands...", lang="zh")

        # Uninstall existing py_wlcommands
        from .installation_manager import InstallationManager

        installation_manager = InstallationManager()
        installation_manager.uninstall_existing(uv_path, env)

        # Install current directory in editable mode
        log_info("Installing current directory in editable mode...")
        log_info("正在以可编辑模式安装当前目录...", lang="zh")

        install_cmd = [uv_path, "tool", "install", "--editable", "."]
        log_info(f"Running: {' '.join(install_cmd)}")

        try:
            subprocess.run(
                install_cmd,
                check=True,
                capture_output=False,
                text=True,
                encoding="utf-8" if sys.platform.startswith("win") else None,
                env=env,
            )
            log_info("Local installation completed successfully!")
            log_info("本地安装成功完成！", lang="zh")
        except subprocess.CalledProcessError as e:
            log_info(f"Local installation failed: {e}")
            log_info(f"本地安装失败: {e}", lang="zh")
            # Try alternative installation method
            self._try_alternative_installation(uv_path, env)

    def _try_alternative_installation(self, uv_path: str, env: dict) -> None:
        """
        Try alternative installation method if primary fails.

        Args:
            uv_path (str): Path to the uv executable.
            env (dict): Environment variables to use for the installation.
        """
        from py_wlcommands.utils.logging import log_info

        from ..self import subprocess, sys

        log_info("Trying alternative installation method...")
        log_info("尝试备选安装方法...", lang="zh")

        alternative_cmd = [
            uv_path,
            "tool",
            "install",
            "--editable",
            ".",
            "--python-preference",
            "only-system",
        ]
        log_info(f"Running: {' '.join(alternative_cmd)}")

        try:
            subprocess.run(
                alternative_cmd,
                check=True,
                capture_output=False,
                text=True,
                encoding="utf-8" if sys.platform.startswith("win") else None,
                env=env,
            )
            log_info(
                "Local installation completed successfully with alternative method!"
            )
            log_info("使用备选方法本地安装成功完成！", lang="zh")
        except subprocess.CalledProcessError as alt_e:
            log_info(f"Alternative installation also failed: {alt_e}")
            log_info(f"备选安装方法也失败: {alt_e}", lang="zh")
            raise

    def run_installation_attempt(
        self,
        uv_path: str,
        env: dict,
        timeout_duration: int,
        use_alternative: bool = False,
    ) -> bool:
        """
        Run a single installation attempt (primary or alternative).
        Returns True if installation succeeded, False otherwise.
        """
        from py_wlcommands.utils.logging import log_info

        from ..self import subprocess, sys

        if use_alternative:
            cmd = [
                uv_path,
                "tool",
                "install",
                "--editable",
                ".",
                "--python-preference",
                "only-system",
            ]
            log_info("Trying alternative installation method...")
            log_info("尝试备选安装方法...", lang="zh")
        else:
            cmd = [uv_path, "tool", "install", "--editable", "."]

        log_info(f"Running: {' '.join(cmd)}")
        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=False,
                text=True,
                encoding="utf-8" if sys.platform.startswith("win") else None,
                env=env,
                timeout=timeout_duration,
            )
            return True
        except subprocess.TimeoutExpired:
            log_info(
                f"{'Alternative' if use_alternative else 'Primary'} installation timed out after {timeout_duration} seconds."
            )
            log_info(
                f"{'备选' if use_alternative else '主'}安装方法在{timeout_duration}秒后超时。",
                lang="zh",
            )
            return False
        except subprocess.CalledProcessError as e:
            log_info(
                f"{'Alternative' if use_alternative else 'Primary'} installation failed: {e}"
            )
            log_info(
                f"{'备选' if use_alternative else '主'}安装方法失败: {e}", lang="zh"
            )
            # Check if this is a Windows file in use error
            from .installation_manager import InstallationManager

            installation_manager = InstallationManager()
            if sys.platform.startswith(
                "win"
            ) and installation_manager.is_file_in_use_error(str(e)):
                from .windows_update import WindowsUpdate

                windows_update = WindowsUpdate()
                windows_update.handle_access_error(uv_path)
                return False  # Will never reach here due to sys.exit or _run_delayed_update
            if use_alternative:
                raise  # Re-raise for alternative method failure
            return False
        except Exception as e:
            log_info(
                f"Unexpected error during {'alternative' if use_alternative else 'primary'} installation: {e}"
            )
            log_info(
                f"{'备选' if use_alternative else '主'}安装过程中发生意外错误: {e}",
                lang="zh",
            )
            if use_alternative:
                raise  # Re-raise for alternative method failure
            return False
