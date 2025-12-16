# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
