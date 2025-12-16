"""Data models for Job Runner using Pydantic."""

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class JobType(str, Enum):
    """Types of jobs."""
    BUILD = "build"
    RUN = "run"
    ALIAS = "alias"
    INSTALL = "install"


class Repository(BaseModel):
    """Git repository configuration."""
    server: Optional[str] = None
    group: Optional[str] = None
    name: Optional[str] = None
    version_ref: Optional[str] = None


class WhenCondition(BaseModel):
    """Conditional execution rule."""
    condition: str = Field(..., description="Python expression to evaluate")
    data: Dict[str, Any] = Field(..., description="Data to merge if condition is true")


class Task(BaseModel):
    """Task definition."""
    script: List[str] = Field(default_factory=list, description="Commands to execute")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")


class Job(BaseModel):
    """Job configuration."""
    type: JobType = Field(..., description="Job type")
    description: Optional[str] = Field(None, description="Job description")
    dependencies: List[str] = Field(default_factory=list, description="Job dependencies")
    script: List[str] = Field(default_factory=list, description="Commands to execute")
    tasks: Dict[str, Union[str, Task]] = Field(default_factory=dict, description="Named tasks")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    template: Optional[Union[str, List[str]]] = Field(None, description="Template(s) to inherit")
    when: List[WhenCondition] = Field(default_factory=list, description="Conditional rules")
    
    # Build-specific fields
    repo: Optional[Repository] = Field(None, description="Repository configuration")
    directory: Optional[str] = Field(None, description="Working directory")
    
    @field_validator("dependencies", "script", mode="before")
    @classmethod
    def ensure_list(cls, v: Any) -> List[str]:
        """Ensure fields are lists."""
        if isinstance(v, str):
            return [v]
        return v or []


class Template(BaseModel):
    """Template configuration - all fields optional for merging."""

    type: JobType | None = None
    description: str | None = None
    directory: str | None = None
    repo: dict[str, str] | None = None  # Use dict to allow partial repo info
    script: list[str] | None = None
    dependencies: list[str] | None = None
    env: dict[str, str] | None = None
    when: list[WhenCondition] | None = None
    templates: list[str] | None = None  # Templates can use templates
    
    @field_validator("script", "dependencies", mode="before")
    @classmethod
    def ensure_list(cls, v: Any) -> list[str]:
        """Convert single values to lists."""
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return v


class Config(BaseModel):
    """Main configuration file structure."""
    model_config = {"populate_by_name": True}
    
    variables: Dict[str, str] = Field(default_factory=dict)
    templates: Dict[str, Template] = Field(default_factory=dict)
    jobs: Dict[str, Job] = Field(default_factory=dict)
    jobs_dir: Optional[str] = Field(None, alias="jobs-dir")
