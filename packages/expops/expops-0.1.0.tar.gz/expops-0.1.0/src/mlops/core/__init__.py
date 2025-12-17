"""
MLOps Core Module (lazy-loading)

Provides the core components for the NetworkX-based pipeline execution system.
Heavy submodules are imported lazily on attribute access to minimize required
runtime dependencies for lightweight utilities (e.g., pipeline_utils).
"""

from typing import Any
import importlib

__all__ = [
    # step_system exports
    "step",
    "process",
    "StepContext",
    "StepContextFactory",
    "StepDefinition",
    "StepRegistry",
    "ProcessDefinition",
    "ProcessRegistry",
    "get_step_registry",
    "get_process_registry",
    "get_current_context",
    "set_current_context",
    "get_context_factory",
    "set_current_process_context",
    "get_current_process_context",
    "get_parameter_resolver",
    "set_state_manager",
    "get_state_manager",
    "log_metric",
    "SerializableData",
    "ModelData",
    # custom model
    "MLOpsCustomModelBase",
    # graph types + parser
    "NetworkXGraphConfig",
    "ProcessConfig",
    "StepConfig",
    "ExecutionResult",
    "NodeType",
    "NetworkXPipelineParser",
    "parse_networkx_pipeline_from_config",
    # state manager
    "StepStateManager",
]

_lazy_attr_to_module = {
    "step": ("mlops.core.step_system", "step"),
    "process": ("mlops.core.step_system", "process"),
    "StepContext": ("mlops.core.step_system", "StepContext"),
    "StepContextFactory": ("mlops.core.step_system", "StepContextFactory"),
    "StepDefinition": ("mlops.core.step_system", "StepDefinition"),
    "StepRegistry": ("mlops.core.step_system", "StepRegistry"),
    "ProcessDefinition": ("mlops.core.step_system", "ProcessDefinition"),
    "ProcessRegistry": ("mlops.core.step_system", "ProcessRegistry"),
    "get_step_registry": ("mlops.core.step_system", "get_step_registry"),
    "get_process_registry": ("mlops.core.step_system", "get_process_registry"),
    "get_current_context": ("mlops.core.step_system", "get_current_context"),
    "set_current_context": ("mlops.core.step_system", "set_current_context"),
    "get_context_factory": ("mlops.core.step_system", "get_context_factory"),
    "set_current_process_context": ("mlops.core.step_system", "set_current_process_context"),
    "get_current_process_context": ("mlops.core.step_system", "get_current_process_context"),
    "get_parameter_resolver": ("mlops.core.step_system", "get_parameter_resolver"),
    "set_state_manager": ("mlops.core.step_system", "set_state_manager"),
    "get_state_manager": ("mlops.core.step_system", "get_state_manager"),
    "log_metric": ("mlops.core.step_system", "log_metric"),
    "SerializableData": ("mlops.core.step_system", "SerializableData"),
    "ModelData": ("mlops.core.step_system", "ModelData"),
    # custom model base
    "MLOpsCustomModelBase": ("mlops.core.custom_model_base", "MLOpsCustomModelBase"),
    # graph types + parser
    "NetworkXGraphConfig": ("mlops.core.graph_types", "NetworkXGraphConfig"),
    "ProcessConfig": ("mlops.core.graph_types", "ProcessConfig"),
    "StepConfig": ("mlops.core.graph_types", "StepConfig"),
    "ExecutionResult": ("mlops.core.graph_types", "ExecutionResult"),
    "NodeType": ("mlops.core.graph_types", "NodeType"),
    "NetworkXPipelineParser": ("mlops.core.networkx_parser", "NetworkXPipelineParser"),
    "parse_networkx_pipeline_from_config": ("mlops.core.networkx_parser", "parse_networkx_pipeline_from_config"),
    # state manager
    "StepStateManager": ("mlops.core.step_state_manager", "StepStateManager"),
}


def __getattr__(name: str) -> Any:
    if name in _lazy_attr_to_module:
        module_name, attr_name = _lazy_attr_to_module[name]
        module = importlib.import_module(module_name)
        return getattr(module, attr_name)
    raise AttributeError(f"module 'mlops.core' has no attribute '{name}'")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + __all__) 