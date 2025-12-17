from __future__ import annotations

from typing import Any

from .base import EnvironmentManager
from .conda_manager import CondaEnvironmentManager
from .venv_manager import VenvEnvironmentManager
from .system_manager import SystemEnvironmentManager
from .pyenv_manager import PyenvEnvironmentManager


class EnvironmentManagerFactory:
    """Factory for creating environment managers based on configuration."""
    
    _managers: dict[str, type[EnvironmentManager]] = {
        "conda": CondaEnvironmentManager,
        "venv": VenvEnvironmentManager,
        "virtualenv": VenvEnvironmentManager,
        "pyenv": PyenvEnvironmentManager,
        "system": SystemEnvironmentManager,
    }
    
    @classmethod
    def create_environment_manager(cls, platform_config: dict[str, Any]) -> EnvironmentManager:
        """Create an environment manager based on the platform configuration."""
        env_config = platform_config.get("environment")
        if not isinstance(env_config, dict) or not env_config:
            return SystemEnvironmentManager({})

        env_type, env_specific_config = cls._select_manager(env_config)
        manager_class = cls._managers.get(env_type)
        if manager_class is None:
            raise ValueError(
                f"Unsupported environment type: {env_type}. Supported types: {sorted(cls._managers.keys())}"
            )
        return manager_class(env_specific_config)

    @classmethod
    def _select_manager(cls, env_config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        # Primary form:
        #   environment: { venv: {...} } or { conda: {...} } etc.
        for supported_type in cls._managers:
            if supported_type in env_config:
                raw = env_config.get(supported_type)
                return supported_type, raw if isinstance(raw, dict) else {}

        # Legacy fallbacks where `environment:` contains the manager's config directly.
        if any(k in env_config for k in ("dependencies", "environment_file")):
            return "conda", env_config
        if any(k in env_config for k in ("requirements", "requirements_file")):
            return "venv", env_config

        return "system", env_config
    
    @classmethod
    def list_supported_types(cls) -> list[str]:
        """List all supported environment types."""
        return list(cls._managers.keys())
    
    @classmethod
    def register_manager(cls, env_type: str, manager_class: type[EnvironmentManager]) -> None:
        """Register a new environment manager type."""
        if not issubclass(manager_class, EnvironmentManager):
            raise ValueError(f"Manager class must inherit from EnvironmentManager")
        cls._managers[env_type] = manager_class


def create_environment_manager(platform_config: dict[str, Any]) -> EnvironmentManager:
    """Convenience function to create an environment manager."""
    return EnvironmentManagerFactory.create_environment_manager(platform_config) 