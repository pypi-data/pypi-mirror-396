# MLOps Platform

A comprehensive MLOps platform with project-based workflows for managing machine learning pipelines.

## Overview

The MLOps platform provides a complete solution for managing ML projects from development to production. It features project isolation, automatic state management, experiment tracking, and support for multiple ML frameworks.

## Key Features

- **Project-Based Workflows**: Isolated workspaces for each ML project
- **Multiple ML Frameworks**: Support for scikit-learn, custom models, and NetworkX pipelines
- **State Management**: Automatic caching and idempotency with project isolation
- **Experiment Tracking**: Built-in tracking with configurable backends
- **Environment Management**: Conda environment isolation per project
- **Artifact Management**: Organized storage of models, data, and logs
- **CLI Interface**: Simple command-line interface for project management

## Quick Start

### Installation

```bash
pip install mlops-platform
```

### Workspace

The platform stores projects under a **workspace directory** (it must contain `projects/`).

- Default workspace: current directory
- Override with an env var:

```bash
export MLOPS_WORKSPACE_DIR="/path/to/your/workspace"
```

- Or pass it per-command:

```bash
mlops --workspace "/path/to/your/workspace" list
```

You can also run via module form (equivalent to `mlops ...`):

```bash
python -m mlops.main --help
```

For local development:

```bash
pip install -e ".[dev]"
```

### Create Your First Project

```bash
# Create a new project
mlops create my-first-project --description "My first ML project"

# Set up configuration
mlops config my-first-project --file config.yaml

# Run the pipeline
mlops run my-first-project

# List all projects
mlops list

# Delete when finished
mlops delete my-first-project
```

### Basic Configuration

Create a `config.yaml` file:

```yaml
metadata:
  name: "my-ml-model"
  description: "Example ML model"
  tags: ["classification", "sklearn"]

data:
  sources:
    training:
      path: "data/train.csv"
    validation:
      path: "data/val.csv"

model:
  framework: "sklearn"
  parameters:
    class_name: "sklearn.ensemble.RandomForestClassifier"
    hyperparameters:
      n_estimators: 100
      max_depth: 10
      random_state: 42

training:
  parameters:
    validation_split: 0.2

reproducibility:
  random_seed: 42
  experiment_tracking:
    enabled: true
    backend: "noop"
```

## Project Structure

Each project creates an isolated workspace:

```
projects/your-project-name/
├── configs/project_config.yaml    # Project configuration
├── state/your-project-name.db     # State database
├── cache/                         # Cache files
├── artifacts/
│   ├── models/                    # Trained models
│   └── data/                      # Data artifacts
├── logs/                          # Execution logs
├── data/                          # Project data
└── project_info.json             # Project metadata
```

## Supported Frameworks

### Scikit-learn
```yaml
model:
  framework: "sklearn"
  parameters:
    class_name: "sklearn.linear_model.LogisticRegression"
    hyperparameters:
      C: 1.0
      max_iter: 1000
```

### Custom Models
```yaml
model:
  framework: "custom"
  parameters:
    custom_script_path: "models/my_model.py"
    custom_target: "MyCustomModel"
    hyperparameters:
      learning_rate: 0.001
      epochs: 100
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `create <project-id>` | Create a new project |
| `list` | List all projects |
| `run <project-id>` | Run a project pipeline |
| `config <project-id>` | Manage project configuration |
| `delete <project-id>` | Delete a project |

### Configuration Management

```bash
# View current config
mlops config my-project

# Set config from file
mlops config my-project --file new_config.yaml

# Update specific values
mlops config my-project --set model.parameters.hyperparameters.n_estimators=200
```

## Documentation

- **[Project-Based Workflow Guide](docs/PROJECT_BASED_WORKFLOW.md)** - Complete guide to using the project system
- **[Advanced Features Guide](docs/ADVANCED_FEATURES.md)** - Custom models, NetworkX pipelines, and advanced features
- **[Custom Model Development Guide](docs/CUSTOM_MODEL_STEP_BY_STEP_GUIDE.md)** - Detailed guide for creating custom models

## Examples

The platform includes comprehensive examples:

```bash
# Explore examples
ls examples/

# Run a neural network example
mlops create neural-net --config examples/custom_models/networkx_examples/configs/neural_network_training.yaml
mlops run neural-net
```

## Local Web UI (experimental)

A minimal local UI is included to visualize a project's process graph and live run status.

Prerequisites:
- `pip install fastapi uvicorn`
- Optional KV backend for live status:
  - Redis: export `MLOPS_KV_BACKEND=redis` and set `MLOPS_REDIS_HOST`, `MLOPS_REDIS_PORT`, `MLOPS_REDIS_DB`, `MLOPS_REDIS_PASSWORD`
  - Firestore emulator: set `FIRESTORE_EMULATOR_HOST` and `GOOGLE_CLOUD_PROJECT`

Run the server:

```bash
python -m mlops.web.server
```

Open `http://127.0.0.1:8000`. Choose a project and Run ID (derived from `projects/<id>/artifacts/charts/<run-id>`). Node colors:
- Grey: pending
- Orange: running
- Green: completed
- Teal: cached
- Red: failed

## Features

### State Management and Caching
- Automatic detection of identical runs (same config + data)
- Intelligent caching to avoid redundant computations
- Project-isolated state databases

### Experiment Tracking
- Multiple backend support (MLflow, Weights & Biases, etc.)
- Automatic parameter and metric logging
- Artifact management

### Environment Management
- Conda environment isolation per project
- Automatic package version tracking
- Reproducible environments

### Data Management
- Data integrity verification with hashing
- Automatic data versioning
- Support for multiple data formats

## Development

### Running Tests

```bash
pytest tests/
```

### Releasing to PyPI (GitHub Actions)

Releases are tag-driven:

```bash
git tag v0.2.0
git push origin v0.2.0
```

This triggers `.github/workflows/release.yml`, which builds wheels/sdist and publishes to PyPI using **Trusted Publishing (OIDC)**.

### Project Structure

```
src/mlops/
├── main.py                     # CLI entry point
├── platform.py                 # Main platform orchestration
├── managers/
│   ├── project_manager.py      # Project lifecycle management
│   ├── state_manager.py        # State and caching
│   └── reproducibility_manager.py
├── adapters/                   # ML framework adapters
├── core/                       # Core pipeline components
└── tracking/                   # Experiment tracking
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[License information]

## Support

For questions and support:
- Check the documentation in `docs/`
- Review examples in `examples/`
- Open an issue on GitHub