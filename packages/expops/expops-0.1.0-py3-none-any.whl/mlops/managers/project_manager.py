import os
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json


class ProjectManager:
    """Manages MLOps projects with isolated state, caching, and configurations."""
    
    def __init__(self, projects_root: Optional[Union[str, Path]] = None):
        # Interpret projects_root relative to workspace root so callers can pass
        # `--workspace` / `MLOPS_WORKSPACE_DIR` and still work from any CWD.
        if projects_root is None:
            try:
                from mlops.core.workspace import get_projects_root
                self.projects_root = get_projects_root()
            except Exception:
                self.projects_root = Path("projects")
        else:
            pr = Path(projects_root)
            if not pr.is_absolute():
                try:
                    from mlops.core.workspace import get_workspace_root
                    pr = get_workspace_root() / pr
                except Exception:
                    pass
            self.projects_root = pr

        self.projects_root.mkdir(parents=True, exist_ok=True)
        self.projects_index_file = self.projects_root / "projects_index.json"
        self._ensure_projects_index()
    
    def _ensure_projects_index(self) -> None:
        """Ensure the projects index file exists."""
        if not self.projects_index_file.exists():
            self._save_projects_index({})
    
    def _load_projects_index(self) -> Dict[str, Any]:
        """Load the projects index."""
        if self.projects_index_file.exists():
            with open(self.projects_index_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_projects_index(self, index: Dict[str, Any]) -> None:
        """Save the projects index."""
        with open(self.projects_index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def create_project(self, project_id: str, base_config_path: Optional[str] = None, 
                      description: str = "") -> Dict[str, Any]:
        """
        Create a new project with isolated workspace.
        
        Args:
            project_id: Unique identifier for the project
            base_config_path: Optional path to base configuration to copy
            description: Project description
            
        Returns:
            Project information dictionary
        """
        if self.project_exists(project_id):
            raise ValueError(f"Project '{project_id}' already exists")
        
        # Create project directory structure
        project_path = self.projects_root / project_id
        project_path.mkdir(exist_ok=True)
        
        # Create subdirectories for isolation (state and cache no longer created locally)
        (project_path / "configs").mkdir(exist_ok=True)
        (project_path / "artifacts").mkdir(exist_ok=True)
        (project_path / "logs").mkdir(exist_ok=True)
        (project_path / "data").mkdir(exist_ok=True)
        (project_path / "keys").mkdir(exist_ok=True)
        (project_path / "models").mkdir(exist_ok=True)
        (project_path / "charts").mkdir(exist_ok=True)
        
        # Create project configuration
        project_info = {
            "project_id": project_id,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "base_config_path": base_config_path,
            "project_path": str(project_path),
            "runs": []
        }
        
        # Copy base configuration if provided
        if base_config_path and Path(base_config_path).exists():
            config_dest = project_path / "configs" / "project_config.yaml"
            shutil.copy2(base_config_path, config_dest)
            project_info["active_config"] = str(config_dest)
        
        # Save project info
        project_info_file = project_path / "project_info.json"
        with open(project_info_file, 'w') as f:
            json.dump(project_info, f, indent=2)
        
        # Update projects index
        projects_index = self._load_projects_index()
        projects_index[project_id] = {
            "project_path": str(project_path),
            "created_at": project_info["created_at"],
            "description": description
        }
        self._save_projects_index(projects_index)
        
        print(f"✅ Project '{project_id}' created successfully at: {project_path}")
        return project_info
    
    def delete_project(self, project_id: str, confirm: bool = False) -> bool:
        """
        Delete a project and all its associated data.
        
        Args:
            project_id: Project to delete
            confirm: If True, skip confirmation prompt
            
        Returns:
            True if project was deleted, False otherwise
        """
        if not self.project_exists(project_id):
            print(f"❌ Project '{project_id}' does not exist")
            return False
        
        project_path = self.get_project_path(project_id)
        
        if not confirm:
            response = input(f"⚠️  Are you sure you want to delete project '{project_id}' and all its data? [y/N]: ")
            if response.lower() != 'y':
                print("❌ Project deletion cancelled")
                return False
        
        # Remove project directory
        shutil.rmtree(project_path)
        
        # Update projects index
        projects_index = self._load_projects_index()
        del projects_index[project_id]
        self._save_projects_index(projects_index)
        
        print(f"✅ Project '{project_id}' deleted successfully")
        return True
    
    def project_exists(self, project_id: str) -> bool:
        """Check if a project exists."""
        return project_id in self._load_projects_index()
    
    def get_project_path(self, project_id: str) -> Path:
        """Get the path to a project."""
        projects_index = self._load_projects_index()
        if project_id not in projects_index:
            raise ValueError(f"Project '{project_id}' does not exist")
        return Path(projects_index[project_id]["project_path"])
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects."""
        projects_index = self._load_projects_index()
        projects = []
        
        for project_id, info in projects_index.items():
            try:
                project_path = Path(info["project_path"])
                project_info_file = project_path / "project_info.json"
                
                if project_info_file.exists():
                    with open(project_info_file, 'r') as f:
                        project_info = json.load(f)
                    projects.append(project_info)
                else:
                    # Fallback to index info if project_info.json is missing
                    projects.append({
                        "project_id": project_id,
                        "description": info.get("description", ""),
                        "created_at": info.get("created_at", ""),
                        "project_path": info["project_path"]
                    })
            except Exception as e:
                print(f"Warning: Could not load info for project '{project_id}': {e}")
                
        return projects
    
    def get_project_info(self, project_id: str) -> Dict[str, Any]:
        """Get detailed information about a project."""
        if not self.project_exists(project_id):
            raise ValueError(f"Project '{project_id}' does not exist")
        
        project_path = self.get_project_path(project_id)
        project_info_file = project_path / "project_info.json"
        
        with open(project_info_file, 'r') as f:
            return json.load(f)
    
    def update_project_config(self, project_id: str, config_updates: Dict[str, Any]) -> None:
        """Update project configuration."""
        if not self.project_exists(project_id):
            raise ValueError(f"Project '{project_id}' does not exist")
        
        project_path = self.get_project_path(project_id)
        config_file = project_path / "configs" / "project_config.yaml"
        
        # Load existing config or create new one
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
        
        # Deep merge config updates
        self._deep_merge(config, config_updates)
        
        # Save updated config
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Update project info
        project_info = self.get_project_info(project_id)
        project_info["last_modified"] = datetime.now().isoformat()
        project_info["active_config"] = str(config_file)
        
        project_info_file = project_path / "project_info.json"
        with open(project_info_file, 'w') as f:
            json.dump(project_info, f, indent=2)
        
        print(f"✅ Project '{project_id}' configuration updated")
    
    def _deep_merge(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """Deep merge two dictionaries."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get_project_config_path(self, project_id: str) -> Path:
        """Get the path to project's active configuration."""
        if not self.project_exists(project_id):
            raise ValueError(f"Project '{project_id}' does not exist")
        
        project_path = self.get_project_path(project_id)
        config_file = project_path / "configs" / "project_config.yaml"
        
        return config_file
    
    def add_run_to_project(self, project_id: str, run_id: str, config_hash: str) -> None:
        """Add a run record to the project."""
        if not self.project_exists(project_id):
            raise ValueError(f"Project '{project_id}' does not exist")
        
        project_info = self.get_project_info(project_id)
        project_info["runs"].append({
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "config_hash": config_hash
        })
        project_info["last_modified"] = datetime.now().isoformat()
        
        project_path = self.get_project_path(project_id)
        project_info_file = project_path / "project_info.json"
        with open(project_info_file, 'w') as f:
            json.dump(project_info, f, indent=2) 