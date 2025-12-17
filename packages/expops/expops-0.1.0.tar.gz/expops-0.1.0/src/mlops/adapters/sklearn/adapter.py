from pathlib import Path
from typing import Any, Dict, Optional
import joblib
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.model_selection import train_test_split
import importlib

from ..base import ModelAdapter
from ..config_schema import AdapterConfig

class Adapter(ModelAdapter):
    """Adapter for scikit-learn models."""
    
    def __init__(self, config: AdapterConfig, python_interpreter: Optional[str] = None, environment_name: Optional[str] = None, conda_env_name: Optional[str] = None):
        super().__init__(config, python_interpreter=python_interpreter, environment_name=environment_name, conda_env_name=conda_env_name)
        self.model: BaseEstimator = None
    
    def initialize(self) -> None:
        """Initialize the scikit-learn model."""
        module_name, class_name_val = self.config.parameters.class_name.rsplit('.', 1)
        try:
            ModelClass = getattr(importlib.import_module(module_name), class_name_val)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Could not import class_name '{self.config.parameters.class_name}': {e}")

        if not issubclass(ModelClass, BaseEstimator):
            raise ValueError(f"class_name '{self.config.parameters.class_name}' must be a scikit-learn BaseEstimator.")

        model_hyperparams = self.config.parameters.hyperparameters if self.config.parameters.hyperparameters is not None else {}
        self.model = ModelClass(**model_hyperparams)
    
    def run(self, data_paths: Dict[str, Path] | None = None, **kwargs) -> Dict[str, Any]:
        """Run a minimal fit/evaluate loop depending on provided data paths."""
        if self.model is None:
            self.initialize()

        data_paths = data_paths or {}
        results: Dict[str, Any] = {}

        def _load_xy(csv_path: Path):
            import pandas as pd
            df = pd.read_csv(csv_path)
            if 'label' not in df.columns:
                raise ValueError("Target column 'label' not found in the CSV.")
            X = df.drop('label', axis=1).values
            y = df['label'].values
            return X, y

        if 'training' in data_paths and data_paths['training'] is not None:
            X, y = _load_xy(data_paths['training'])
            self.model.fit(X, y)
            results['model_type'] = self.model.__class__.__name__
            results['parameters'] = self.model.get_params()

        if 'validation' in data_paths and data_paths['validation'] is not None:
            Xv, yv = _load_xy(data_paths['validation'])
            results['validation_score'] = self.model.score(Xv, yv)

        return results
    
    def save(self, path: Path) -> None:
        """Save the scikit-learn model."""
        if self.model is None:
            raise ValueError("No model to save")
        path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path / "model.joblib")
    
    def load(self, path: Path) -> None:
        """Load the scikit-learn model."""
        self.model = joblib.load(path / "model.joblib")
    
    def predict(self, data: Any) -> Any:
        """Make predictions using the scikit-learn model."""
        if self.model is None:
            raise ValueError("Model not initialized")
        return self.model.predict(data)
    
    @classmethod
    def validate_config(cls, config: AdapterConfig) -> bool:
        """Validate the configuration for this adapter."""
        if not hasattr(config, 'parameters') or config.parameters is None:
            print("Validation failed: config has no parameters attribute or it is None")
            return False

        if not hasattr(config.parameters, 'class_name') or not isinstance(config.parameters.class_name, str) or not config.parameters.class_name:
            print(f"Validation failed: class_name issue. Has attr: {hasattr(config.parameters, 'class_name')}, Is str: {isinstance(config.parameters.class_name, str) if hasattr(config.parameters, 'class_name') else 'N/A'}, Value: {config.parameters.class_name if hasattr(config.parameters, 'class_name') else 'N/A'}")
            return False

        if not hasattr(config.parameters, 'hyperparameters') or not isinstance(config.parameters.hyperparameters, dict):
            print(f"Validation failed: hyperparameters issue. Has attr: {hasattr(config.parameters, 'hyperparameters')}, Is dict: {isinstance(config.parameters.hyperparameters, dict) if hasattr(config.parameters, 'hyperparameters') else 'N/A'}")
            return False
            
        return True 