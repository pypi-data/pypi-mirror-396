"""Job execution engine."""

import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, Set, Iterator

from jobrunner.config import ConfigLoader
from jobrunner.exceptions import ExecutionError
from jobrunner.git import GitManager
from jobrunner.models import Job, JobType


class JobExecutor:
    """Executes jobs with dependency resolution."""

    # Constants
    TREE_CHAR = "├─ "
    SEPARATOR = "=" * 60
    SUCCESS_MARK = "✓"

    def __init__(
        self,
        config: ConfigLoader,
        verbose: bool = False,
        jobs_dir: Optional[Path] = None,
    ) -> None:
        """Initialize the executor.
        
        Args:
            config: Configuration loader instance
            verbose: Enable verbose output
            jobs_dir: Directory for repository clones
        """
        # Handle both ConfigLoader and Config objects
        if hasattr(config, 'config'):
            self.config = config.config
        else:
            self.config = config
        self.verbose = verbose
        self.jobs_dir = jobs_dir or Path.home() / "job-runner-repos"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.git = GitManager(config, verbose)
        self.completed: Set[str] = set()
        self.current_depth = 0  # Track current dependency depth for indentation

    # ------------------------------------------------------------------
    # Context Managers
    # ------------------------------------------------------------------

    @contextmanager
    def _env_context(self, env_vars: dict) -> Iterator[None]:
        """Context manager for temporary environment variables.
        
        Args:
            env_vars: Dictionary of environment variables to set
            
        Yields:
            None
            
        Note:
            Keys starting with '^' have the prefix removed.
            Original values are restored on exit.
        """
        if not env_vars:
            yield
            return

        original = {}
        clean_vars = {k.lstrip("^"): v for k, v in env_vars.items()}
        
        # Save original values and set new ones
        for key, value in clean_vars.items():
            original[key] = os.environ.get(key)
            os.environ[key] = value
        
        try:
            yield
        finally:
            # Restore original values
            for key, orig_value in original.items():
                if orig_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = orig_value

    @contextmanager
    def _working_dir(self, path: Path) -> Iterator[None]:
        """Context manager for temporary directory changes.
        
        Args:
            path: Directory to change to
            
        Yields:
            None
        """
        original = Path.cwd()
        try:
            os.chdir(path)
            if self.verbose:
                print(f"Working directory: {path}")
            yield
        finally:
            os.chdir(original)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, job_name: str, max_depth: Optional[int] = None) -> None:
        """Run a job with its dependencies.
        
        Args:
            job_name: Name of the job to run
            max_depth: Maximum dependency depth to follow (None = unlimited)
        """
        if job_name in self.completed:
            return

        if job_name not in self.config.jobs:
            raise ExecutionError(f"Job '{job_name}' not found")
        
        job = self.config.jobs[job_name]
        
        # Print start message first (before dependencies)
        self._print_execution_start(job_name, is_task=False)
        
        # Run dependencies (only if we haven't reached max depth)
        if self._should_process_dependencies(job.dependencies, max_depth):
            self.current_depth += 1
            self.git.current_depth = self.current_depth
            new_depth = self._decrement_depth(max_depth)
            for dep in job.dependencies:
                self.run(dep, new_depth)
            self.current_depth -= 1
            self.git.current_depth = self.current_depth

        # Execute the job
        self._execute_job_internal(job_name, job)
        self.completed.add(job_name)
        
        # Print completion message after execution
        self._print_execution_end(job_name, is_task=False)

    def fetch(self, job_name: str) -> None:
        """Fetch (clone) a repository for a build job without running scripts.
        
        Args:
            job_name: Name of the build job to fetch
            
        Raises:
            ExecutionError: If job is not found or not a build job
        """
        if job_name not in self.config.jobs:
            raise ExecutionError(f"Job '{job_name}' not found")
        
        job = self.config.jobs[job_name]
        
        # Verify this is a build job
        if job.type != JobType.BUILD:
            raise ExecutionError(
                f"Job '{job_name}' is not a build job (type: {job.type}). "
                f"Only build jobs can be fetched."
            )
        
        # Verify job has repository configuration
        if not job.repo:
            raise ExecutionError(
                f"Build job '{job_name}' has no repository configuration"
            )
        
        # Clone/update the repository
        if self.verbose:
            print(f"\n{self.SEPARATOR}")
            print(f"Fetching repository for job: {job_name}")
            print(f"{self.SEPARATOR}")
        else:
            print(f"[{job_name}] Fetching repository...")
        
        self.git.ensure_repository(job_name, job)
        repo_path = self.git.get_repo_path(job)
        
        if self.verbose:
            print(f"Repository cloned to: {repo_path}")
        
        print(f"[{job_name}] {self.SUCCESS_MARK} Repository fetched: {repo_path}")

    def run_tasks(
        self,
        job_name: str,
        task_names: List[str],
        max_depth: Optional[int] = None
    ) -> None:
        """Run multiple tasks within a job.
        
        Args:
            job_name: Name of the job containing the tasks
            task_names: List of task names to run (can include "default")
            max_depth: Maximum dependency depth to follow (None = unlimited)
        """
        if job_name not in self.config.jobs:
            raise ExecutionError(f"Job '{job_name}' not found")
        
        job = self.config.jobs[job_name]
        
        # Run job dependencies once (not per task)
        if self._should_process_dependencies(job.dependencies, max_depth):
            self.current_depth += 1
            self.git.current_depth = self.current_depth
            new_depth = self._decrement_depth(max_depth)
            for dep in job.dependencies:
                self.run(dep, new_depth)
            self.current_depth -= 1
            self.git.current_depth = self.current_depth
        
        # Run each task in order
        for task_name in task_names:
            if task_name == "default":
                # Special case: run the default job script with print messages
                self._print_execution_start(job_name, is_task=False)
                self._execute_job_internal(job_name, job)
                self._print_execution_end(job_name, is_task=False)
            else:
                # Regular task execution
                self._run_single_task(job_name, job, task_name, max_depth)

    def run_task(
        self, 
        job_name: str, 
        task_name: str, 
        max_depth: Optional[int] = None
    ) -> None:
        """Run a specific task within a job.
        
        Args:
            job_name: Name of the job containing the task
            task_name: Name of the task to run (can be "default")
            max_depth: Maximum dependency depth to follow (None = unlimited)
        """
        # Delegate to run_tasks for consistency
        self.run_tasks(job_name, [task_name], max_depth)

    def _run_single_task(
        self,
        job_name: str,
        job: Job,
        task_name: str,
        max_depth: Optional[int] = None
    ) -> None:
        """Run a single task (internal helper).
        
        Args:
            job_name: Name of the job
            job: Job object
            task_name: Name of the task to run
            max_depth: Maximum dependency depth to follow
        """
        # Check if task exists
        if not job.tasks or task_name not in job.tasks:
            available = ", ".join(job.tasks.keys()) if job.tasks else "none"
            raise ExecutionError(
                f"Task '{task_name}' not found in job '{job_name}'. "
                f"Available tasks: {available}"
            )
        
        task = job.tasks[task_name]
        
        # Run task dependencies
        task_deps = getattr(task, 'dependencies', None)
        if self._should_process_dependencies(task_deps, max_depth):
            self.current_depth += 1
            self.git.current_depth = self.current_depth
            new_depth = self._decrement_depth(max_depth)
            for dep in task_deps:
                self._run_dependency(dep, new_depth)
            self.current_depth -= 1
            self.git.current_depth = self.current_depth
        
        # Execute the task
        self._execute_task(job_name, job, task_name, task)

    # ------------------------------------------------------------------
    # Execution Logic
    # ------------------------------------------------------------------

    def _execute_job_internal(self, name: str, job: Job) -> None:
        """Execute a single job (internal, no print messages)."""
        # Combine environment setup and execution
        with self._env_context(job.env):
            work_dir = self._get_work_directory(name, job)
            
            if work_dir:
                with self._working_dir(work_dir):
                    self._run_job_scripts(job.script, name, job)
            else:
                self._run_job_scripts(job.script, name, job)

    def _execute_task(self, job_name: str, job: Job, task_name: str, task) -> None:
        """Execute a single task within a job."""
        full_name = f"{job_name}:{task_name}"
        self._print_execution_start(full_name, is_task=True)
        
        # Merge job and task environment variables
        merged_env = {**job.env}
        if hasattr(task, 'env') and task.env:
            merged_env.update(task.env)
        
        with self._env_context(merged_env):
            work_dir = self._get_work_directory(job_name, job)
            
            # Execute task scripts
            task_script = getattr(task, 'script', None)
            if not task_script:
                raise ExecutionError(f"Task '{task_name}' has no script to execute")
            
            if work_dir:
                with self._working_dir(work_dir):
                    self._run_job_scripts(task_script, job_name, job)
            else:
                self._run_job_scripts(task_script, job_name, job)
        
        self._print_execution_end(full_name, is_task=True)

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    def _should_process_dependencies(
        self, 
        dependencies: Optional[List[str]], 
        max_depth: Optional[int]
    ) -> bool:
        """Check if dependencies should be processed.
        
        Args:
            dependencies: List of dependency names
            max_depth: Maximum depth remaining
            
        Returns:
            True if dependencies should be processed
        """
        return bool(dependencies and (max_depth is None or max_depth > 0))

    def _decrement_depth(self, max_depth: Optional[int]) -> Optional[int]:
        """Decrement depth counter, handling None (unlimited).
        
        Args:
            max_depth: Current max depth
            
        Returns:
            Decremented depth, or None if unlimited
        """
        return None if max_depth is None else max_depth - 1

    def _run_dependency(self, dep: str, max_depth: Optional[int]) -> None:
        """Run a dependency (either a job or a task reference).
        
        Args:
            dep: Dependency name (job or job:task format)
            max_depth: Maximum depth to follow
        """
        if ':' in dep:
            # Task reference: job:task
            dep_job, dep_task = dep.split(':', 1)
            self.run_task(dep_job, dep_task, max_depth)
        else:
            # Job reference
            self.run(dep, max_depth)

    def _get_work_directory(self, name: str, job: Job) -> Optional[Path]:
        """Get the working directory for a job.
        
        Args:
            name: Job name
            job: Job object
            
        Returns:
            Path to working directory, or None if no directory needed
        """
        if job.type == JobType.BUILD:
            if not job.repo:
                raise ExecutionError(
                    f"Build job '{name}' missing repository configuration"
                )
            
            self.git.ensure_repository(name, job)
            return self.git.get_repo_path(job)
        
        elif job.type == JobType.RUN and job.directory:
            work_dir = Path(job.directory).expanduser()
            work_dir.mkdir(parents=True, exist_ok=True)
            return work_dir
        
        return None

    def _run_job_scripts(
        self, 
        scripts: Optional[List[str]], 
        job_name: str, 
        job: Job
    ) -> None:
        """Execute job scripts if they exist.
        
        Args:
            scripts: List of script commands
            job_name: Name of the job
            job: Job object
        """
        if scripts:
            self._run_scripts(scripts, job_name, job)

    def _run_scripts(self, scripts: List[str], job_name: str, job: Job) -> None:
        """Execute a list of script commands.
        
        Args:
            scripts: List of shell commands to execute
            job_name: Name of the job (for variable substitution)
            job: Job object (for environment variables)
        """
        for cmd in scripts:
            resolved_cmd = self._resolve_command(cmd, job_name, job)
            
            if self.verbose:
                print(f"$ {resolved_cmd}")
            else:
                # Print command (first line only for multi-line commands)
                cmd_lines = resolved_cmd.split('\n')
                if len(cmd_lines) > 1:
                    indent = "  " * (self.current_depth + 1)
                    print(f"{indent}$ {cmd_lines[0].strip()} ...")
                else:
                    indent = "  " * (self.current_depth + 1)
                    print(f"{indent}$ {resolved_cmd.strip()}")
            
            try:
                subprocess.run(
                    resolved_cmd,
                    shell=True,
                    capture_output=not self.verbose,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                raise ExecutionError(
                    f"Command failed with exit code {e.returncode}: {resolved_cmd}"
                ) from e

    def _resolve_command(self, cmd: str, job_name: str, job: Job) -> str:
        """Resolve variables and special markers in command.
        
        Special markers:
            {name}: Replaced with job name
            $$: Replaced with 'sudo' (if not root) or '' (if root)
        
        Args:
            cmd: Command template
            job_name: Job name for substitution
            job: Job object for environment variables
            
        Returns:
            Resolved command string
        """
        # Determine sudo replacement
        sudo_cmd = "" if os.geteuid() == 0 else "sudo"
        
        # Resolve variables
        resolved = cmd.format(
            name=job_name,
            **self.config.variables,
            **job.env
        )
        
        # Replace $$ with sudo or empty
        resolved = resolved.replace("$$", sudo_cmd)
        
        # Clean up extra spaces
        return " ".join(resolved.split())

    # ------------------------------------------------------------------
    # Output Formatting
    # ------------------------------------------------------------------

    def _print_execution_start(self, name: str, is_task: bool = False) -> None:
        """Print execution start message.
        
        Args:
            name: Job or task name
            is_task: True if this is a task, False if job
        """
        indent = "  " * self.current_depth
        entity_type = "task" if is_task else "job"
        
        if self.verbose:
            print(f"\n{self.SEPARATOR}")
            print(f"Executing {entity_type}: {name}")
            print(f"{self.SEPARATOR}")
        else:
            print(f"{indent}[{name}] Running {entity_type}...")

    def _print_execution_end(self, name: str, is_task: bool = False) -> None:
        """Print execution completion message.
        
        Args:
            name: Job or task name
            is_task: True if this is a task, False if job
        """
        if not self.verbose:
            indent = "  " * self.current_depth
            entity_type = "Task" if is_task else "Job"
            print(f"{indent}[{name}] {self.SUCCESS_MARK} {entity_type} completed")
