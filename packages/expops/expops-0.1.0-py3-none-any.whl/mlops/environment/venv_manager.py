from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from .base import EnvironmentManager
from .utils import load_requirements, verify_pip_requirements


class VenvEnvironmentManager(EnvironmentManager):
    """Standard Python venv-based environment management."""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.requirements = load_requirements(config)
        
        env_name = config.get("name")
        if not env_name:
            raise ValueError(
                "Virtual environment name must be explicitly specified in the configuration. "
                "Please add 'name' field under 'environment.venv' in your config file."
            )
        self.environment_name = env_name
        # Prefer project-local `.venvs/` but preserve existing cache environments if present.
        preferred_path = Path.cwd() / ".venvs" / self.environment_name
        cache_path = Path.home() / ".cache" / "mlops-platform" / "venvs" / self.environment_name

        if self._python_path(preferred_path).exists():
            self.venv_path = preferred_path
        elif self._python_path(cache_path).exists():
            self.venv_path = cache_path
        else:
            self.venv_path = preferred_path if self._ensure_writable_dir(preferred_path.parent) else cache_path

    @staticmethod
    def _python_path(venv_path: Path) -> Path:
        if os.name == "nt":
            return venv_path / "Scripts" / "python.exe"
        return venv_path / "bin" / "python"

    @staticmethod
    def _ensure_writable_dir(dir_path: Path) -> bool:
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            probe = dir_path / ".mlops_write_probe"
            probe.write_text("", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return True
        except Exception:
            return False

    def get_environment_type(self) -> str:
        return "venv"

    def get_environment_name(self) -> str:
        return self.environment_name

    def get_python_interpreter(self) -> str:
        if not self.python_interpreter:
            raise RuntimeError("Environment not set up yet. Call setup_environment() first.")
        return self.python_interpreter

    def environment_exists(self) -> bool:
        """Check if the virtual environment already exists."""
        return self._python_path(self.venv_path).exists()

    def setup_environment(self) -> None:
        """Set up the virtual environment based on configuration."""
        print(f"[VenvEnvironmentManager] Starting venv environment setup for '{self.environment_name}'...")
        
        if not self.environment_exists():
            print(f"[VenvEnvironmentManager] Environment '{self.environment_name}' not found. Creating it...")
            
            self.venv_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
                print(f"[VenvEnvironmentManager] Environment '{self.environment_name}' created successfully.")
            except subprocess.CalledProcessError as e:
                # One more fallback: use virtualenv if available
                try:
                    subprocess.run([sys.executable, "-m", "virtualenv", str(self.venv_path)], check=True)
                    print(f"[VenvEnvironmentManager] Environment '{self.environment_name}' created via virtualenv.")
                except Exception:
                    raise RuntimeError(f"Failed to create virtual environment '{self.environment_name}': {e}")
        else:
            print(f"[VenvEnvironmentManager] Using existing environment: '{self.environment_name}'")

        self.python_interpreter = str(self._python_path(self.venv_path))
        
        if not Path(self.python_interpreter).exists():
            raise FileNotFoundError(f"Python interpreter not found in environment '{self.environment_name}' at expected path: {self.python_interpreter}")

        if self.requirements:
            print(f"[VenvEnvironmentManager] Installing requirements...")
            try:
                # Ensure modern build tooling to prefer wheels over source builds
                subprocess.run([self.python_interpreter, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
                pip_install_cmd = [self.python_interpreter, "-m", "pip", "install", "--no-cache-dir"] + self.requirements
                subprocess.run(pip_install_cmd, check=True)
                print(f"[VenvEnvironmentManager] Requirements installed successfully.")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to install requirements: {e}")

        print(f"[VenvEnvironmentManager] Python interpreter: {self.python_interpreter}")
        print(f"[VenvEnvironmentManager] Environment setup completed for '{self.environment_name}'.")

    def verify_environment(self) -> bool:
        """Verify that the environment is properly configured."""
        if not self.python_interpreter:
            print("[VenvEnvironmentManager] Python interpreter not set. Cannot verify environment.")
            return False

        print(f"[VenvEnvironmentManager] Verifying environment '{self.environment_name}'...")

        try:
            python_version_output = subprocess.check_output([self.python_interpreter, '--version'], text=True, stderr=subprocess.STDOUT).strip()
            print(f"[VenvEnvironmentManager] Python interpreter is working: {python_version_output}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"[VenvEnvironmentManager] Python interpreter '{self.python_interpreter}' is not working: {e}")
            return False

        if self.requirements:
            ok, missing = verify_pip_requirements(self.python_interpreter, self.requirements)
            if not ok:
                print(f"[VenvEnvironmentManager] Missing packages: {', '.join(missing)}")
                print(f"[VenvEnvironmentManager] Environment verification failed for '{self.environment_name}'.")
                return False
        
        print(f"[VenvEnvironmentManager] Environment verification successful for '{self.environment_name}'.")
        return True 