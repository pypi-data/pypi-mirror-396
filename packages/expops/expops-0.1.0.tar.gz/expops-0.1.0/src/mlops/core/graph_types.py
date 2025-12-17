from __future__ import annotations

from typing import Any, Optional
from dataclasses import dataclass
from enum import Enum


class NodeType(Enum):
    """Types of nodes in the execution graph."""
    PROCESS = "process"
    STEP = "step"


@dataclass
class ProcessConfig:
    """Configuration for a process node."""
    name: str
    depends_on: list[str] | None = None
    parallel: bool = True
    code_function: Optional[str] = None  # Function name to execute (if different from name)
    process_type: str = "process"  # e.g., "process" or special types like "chart"
    
    def __post_init__(self) -> None:
        if self.depends_on is None:
            self.depends_on = []


@dataclass 
class StepConfig:
    """Configuration for a step node."""
    name: str
    type: str = "step"
    process: Optional[str] = None
    inputs: list[str] | None = None
    outputs: list[str] | None = None
    loop_back_to: Optional[str] = None
    condition: Optional[str] = None
    parallel: bool = True


@dataclass
class NetworkXGraphConfig:
    """Configuration for NetworkX-based graph execution."""
    processes: list[ProcessConfig] | None = None
    steps: list[StepConfig] | None = None
    execution: dict[str, Any] | None = None
    
    def __post_init__(self) -> None:
        if self.processes is None:
            self.processes = []
        if self.steps is None:
            self.steps = []
        if self.execution is None:
            self.execution = {}


@dataclass 
class ExecutionResult:
    """Result of executing a node (process or step)."""
    name: str
    result: Optional[dict[str, Any]] = None  # Dictionary containing step/process results
    execution_time: float = 0.0
    was_cached: bool = False
    error: Optional[str] = None 