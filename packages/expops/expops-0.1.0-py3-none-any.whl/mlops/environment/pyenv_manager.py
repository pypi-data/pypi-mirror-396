from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from .base import EnvironmentManager
from .utils import load_requirements, verify_pip_requirements


class PyenvEnvironmentManager(EnvironmentManager):
    """Pyenv-based environment management."""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.requirements = load_requirements(config)
        self.python_version = config.get("python_version", "3.9.0")
        
        env_name = config.get("name")
        if not env_name:
            raise ValueError(
                "Pyenv environment name must be explicitly specified in the configuration. "
                "Please add 'name' field under 'environment.pyenv' in your config file."
            )
        self.environment_name = env_name

    def get_environment_type(self) -> str:
        return "pyenv"

    def get_environment_name(self) -> str:
        return self.environment_name

    def get_python_interpreter(self) -> str:
        if not self.python_interpreter:
            raise RuntimeError("Environment not set up yet. Call setup_environment() first.")
        return self.python_interpreter

    def _get_pyenv_executable(self) -> str:
        """Get the pyenv executable path."""
        try:
            subprocess.run(["pyenv", "--version"], capture_output=True, check=True, text=True)
            return "pyenv"
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            raise RuntimeError(
                "pyenv executable not found or not runnable. "
                "Please ensure pyenv is installed and configured correctly in your PATH. "
                f"Error: {e}"
            )

    def environment_exists(self) -> bool:
        """Check if the pyenv virtual environment already exists."""
        try:
            pyenv_exe = self._get_pyenv_executable()
            result = subprocess.run([pyenv_exe, "versions"], capture_output=True, text=True, check=True)
            return self.environment_name in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"[PyenvEnvironmentManager] Failed to list pyenv versions: {e}")
            return False

    def setup_environment(self) -> None:
        """Set up the pyenv environment based on configuration."""
        print(f"[PyenvEnvironmentManager] Starting pyenv environment setup for '{self.environment_name}'...")
        
        pyenv_exe = self._get_pyenv_executable()

        try:
            result = subprocess.run([pyenv_exe, "versions"], capture_output=True, text=True, check=True)
            if self.python_version not in result.stdout:
                print(f"[PyenvEnvironmentManager] Python version {self.python_version} not found. Installing it...")
                subprocess.run([pyenv_exe, "install", self.python_version], check=True)
                print(f"[PyenvEnvironmentManager] Python version {self.python_version} installed successfully.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install Python version {self.python_version}: {e}")

        if not self.environment_exists():
            print(f"[PyenvEnvironmentManager] Environment '{self.environment_name}' not found. Creating it...")
            
            # Create virtual environment
            try:
                subprocess.run([pyenv_exe, "virtualenv", self.python_version, self.environment_name], check=True)
                print(f"[PyenvEnvironmentManager] Environment '{self.environment_name}' created successfully.")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to create pyenv virtual environment '{self.environment_name}': {e}")
        else:
            print(f"[PyenvEnvironmentManager] Using existing environment: '{self.environment_name}'")

        try:
            pyenv_root_result = subprocess.run([pyenv_exe, "root"], capture_output=True, text=True, check=True)
            pyenv_root = Path(pyenv_root_result.stdout.strip())
            
            self.python_interpreter = str(pyenv_root / "versions" / self.environment_name / "bin" / "python")
            
            if not Path(self.python_interpreter).exists():
                raise FileNotFoundError(f"Python interpreter not found at expected path: {self.python_interpreter}")

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError(f"Failed to determine Python interpreter for pyenv environment '{self.environment_name}': {e}")

        if self.requirements:
            print(f"[PyenvEnvironmentManager] Installing requirements...")
            try:
                pip_install_cmd = [self.python_interpreter, "-m", "pip", "install"] + self.requirements
                subprocess.run(pip_install_cmd, check=True)
                print(f"[PyenvEnvironmentManager] Requirements installed successfully.")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to install requirements: {e}")

        print(f"[PyenvEnvironmentManager] Python interpreter: {self.python_interpreter}")
        print(f"[PyenvEnvironmentManager] Environment setup completed for '{self.environment_name}'.")

    def verify_environment(self) -> bool:
        """Verify that the environment is properly configured."""
        if not self.python_interpreter:
            print("[PyenvEnvironmentManager] Python interpreter not set. Cannot verify environment.")
            return False

        print(f"[PyenvEnvironmentManager] Verifying environment '{self.environment_name}'...")

        try:
            python_version_output = subprocess.check_output([self.python_interpreter, '--version'], text=True, stderr=subprocess.STDOUT).strip()
            print(f"[PyenvEnvironmentManager] Python interpreter is working: {python_version_output}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"[PyenvEnvironmentManager] Python interpreter '{self.python_interpreter}' is not working: {e}")
            return False

        try:
            current_py_ver_full = subprocess.check_output([self.python_interpreter, '--version'], text=True, stderr=subprocess.STDOUT).strip()
            current_py_ver = current_py_ver_full.split()[-1] if current_py_ver_full.split() else ""
            
            if not current_py_ver.startswith(self.python_version.split('.')[0]):  # Check major version
                print(f"[PyenvEnvironmentManager] Python version mismatch. Expected: {self.python_version}, Found: {current_py_ver}")
                return False
            print(f"[PyenvEnvironmentManager] Python version OK: {current_py_ver}")
        except subprocess.CalledProcessError as e:
            print(f"[PyenvEnvironmentManager] Could not verify Python version: {e}")
            return False

        if self.requirements:
            ok, missing = verify_pip_requirements(self.python_interpreter, self.requirements)
            if not ok:
                print(f"[PyenvEnvironmentManager] Missing packages: {', '.join(missing)}")
                print(f"[PyenvEnvironmentManager] Environment verification failed for '{self.environment_name}'.")
                return False
        
        print(f"[PyenvEnvironmentManager] Environment verification successful for '{self.environment_name}'.")
        return True 