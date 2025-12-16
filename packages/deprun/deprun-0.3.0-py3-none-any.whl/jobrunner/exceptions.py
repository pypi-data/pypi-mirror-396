"""Custom exceptions for Job Runner."""


class JobRunnerError(Exception):
    """Base exception for all Job Runner errors."""
    pass


class ConfigError(JobRunnerError):
    """Configuration-related errors."""
    pass


class ExecutionError(JobRunnerError):
    """Job execution errors."""
    pass


class GitError(JobRunnerError):
    """Git operation errors."""
    pass


class ValidationError(JobRunnerError):
    """Configuration validation errors."""
    pass
