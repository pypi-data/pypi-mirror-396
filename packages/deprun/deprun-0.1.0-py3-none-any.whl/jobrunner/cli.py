"""Command-line interface for Job Runner."""

import json
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import Any, Optional

import click
import yaml
from rich.console import Console
from rich.table import Table

from jobrunner.config import ConfigLoader
from jobrunner.executor import JobExecutor
from jobrunner.exceptions import JobRunnerError, ConfigError
from jobrunner.graph import DependencyGraph

# ----------------------------------------------------------------------
# Constants and Enums
# ----------------------------------------------------------------------

class JobType(str, Enum):
    """Job types supported by the runner."""
    BUILD = "build"
    RUN = "run"


SUCCESS_MARK = "✓"
DEFAULT_JOBS_FILE = "jobs.yml"

console = Console()


# ----------------------------------------------------------------------
# Context Management
# ----------------------------------------------------------------------

@dataclass
class CliContext:
    """Context object for CLI state."""
    jobs_file: Path
    verbose: bool
    
    @cached_property
    def loader(self) -> ConfigLoader:
        """Lazy-load and cache the ConfigLoader."""
        if not self.jobs_file.exists():
            raise click.BadParameter(
                f"Path '{self.jobs_file}' does not exist",
                param_hint="'--jobs'"
            )
        return ConfigLoader(self.jobs_file)


# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------

def get_type_value(job: Any) -> str:
    """Extract type value from job, handling both enum and string types."""
    return getattr(job.type, "value", str(job.type))


def model_to_dict(obj: Any, exclude_none: bool = True) -> dict:
    """Convert a Pydantic model to dictionary.
    
    Args:
        obj: Pydantic model instance
        exclude_none: Whether to exclude None values
        
    Returns:
        Dictionary representation
    """
    if hasattr(obj, "model_dump"):
        return obj.model_dump(exclude_none=exclude_none)
    return vars(obj)


def compute_repository(job: Any) -> Optional[str]:
    """Compute full repository path from job configuration."""
    if not job.repo:
        return None
    return f"{job.repo.server}{job.repo.group}{job.repo.name}"


def compute_directory(job: Any) -> Optional[str]:
    """Compute the working directory for a job.
    
    For build jobs with repositories, constructs the local clone path.
    For other jobs, returns the configured directory as-is.
    """
    if not job.directory:
        return None

    # Build jobs compute local repo directory
    if get_type_value(job) == JobType.BUILD.value and job.repo:
        repo_name = Path(job.repo.name).stem
        return str(Path(job.directory) / job.repo.group / repo_name)

    return job.directory


def format_dependencies(job: Any) -> Optional[str]:
    """Format job dependencies as comma-separated string."""
    return ", ".join(job.dependencies) if job.dependencies else None


def get_job_info(job_name: str, job: Any, field: str) -> Optional[str]:
    """Get a specific field from a job.
    
    Args:
        job_name: Name of the job
        job: Job object
        field: Field name to extract
        
    Returns:
        Field value as string, or None if not applicable
    """
    field_getters = {
        "name": lambda: job_name,
        "type": lambda: get_type_value(job),
        "dependencies": lambda: format_dependencies(job),
        "repository": lambda: compute_repository(job),
        "directory": lambda: compute_directory(job),
        "description": lambda: job.description,
    }
    
    getter = field_getters.get(field)
    return getter() if getter else None


def get_available_info_fields() -> list[str]:
    """Get list of available info fields."""
    return ["name", "type", "dependencies", "repository", "directory", "description"]


def get_context(ctx: click.Context) -> CliContext:
    """Retrieve the CliContext from Click context."""
    return ctx.obj


# ----------------------------------------------------------------------
# Root CLI Group
# ----------------------------------------------------------------------

@click.group()
@click.option(
    "--jobs",
    type=click.Path(path_type=Path),
    default=DEFAULT_JOBS_FILE,
    envvar="JOBS_FILE",
    help="Path to the jobs definition file",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, jobs: Path, verbose: bool):
    """Job Runner - Multi-repository task automation."""
    ctx.obj = CliContext(jobs_file=jobs, verbose=verbose)


# ----------------------------------------------------------------------
# list Command
# ----------------------------------------------------------------------

@cli.command()
@click.pass_context
def list(ctx: click.Context):
    """List all available jobs."""
    try:
        cli_ctx = get_context(ctx)
        config = cli_ctx.loader.config

        if not config.jobs:
            console.print("[yellow]No jobs found.[/yellow]")
            return

        for name in sorted(config.jobs.keys()):
            print(name)

    except JobRunnerError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# run Command
# ----------------------------------------------------------------------

@cli.command()
@click.argument("job_name")
@click.argument("tasks", required=False, default=None)
@click.option("--depth", type=int, default=None, help="Maximum dependency depth (unlimited if not specified)")
@click.pass_context
def run(ctx: click.Context, job_name: str, tasks: Optional[str], depth: Optional[int]):
    """Run a job with its dependencies, or specific tasks within a job.
    
    TASKS can be a single task name or comma-separated list of tasks.
    Use "default" to refer to the job's main script.
    
    Examples:
        job-runner run libamxc                  # Run the job's main script
        job-runner run libamxc clean            # Run the 'clean' task
        job-runner run libamxc test             # Run the 'test' task
        job-runner run libamxc clean,default    # Run 'clean' task then main script
        job-runner run libamxc clean,test       # Run 'clean' then 'test' tasks
        job-runner run libamxc default          # Same as: job-runner run libamxc
    """
    try:
        cli_ctx = get_context(ctx)
        executor = JobExecutor(cli_ctx.loader, verbose=cli_ctx.verbose)

        if tasks:
            # Parse comma-separated task list
            task_list = [t.strip() for t in tasks.split(',')]
            
            if len(task_list) == 1:
                task_name = task_list[0]
                console.print(f"[bold green]Running task '{task_name}' in job:[/bold green] {job_name}")
                executor.run_task(job_name, task_name, max_depth=depth)
                console.print(f"[bold green]{SUCCESS_MARK} Task completed:[/bold green] {job_name}:{task_name}")
            else:
                task_display = ", ".join(task_list)
                console.print(f"[bold green]Running tasks in job {job_name}:[/bold green] {task_display}")
                executor.run_tasks(job_name, task_list, max_depth=depth)
                console.print(f"[bold green]{SUCCESS_MARK} Tasks completed:[/bold green] {job_name}")
        else:
            console.print(f"[bold green]Running job:[/bold green] {job_name}")
            executor.run(job_name, max_depth=depth)
            console.print(f"[bold green]{SUCCESS_MARK} Job completed:[/bold green] {job_name}")

    except JobRunnerError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# fetch Command
# ----------------------------------------------------------------------

@cli.command()
@click.argument("job_name")
@click.pass_context
def fetch(ctx: click.Context, job_name: str):
    """Fetch (clone) a repository for a build job without running scripts.
    
    This command only works on build jobs and will clone the repository
    to the correct directory without executing any build scripts.
    
    Example:
        job-runner fetch libamxc    # Clone the repository only
    """
    try:
        cli_ctx = get_context(ctx)
        executor = JobExecutor(cli_ctx.loader, verbose=cli_ctx.verbose)
        
        console.print(f"[bold green]Fetching job:[/bold green] {job_name}")
        executor.fetch(job_name)
        console.print(f"[bold green]{SUCCESS_MARK} Fetch completed:[/bold green] {job_name}")
        
    except JobRunnerError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# info Command
# ----------------------------------------------------------------------

@cli.command()
@click.argument("job_name")
@click.argument("info_type", required=False)
@click.pass_context
def info(ctx: click.Context, job_name: str, info_type: Optional[str]):
    """Show information about a job.

    INFO_TYPE can be one of: name, type, dependencies, repository, directory, description.
    If not specified, shows all information.
    """
    try:
        cli_ctx = get_context(ctx)
        config = cli_ctx.loader.config
        job = config.jobs.get(job_name)

        if not job:
            raise click.ClickException(f"Job not found: {job_name}")

        available_fields = get_available_info_fields()

        # If a specific field is requested, validate and print it
        if info_type:
            field = info_type.lower()
            if field not in available_fields:
                valid_fields = ", ".join(available_fields)
                raise click.ClickException(
                    f"Invalid info type: {info_type}. Valid: {valid_fields}"
                )
            value = get_job_info(job_name, job, field)
            if value is not None:
                click.echo(value)
            return

        # Show full table
        table = Table(title=f"Job Information: {job_name}", header_style="bold cyan")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        for field in available_fields:
            value = get_job_info(job_name, job, field)
            if value is not None:
                table.add_row(field.capitalize(), value)

        console.print(table)

    except JobRunnerError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# validate Command
# ----------------------------------------------------------------------

@cli.command()
@click.pass_context
def validate(ctx: click.Context):
    """Validate jobs configuration."""
    try:
        cli_ctx = get_context(ctx)
        _ = cli_ctx.loader.config
        console.print(f"[green]{SUCCESS_MARK} Configuration is valid[/green]")
    except JobRunnerError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# dump Command (Refactored)
# ----------------------------------------------------------------------

@cli.command()
@click.argument("job_name")
@click.option(
    "--format", "-f",
    type=click.Choice(["yaml", "json", "script"], case_sensitive=False),
    default="yaml",
    help="Output format (default: yaml)",
)
@click.pass_context
def dump(ctx: click.Context, job_name: str, format: str):
    """Dump a job definition in YAML, JSON, or script form.
    
    Examples:
        job-runner dump libamxc                # YAML format (default)
        job-runner dump libamxc --format json  # JSON format
        job-runner dump libamxc -f script      # Script of the job
    """
    try:
        cli_ctx = get_context(ctx)
        config = cli_ctx.loader.config
        job = config.jobs.get(job_name)

        if not job:
            raise click.ClickException(f"Job not found: {job_name}")

        # Build job dictionary
        job_dict = model_to_dict(job)
        job_dict["type"] = get_type_value(job)

        if getattr(job, "repo", None):
            job_dict["repo"] = model_to_dict(job.repo)

        if getattr(job, "tasks", None):
            job_dict["tasks"] = {
                name: model_to_dict(task)
                for name, task in job.tasks.items()
            }

        # Format output
        if format == "json":
            output = json.dumps({job_name: job_dict}, indent=2)
        elif format == "script":
            output = "\n".join(job.script) if job.script else "# No script defined"
        else:  # YAML
            output = yaml.dump(
                {job_name: job_dict},
                default_flow_style=False,
                sort_keys=False
            )

        console.print(output, markup=False, highlight=False)

    except ConfigError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# graph Command
# ----------------------------------------------------------------------

@cli.command()
@click.argument("job_name")
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file path (default: <job_name>-deps.md)"
)
@click.pass_context
def graph(ctx: click.Context, job_name: str, output: Optional[Path]):
    """Generate a Mermaid dependency graph for a job.
    
    Creates a Markdown file with a Mermaid flowchart showing the job's
    dependency tree.
    """
    try:
        cli_ctx = get_context(ctx)
        
        if job_name not in cli_ctx.loader.config.jobs:
            raise click.ClickException(f"Job not found: {job_name}")
        
        # Default output filename
        if not output:
            output = Path(f"{job_name}-deps.md")
        
        # Generate graph
        dep_graph = DependencyGraph(cli_ctx.loader)
        dep_graph.generate(job_name, output)
        
        console.print(f"[green]{SUCCESS_MARK} Dependency graph written to:[/green] {output}")
        
    except JobRunnerError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# Main Entry Point
# ----------------------------------------------------------------------

def main() -> None:
    """Main entry point for the CLI."""
    cli(obj=None)


if __name__ == "__main__":
    main()
