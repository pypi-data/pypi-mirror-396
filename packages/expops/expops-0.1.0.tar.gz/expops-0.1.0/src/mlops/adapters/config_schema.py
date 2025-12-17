from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, ConfigDict

class HardwareRequirements(BaseModel):
    """Hardware requirements for model training."""
    gpu: bool = False
    min_memory_gb: Optional[float] = None
    min_cpu_cores: Optional[int] = None

class ModelParameters(BaseModel):
    """Model-specific parameters."""
    class_name: Optional[str] = Field(None, description="Fully qualified class name of the model (for pre-built frameworks)")
    custom_script_path: Optional[str] = Field(None, description="Path to the custom Python script (relative to project root or absolute)")
    custom_target: Optional[str] = Field(None, description="(Optional) Name of the class or function within the custom script. If not provided, the adapter will look for a MLOpsCustomModelBase subclass.")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict, description="Model initialization parameters")
    training_params: Dict[str, Any] = Field(default_factory=dict, description="Training-specific parameters")
    # Caching and execution
    cache: Dict[str, Any] = Field(default_factory=dict, description="Caching configuration (ttl_hours, backend, object_store)")
    executor: Dict[str, Any] = Field(default_factory=dict, description="Executor configuration (n_workers, scheduler_address)")
    
    # NetworkX pipeline configuration - supports process-level DAGs with step-level loops
    pipeline: Optional[Dict[str, Any]] = Field(None, description="NetworkX pipeline configuration with processes and steps")

class AdapterConfig(BaseModel):
    """Configuration for a model adapter."""
    name: str = Field(..., description="Name of the model")
    framework: str = Field(..., description="ML framework (e.g., sklearn, pytorch, tensorflow, custom)")
    language: str = Field(..., description="Programming language (e.g., python, cpp)")
    version: str = Field(..., description="Version of the framework or custom model")
    parameters: ModelParameters = Field(..., description="Model-specific parameters")
    requirements: Dict[str, str] = Field(
        default_factory=dict,
        description="Package requirements (package_name: version)"
    )
    hardware_requirements: Optional[HardwareRequirements] = Field(
        None,
        description="Hardware requirements for training"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "custom_model_with_loops",
                "framework": "custom",
                "language": "python",
                "version": "1.0.0",
                "parameters": {
                    "custom_script_path": "examples/custom_models/networkx_examples/models/kmeans_model.py",
                    "custom_target": "KMeansCustomModel",
                    "hyperparameters": {
                        "n_clusters": 3,
                        "max_iterations": 100,
                        "convergence_threshold": 0.001
                    },
                    # NetworkX pipeline configuration with process-level DAGs and step-level loops
                    "pipeline": {
                        "process_adjlist": "data_prep clustering\nclustering evaluation",
                        "processes": [
                            {"name": "data_prep", "max_iterations": 1},
                            {"name": "clustering", "max_iterations": 100, "convergence_threshold": 0.001},
                            {"name": "evaluation", "max_iterations": 1}
                        ],
                        "steps": [
                            {"name": "preprocess_data", "process": "data_prep"},
                            {"name": "initialize_centroids", "process": "clustering"},
                            {"name": "update_centroids", "process": "clustering", "loop_back_to": "assign_clusters"},
                            {"name": "assign_clusters", "process": "clustering", "depends_on": ["update_centroids"], "loop_back_to": "update_centroids"},
                            {"name": "evaluate_clustering", "process": "evaluation", "depends_on": ["assign_clusters"]}
                        ],
                        "execution": {
                            "parallel": True,
                            "failure_mode": "stop_and_resume",
                            "max_workers": 4
                        }
                    }
                },
                "requirements": {
                    "networkx": "3.0",
                    "numpy": "1.24.0",
                    "scikit-learn": "1.3.0"
                },
                "hardware_requirements": {
                    "gpu": False,
                    "min_memory_gb": 4.0,
                    "min_cpu_cores": 2
                }
            }
        }
    ) 