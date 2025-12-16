 
"""Configuration loading and processing."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Set, Optional

import yaml

from jobrunner.exceptions import ConfigError
from jobrunner.models import Config, Job, Template, Repository, Task, WhenCondition

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Helper Classes
# ----------------------------------------------------------------------

class AttrDict:
    """Dictionary wrapper that allows attribute-style access.
    
    Used for safe evaluation of conditional expressions.
    """
    
    def __init__(self, data: dict) -> None:
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, AttrDict(value))
            else:
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        return f"AttrDict({self.__dict__})"


# ----------------------------------------------------------------------
# Main Configuration Loader
# ----------------------------------------------------------------------

class ConfigLoader:
    """Loads and processes job configuration from YAML files.
    
    Processing Steps:
        1. Load YAML files (main + jobs-dir)
        2. Process and resolve variables
        3. Resolve template inheritance
        4. Apply templates to jobs
        5. Resolve variables in final job definitions
        6. Validate all job configurations
    """

    def __init__(self, config_file: Path) -> None:
        """Initialize config loader.
        
        Args:
            config_file: Path to the main YAML configuration file
        """
        logger.info(f"Loading configuration from {config_file}")
        self.config_file = config_file
        
        # Initialize raw data storage
        self._raw_templates: Dict[str, dict] = {}
        self._raw_jobs: Dict[str, dict] = {}
        
        # Track source files for better error messages
        self._job_sources: Dict[str, Path] = {}
        self._template_sources: Dict[str, Path] = {}
        
        # Step 1: Load YAML files
        self._load_config()
        self._load_additional_configs()
        
        # Step 2: Process and resolve variables
        self._process_variables()
        
        # Step 3: Resolve all templates (templates can use templates)
        self._resolve_templates()
        
        # Step 4: Apply templates to jobs
        self._resolve_jobs()
        
        # Step 5: Resolve variables in final jobs
        self._resolve_job_variables()
        
        logger.info(f"Successfully loaded {len(self.config.jobs)} jobs and {len(self._raw_templates)} templates")

    # ------------------------------------------------------------------
    # YAML Loading
    # ------------------------------------------------------------------

    def _load_yaml_file(self, file_path: Path) -> dict:
        """Load a YAML file and extract templates, jobs, and variables.
        
        Args:
            file_path: Path to the YAML file to load
            
        Returns:
            The loaded YAML data dictionary
            
        Raises:
            ConfigError: If file cannot be loaded or parsed
        """
        logger.debug(f"Loading YAML file: {file_path}")
        
        try:
            with open(file_path) as f:
                data = yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise ConfigError(f"Config file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in {file_path}: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to load {file_path}: {e}")
        
        # Store templates as raw data with source tracking
        if "templates" in data:
            for name, template_data in data["templates"].items():
                if name in self._raw_templates:
                    existing_source = self._template_sources[name]
                    raise ConfigError(
                        f"Duplicate template '{name}' found in {file_path} "
                        f"(already defined in {existing_source})"
                    )
                self._raw_templates[name] = template_data
                self._template_sources[name] = file_path
                logger.debug(f"Loaded template '{name}' from {file_path}")
        
        # Store jobs as raw data with source tracking
        if "jobs" in data:
            for name, job_data in data["jobs"].items():
                if name in self._raw_jobs:
                    existing_source = self._job_sources[name]
                    raise ConfigError(
                        f"Duplicate job '{name}' found in {file_path} "
                        f"(already defined in {existing_source})"
                    )
                self._raw_jobs[name] = job_data
                self._job_sources[name] = file_path
                logger.debug(f"Loaded job '{name}' from {file_path}")
        
        # Merge variables into config
        if "variables" in data and hasattr(self, 'config'):
            self.config.variables.update(data["variables"])
            logger.debug(f"Merged variables from {file_path}")
        
        return data

    def _load_config(self) -> None:
        """Load the main configuration file."""
        data = self._load_yaml_file(self.config_file)
        
        # Create config object with variables and jobs-dir
        self.config = Config(
            variables=data.get("variables", {}),
            templates={},
            jobs={},
            jobs_dir=data.get("jobs-dir")
        )

    def _load_additional_configs(self) -> None:
        """Load additional configuration files from jobs-dir."""
        if not self.config.jobs_dir:
            logger.debug("No jobs-dir specified, skipping additional configs")
            return

        jobs_dir = Path(self.config.jobs_dir)
        if not jobs_dir.is_absolute():
            jobs_dir = self.config_file.parent / jobs_dir
        
        jobs_dir = jobs_dir.expanduser()
        
        if not jobs_dir.exists():
            raise ConfigError(f"jobs-dir does not exist: {jobs_dir}")
        
        if not jobs_dir.is_dir():
            raise ConfigError(f"jobs-dir is not a directory: {jobs_dir}")

        # Find all YAML files recursively
        yaml_files = sorted(jobs_dir.rglob("*.yml")) + sorted(jobs_dir.rglob("*.yaml"))
        logger.info(f"Loading {len(yaml_files)} additional YAML files from {jobs_dir}")
        
        # Load each YAML file
        for yaml_file in yaml_files:
            self._load_yaml_file(yaml_file)

    # ------------------------------------------------------------------
    # Variable Processing
    # ------------------------------------------------------------------

    def _process_variables(self) -> None:
        """Process and resolve variables from environment and config."""
        logger.debug("Processing variables")
        
        # Add environment variables
        env_vars = dict(os.environ)
        if "SUDO_USER" in env_vars:
            env_vars["USER"] = env_vars["SUDO_USER"]
        
        # Merge with config variables (config overrides environment)
        self.variables = {**env_vars, **self.config.variables}
        
        # Resolve variable references (variables can reference other variables)
        self._resolve_dict_vars(self.variables)
        
        logger.debug(f"Processed {len(self.variables)} variables")

    def _resolve_dict_vars(self, data: Dict[str, Any]) -> None:
        """Recursively resolve variables in a dictionary.
        
        Variables use Python format string syntax: {variable_name}
        """
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    data[key] = value.format(**self.variables)
                except KeyError as e:
                    logger.debug(f"Unresolved variable in '{key}': {e}")
            elif isinstance(value, dict):
                self._resolve_dict_vars(value)
            elif isinstance(value, list):
                self._resolve_list_vars(value)

    def _resolve_list_vars(self, data: list) -> None:
        """Recursively resolve variables in a list."""
        for i, value in enumerate(data):
            if isinstance(value, str):
                try:
                    data[i] = value.format(**self.variables)
                except KeyError as e:
                    logger.debug(f"Unresolved variable in list item: {e}")
            elif isinstance(value, dict):
                self._resolve_dict_vars(value)
            elif isinstance(value, list):
                self._resolve_list_vars(value)

    def _resolve_object_vars(self, obj: Any) -> None:
        """Resolve variables in a Pydantic model."""
        # Iterate through model fields
        for field_name in obj.model_fields:
            field_value = getattr(obj, field_name)
            
            if isinstance(field_value, str):
                try:
                    resolved = field_value.format(**self.variables)
                    setattr(obj, field_name, resolved)
                except KeyError as e:
                    logger.debug(f"Unresolved variable in {field_name}: {e}")
            elif isinstance(field_value, dict):
                self._resolve_dict_vars(field_value)
            elif isinstance(field_value, list):
                self._resolve_list_vars(field_value)
            elif isinstance(field_value, Repository):
                # Recursively resolve Repository fields
                self._resolve_object_vars(field_value)
            elif isinstance(field_value, (Task, WhenCondition)):
                # Recursively resolve nested models
                self._resolve_object_vars(field_value)

    # ------------------------------------------------------------------
    # Template Resolution
    # ------------------------------------------------------------------

    def _get_template_list(self, data: dict) -> List[str]:
        """Extract template list from data, normalizing to list format.
        
        Supports both 'template' (single) and 'templates' (list) keys.
        """
        if "templates" in data:
            templates = data["templates"]
        elif "template" in data:
            templates = data["template"]
        else:
            return []
        
        return [templates] if isinstance(templates, str) else templates

    def _resolve_templates(self) -> None:
        """Resolve templates that use other templates.
        
        Templates can inherit from other templates, creating a chain.
        This method resolves the entire inheritance chain.
        """
        logger.debug("Resolving template inheritance")
        resolved = set()
        
        def resolve_template(template_name: str, visited: Set[str]) -> dict:
            """Recursively resolve a template's inheritance chain."""
            if template_name in resolved:
                return self._raw_templates[template_name]
            
            if template_name in visited:
                chain = " -> ".join(visited) + f" -> {template_name}"
                raise ConfigError(f"Circular template dependency: {chain}")
            
            if template_name not in self._raw_templates:
                source = self._template_sources.get(template_name, "unknown")
                raise ConfigError(
                    f"Template '{template_name}' not found (referenced from {source})"
                )
            
            visited.add(template_name)
            template_data = self._raw_templates[template_name].copy()
            
            # Get parent templates
            parent_templates = self._get_template_list(template_data)
            
            if parent_templates:
                # Remove template key from data
                template_data.pop("templates", None)
                template_data.pop("template", None)
                
                # Merge parent templates in order
                merged_data = {}
                for parent_name in parent_templates:
                    parent_data = resolve_template(parent_name, visited.copy())
                    merged_data = self._deep_merge(merged_data, parent_data)
                
                # Merge current template on top
                template_data = self._deep_merge(merged_data, template_data)
            
            # Process when conditions in the template
            template_data = self._process_when_conditions(template_data)
            
            self._raw_templates[template_name] = template_data
            resolved.add(template_name)
            logger.debug(f"Resolved template '{template_name}'")
            return template_data
        
        # Resolve all templates
        for template_name in list(self._raw_templates.keys()):
            resolve_template(template_name, set())
        
        logger.debug(f"Resolved {len(resolved)} templates")

    # ------------------------------------------------------------------
    # Job Resolution
    # ------------------------------------------------------------------

    def _resolve_jobs(self) -> None:
        """Resolve jobs by applying template inheritance.
        
        Templates are applied left-to-right, with later templates
        overriding earlier ones. Job data overrides all templates.
        """
        logger.debug("Resolving jobs with template inheritance")
        
        for job_name, job_data in self._raw_jobs.items():
            try:
                # Get template list
                job_templates = self._get_template_list(job_data)
                
                if job_templates:
                    # Remove template keys from job data
                    job_data.pop("templates", None)
                    job_data.pop("template", None)
                    
                    # Apply template chain
                    merged_data = self._apply_template_chain(job_templates)
                    
                    # Merge job data on top (job overrides templates)
                    job_data = self._deep_merge(merged_data, job_data)
                    
                    logger.debug(f"Applied templates {job_templates} to job '{job_name}'")
                
                # Process when conditions
                job_data = self._process_when_conditions(job_data)
                
                # Substitute {job_name} placeholder in all string values
                job_data = self._substitute_job_name(job_data, job_name)
                
                # Create and validate the Job object
                self.config.jobs[job_name] = Job(**job_data)
                logger.debug(f"Created job '{job_name}'")
                
            except Exception as e:
                source = self._job_sources.get(job_name, "unknown")
                raise ConfigError(
                    f"Failed to process job '{job_name}' from {source}: {e}"
                ) from e

    def _apply_template_chain(self, template_names: List[str]) -> dict:
        """Apply a chain of templates, merging them left-to-right.
        
        Args:
            template_names: List of template names to apply in order
            
        Returns:
            Merged template data
            
        Example:
            templates: [common, python, django]
            Result: common <- python <- django
        """
        merged = {}
        for template_name in template_names:
            if template_name not in self._raw_templates:
                raise ConfigError(f"Template '{template_name}' not found")
            
            template_data = self._raw_templates[template_name].copy()
            merged = self._deep_merge(merged, template_data)
        
        return merged

    def _resolve_job_variables(self) -> None:
        """Resolve variables in all jobs after they're created."""
        logger.debug("Resolving variables in jobs")
        
        for job_name, job in self.config.jobs.items():
            try:
                self._resolve_object_vars(job)
            except Exception as e:
                logger.warning(f"Failed to resolve variables in job '{job_name}': {e}")

    # ------------------------------------------------------------------
    # Conditional Processing
    # ------------------------------------------------------------------

    def _process_when_conditions(self, data: dict) -> dict:
        """Process and apply 'when' conditional data.
        
        When conditions allow conditional inclusion of data based on
        expressions that can reference variables and current data fields.
        """
        if "when" not in data:
            return data
        
        when_conditions = data.get("when", [])
        if not when_conditions:
            return data
        
        # Process each condition
        for condition in when_conditions:
            if not isinstance(condition, dict):
                continue
            
            condition_expr = condition.get("condition", "")
            condition_data = condition.get("data", {})
            
            # Evaluate the condition with current data state
            if self._evaluate_condition(condition_expr, data):
                # Merge the conditional data
                data = self._deep_merge(data, condition_data)
                logger.debug(f"Applied conditional data: {condition_expr}")
        
        # Remove 'when' field after processing
        return {k: v for k, v in data.items() if k != "when"}

    def _evaluate_condition(self, condition: str, current_data: dict) -> bool:
        """Evaluate a when condition expression.
        
        The condition can reference:
        - variables: dict of configuration variables
        - Fields from current_data (e.g., repo.server, repo.group, etc.)
        
        WARNING: Uses eval() with restricted builtins. Consider using
        a safer expression evaluator like simpleeval for production.
        """
        if not condition:
            return False
        
        try:
            # Create a safe evaluation context
            eval_context = {
                "variables": self.variables,
            }
            
            # Convert current_data dictionaries to AttrDict for attribute access
            for key, value in current_data.items():
                if isinstance(value, dict):
                    eval_context[key] = AttrDict(value)
                else:
                    eval_context[key] = value
            
            # Evaluate with restricted builtins
            result = eval(condition, {"__builtins__": {}}, eval_context)
            return bool(result)
            
        except Exception as e:
            logger.warning(f"Failed to evaluate condition '{condition}': {e}")
            return False

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    def _substitute_job_name(self, data: Any, job_name: str) -> Any:
        """Recursively substitute {job_name} placeholder in all string values."""
        if isinstance(data, str):
            return data.replace("{job_name}", job_name)
        elif isinstance(data, dict):
            return {k: self._substitute_job_name(v, job_name) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._substitute_job_name(item, job_name) for item in data]
        else:
            return data

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries, with override taking precedence.
        
        Args:
            base: Base dictionary
            override: Override dictionary (values take precedence)
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override value
                result[key] = value
        
        return result
