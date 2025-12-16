# Job Runner

[![PyPI version](https://badge.fury.io/py/job-runner.svg)](https://badge.fury.io/py/job-runner)
[![Python versions](https://img.shields.io/pypi/pyversions/job-runner.svg)](https://pypi.org/project/job-runner/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/job-runner)](https://pepy.tech/project/job-runner)

Multi-repository task automation with intelligent dependency management.

## Features

- **Dependency Resolution**: Automatically handles job dependencies with circular dependency protection
- **Template System**: Reusable job templates with inheritance
- **Git Integration**: Clone and manage multiple repositories
- **Task-Level Execution**: Run specific tasks within jobs
- **Dependency Graphs**: Visualize job dependencies with Mermaid
- **Conditional Configuration**: Use `when` clauses for dynamic configs
- **Environment Management**: Isolated environment variables per job

## Installation

```bash
pip install job-runner
```

### For development:

```bash
pip install job-runner[dev]
```

## Quick Start

### 1. Create a `jobs.yml` file:

```yaml
variables:
  build_dir: /tmp/builds
  user: ${USER}

jobs:
  build-frontend:
    type: build
    description: Build the frontend application
    repo:
      server: https://github.com/
      group: myorg/
      name: frontend
    directory: ${build_dir}
    script:
      - npm install
      - npm run build

  build-backend:
    type: build
    description: Build the backend service
    repo:
      server: https://github.com/
      group: myorg/
      name: backend
    directory: ${build_dir}
    script:
      - go mod download
      - go build -o server

  deploy:
    type: run
    description: Deploy all services
    dependencies:
      - build-frontend
      - build-backend
    script:
      - echo "Deploying services..."
      - ./deploy.sh
```

### 2. Run a job:

```bash
# Run a job with all its dependencies
job-runner run deploy

# Run a specific task within a job
job-runner run build-frontend test

# Run multiple tasks in sequence
job-runner run build-frontend clean,default,test

# Use "default" to refer to the main script
job-runner run build-frontend default    # Same as: job-runner run build-frontend

# Limit dependency depth
job-runner run deploy --depth 1

# Fetch (clone) a repository without running scripts
job-runner fetch build-frontend
```

### 3. List available jobs:

```bash
job-runner list
```

### 4. Visualize dependencies:

```bash
job-runner graph deploy
```

## Configuration

### Job Types

- **build**: Clone a repository and run build scripts
- **run**: Execute scripts in a specified directory

### Templates

Create reusable job configurations:

```yaml
templates:
  python-build:
    type: build
    script:
      - python -m pip install -r requirements.txt
      - python -m pytest
      - python -m build

jobs:
  my-python-app:
    template: python-build
    repo:
      server: https://github.com/
      group: myorg/
      name: my-app
```

### Conditional Configuration

Use `when` clauses for dynamic configurations:

```yaml
jobs:
  deploy:
    type: run
    script:
      - echo "Base script"
    when:
      - condition: "variables.get('ENVIRONMENT') == 'production'"
        data:
          script:
            - echo "Production deployment"
            - ./deploy-prod.sh
```

### Tasks

Define multiple tasks within a job:

```yaml
jobs:
  myapp:
    type: build
    repo:
      server: https://github.com/
      group: myorg/
      name: app
    script:
      - make build
    tasks:
      test:
        script:
          - make test
      clean:
        script:
          - make clean
      deploy:
        dependencies:
          - myapp:test
        script:
          - make deploy
```

Run specific tasks:

```bash
# Run a single task
job-runner run myapp test

# Run multiple tasks in sequence
job-runner run myapp clean,default,test

# The "default" task refers to the job's main script
job-runner run myapp default              # Runs: make build
job-runner run myapp clean,default        # Runs: make clean, then make build

# Run tasks with dependencies
job-runner run myapp deploy               # Runs test first, then deploy
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `job-runner list` | List all available jobs |
| `job-runner run JOB [TASKS]` | Run a job or specific tasks (comma-separated) |
| `job-runner fetch JOB` | Clone repository for build job without running scripts |
| `job-runner info JOB [FIELD]` | Show job information |
| `job-runner validate` | Validate configuration |
| `job-runner dump JOB` | Export job definition |
| `job-runner graph JOB` | Generate dependency graph |

## Advanced Features

### Environment Variables

```yaml
jobs:
  myapp:
    type: run
    env:
      NODE_ENV: production
      DEBUG: "false"
    script:
      - npm start
```

### Variable Substitution

```yaml
variables:
  version: "1.0.0"
  output: /tmp/builds

jobs:
  build:
    script:
      - echo "Building version {version}"
      - cp output {output}/app-{version}
```

### Multiple Configuration Files

Organize jobs across multiple files:

```yaml
# jobs.yml
jobs-dir: ./jobs

# jobs/frontend.yml
jobs:
  frontend:
    type: build
    # ...

# jobs/backend.yml
jobs:
  backend:
    type: build
    # ...
```

## Development

```bash
# Clone the repository
git clone https://gitlab.com/proj_amx_01/tools/job-runner.git
cd job-runner

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black deprun tests

# Lint
ruff check deprun tests

# Type check
mypy deprun

# Build wheel package
python -m build

# Or use the Makefile
make build

# Clean build artifacts
make clean
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Created by [Peter De Herdt](https://gitlab.com/proj_amx_01/tools/job-runner)

## Support

- [Documentation](https://gitlab.com/proj_amx_01/tools/job-runner/-/blob/main/README.md)
- [Issue Tracker](https://gitlab.com/proj_amx_01/tools/job-runner/-/issues)
