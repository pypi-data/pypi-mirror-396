from __future__ import annotations

from typing import Any, Dict
import logging

from .graph_types import NetworkXGraphConfig, ProcessConfig, StepConfig
from .step_system import get_step_registry

logger = logging.getLogger(__name__)


class NetworkXPipelineParser:
    """Parser for NetworkX-based pipeline configurations with loop support."""
    
    def __init__(self) -> None:
        self.processes: Dict[str, ProcessConfig] = {}
        self.steps: Dict[str, StepConfig] = {}
        
    def parse_pipeline_config(self, pipeline_config: Dict[str, Any]) -> NetworkXGraphConfig:
        """Parse pipeline config and return NetworkX graph configuration."""
        self.processes = {}
        self.steps = {}
        
        if "processes" in pipeline_config:
            self._parse_networkx_format(pipeline_config)

        config = self._generate_networkx_config(pipeline_config)
        
        logger.info(f"Parsed pipeline with {len(self.processes)} processes and {len(self.steps)} steps")
        return config
        
    def _parse_networkx_format(self, pipeline_config: Dict[str, Any]) -> None:
        """Parse NetworkX configuration format with DAG flow support."""
        
        if "process_adjlist" in pipeline_config:
            self._parse_process_adjlist(pipeline_config["process_adjlist"])
        
        for process_data in pipeline_config.get("processes", []):
            process_name = process_data["name"]
            code_function = process_data.get("code_function")  # Extract code_function if provided
            proc_type = process_data.get("type", "process")
            
            if process_name in self.processes:
                process_config = self.processes[process_name]
                process_config.parallel = process_data.get("parallel", process_config.parallel)
                # Update code_function if provided in config
                if code_function:
                    process_config.code_function = code_function
                # Update process_type if provided (important for chart processes)
                if proc_type:
                    process_config.process_type = str(proc_type)
                    logger.debug(f"Updated process '{process_name}' type to '{proc_type}'")
            else:
                process_config = ProcessConfig(
                    name=process_name,
                    parallel=process_data.get("parallel", True),
                    code_function=code_function,  # Set code_function from config
                    process_type=str(proc_type)
                )
                    
                self.processes[process_name] = process_config
            
        # Manual-step mode: steps are executed inside process runners, not scheduled as nodes.
    
    def _parse_process_adjlist(self, adjlist_value: Any) -> None:
        """Parse process-level DAG from adjacency list string or list of lines.
        
        Adjacency list lines follow NetworkX semantics: first token is the source node,
        subsequent tokens are target nodes. Lines may include comments after a '#'.
        """
        if isinstance(adjlist_value, str):
            lines = adjlist_value.splitlines()
        elif isinstance(adjlist_value, list):
            lines = [str(x) for x in adjlist_value]
        else:
            raise ValueError("process_adjlist must be a string or list of lines")
        
        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue
            # Remove comments after '#'
            if "#" in line:
                line = line.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            if not parts:
                continue
            source = parts[0]
            targets = parts[1:]
            
            # Ensure source process exists
            if source not in self.processes:
                self.processes[source] = ProcessConfig(name=source, depends_on=[])
            
            # Add or update targets with dependency on source
            for target in targets:
                if target not in self.processes:
                    self.processes[target] = ProcessConfig(name=target, depends_on=[source])
                else:
                    deps = self.processes[target].depends_on or []
                    if source not in deps:
                        self.processes[target].depends_on = deps + [source]
    
    def _discover_steps_from_registry(self) -> None:
        """Manual-step mode: keep for compatibility; intentionally a no-op."""
        try:
            step_registry = get_step_registry()
            registered_steps = step_registry.list_steps() if step_registry else []
            logger.debug(f"Manual-step mode enabled; ignoring {len(registered_steps)} registered steps during parsing")
        except Exception:
            logger.debug("Manual-step mode enabled; no step registry available")
    
    def _generate_networkx_config(self, pipeline_config: Dict[str, Any]) -> NetworkXGraphConfig:
        """Generate NetworkX configuration from parsed processes and steps."""
        
        execution_config = pipeline_config.get("execution", {})
        execution = {
            "parallel": execution_config.get("parallel", True),
            "failure_mode": execution_config.get("failure_mode", "stop_and_resume"),
            "max_workers": execution_config.get("max_workers", 4)
        }
        
        return NetworkXGraphConfig(
            processes=list(self.processes.values()),
            steps=list(self.steps.values()),
            execution=execution
        )


def parse_networkx_pipeline_from_config(pipeline_config: Dict[str, Any]) -> NetworkXGraphConfig:
    """Parse pipeline configuration into NetworkX format."""
    parser = NetworkXPipelineParser()
    return parser.parse_pipeline_config(pipeline_config) 