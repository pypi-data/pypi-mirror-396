# Getting Started

## Installation

Install Job Runner using pip:

```bash
pip install deprun
```

## Your First Job

Create a `jobs.yml` file:

```yaml
variables:
  workspace: /home/user/workspace

jobs:
  hello:
    type: run
    script:
      - echo "Hello from Job Runner!"
```

Run it:

```bash
deprun run hello
```

## Working with Git Repositories

```yaml
variables:
  workspace: ~/projects

jobs:
  my-project:
    type: build
    repo:
      server: https://github.com/
      group: myusername/
      name: my-project.git
      version_ref: main
    directory: "{workspace}"
    script:
      - npm install
      - npm run build
```

This will:
1. Clone the repository if not present
2. Checkout the `main` branch
3. Run the build scripts

## Adding Dependencies

```yaml
jobs:
  backend:
    type: build
    repo:
      server: https://github.com/
      group: myorg/
      name: backend
    directory: "{workspace}"
    script:
      - make build

  frontend:
    type: build
    repo:
      server: https://github.com/
      group: myorg/
      name: frontend
    directory: "{workspace}"
    dependencies:
      - backend
    script:
      - npm run build
```

Running `deprun run frontend` will automatically build `backend` first.

## Next Steps

- Read the [Configuration Guide](configuration.md)
- Check out [Examples](examples/)
- Learn about [Templates](templates.md)
