from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ModelConfig:
    """Configuration for a model adapter."""
    name: str
    framework: str
    language: str
    version: str
    parameters: Dict[str, Any]
    requirements: Dict[str, str]
    hardware_requirements: Optional[Dict[str, Any]] = None

class ModelAdapter(ABC):
    """Base class for all model adapters.
    
    This interface defines the contract that all model adapters must implement.
    It provides methods for training, evaluation, and model management.
    """
    
    def __init__(self, config: ModelConfig, python_interpreter: Optional[str] = None, environment_name: Optional[str] = None, conda_env_name: Optional[str] = None):
        self.config = config
        self.model = None
        self.python_interpreter = python_interpreter
        
        # Support both new and legacy parameter names
        self.environment_name = environment_name or conda_env_name
        # Keep legacy property for backward compatibility
        self.conda_env_name = self.environment_name
        
        if self.python_interpreter:
            print(f"[{self.__class__.__name__}] Initialized with Python interpreter: {self.python_interpreter}")
        
        if self.environment_name:
            print(f"[{self.__class__.__name__}] Initialized with environment: {self.environment_name}")
        else:
            print(f"[{self.__class__.__name__}] Initialized without specific environment")
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the model with the given configuration."""
        pass
    
    @abstractmethod
    def run(self, data_paths: Dict[str, Path] | None = None, **kwargs) -> Dict[str, Any]:
        """Run the pipeline according to the configured processes/steps.
        
        Args:
            data_paths: Optional mapping of named data roles to paths (e.g., {"training": Path(...), "validation": Path(...)}).
            **kwargs: Additional parameters forwarded to the adapter/pipeline.
            
        Returns:
            Dictionary containing pipeline results and/or metrics.
        """
        pass
    
    @abstractmethod
    def save(self, path: Path) -> None:
        """Save the model to the specified path."""
        pass
    
    @abstractmethod
    def load(self, path: Path) -> None:
        """Load the model from the specified path."""
        pass
    
    # Optional prediction interface for adapters that expose direct predict APIs
    def predict(self, data: Any) -> Any:
        """Optional: Make predictions using the model if supported by the adapter."""
        raise NotImplementedError("This adapter does not implement a direct predict() API.")
    
    @classmethod
    @abstractmethod
    def validate_config(cls, config: ModelConfig) -> bool:
        """Validate the configuration for this adapter.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        pass 