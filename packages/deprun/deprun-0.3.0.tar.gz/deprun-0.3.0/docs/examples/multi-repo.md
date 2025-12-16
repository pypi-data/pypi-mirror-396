# Multi-Repository Build Example

Demonstrates managing multiple Git repositories with dependencies.

## Configuration

```yaml
variables:
  workspace: ~/projects

jobs:
  common-lib:
    type: build
    repo:
      server: https://github.com/
      group: myorg/
      name: common-lib
    directory: "{workspace}"
    script:
      - make build

  backend:
    type: build
    dependencies:
      - common-lib
    repo:
      server: https://github.com/
      group: myorg/
      name: backend
    directory: "{workspace}"
    script:
      - make build

  build-all:
    type: alias
    dependencies:
      - backend
```

## Usage

```bash
# Build everything
deprun run build-all

# Build just backend (will build common-lib first)
deprun run backend

# Alternative: Run all build jobs at once
deprun run-all --type build

# Preview what would be built
deprun run-all --type build --dry-run

# Capture only build output (no job runner messages)
deprun run backend --quiet > build.log
deprun run backend -q | grep "Build complete"
```

**Note**: Using `run-all --type build` will automatically skip jobs that were already built as dependencies, so each repository is only built once even if multiple jobs depend on it.

## Visualizing Dependencies

Generate a dependency graph to see the build order:

```bash
# Graph for all build jobs
deprun graph

# Graph for specific job
deprun graph backend
```

This will show that `backend` depends on `common-lib`, making the build order clear to your team.
