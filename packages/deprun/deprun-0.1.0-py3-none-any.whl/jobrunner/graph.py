"""Dependency graph generation."""

from pathlib import Path
from typing import Dict, List, Set

from jobrunner.config import ConfigLoader
from jobrunner.models import Job


class DependencyGraph:
    """Generates Mermaid dependency graphs."""

    def __init__(self, config: ConfigLoader) -> None:
        """Initialize graph generator.
        
        Args:
            config: Configuration loader instance
        """
        # Handle both ConfigLoader and Config objects
        if hasattr(config, 'config'):
            self.config = config.config
        else:
            self.config = config
        self.edges: Set[tuple[str, str]] = set()

    def generate(self, job_name: str, output_file: Path) -> None:
        """Generate dependency graph for a job.
        
        Args:
            job_name: Root job name
            output_file: Output markdown file path
        """
        self._collect_dependencies(job_name)
        self._remove_transitive_edges()
        self._write_mermaid(output_file)

    def _collect_dependencies(self, job_name: str, visited: Set[str] = None) -> None:
        """Recursively collect job dependencies."""
        if visited is None:
            visited = set()
        
        if job_name in visited:
            return
        visited.add(job_name)
        
        if job_name not in self.config.jobs:
            return
        
        job = self.config.jobs[job_name]
        
        if job.dependencies:
            for dep in job.dependencies:
                self.edges.add((job_name, dep))
                if dep in self.config.jobs:
                    self._collect_dependencies(dep, visited)
    
    def _remove_transitive_edges(self) -> None:
        """Remove redundant transitive edges.
        
        If A -> B and B -> C and A -> C, remove the direct A -> C edge
        since it's implied by the transitive path A -> B -> C.
        """
        # Build adjacency list
        graph: Dict[str, Set[str]] = {}
        for src, dst in self.edges:
            if src not in graph:
                graph[src] = set()
            graph[src].add(dst)
        
        # Find all transitive paths using DFS
        def get_all_reachable(node: str, exclude_direct: bool = False) -> Set[str]:
            """Get all nodes reachable from this node."""
            reachable = set()
            if node not in graph:
                return reachable
            
            for neighbor in graph[node]:
                if exclude_direct:
                    # Only add nodes reachable through paths of length > 1
                    reachable.update(get_all_reachable(neighbor, False))
                else:
                    reachable.add(neighbor)
                    reachable.update(get_all_reachable(neighbor, False))
            
            return reachable
        
        # Remove edges that are transitive
        edges_to_remove = set()
        for src, dst in self.edges:
            # Check if dst is reachable from src through other paths
            # (excluding the direct edge)
            transitive_reachable = set()
            if src in graph:
                for intermediate in graph[src]:
                    if intermediate != dst:  # Exclude the direct edge
                        transitive_reachable.update(get_all_reachable(intermediate, False))
            
            # If dst is reachable transitively, mark direct edge for removal
            if dst in transitive_reachable:
                edges_to_remove.add((src, dst))
        
        # Remove the redundant edges
        self.edges -= edges_to_remove

    def _write_mermaid(self, output_file: Path) -> None:
        """Write Mermaid diagram to file."""
        with open(output_file, "w") as f:
            f.write("```mermaid\n")
            f.write("flowchart LR\n")
            for src, dst in sorted(self.edges):
                f.write(f"    {src} --> {dst}\n")
            f.write("```\n")
