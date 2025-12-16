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
```
