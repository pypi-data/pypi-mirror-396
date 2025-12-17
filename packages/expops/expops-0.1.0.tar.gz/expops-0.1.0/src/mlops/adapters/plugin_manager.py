import importlib
import pkgutil
from pathlib import Path
from typing import Dict, Type, Optional
from .base import ModelAdapter, ModelConfig
from .config_schema import AdapterConfig

class AdapterPluginManager:
    """Manages the discovery and loading of model adapters."""
    
    def __init__(self):
        self._adapters: Dict[str, Type[ModelAdapter]] = {}
    
    def discover_adapters(self, package_path: str) -> None:
        """Discover and load all adapter plugins in the given package.

        Tries both the provided path and a 'src.'-prefixed or de-prefixed variant
        to support source-tree layouts (src/mlops) and installed packages (mlops).

        Args:
            package_path: Dotted path to the package containing adapters
                          (e.g., 'mlops.adapters' or 'src.mlops.adapters').
        """
        candidate_paths = [package_path]
        # Add fallback variants for common source layout differences
        if package_path.startswith("src."):
            candidate_paths.append(package_path[len("src."):])
        else:
            candidate_paths.append(f"src.{package_path}")

        for pkg in candidate_paths:
            try:
                package = importlib.import_module(pkg)
            except Exception:
                continue
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
                if not is_pkg:
                    continue
                try:
                    module = importlib.import_module(f"{pkg}.{name}")
                    if hasattr(module, "Adapter"):
                        adapter_class = getattr(module, "Adapter")
                        if issubclass(adapter_class, ModelAdapter):
                            self._adapters[name] = adapter_class
                except Exception as e:
                    print(f"Failed to load adapter {name}: {e}")
    
    def get_adapter(self, name: str) -> Optional[Type[ModelAdapter]]:
        """Get an adapter class by name.
        
        Args:
            name: Name of the adapter
            
        Returns:
            The adapter class if found, None otherwise
        """
        return self._adapters.get(name)
    
    def list_adapters(self) -> Dict[str, Type[ModelAdapter]]:
        """List all available adapters.
        
        Returns:
            Dictionary mapping adapter names to their classes
        """
        return self._adapters.copy()
    
    def create_adapter(self, name: str, config: AdapterConfig, python_interpreter: Optional[str] = None, environment_name: Optional[str] = None, conda_env_name: Optional[str] = None, project_path: Optional[Path] = None) -> Optional[ModelAdapter]:
        """
        Create an adapter by name with the given configuration.
        
        Args:
            name: Name of the adapter.
            config: Configuration for the adapter.
            python_interpreter: Path to the python interpreter in the environment.
            environment_name: Name of the environment (supports all types: conda, venv, etc.).
            conda_env_name: Legacy parameter name for backward compatibility.
            project_path: Path to the project directory for project-specific artifact storage.
        
        Returns:
            An instance of the adapter or None if not found.
        """
        if name not in self._adapters:
            print(f"Adapter '{name}' not found.")
            return None
        
        adapter_class = self._adapters[name]
        
        # Support both new and legacy parameter names
        env_name = environment_name or conda_env_name
        
        # Check if the adapter class supports project_path parameter
        import inspect
        signature = inspect.signature(adapter_class.__init__)
        if 'project_path' in signature.parameters:
            return adapter_class(config, python_interpreter=python_interpreter, environment_name=env_name, conda_env_name=env_name, project_path=project_path)
        else:
            # For backward compatibility with adapters that don't support project_path
            return adapter_class(config, python_interpreter=python_interpreter, environment_name=env_name, conda_env_name=env_name) 