# Configuration Reference

## File Structure

```yaml
variables:
  # Global variables
  
templates:
  # Reusable templates
  
jobs:
  # Job definitions

jobs-dir: optional/path/to/additional/jobs
```

## Variables

Variables can be used throughout your configuration with `{variable_name}` syntax.

```yaml
variables:
  workspace: /home/user/workspace
  build_type: release

jobs:
  my-job:
    type: run
    directory: "{workspace}/builds/{build_type}"
```

Environment variables are automatically available:

```yaml
jobs:
  my-job:
    script:
      - echo "User is {USER}"
```

## Job Types

### build
For projects that need to be cloned from Git:

```yaml
my-app:
  type: build
  repo:
    server: https://github.com/
    group: myorg/
    name: my-app
    version_ref: v1.0.0  # optional
  directory: "{workspace}"
  script:
    - make build
```

### run
For local tasks:

```yaml
deploy:
  type: run
  directory: /opt/deploy
  script:
    - ./deploy.sh
```

### alias
For grouping multiple jobs:

```yaml
build-all:
  type: alias
  dependencies:
    - backend
    - frontend
    - database
```

## Templates

Create reusable configuration:

```yaml
templates:
  node-app:
    script:
      - npm install
      - npm run build
    env:
      NODE_ENV: production

jobs:
  frontend:
    type: build
    template: node-app
    repo:
      server: https://github.com/
      group: myorg/
      name: frontend
    directory: "{workspace}"
```

## Dependencies

Jobs can depend on other jobs:

```yaml
jobs:
  database:
    type: run
    script:
      - docker-compose up -d postgres

  backend:
    type: build
    dependencies:
      - database
    # ...
```

## Environment Variables

Set job-specific environment variables:

```yaml
jobs:
  my-job:
    type: run
    env:
      DATABASE_URL: postgres://localhost/mydb
      LOG_LEVEL: debug
    script:
      - python app.py
```

Use `^` prefix to override existing variables:

```yaml
jobs:
  my-job:
    env:
      ^PATH: /custom/path:$PATH
```

## Tasks

Define multiple tasks within a job:

```yaml
jobs:
  my-app:
    type: build
    repo:
      # ...
    tasks:
      build:
        script:
          - make build
      test:
        script:
          - make test
      deploy:
        dependencies:
          - build
          - test
        script:
          - make deploy
```

Run specific tasks:

```bash
deprun task my-app --tasks build,test
```

## Conditional Execution

Use `when` clauses for conditional logic:

```yaml
jobs:
  my-app:
    type: build
    script:
      - echo "Building..."
    when:
      - condition: "getuid() == 0"
        data:
          script:
            - echo "Running as root"
```
