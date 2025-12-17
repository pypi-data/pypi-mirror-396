from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ExperimentTracker(ABC):
    """
    Abstract base class for an experiment tracker.
    Defines the common interface for logging parameters, metrics, artifacts, and tags.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config if config else {}
        self._active_run_context = None # For trackers that use context managers

    @abstractmethod
    def log_param(self, key: str, value: Any) -> None:
        """Log a single parameter."""
        pass

    @abstractmethod
    def log_params(self, params: Dict[str, Any]) -> None:
        """Log multiple parameters from a dictionary."""
        pass

    @abstractmethod
    def log_metric(self, key: str, value: float, step: Optional[int] = None) -> None:
        """Log a single metric."""
        pass

    @abstractmethod
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        """Log multiple metrics from a dictionary."""
        pass

    @abstractmethod
    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        """Log a local file as an artifact."""
        pass

    @abstractmethod
    def log_artifacts(self, local_dir: str, artifact_path: Optional[str] = None) -> None:
        """Log all files in a local directory as artifacts."""
        pass

    @abstractmethod
    def set_tag(self, key: str, value: Any) -> None:
        """Set a tag for the current run."""
        pass
    
    @abstractmethod
    def set_tags(self, tags: Dict[str, Any]) -> None:
        """Set multiple tags for the current run."""
        pass

    @abstractmethod
    def start_run(self, run_name: Optional[str] = None, run_id: Optional[str] = None, tags: Optional[Dict[str, Any]] = None) -> Any:
        """
        Start a new run.
        Returns a context manager or an identifier for the run.
        Implementations should handle nested runs if supported.
        """
        pass

    @abstractmethod
    def end_run(self, status: Optional[str] = "FINISHED") -> None:
        """
        End the current active run.
        Status could be FINISHED, FAILED, KILLED, etc.
        """
        pass

    # Optional: A context manager interface for runs
    def __enter__(self):
        # This allows 'with tracker.start_run() as run:'
        # The start_run method itself can return 'self' if it's designed as a context manager
        if self._active_run_context is None: # Avoid re-entering if already in a run started by this instance
             # This is a simplified context management. Real implementations might need more.
            self._active_run_context = self.start_run() # Default run if not specified
        return self._active_run_context


    def __exit__(self, exc_type, exc_val, exc_tb):
        status = "FAILED" if exc_type else "FINISHED"
        self.end_run(status=status)
        self._active_run_context = None


class NoOpExperimentTracker(ExperimentTracker):
    """
    A no-operation experiment tracker that prints log messages to the console.
    Useful for development, testing, or when no tracking backend is configured.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.run_active = False
        self.current_run_id = None
        print(f"[NoOpTracker] Initialized with config: {self.config}")

    def log_param(self, key: str, value: Any) -> None:
        if self.run_active:
            print(f"[NoOpTracker][RunID: {self.current_run_id}] Logged param: {{'{key}': {value}}}")
        else:
            print(f"[NoOpTracker] No active run. Param not logged: {{'{key}': {value}}}")


    def log_params(self, params: Dict[str, Any]) -> None:
        if self.run_active:
            for key, value in params.items():
                self.log_param(key, value) # Reuse single log_param
        else:
            print(f"[NoOpTracker] No active run. Params not logged: {params}")


    def log_metric(self, key: str, value: float, step: Optional[int] = None) -> None:
        # Intentionally do not print metrics or values to avoid verbose logs
        return


    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        # Intentionally do not print metrics or dictionaries
        return


    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        if self.run_active:
            target_path = artifact_path if artifact_path else local_path
            print(f"[NoOpTracker][RunID: {self.current_run_id}] Logged artifact: '{local_path}' to '{target_path}'")
        else:
            print(f"[NoOpTracker] No active run. Artifact not logged: '{local_path}'")


    def log_artifacts(self, local_dir: str, artifact_path: Optional[str] = None) -> None:
        if self.run_active:
            target_path = artifact_path if artifact_path else local_dir
            print(f"[NoOpTracker][RunID: {self.current_run_id}] Logged artifacts from directory: '{local_dir}' to '{target_path}'")
        else:
            print(f"[NoOpTracker] No active run. Artifacts not logged from: '{local_dir}'")


    def set_tag(self, key: str, value: Any) -> None:
        if self.run_active:
            print(f"[NoOpTracker][RunID: {self.current_run_id}] Set tag: {{'{key}': {value}}}")
        else:
            print(f"[NoOpTracker] No active run. Tag not set: {{'{key}': {value}}}")

    def set_tags(self, tags: Dict[str, Any]) -> None:
        if self.run_active:
            for key, value in tags.items():
                self.set_tag(key, value)
        else:
            print(f"[NoOpTracker] No active run. Tags not set: {tags}")


    def start_run(self, run_name: Optional[str] = None, run_id: Optional[str] = None, tags: Optional[Dict[str, Any]] = None) -> 'NoOpExperimentTracker':
        import uuid
        if self.run_active:
            print(f"[NoOpTracker] Warning: A run (ID: {self.current_run_id}) is already active. Starting a new nested run is not fully supported by NoOpTracker; state will be overridden.")
        
        self.current_run_id = run_id if run_id else str(uuid.uuid4())
        self.run_active = True
        
        run_display_name = run_name if run_name else "default_run"
        print(f"[NoOpTracker] Started run. Name: '{run_display_name}', ID: '{self.current_run_id}'")
        if tags:
            self.set_tags(tags)
        return self # Return self to allow use as a context manager

    def end_run(self, status: Optional[str] = "FINISHED") -> None:
        if self.run_active:
            print(f"[NoOpTracker][RunID: {self.current_run_id}] Ended run with status: {status}")
            self.run_active = False
            self.current_run_id = None
        else:
            print("[NoOpTracker] No active run to end.")

    # Implementing __enter__ and __exit__ for context management
    def __enter__(self):
        # If start_run wasn't called explicitly before 'with', start a default run
        if not self.run_active:
            self.start_run() 
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        status = "FAILED" if exc_type else "FINISHED"
        self.end_run(status=status)
