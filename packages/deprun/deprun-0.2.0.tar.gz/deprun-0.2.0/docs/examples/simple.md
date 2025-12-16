# Simple Project Example

A basic example showing local task automation.

## Configuration

```yaml
variables:
  workspace: ~/workspace
  python_version: "3.11"

jobs:
  setup:
    type: run
    script:
      - python{python_version} -m venv venv
      - pip install -r requirements.txt

  test:
    type: run
    dependencies:
      - setup
    script:
      - pytest tests/

  ci:
    type: alias
    dependencies:
      - test
```

## Usage

```bash
# Run tests
deprun run test

# Run all CI checks
deprun run ci
```
