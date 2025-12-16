# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New `run-all` command to run multiple jobs in sequence
  - Filter by job type (`--type build` or `--type run`)
  - Filter by name pattern using wildcards (`--pattern "lib*"`)
  - Dry-run mode to preview execution (`--dry-run`)
  - Depth control for dependency traversal (`--depth N`)
  - Smart job tracking: skips jobs already run as dependencies
  - Stops on first failure for fast feedback
  - Progress indicator showing `[N/Total]` for each job
  - Summary report showing successfully completed and skipped jobs

### Changed
- Jobs loaded from `jobs-dir` are now always sorted alphabetically for predictable ordering

## [0.2.0] - 2025-12-12

### Added
- Multiple tasks execution support in single command
- Task chaining with comma-separated task list
- "default" keyword to reference job's main script

## [0.1.0] - 2025-12-11

### Added
- Initial release
- Job dependency resolution with circular dependency handling
- Template system with inheritance
- Git repository fetching
- Task-level execution within jobs
- Conditional configuration with `when` clauses
- Variable substitution system
- Multiple output formats (YAML, JSON, script)
- Dependency graph visualization with Mermaid
- CLI commands: list, run, info, validate, dump, graph
- Environment variable management per job
- Depth-limited dependency traversal
- Multi-file configuration support with jobs-dir

### Features
- Build jobs: Clone repositories and run build scripts
- Run jobs: Execute scripts in specified directories
- Template inheritance chains
- Source tracking for better error messages
- Verbose mode for debugging

[Unreleased]: https://gitlab.com/proj_amx_01/tools/job-runner/-/compare/v0.1.0...main
[0.1.0]: https://gitlab.com/proj_amx_01/tools/job-runner/-/releases/v0.1.0
