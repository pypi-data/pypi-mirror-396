# This file makes Python treat the 'plugins' directory as a package.
# Users can add their custom ExperimentTracker implementations here.
# For example, a tensorboard_tracker.py, etc.

# To make a tracker discoverable, it should be a Python module in this directory
# (or a sub-package that is findable by pkgutil) and contain a class named 'Tracker'
# that inherits from mlops.tracking.base.ExperimentTracker.
# Each plugin should inherit from the BaseTracker class in mlops.tracking.base_tracker.