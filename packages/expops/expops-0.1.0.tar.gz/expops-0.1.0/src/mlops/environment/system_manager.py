from __future__ import annotations

import subprocess
import sys
from typing import Any

from .base import EnvironmentManager
from .utils import load_requirements, verify_pip_requirements


class SystemEnvironmentManager(EnvironmentManager):
    """System Python environment management (no virtual environment)."""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.requirements = load_requirements(config)
        self.environment_name = "system"
        self.python_interpreter = sys.executable

    def get_environment_type(self) -> str:
        return "system"

    def get_environment_name(self) -> str:
        return self.environment_name

    def get_python_interpreter(self) -> str:
        return self.python_interpreter

    def environment_exists(self) -> bool:
        """System environment always exists."""
        return True

    def setup_environment(self) -> None:
        """Set up using the system Python environment."""
        print(f"[SystemEnvironmentManager] Using system Python environment...")
        
        if self.requirements:
            print(f"[SystemEnvironmentManager] Installing requirements to system Python...")
            try:
                pip_install_cmd = [self.python_interpreter, "-m", "pip", "install"] + self.requirements
                subprocess.run(pip_install_cmd, check=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to install requirements to system Python: {e}")

        print(f"[SystemEnvironmentManager] Python interpreter: {self.python_interpreter}")

    def verify_environment(self) -> bool:
        """Verify that the system environment is properly configured."""
        print(f"[SystemEnvironmentManager] Verifying system Python environment...")

        try:
            python_version_output = subprocess.check_output([self.python_interpreter, '--version'], text=True, stderr=subprocess.STDOUT).strip()
            print(f"[SystemEnvironmentManager] Python interpreter is working: {python_version_output}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"[SystemEnvironmentManager] Python interpreter '{self.python_interpreter}' is not working: {e}")
            return False

        if self.requirements:
            ok, missing = verify_pip_requirements(self.python_interpreter, self.requirements)
            if not ok:
                print(f"[SystemEnvironmentManager] Missing packages: {', '.join(missing)}")
                print(f"[SystemEnvironmentManager] Environment verification failed for system Python.")
                return False
        
        print(f"[SystemEnvironmentManager] Environment verification successful for system Python.")
        return True 