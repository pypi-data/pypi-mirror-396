from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EnvironmentManager(ABC):
    """Abstract base class for environment managers (venv/conda/pyenv/system)."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.environment_name: str | None = None
        self.python_interpreter: str | None = None

    @abstractmethod
    def setup_environment(self) -> None:
        """Set up the environment based on configuration."""
        raise NotImplementedError
    
    @abstractmethod
    def verify_environment(self) -> bool:
        """Verify that the environment is properly configured."""
        raise NotImplementedError
    
    @abstractmethod
    def get_python_interpreter(self) -> str:
        """Get the path to the Python interpreter for this environment."""
        raise NotImplementedError
    
    @abstractmethod
    def get_environment_name(self) -> str:
        """Get the name of the environment."""
        raise NotImplementedError
    
    @abstractmethod
    def environment_exists(self) -> bool:
        """Check if the environment already exists."""
        raise NotImplementedError
    
    @abstractmethod
    def get_environment_type(self) -> str:
        """Return the type of environment manager (conda, pyenv, etc.)."""
        raise NotImplementedError