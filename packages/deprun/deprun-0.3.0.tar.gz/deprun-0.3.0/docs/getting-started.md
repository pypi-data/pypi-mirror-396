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

# Quiet mode: only show script output
deprun run hello --quiet
deprun run hello -q

# Useful for piping output to other commands
deprun run hello -q | grep "Hello"
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

## Running Multiple Jobs

You can run all jobs or a filtered subset at once:

```bash
# Run all build jobs
deprun run-all --type build

# Run all jobs matching a pattern
deprun run-all --pattern "lib*"

# Combine filters
deprun run-all --type build --pattern "amx*"

# Preview what would run without executing
deprun run-all --dry-run
```

Key features:
- **Smart dependency handling**: Jobs already run as dependencies are automatically skipped
- **Fail-fast**: Execution stops on first failure
- **Predictable order**: Jobs run in alphabetical order
- **Progress tracking**: Shows `[N/Total]` progress for each job

## Visualizing Dependencies

Generate dependency graphs to understand your job relationships:

```bash
# Generate graph for a specific job
deprun graph frontend

# Generate graph for all jobs (entire project)
deprun graph

# Specify custom output file
deprun graph backend --output backend-deps.md
deprun graph --output project-structure.md
```

This creates a Markdown file with a Mermaid diagram that you can:
- View on GitHub/GitLab (they render Mermaid automatically)
- Open in VS Code with a Mermaid extension
- Convert to images using Mermaid CLI

The graph automatically:
- Removes transitive edges for cleaner visualization
- Shows only direct dependencies
- Includes all jobs when no specific job is specified

## Next Steps

- Read the [Configuration Guide](configuration.md)
- Check out [Examples](examples/)
- Learn about [Templates](templates.md)
