import importlib
import pkgutil
from typing import Dict, Type, Optional, Any

from .base import ExperimentTracker

class TrackerPluginManager:
    """
    Manages the discovery and loading of experiment tracker plugins.
    Each tracker plugin should be a module in the specified package path,
    and should contain a class named 'Tracker' that inherits from ExperimentTracker.
    """

    def __init__(self):
        self._trackers: Dict[str, Type[ExperimentTracker]] = {}

    def discover_trackers(self, package_path: str) -> None:
        """
        Discover and load all tracker plugins in the given package.

        Args:
            package_path: Dotted path to the package containing tracker plugins
                          (e.g., 'mlops.tracking.plugins').
        """
        try:
            package = importlib.import_module(package_path)
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
                if not is_pkg:
                    try:
                        module = importlib.import_module(name)
                        if hasattr(module, "Tracker"):
                            tracker_class = getattr(module, "Tracker")
                            if isinstance(tracker_class, type) and issubclass(tracker_class, ExperimentTracker):
                                tracker_key = name.split('.')[-1]
                                self._trackers[tracker_key] = tracker_class
                                print(f"[TrackerPluginManager] Discovered tracker: {tracker_key}")
                            else:
                                print(f"[TrackerPluginManager] Module {name} has 'Tracker' but it's not a valid ExperimentTracker subclass.")
                    except ImportError as e:
                        print(f"[TrackerPluginManager] Failed to import tracker module {name}: {e}")
                    except Exception as e:
                        print(f"[TrackerPluginManager] Error loading tracker from module {name}: {e}")
        except ImportError as e:
            print(f"[TrackerPluginManager] Could not import package {package_path}: {e}")

    def get_tracker_class(self, name: str) -> Optional[Type[ExperimentTracker]]:
        """
        Get a tracker class by its registered name.

        Args:
            name: The name of the tracker (typically the module name).

        Returns:
            The tracker class if found, otherwise None.
        """
        return self._trackers.get(name)

    def create_tracker(
        self, 
        name: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> Optional[ExperimentTracker]:
        """
        Create an instance of a specified tracker.

        Args:
            name: The name of the tracker to create.
            config: Configuration dictionary to pass to the tracker's constructor.

        Returns:
            An instance of the ExperimentTracker, or None if the tracker is not found.
        
        Raises:
            ValueError: If the tracker class is found but cannot be instantiated.
        """
        tracker_class = self.get_tracker_class(name)
        if tracker_class:
            try:
                return tracker_class(config=config)
            except Exception as e:
                raise ValueError(f"Could not instantiate tracker '{name}': {e}")
        print(f"[TrackerPluginManager] Tracker '{name}' not found.")
        return None

    def list_available_trackers(self) -> Dict[str, Type[ExperimentTracker]]:
        """
        List all discovered and available trackers.

        Returns:
            A dictionary mapping tracker names to their classes.
        """
        return self._trackers.copy() 