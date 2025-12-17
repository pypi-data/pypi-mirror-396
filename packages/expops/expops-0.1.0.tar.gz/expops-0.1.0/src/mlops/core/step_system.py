from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
import joblib
import time
from datetime import datetime
import logging
from functools import wraps
import contextvars

from .payload_spill import hydrate_payload_refs

SerializableData = Union[
    str, int, float, bool,
    List[Union[str, int, float, bool]],
    Dict[str, Union[str, int, float, bool]],
    None
]

ModelData = Any

class StepContext:
    """Simplified context object for steps."""
    
    def __init__(self, 
                 project_id: str,
                 run_id: str = None,
                 tracker: Any = None,
                 step_results: Dict[str, Dict[str, Any]] = None,
                 global_config: Dict[str, Any] = None,
                 data_paths: Dict[str, Path] = None,
                 checkpoint_dir: Optional[Path] = None):
        self.project_id = project_id
        self.run_id = run_id
        self.tracker = tracker
        self.step_results = step_results or {}
        self.global_config = global_config or {}
        self.data_paths = data_paths or {}
        self.shared_state = {}
        self.checkpoint_dir = checkpoint_dir or Path("artifacts/checkpoints")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.iteration = 0
        # Name of the process currently being executed; used for resolving per-process settings
        self.current_process: Optional[str] = None

    def _hydrate_payload(self, payload: Any) -> Any:
        try:
            sm = get_state_manager()
        except Exception:
            sm = None
        try:
            return hydrate_payload_refs(payload, sm)
        except Exception:
            return payload

    def _resolve_process_for_step(self, step_name: str) -> Optional[str]:
        try:
            pr = get_process_registry()
            return pr.get_process_for_step(step_name) if pr else None
        except Exception:
            return None
        
    def get_step_result(self, step_name: str) -> Optional[Dict[str, Any]]:
        """Get result from a previously executed step (returns data dictionary)."""
        result = self.step_results.get(step_name)
        if result is None and getattr(self, 'run_id', None):
            try:
                sm = get_state_manager()
            except Exception:
                sm = None
            if sm:
                try:
                    cached = sm.get_cached_step_result(
                        run_id=self.run_id,
                        step_name=step_name,
                        process_name=self._resolve_process_for_step(step_name),
                        input_hash=None,
                        config_hash=None,
                        function_hash=None,
                    )
                    if cached:
                        self.step_results[step_name] = cached
                        result = cached
                except Exception:
                    pass
        if result is None:
            return None
        hydrated = self._hydrate_payload(result)
        if hydrated is not result:
            self.step_results[step_name] = hydrated
        return hydrated
        
    def get_step_data(self, step_name: str, data_key: str, process_name: Optional[str] = None) -> Any:
        """Get specific data output from a previous step.

        In distributed mode, if the step result is not present in the in-memory
        context (e.g., from a prior process executed on a different worker), this
        method attempts to load the step result from the cache for the current run
        and hydrate it into the context for subsequent accesses.
        """
        step_result = self.get_step_result(step_name)
        if isinstance(step_result, dict):
            try:
                return step_result.get(data_key)
            except Exception:
                return None
        return None

    def get_process_data(self, process_name: str, data_key: str) -> Any:
        """Get specific data output returned by a previous process.

        Falls back to loading the process result from cache for this run when
        not available in memory (distributed mode).
        """
        try:
            proc_result = self.step_results.get(process_name)
        except Exception:
            proc_result = None
        if proc_result and isinstance(proc_result, dict):
            hydrated = self._hydrate_payload(proc_result)
            if hydrated is not proc_result:
                self.step_results[process_name] = hydrated
            try:
                return hydrated.get(data_key)
            except Exception:
                return None

        # Not present in memory, try cache
        try:
            sm = get_state_manager()
        except Exception:
            sm = None
        if sm and getattr(self, 'run_id', None):
            try:
                # Generic cached lookup via known API
                loaded = sm.get_cached_process_result(process_name, input_hash=None, config_hash=None, function_hash=None)
                if loaded:
                    self.step_results[process_name] = loaded
                    hydrated = self._hydrate_payload(loaded)
                    if hydrated is not loaded:
                        self.step_results[process_name] = hydrated
                    try:
                        return hydrated.get(data_key)
                    except Exception:
                        return None
            except Exception:
                return None
        return None
        
    def log_metric(self, key: str, value: Any, step: Optional[int] = None) -> None:
        """Log a metric with MLflow-style step tracking.
        
        Args:
            key: Metric name
            value: Metric value. Numeric values are tracked per step; non-numeric values
                (e.g., lists, dicts) are stored as last-snapshot under a shadow key
                with "__last" suffix in the KV store.
            step: Step number (if None, auto-increments from largest existing step).
        """
        # Enforce logging flag from current step/process
        try:
            from .step_system import (
                get_current_process_context as _get_cproc,
                get_current_step_context as _get_cstep,
                get_step_registry as _get_sreg,
                get_process_registry as _get_preg,
            )
            cur_step = _get_cstep()
            cur_proc = _get_cproc()
            if cur_step:
                try:
                    sdef = _get_sreg().get_step(cur_step)
                    if sdef is not None and (getattr(sdef, 'logging', True) is False):
                        raise RuntimeError(f"Metric logging is disabled for step '{cur_step}' (logging=False).")
                except Exception:
                    pass
            if cur_proc:
                try:
                    pdef = _get_preg().get_process(cur_proc)
                    if pdef is not None and (getattr(pdef, 'logging', True) is False):
                        raise RuntimeError(f"Metric logging is disabled for process '{cur_proc}' (logging=False).")
                except Exception:
                    pass
        except RuntimeError:
            # Re-raise explicit logging disabled errors
            raise
        except Exception:
            # On any inspection failure, fall through and attempt to log
            pass

        
        try:
            from .step_system import get_state_manager, get_current_process_context, get_current_step_context
            state_manager = get_state_manager()
            if state_manager and self.run_id:
                process_name = get_current_process_context()
                step_name = get_current_step_context()
                try:
                    import logging as _logging
                    _logger = _logging.getLogger(__name__)
                    kv_cls = type(getattr(state_manager, 'kv_store', None)).__name__ if getattr(state_manager, 'kv_store', None) is not None else 'None'
                    _logger.info(f"[Metrics] log_metric call -> run_id={self.run_id}, process={process_name}, step={step_name}, key={key}, step_idx={step if step is not None else 'auto'}, kv_store={kv_cls}")
                except Exception:
                    pass
                state_manager.log_metric(
                    run_id=self.run_id,
                    process_name=process_name,
                    step_name=step_name,
                    metric_name=key,
                    value=value,
                    step=step
                )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to log metric to KV store: {e}")
            
    def log_param(self, key: str, value: Union[int, float, str, bool]) -> None:
        """Log a parameter to the experiment tracker."""
        if self.tracker:
            self.tracker.log_param(key, value)

    def load_checkpoint(self, checkpoint_path: str) -> Dict[str, Any]:
        """Load a checkpoint from the given path."""
        try:
            checkpoint_data = joblib.load(checkpoint_path)
            print(f"[Checkpoint] Model loaded from: {checkpoint_path}")
            return checkpoint_data
        except Exception as e:
            print(f"[Checkpoint] Failed to load checkpoint {checkpoint_path}: {e}")
            raise

    def get_hyperparameters(self, process_name: Optional[str] = None) -> Dict[str, Any]:
        """Return hyperparameters with per-process overrides taking precedence.

        Resolution order (later overrides earlier):
        1) Global hyperparameters from context (supports both legacy and current layouts)
        2) Process-specific hyperparameters from pipeline.processes[name].hyperparameters
        Args:
            process_name: Explicit process name; if None, uses context.current_process
        Returns:
            Merged hyperparameters dict
        """
        try:
            # Support current layout (parameters model dumped directly) and legacy layout nested under model.parameters
            global_hp = {}
            try:
                if isinstance(self.global_config, dict):
                    if 'hyperparameters' in self.global_config:
                        maybe = self.global_config.get('hyperparameters')
                        if isinstance(maybe, dict):
                            global_hp = dict(maybe)
                    elif 'model' in self.global_config:
                        maybe = (
                            self.global_config.get('model', {})
                            .get('parameters', {})
                            .get('hyperparameters', {})
                        )
                        if isinstance(maybe, dict):
                            global_hp = dict(maybe)
            except Exception:
                global_hp = {}

            proc_hp = {}
            try:
                proc = process_name or getattr(self, 'current_process', None)
                pipeline_cfg = self.global_config.get('pipeline') if isinstance(self.global_config, dict) else None
                processes_list = (pipeline_cfg or {}).get('processes') if isinstance(pipeline_cfg, dict) else None
                if isinstance(processes_list, list) and proc:
                    for p in processes_list:
                        try:
                            if isinstance(p, dict) and p.get('name') == proc:
                                maybe = p.get('hyperparameters')
                                if isinstance(maybe, dict):
                                    proc_hp = dict(maybe)
                                break
                        except Exception:
                            continue
            except Exception:
                proc_hp = {}

            merged = {}
            try:
                merged.update(global_hp)
            except Exception:
                pass
            try:
                merged.update(proc_hp)
            except Exception:
                pass
            return merged
        except Exception:
            return {}


class StepContextFactory:
    """
    Singleton factory for managing StepContext instances.
    
    This factory ensures that each project has a unique context instance
    and provides automatic context management for steps.
    """
    
    _instance = None
    _contexts: Dict[str, StepContext] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def create_context(self, 
                      project_id: str,
                      run_id: str,
                      tracker: Any = None,
                      step_results: Dict[str, Dict[str, Any]] = None,
                      global_config: Dict[str, Any] = None,
                      data_paths: Dict[str, Path] = None,
                      checkpoint_dir: Optional[Path] = None) -> StepContext:
        """
        Create or get a context for a specific project.
        
        Args:
            project_id: Unique project identifier (context key)
            run_id: Unique run identifier (stored in context state)
            tracker: Experiment tracker instance
            step_results: Dictionary of step results (data dictionaries)
            global_config: Global configuration
            data_paths: Paths to data files
            checkpoint_dir: Directory for checkpoints
            
        Returns:
            StepContext instance for the project
        """
        if project_id not in self._contexts:
            self._contexts[project_id] = StepContext(
                project_id=project_id,
                run_id=run_id,
                tracker=tracker,
                step_results=step_results or {},
                global_config=global_config or {},
                data_paths=data_paths or {},
                checkpoint_dir=checkpoint_dir
            )
        else:
            self._contexts[project_id].run_id = run_id
            
        return self._contexts[project_id]


@dataclass 
class StepDefinition:
    """Definition of a step."""
    name: str
    func: Callable
    step_type: str = "general"
    process_name: Optional[str] = None
    original_func: Optional[Callable] = field(default=None, init=False)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    logging: bool = True


@dataclass
class ProcessDefinition:
    """Definition of a process that groups related steps."""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    step_names: List[str] = field(default_factory=list)
    runner: Optional[Callable] = None
    original_func: Optional[Callable] = field(default=None, init=False)
    logging: bool = True


class StepRegistry:
    """Simple registry for step functions."""
    
    def __init__(self):
        self._steps: Dict[str, StepDefinition] = {}
        
    def register_step(self, step_def: StepDefinition) -> None:
        """Register a step definition."""
        self._steps[step_def.name] = step_def
        
    def get_step(self, name: str) -> Optional[StepDefinition]:
        """Get a step definition by name."""
        return self._steps.get(name)

    def list_steps(self) -> List[str]:
        """List all registered step names."""
        return list(self._steps.keys())


class ProcessRegistry:
    """Simple registry for process definitions."""
    
    def __init__(self):
        self._processes: Dict[str, ProcessDefinition] = {}
        self._step_to_process: Dict[str, str] = {}
        
    def register_process(self, process_def: ProcessDefinition) -> None:
        """Register a process definition."""
        self._processes[process_def.name] = process_def
        for step_name in process_def.step_names:
            self._step_to_process[step_name] = process_def.name
        
    def get_process(self, name: str) -> Optional[ProcessDefinition]:
        """Get a process definition by name."""
        return self._processes.get(name)
    
    def get_process_for_step(self, step_name: str) -> Optional[str]:
        """Get the process name that contains a given step."""
        return self._step_to_process.get(step_name)


_step_registry = StepRegistry()
_process_registry = ProcessRegistry()

# Use contextvars for thread-safe context propagation in Dask workers
_current_process_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('current_process_context', default=None)
_current_step_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('current_step_context', default=None)
_current_context: contextvars.ContextVar[Optional[StepContext]] = contextvars.ContextVar('current_context', default=None)
_current_state_manager: contextvars.ContextVar[Any] = contextvars.ContextVar('current_state_manager', default=None)

_context_factory = StepContextFactory()


def get_context_factory() -> StepContextFactory:
    """Get the global context factory instance."""
    return _context_factory


def set_current_context(context: StepContext) -> None:
    """Set the current active context (thread-safe)."""
    _current_context.set(context)


def get_current_context() -> Optional[StepContext]:
    """Get the current active context (thread-safe)."""
    return _current_context.get()


def set_current_process_context(process_name: Optional[str]) -> None:
    """Set the current process context name for step registration/caching (thread-safe)."""
    _current_process_context.set(process_name)


def get_current_process_context() -> Optional[str]:
    """Get the current process context name (thread-safe)."""
    return _current_process_context.get()


def set_current_step_context(step_name: Optional[str]) -> None:
    """Set the current step context name (thread-safe)."""
    _current_step_context.set(step_name)


def get_current_step_context() -> Optional[str]:
    """Get the current step context name (thread-safe)."""
    return _current_step_context.get()


def log_metric(key: str, value: Any, step: Optional[int] = None) -> None:
    """Convenience function to log metrics from anywhere in your model code.
    
    This is the main function users should call to log metrics during training.
    
    Args:
        key: Metric name (e.g., 'loss', 'accuracy', 'learning_rate')
        value: Metric value. Numeric values are tracked per step; non-numeric values
            (e.g., lists, dicts) are stored as last-snapshot under a shadow key
            with "__last" suffix in the KV store.
        step: Step/iteration number (optional). If not provided, auto-increments from largest existing step.
    
    Example:
        >>> from mlops.core import log_metric
        >>> for epoch in range(100):
        >>>     loss = train_one_epoch()
        >>>     log_metric('loss', loss, step=epoch+1)
    """
    ctx = get_current_context()
    if ctx:
        ctx.log_metric(key, value, step=step)
    else:
        import logging
        logging.getLogger(__name__).warning(
            "log_metric called but no context is active. Metric will not be logged."
        )


def set_state_manager(state_manager: Any) -> None:
    """Provide global access to the current StepStateManager for manual step caching (thread-safe)."""
    _current_state_manager.set(state_manager)


def get_state_manager() -> Any:
    """Get the current StepStateManager if available (thread-safe)."""
    return _current_state_manager.get()


def process(description: str = "", parameters: Dict[str, Any] = None, logging: bool = True):
    """
    Simplified decorator to define a process and group the steps.
    """
    def decorator(func):
        # Use function name as the process name for registry lookup
        name = func.__name__
        # Wrap the runner so that steps defined inside can capture the process name
        # via _current_process_context at decoration/runtime.
        def _wrapped_runner(*args, **kwargs):
            prev = get_current_process_context()
            if prev is None:
                set_current_process_context(name)
            try:
                # Auto-inject context and merged hyperparameters for this process runner
                _kwargs = dict(kwargs)
                try:
                    _ctx = get_current_context()
                except Exception:
                    _ctx = None
                if _ctx is not None:
                    _kwargs = _inject_context_and_hparams(func, _ctx, _kwargs)
                result = func(*args, **_kwargs)
                if result is None:
                    raise ValueError(f"Process '{name}' must return a dictionary of data.")
                # Validate result is a dictionary
                if not isinstance(result, dict):
                    raise ValueError(f"Process '{name}' must return a dictionary, got {type(result).__name__}.")
                # Attach to context
                try:
                    ctx = get_current_context()
                    if ctx:
                        ctx.step_results[name] = result
                except Exception:
                    # Do not block process execution on context issues
                    pass
                return result
            finally:
                # Only restore if we actually changed it (i.e., if it was None before)
                if prev is None:
                    set_current_process_context(prev)

        # Register the process runner without executing it now.
        # Users call steps manually inside this function at runtime.
        process_def = ProcessDefinition(
            name=name,
            description=description,
            parameters=parameters or {},
            step_names=[],
            runner=_wrapped_runner,
            logging=logging,
        )
        # Preserve original user function for cache hashing
        process_def.original_func = func
        _process_registry.register_process(process_def)

        return _wrapped_runner
    
    return decorator


def step(name: str = None, 
         step_type: str = "general",
         logging: bool = True):
    """
    Simplified decorator to register a function as a step.
    """
    def decorator(func: Callable) -> Callable:
        step_name = name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            import inspect
            sig = inspect.signature(func)
            
            # (removed) has_var_keyword detection - unused

            ctx = kwargs.get('context')
            if not ctx:
                ctx = get_current_context()
            
            if 'context' in sig.parameters and 'context' not in kwargs:
                if ctx:
                    kwargs['context'] = ctx
            
            # Attempt step-level cache lookup for manual calls
            result: Dict[str, Any]
            try:
                from .step_state_manager import StepExecutionResult  # Local import to avoid circular import at module load
            except Exception:
                StepExecutionResult = None  # type: ignore
            try:
                state_manager = get_state_manager()
            except Exception:
                state_manager = None

            # Lazily initialize a state manager on workers when missing so step-level
            # caching works in distributed mode. This is crucial for distributed execution.
            if state_manager is None and ctx is not None:
                try:
                    state_manager = _init_worker_state_manager_if_needed(ctx)
                except Exception:
                    state_manager = get_state_manager()

            step_key = getattr(wrapper, '_step_name', name or func.__name__)
            # Resolve process_name at runtime: prefer current process context over decoration-time value
            # This allows steps to be defined outside processes and pick up the process they're called from
            runtime_process = get_current_process_context()
            decoration_process = getattr(getattr(wrapper, '_step_definition', None), 'process_name', None)
            process_name_for_step = runtime_process if runtime_process is not None else decoration_process

            cached_used = False
            input_hash = None
            config_hash = None
            function_hash = None

            if state_manager and ctx and step_key:
                try:
                    # Compute hashes similar to executor
                    try:
                        import inspect as _inspect
                        # Prefer original user function signature to bind call-time args
                        _orig_func = getattr(wrapper, '_original_func', func)
                        _sig = _inspect.signature(_orig_func)
                        _bound = _sig.bind_partial(*args, **kwargs)
                        # Exclude context from hashing
                        _call_params = {k: v for k, v in _bound.arguments.items() if k != 'context'}
                        input_hash = state_manager._compute_hash(_call_params)
                    except Exception:
                        input_hash = None
                    try:
                        _orig_func = getattr(wrapper, '_original_func', func)
                        function_hash = state_manager._compute_function_hash(_orig_func)
                    except Exception:
                        function_hash = None
                    try:
                        config_hash = state_manager._compute_hash(getattr(ctx, 'global_config', {}) or {})
                    except Exception:
                        config_hash = None

                    cached_result = state_manager.get_cached_step_result_with_metadata(
                        run_id=getattr(ctx, 'run_id', None) or 'default',
                        step_name=step_key,
                        process_name=process_name_for_step,
                        input_hash=input_hash,
                        config_hash=config_hash,
                        function_hash=function_hash,
                    )
                    if cached_result is not None:
                        cached_used = True
                        result, cached_run_id, cached_metadata = cached_result
                        # Tag and log cache usage
                        try:
                            logging.getLogger(__name__).info(f"Using cached result for step: {step_key} (process {process_name_for_step}) from run {cached_run_id}")
                            if isinstance(result, dict):
                                result.setdefault('__was_cached__', True)
                                # Set execution time to 0 for cached results since they're loaded instantly
                                result.setdefault('__execution_time__', 0.0)
                        except Exception:
                            pass
                        # Attach to context
                        try:
                            if ctx:
                                ctx.step_results[step_key] = result
                        except Exception:
                            pass
                    else:
                        # Execute step (local or distributed)
                        # Set step context before execution
                        prev_step = get_current_step_context()
                        set_current_step_context(step_key)
                        try:
                            # Record step start for live UI/tooling
                            try:
                                if state_manager and ctx and process_name_for_step and step_key:
                                    state_manager.record_step_started(
                                        getattr(ctx, 'run_id', None) or 'default',
                                        process_name_for_step,
                                        step_key,
                                    )
                            except Exception:
                                pass
                            result = func(*args, **kwargs)
                        finally:
                            # Restore previous step context
                            set_current_step_context(prev_step)
                        
                        # Validate result is a dictionary
                        if not isinstance(result, dict):
                            raise ValueError(f"Step '{step_key}' must return a dictionary, got {type(result).__name__}.")
                        
                        # Mark as NOT cached since we executed the function
                        try:
                            if isinstance(result, dict):
                                result.setdefault('__was_cached__', False)
                        except Exception:
                            pass
                except Exception:
                    # On any error, fall back to direct execution
                    result = func(*args, **kwargs)
                    # Validate result is a dictionary
                    if not isinstance(result, dict):
                        raise ValueError(f"Step '{step_key}' must return a dictionary, got {type(result).__name__}.")
            else:
                # No state manager or context - execute directly (threaded mode fallback)
                result = func(*args, **kwargs)
                # Validate result is a dictionary
                if not isinstance(result, dict):
                    raise ValueError(f"Step '{step_key}' must return a dictionary, got {type(result).__name__}.")
            
                try:
                    if isinstance(result, dict):
                        result.setdefault('__was_cached__', False)
                except Exception:
                    pass
            
            # Attach result to context
            try:
                if ctx and isinstance(result, dict):
                    step_key = getattr(wrapper, '_step_name', name or func.__name__)
                    if step_key:
                        ctx.step_results[step_key] = result
            except Exception:
                pass
            
            # Post-execution: record cache entry or cached hit event for manual steps
            try:
                if state_manager and isinstance(result, dict) and StepExecutionResult is not None:
                    try:
                        # Recompute hashes if missing
                        if input_hash is None:
                            try:
                                import inspect as _inspect
                                _orig_func = getattr(wrapper, '_original_func', func)
                                _sig = _inspect.signature(_orig_func)
                                _bound = _sig.bind_partial(*args, **kwargs)
                                _call_params = {k: v for k, v in _bound.arguments.items() if k != 'context'}
                                input_hash = state_manager._compute_hash(_call_params)
                            except Exception:
                                input_hash = None
                        if function_hash is None:
                            try:
                                _orig_func = getattr(wrapper, '_original_func', func)
                                function_hash = state_manager._compute_function_hash(_orig_func)
                            except Exception:
                                function_hash = None
                        if config_hash is None:
                            try:
                                config_hash = state_manager._compute_hash(getattr(ctx, 'global_config', {}) or {})
                            except Exception:
                                config_hash = None
                    except Exception:
                        pass
                    try:
                        # Get logging flag from step definition (default to True if not available)
                        _step_def_for_logging = getattr(wrapper, '_step_definition', None)
                        enable_logging = getattr(_step_def_for_logging, 'logging', True) if _step_def_for_logging else True
                        
                        step_exec_result = StepExecutionResult(
                            step_name=step_key,
                            success=True,
                            result=result,
                            execution_time=0.0,
                            timestamp=datetime.now().isoformat(),
                        )
                        # Pass cached metadata if this was a cache hit
                        cached_run_id = None
                        cached_started_at = None
                        cached_ended_at = None
                        cached_execution_time = None
                        if cached_used and 'cached_metadata' in locals():
                            cached_run_id = cached_metadata.get('run_id')
                            cached_started_at = cached_metadata.get('started_at')
                            cached_ended_at = cached_metadata.get('ended_at')
                            cached_execution_time = cached_metadata.get('execution_time')
                        
                        state_manager.record_step_completion(
                            getattr(ctx, 'run_id', None) or 'default',
                            step_exec_result,
                            input_hash=input_hash,
                            config_hash=config_hash,
                            function_name=step_key,
                            function_hash=function_hash,
                            was_cached=bool(cached_used),
                            process_name=process_name_for_step,
                            enable_logging=enable_logging,
                            cached_run_id=cached_run_id,
                            cached_started_at=cached_started_at,
                            cached_ended_at=cached_ended_at,
                            cached_execution_time=cached_execution_time,
                        )
                    except Exception:
                        pass
            except Exception:
                pass
            
            return result
        
        # Store decoration-time process_name (can be None if step defined outside process)
        # At runtime, the actual process will be resolved from get_current_process_context()
        step_def = StepDefinition(
            name=step_name,
            func=wrapper,
            step_type=step_type,
            process_name=get_current_process_context(),  # Can be None
            logging=logging,
        )
        step_def.original_func = func
        
        _step_registry.register_step(step_def)
        
        wrapper._step_name = step_name
        wrapper._step_definition = step_def
        wrapper._original_func = func
        
        return wrapper
    
    return decorator


def get_step_registry() -> StepRegistry:
    """Get the global step registry."""
    return _step_registry 


def get_process_registry() -> ProcessRegistry:
    """Get the global process registry."""
    return _process_registry

def _init_worker_state_manager_if_needed(ctx: 'StepContext') -> Any:
    """Ensure a StepStateManager exists on the worker when executing steps.
    Returns the state manager or None.
    """
    try:
        from .step_state_manager import StepStateManager  # local to avoid import cycles at module import
        # If already present, reuse
        sm = get_state_manager()
        if sm is not None:
            return sm
        # Build from context cache configuration
        kv_store = None
        obj_store = None
        obj_prefix = None
        cache_dir = Path("step_cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        cfg = ctx.global_config if isinstance(ctx.global_config, dict) else {}
        cache_cfg = (cfg.get('cache') or (cfg.get('model', {}) or {}).get('parameters', {}).get('cache')) if isinstance(cfg, dict) else {}
        backend_cfg = (cache_cfg or {}).get('backend') if isinstance(cache_cfg, dict) else {}
        store_cfg = (cache_cfg or {}).get('object_store') if isinstance(cache_cfg, dict) else {}
        # Ensure GCP env is available on workers (derive from project config when missing)
        try:
            import os as _os
            from pathlib import Path as _Path
            # Prefer explicit env vars; otherwise derive from backend config
            creds_rel = (backend_cfg or {}).get('credentials_json')
            gcp_project = (backend_cfg or {}).get('gcp_project')
            if creds_rel and not _os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                try:
                    pid_effective = str(getattr(ctx, 'project_id', None) or _os.getenv('MLOPS_PROJECT_ID') or 'default')
                    try:
                        from mlops.core.workspace import get_projects_root, get_workspace_root
                        _ws = get_workspace_root()
                        _projects = get_projects_root(_ws)
                        cred_path = (_projects / pid_effective / str(creds_rel)).resolve()
                        if not cred_path.exists():
                            cred_path = (_ws / str(creds_rel)).resolve()
                    except Exception:
                        cred_path = (_Path("projects") / pid_effective / str(creds_rel)).resolve()
                    if cred_path.exists():
                        _os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', str(cred_path))
                except Exception:
                    pass
            if gcp_project and not _os.getenv('GOOGLE_CLOUD_PROJECT'):
                _os.environ.setdefault('GOOGLE_CLOUD_PROJECT', str(gcp_project))
        except Exception:
            pass
        try:
            from mlops.storage.adapters.memory_store import InMemoryStore  # type: ignore
        except Exception:
            InMemoryStore = None  # type: ignore
        # Config-first backend selection with env fallback
        backend_type = None
        try:
            backend_type = (backend_cfg or {}).get('type') if isinstance(backend_cfg, dict) else None
        except Exception:
            backend_type = None
        if backend_type is None:
            try:
                import os as _os
                backend_type = _os.getenv('MLOPS_KV_BACKEND') or None
            except Exception:
                backend_type = None
        if backend_type == 'redis':
            try:
                from mlops.storage.adapters.redis_store import RedisStore  # type: ignore
                kv_store = RedisStore(
                    project_id=str(getattr(ctx, 'project_id', 'default')),
                    host=(backend_cfg or {}).get('host'),
                    port=(backend_cfg or {}).get('port'),
                    db=(backend_cfg or {}).get('db'),
                    password=(backend_cfg or {}).get('password'),
                )
            except Exception:
                kv_store = InMemoryStore(str(getattr(ctx, 'project_id', 'default'))) if InMemoryStore else None
        elif backend_type == 'gcp':
            try:
                from mlops.storage.adapters.gcp_kv_store import GCPStore  # type: ignore
                # Ensure we honor MLOPS_PROJECT_ID if ctx.project_id is missing
                import os as _os
                _pid = str(getattr(ctx, 'project_id', None) or _os.getenv('MLOPS_PROJECT_ID') or 'default')
                kv_store = GCPStore(
                    project_id=_pid,
                    gcp_project=(backend_cfg or {}).get('gcp_project'),
                    topic_name=(backend_cfg or {}).get('topic_name'),
                    emulator_host=(backend_cfg or {}).get('emulator_host'),
                )
            except Exception:
                kv_store = InMemoryStore(str(getattr(ctx, 'project_id', 'default'))) if InMemoryStore else None
        else:
            try:
                import os as _os
                _pid = str(getattr(ctx, 'project_id', None) or _os.getenv('MLOPS_PROJECT_ID') or 'default')
            except Exception:
                _pid = str(getattr(ctx, 'project_id', 'default'))
            kv_store = InMemoryStore(_pid) if InMemoryStore else None
        try:
            if isinstance(store_cfg, dict) and store_cfg.get('type') == 'gcs':
                from mlops.storage.adapters.gcs_object_store import GCSObjectStore  # type: ignore
                obj_store = GCSObjectStore(
                    bucket=store_cfg.get('bucket'),
                    prefix=store_cfg.get('prefix'),
                )
                obj_prefix = None
        except Exception:
            obj_store = None
            obj_prefix = None
        sm_new = StepStateManager(
            cache_dir=cache_dir,
            kv_store=kv_store,
            logger=logging.getLogger(__name__),
            cache_ttl_hours=int(((cache_cfg or {}).get('ttl_hours') if isinstance(cache_cfg, dict) else 24) or 24),
            object_store=obj_store,
            object_prefix=obj_prefix,
        )
        set_state_manager(sm_new)
        return sm_new
    except Exception:
        return get_state_manager()


def _inject_context_and_hparams(func: Callable, ctx: 'StepContext', kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Return kwargs with context/hyperparameters injected when requested by signature.
    
    Context and hyperparameters are ONLY injected if explicitly declared as parameters,
    NOT into **kwargs.
    """
    import inspect as _inspect
    try:
        sig = _inspect.signature(func)
    except Exception:
        sig = None
    new_kwargs = dict(kwargs)
    if sig and ctx is not None:
        # Inject context ONLY if explicitly declared as a parameter
        if 'context' in sig.parameters and 'context' not in new_kwargs:
            new_kwargs['context'] = ctx
        
        # Inject hyperparameters ONLY if explicitly declared as a parameter
        try:
            if ('hyperparameters' in sig.parameters and 'hyperparameters' not in new_kwargs) or \
               ('hparams' in sig.parameters and 'hparams' not in new_kwargs):
                merged = ctx.get_hyperparameters(get_current_process_context()) if hasattr(ctx, 'get_hyperparameters') else {}
                if 'hyperparameters' in sig.parameters and 'hyperparameters' not in new_kwargs:
                    new_kwargs['hyperparameters'] = merged
                if 'hparams' in sig.parameters and 'hparams' not in new_kwargs:
                    new_kwargs['hparams'] = merged
        except Exception:
            pass
    return new_kwargs 