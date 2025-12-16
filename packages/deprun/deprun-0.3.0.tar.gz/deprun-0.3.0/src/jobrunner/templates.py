"""Template processing and merging utilities."""

from typing import Any, Dict

from jobrunner.models import Job, Template


class TemplateProcessor:
    """Processes and merges job templates."""

    @staticmethod
    def merge_template(job: Job, template: Template) -> None:
        """Merge a template into a job.
        
        Args:
            job: Job to merge into
            template: Template to merge from
        """
        # Merge scripts (template first, then job-specific)
        if template.script and not job.script:
            job.script = template.script.copy()
        
        # Merge dependencies
        if template.dependencies:
            existing = set(job.dependencies)
            for dep in template.dependencies:
                if dep not in existing:
                    job.dependencies.append(dep)
        
        # Merge environment variables (job overrides template)
        job.env = {**template.env, **job.env}

    @staticmethod
    def evaluate_conditions(job: Job, variables: Dict[str, Any]) -> None:
        """Evaluate and apply conditional rules.
        
        Args:
            job: Job to evaluate conditions for
            variables: Available variables for condition evaluation
        """
        for condition in job.when:
            try:
                # Safely evaluate condition
                result = eval(condition.condition, {"__builtins__": {}}, variables)
                if result:
                    # Merge conditional data
                    for key, value in condition.data.items():
                        if hasattr(job, key):
                            current = getattr(job, key)
                            if isinstance(current, list):
                                current.extend(value if isinstance(value, list) else [value])
                            elif isinstance(current, dict):
                                current.update(value if isinstance(value, dict) else {})
                            else:
                                setattr(job, key, value)
            except Exception:
                # Skip invalid conditions
                pass
