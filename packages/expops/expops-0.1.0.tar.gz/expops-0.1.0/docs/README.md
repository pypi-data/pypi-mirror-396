# MLOps Platform Documentation

Welcome to the MLOps Platform documentation. This guide will help you get started with the project-based workflow system and advanced features.

## Documentation Structure

### Getting Started

**[Project-Based Workflow Guide](PROJECT_BASED_WORKFLOW.md)**
- Complete guide to the new project-based workflow system
- CLI commands and project management
- Configuration structure and examples
- State management and artifact organization
- Best practices and troubleshooting

Start here if you're new to the platform or migrating from the legacy system.

### Advanced Usage

**[Advanced Features Guide](ADVANCED_FEATURES.md)**
- Custom model development patterns
- NetworkX pipeline execution with loops and conditions
- Advanced state management and caching
- Environment isolation and management
- Experiment tracking configuration
- Performance optimization techniques
- CI/CD integration patterns
- Troubleshooting and migration guides

Read this for sophisticated ML workflows and advanced platform features.

**[Custom Model Development Guide](CUSTOM_MODEL_STEP_BY_STEP_GUIDE.md)**
- Detailed step-by-step guide for creating custom models
- MLOpsCustomModelBase usage patterns
- Step system and pipeline integration
- Advanced model architectures and patterns
- Testing and validation approaches

Refer to this for implementing custom ML models and complex pipelines.

## Quick Navigation

### New Users
1. Start with [Project-Based Workflow Guide](PROJECT_BASED_WORKFLOW.md)
2. Follow the Quick Start section
3. Try the basic examples
4. Explore configuration options

### Experienced Users
1. Review [Advanced Features Guide](ADVANCED_FEATURES.md)
2. Explore custom model development in [Custom Model Development Guide](CUSTOM_MODEL_STEP_BY_STEP_GUIDE.md)
3. Check out NetworkX pipeline configurations
4. Set up advanced experiment tracking

### Developers
1. Read the [Advanced Features Guide](ADVANCED_FEATURES.md) for API usage
2. Check [Custom Model Development Guide](CUSTOM_MODEL_STEP_BY_STEP_GUIDE.md) for extension patterns
3. Review the main [README.md](../README.md) for development setup

## Key Concepts

### Project-Based Workflow
The platform organizes work into isolated projects, each with its own:
- Configuration and parameters
- State database and caching
- Artifacts and logs
- Data and models

### Supported Frameworks
- **Scikit-learn**: Built-in adapter for sklearn models
- **Custom Models**: Full Python-based custom model development
- **NetworkX Pipelines**: Complex workflows with loops and conditions

### State Management
- Automatic detection of duplicate runs
- Intelligent caching based on configuration and data hashes
- Project isolation prevents interference between projects

## Examples

The platform includes comprehensive examples in the `examples/` directory:
- Basic scikit-learn models
- Custom model implementations
- NetworkX pipeline configurations
- Advanced training patterns

## Migration from Legacy System

If you're migrating from the previous workflow system:
1. Review the migration section in [Project-Based Workflow Guide](PROJECT_BASED_WORKFLOW.md)
2. Create projects for your existing pipelines
3. Update configurations to use project-relative paths
4. Test with the new CLI commands

## Getting Help

- Check the relevant documentation section above
- Review examples in the `examples/` directory
- Open an issue on GitHub for bugs or feature requests
- Consult the main [README.md](../README.md) for basic setup

## Documentation Maintenance

This documentation reflects the current project-based workflow system. Previous workflow approaches have been deprecated in favor of the unified project system that provides better isolation, management, and scalability. 