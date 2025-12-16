"""
MCP Resources - Direct dcisionai_graph Integration

These resources directly import from dcisionai_graph.core.models.model_registry,
eliminating the HTTP client layer.

⚠️ NOTE: api.models_endpoint is deprecated - use dcisionai_graph.core.models.model_registry instead
"""

from .models import get_model_resources, read_model_resource
from .solvers import get_solver_resources, read_solver_resource
from .jobs import read_job_resource, list_job_resources


def get_all_resources():
    """Get all available MCP resources"""
    resources = []
    resources.extend(get_model_resources())
    resources.extend(get_solver_resources())
    # Note: Job resources are dynamic (created on-demand) and not listed here
    return resources

