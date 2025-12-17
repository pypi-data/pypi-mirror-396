from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

from .base import EnvironmentManager
from .utils import verify_pip_requirements


class CondaEnvironmentManager(EnvironmentManager):
    """Conda-based environment management."""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.dependencies = self._load_dependencies(config)
        
        env_name = config.get("name")
        if not env_name:
            raise ValueError(
                "Conda environment name must be explicitly specified in the configuration. "
                "Please add 'name' field under 'environment.conda' in your config file."
            )
        self.environment_name = env_name

    def _load_dependencies(self, config: dict[str, Any]) -> list[Any]:
        """Load dependencies from inline config or environment.yml file."""
        # Option 1: Inline dependencies
        if "dependencies" in config:
            print("[CondaEnvironmentManager] Using inline dependencies from config.")
            return config["dependencies"]
        
        # Option 2: From conda environment.yml file
        if "environment_file" in config:
            env_file_path = Path(config["environment_file"])
            if not env_file_path.exists():
                raise FileNotFoundError(f"Environment file not found: {env_file_path}")
            
            print(f"[CondaEnvironmentManager] Loading dependencies from environment file: {env_file_path}")
            with open(env_file_path, 'r') as f:
                env_data = yaml.safe_load(f)
            
            if "dependencies" not in env_data:
                raise ValueError(f"No 'dependencies' section found in {env_file_path}")
            
            return env_data["dependencies"]
        
        print("[CondaEnvironmentManager] No dependencies specified.")
        return []

    def get_environment_type(self) -> str:
        return "conda"

    def get_environment_name(self) -> str:
        return self.environment_name

    def get_python_interpreter(self) -> str:
        if not self.python_interpreter:
            raise RuntimeError("Environment not set up yet. Call setup_environment() first.")
        return self.python_interpreter

    def _get_conda_base_prefix(self) -> str | None:
        """Attempts to find the Conda base prefix."""
        try:
            result = subprocess.run(["conda", "info", "--json"], capture_output=True, text=True, check=True)
            conda_info = json.loads(result.stdout)
            return conda_info.get("root_prefix") or conda_info.get("conda_prefix")
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[CondaEnvironmentManager] Could not get conda info: {e}")
            conda_exe_path = os.environ.get("CONDA_EXE")
            if conda_exe_path:
                return str(Path(conda_exe_path).parent.parent)
        return None

    def _get_conda_executable(self) -> str:
        """Determines the path to the conda executable."""
        conda_exe = "conda"
        conda_base = self._get_conda_base_prefix()
        if conda_base:
            specific_conda_exe = Path(conda_base) / "bin" / "conda"
            if specific_conda_exe.exists():
                conda_exe = str(specific_conda_exe)
            else: # Try Scripts for Windows
                specific_conda_exe_win = Path(conda_base) / "Scripts" / "conda.exe"
                if specific_conda_exe_win.exists():
                    conda_exe = str(specific_conda_exe_win)
        
        try:
            subprocess.run([conda_exe, "--version"], capture_output=True, check=True, text=True)
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            raise RuntimeError(
                f"Conda executable ('{conda_exe}') not found or not runnable. "
                "Please ensure Conda is installed and configured correctly in your PATH. "
                f"Error: {e}"
            )
        return conda_exe

    def environment_exists(self) -> bool:
        """Check if the conda environment already exists."""
        try:
            conda_exe = self._get_conda_executable()
            result = subprocess.run([conda_exe, "env", "list", "--json"], capture_output=True, text=True, check=True)
            env_list = json.loads(result.stdout).get("envs", [])
            return any(Path(env_path).name == self.environment_name for env_path in env_list)
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"[CondaEnvironmentManager] Failed to list Conda environments: {e}")
            return False

    @staticmethod
    def _python_path(env_path: Path) -> Path:
        if os.name == "nt":
            return env_path / "python.exe"
        return env_path / "bin" / "python"

    def setup_environment(self) -> None:
        """Set up the conda environment based on configuration."""
        print(f"[CondaEnvironmentManager] Starting Conda environment setup for '{self.environment_name}'...")
        
        if not self.dependencies:
            print("[CondaEnvironmentManager] No dependencies specified. Using current environment.")
            self.python_interpreter = sys.executable
            return

        conda_exe = self._get_conda_executable()

        if not self.environment_exists():
            print(f"[CondaEnvironmentManager] Environment '{self.environment_name}' not found. Creating it...")
            
            env_yaml_content = {"name": self.environment_name, "dependencies": self.dependencies}
            
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp_env_file:
                yaml.dump(env_yaml_content, tmp_env_file)
                tmp_env_file_path = tmp_env_file.name
            
            try:
                print(f"[CondaEnvironmentManager] Creating environment from temporary file: {tmp_env_file_path}")
                cmd_libmamba = [conda_exe, "env", "create", "-f", tmp_env_file_path, "-q", "--solver=libmamba"]
                res = subprocess.run(cmd_libmamba, capture_output=True, text=True)

                cmd_used = cmd_libmamba
                if res.returncode != 0:
                    stderr_lower = (res.stderr or "").lower()
                    if "libmamba" in stderr_lower or "invalid choice" in stderr_lower:
                        print("[CondaEnvironmentManager] libmamba solver not available, falling back to classic solver...")
                        cmd_classic = [conda_exe, "env", "create", "-f", tmp_env_file_path, "-q"]
                        res = subprocess.run(cmd_classic, capture_output=True, text=True)
                        cmd_used = cmd_classic

                if res.returncode != 0:
                    error_message = (
                        f"Failed to create Conda environment '{self.environment_name}'. Return code: {res.returncode}\n"
                        f"Command: {' '.join(cmd_used)}\n"
                        f"Stdout:\n{res.stdout}\n"
                        f"Stderr:\n{res.stderr}"
                    )
                    raise RuntimeError(error_message)
                
                print(f"[CondaEnvironmentManager] Environment '{self.environment_name}' created successfully.")
            finally:
                try:
                    os.remove(tmp_env_file_path)
                except OSError:
                    print(f"[CondaEnvironmentManager] Warning: Could not remove temporary env file {tmp_env_file_path}")
        else:
            print(f"[CondaEnvironmentManager] Using existing environment: '{self.environment_name}'")

        # Set up Python interpreter path
        try:
            info_result = subprocess.run([conda_exe, "info", "--envs", "--json"], capture_output=True, text=True, check=True)
            envs_info = json.loads(info_result.stdout).get("envs", [])
            env_path_str = next((p for p in envs_info if Path(p).name == self.environment_name), None)

            if not env_path_str: 
                conda_base = self._get_conda_base_prefix()
                if conda_base:
                    env_path_str = str(Path(conda_base) / "envs" / self.environment_name)
                else: 
                    env_path_str = self.environment_name

            env_path = Path(env_path_str)
            if not env_path.exists():
                raise RuntimeError(
                    f"Could not determine path for environment '{self.environment_name}'. "
                    f"Path '{env_path_str}' does not exist."
                )

            self.python_interpreter = str(self._python_path(env_path))
            
            if not Path(self.python_interpreter).exists():
                raise FileNotFoundError(f"Python interpreter not found in environment '{self.environment_name}' at expected path: {self.python_interpreter}")

        except (subprocess.CalledProcessError, json.JSONDecodeError, StopIteration, FileNotFoundError) as e:
            raise RuntimeError(f"Failed to determine Python interpreter for environment '{self.environment_name}': {e}")

        print(f"[CondaEnvironmentManager] Python interpreter: {self.python_interpreter}")
        print(f"[CondaEnvironmentManager] Environment setup completed for '{self.environment_name}'.")

    def verify_environment(self) -> bool:
        """Verify that the environment is properly configured."""
        if not self.python_interpreter:
            print("[CondaEnvironmentManager] Python interpreter not set. Cannot verify environment.")
            return False

        print(f"[CondaEnvironmentManager] Verifying environment '{self.environment_name}'...")

        if not self.dependencies:
            print("[CondaEnvironmentManager] No dependencies to verify. Skipping verification.")
            return True

        # Verify that the Python interpreter exists and works
        try:
            python_version_output = subprocess.check_output([self.python_interpreter, '--version'], text=True, stderr=subprocess.STDOUT).strip()
            print(f"[CondaEnvironmentManager] Python interpreter is working: {python_version_output}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"[CondaEnvironmentManager] Python interpreter '{self.python_interpreter}' is not working: {e}")
            return False

        # Verify Python version if specified
        python_version_config = next(
            (d for d in (self.dependencies or []) if isinstance(d, str) and d.startswith("python=")),
            None,
        )
        if isinstance(python_version_config, str) and python_version_config.startswith("python="):
            expected_py_ver = python_version_config.split("=")[1]
            try:
                current_py_ver_full = subprocess.check_output([self.python_interpreter, '--version'], text=True, stderr=subprocess.STDOUT).strip()
                current_py_ver_parts = current_py_ver_full.split()
                current_py_ver = current_py_ver_parts[-1] if current_py_ver_parts else ""
                
                if '.' in expected_py_ver:
                    expected_parts = expected_py_ver.split('.')
                    current_parts = current_py_ver.split('.')
                    if len(expected_parts) <= len(current_parts):
                        match = all(expected_parts[i] == current_parts[i] for i in range(len(expected_parts)))
                        if not match:
                            print(f"[CondaEnvironmentManager] Python version mismatch. Expected prefix: {expected_py_ver}, Found: {current_py_ver}")
                            return False
                    else: 
                        print(f"[CondaEnvironmentManager] Python version precision mismatch. Expected: {expected_py_ver}, Found: {current_py_ver}")
                        return False
                elif current_py_ver != expected_py_ver:
                    print(f"[CondaEnvironmentManager] Python version mismatch. Expected: {expected_py_ver}, Found: {current_py_ver}")
                    return False
                print(f"[CondaEnvironmentManager] Python version OK: {current_py_ver} (matches expected: {expected_py_ver})")

            except subprocess.CalledProcessError as e:
                print(f"[CondaEnvironmentManager] Could not verify Python version: {e.output if hasattr(e, 'output') else e}")
                return False
        
        # Basic package verification (simplified for now)
        verification_failed = False
        
        for package_entry in self.dependencies:
            if isinstance(package_entry, dict) and "pip" in package_entry:
                pip_specs = package_entry.get("pip") or []
                if isinstance(pip_specs, list):
                    ok, missing = verify_pip_requirements(self.python_interpreter, [str(x) for x in pip_specs])
                    if not ok:
                        print(f"[CondaEnvironmentManager] Missing pip packages: {', '.join(missing)}")
                        verification_failed = True
            elif isinstance(package_entry, str) and ("==" in package_entry or "=" in package_entry):
                try:
                    # Support both conda-style `pkg=1.2` and pip-style `pkg==1.2`
                    if "==" in package_entry:
                        name, version = package_entry.split("==", 1)
                    else:
                        name, version = package_entry.split("=", 1)
                    name = name.split("::")[-1].strip()
                    if name == "python":
                        continue
                    
                    conda_exe = self._get_conda_executable()
                    conda_list_cmd = [conda_exe, "list", "-n", self.environment_name, name, "--json"]
                    result = subprocess.run(conda_list_cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        package_info_list = json.loads(result.stdout)
                        if package_info_list:
                            installed_version = package_info_list[0].get("version", "")
                            if installed_version == version:
                                print(f"[CondaEnvironmentManager] Package {name} (conda) found with correct version {version}.")
                            else:
                                print(f"[CondaEnvironmentManager] Package {name} (conda) version mismatch. Expected: {version}, Found: {installed_version}.")
                                verification_failed = True
                        else:
                            print(f"[CondaEnvironmentManager] Package {name} (conda) not found.")
                            verification_failed = True
                    else:
                        print(f"[CondaEnvironmentManager] Package {name} verification failed.")
                        verification_failed = True
                
                except Exception as e:
                    print(f"[CondaEnvironmentManager] Error verifying package {name}: {e}")
                    verification_failed = True
        
        if verification_failed:
            print(f"[CondaEnvironmentManager] Environment verification failed for '{self.environment_name}'.")
            return False
        
        print(f"[CondaEnvironmentManager] Environment verification successful for '{self.environment_name}'.")
        return True 