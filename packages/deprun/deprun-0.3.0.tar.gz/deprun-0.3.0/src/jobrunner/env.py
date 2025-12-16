"""Environment variable management utilities."""

import os
from typing import Dict, Optional


class EnvManager:
    """Manages environment variable context."""

    def __init__(self) -> None:
        """Initialize environment manager."""
        self.saved_vars: Dict[str, Optional[str]] = {}

    def push(self, env_vars: Dict[str, str]) -> None:
        """Save current environment and apply new variables.
        
        Args:
            env_vars: Variables to set
        """
        for key, value in env_vars.items():
            # Handle override prefix (^)
            actual_key = key.lstrip("^")
            
            # Save current value
            if actual_key not in self.saved_vars:
                self.saved_vars[actual_key] = os.environ.get(actual_key)
            
            # Set new value
            os.environ[actual_key] = value

    def pop(self) -> None:
        """Restore saved environment variables."""
        for key, value in self.saved_vars.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.saved_vars.clear()
