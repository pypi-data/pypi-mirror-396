"""
MCP Resource Handler for Jobs

Exposes job results as MCP resources following the protocol:
- job://job_id/status - Job status and metadata
- job://job_id/result - Final workflow result
- job://job_id/intent - Intent discovery results
- job://job_id/data - Data generation results
- job://job_id/solver - Solver optimization results
- job://job_id/explanation - Business explanation results
- job://job_id/progress - Current progress (for running jobs)

Following MCP Protocol:
- Resources are read-only (GET only)
- URIs follow job:// scheme
- Responses include HATEOAS links
- Compatible with existing MCP resource patterns
"""

import json
import logging
from typing import Dict, Any, Optional

from dcisionai_mcp_server.jobs.storage import get_job
from dcisionai_mcp_server.jobs.schemas import JobStatus

logger = logging.getLogger(__name__)


def read_job_resource(uri: str) -> Dict[str, Any]:
    """
    Read a job resource by URI.

    MCP Resource Pattern:
    - job://job_id/status -> Job status and metadata
    - job://job_id/result -> Final workflow result
    - job://job_id/intent -> Intent discovery results
    - job://job_id/data -> Data generation results
    - job://job_id/solver -> Solver optimization results
    - job://job_id/explanation -> Business explanation results
    - job://job_id/progress -> Current progress

    Args:
        uri: MCP resource URI (e.g., "job://test_123/status")

    Returns:
        Resource content dictionary

    Raises:
        ValueError: If URI format is invalid
        KeyError: If job not found
        RuntimeError: If resource type is invalid for job status
    """
    logger.info(f"Reading job resource: {uri}")

    # Parse URI: job://job_id/resource_type
    if not uri.startswith("job://"):
        raise ValueError(f"Invalid job URI scheme: {uri}. Must start with 'job://'")

    parts = uri[6:].split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid job URI format: {uri}. Expected 'job://job_id/resource_type'")

    job_id, resource_type = parts

    # Get job from storage
    job_record = get_job(job_id)
    if not job_record:
        raise KeyError(f"Job not found: {job_id}")

    # Route to resource handler
    if resource_type == "status":
        return _read_job_status(job_record)
    elif resource_type == "result":
        return _read_job_result(job_record)
    elif resource_type == "intent":
        return _read_job_intent(job_record)
    elif resource_type == "data":
        return _read_job_data(job_record)
    elif resource_type == "solver":
        return _read_job_solver(job_record)
    elif resource_type == "explanation":
        return _read_job_explanation(job_record)
    elif resource_type == "progress":
        return _read_job_progress(job_record)
    else:
        raise ValueError(f"Unknown resource type: {resource_type}")


def _read_job_status(job_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read job status resource.

    Returns job metadata, status, and HATEOAS links.

    Args:
        job_record: Job record from storage

    Returns:
        Status resource with metadata and links
    """
    job_id = job_record["job_id"]
    status = job_record["status"]

    # Parse progress if available
    progress = None
    if job_record["progress"]:
        progress = json.loads(job_record["progress"])

    # Parse error if available
    error = None
    if job_record["error"]:
        error = job_record["error"]

    # Build HATEOAS links
    links = {
        "self": f"job://{job_id}/status",
        "progress": f"job://{job_id}/progress",
    }

    # Add result links if completed
    if status == JobStatus.COMPLETED.value:
        links["result"] = f"job://{job_id}/result"
        links["intent"] = f"job://{job_id}/intent"
        links["data"] = f"job://{job_id}/data"
        links["solver"] = f"job://{job_id}/solver"
        links["explanation"] = f"job://{job_id}/explanation"

    resource = {
        "uri": f"job://{job_id}/status",
        "type": "job_status",
        "job_id": job_id,
        "session_id": job_record["session_id"],
        "status": status,
        "priority": job_record["priority"],
        "created_at": job_record["created_at"],
        "started_at": job_record["started_at"],
        "completed_at": job_record["completed_at"],
        "user_query": job_record["user_query"],
        "use_case": job_record["use_case"],
        "progress": progress,
        "error": error,
        "links": links,
    }

    logger.info(f"Job status resource: {job_id} -> {status}")
    return resource


def _read_job_result(job_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read job result resource.

    Returns final workflow result with all artifacts.

    Args:
        job_record: Job record from storage

    Returns:
        Result resource with workflow state

    Raises:
        RuntimeError: If job is not completed
    """
    job_id = job_record["job_id"]
    status = job_record["status"]

    if status != JobStatus.COMPLETED.value:
        raise RuntimeError(f"Job {job_id} not completed (status: {status}). Result not available.")

    # Parse result
    if not job_record["result"]:
        raise RuntimeError(f"Job {job_id} marked as completed but has no result")

    result = json.loads(job_record["result"])

    # Build HATEOAS links
    links = {
        "self": f"job://{job_id}/result",
        "status": f"job://{job_id}/status",
        "intent": f"job://{job_id}/intent",
        "data": f"job://{job_id}/data",
        "solver": f"job://{job_id}/solver",
        "explanation": f"job://{job_id}/explanation",
    }

    resource = {
        "uri": f"job://{job_id}/result",
        "type": "job_result",
        "job_id": job_id,
        "status": status,
        "completed_at": job_record["completed_at"],
        "result": result,
        "links": links,
    }

    logger.info(f"Job result resource: {job_id}")
    return resource


def _read_job_intent(job_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read job intent discovery resource.

    Returns intent discovery results from Dame Workflow.

    Args:
        job_record: Job record from storage

    Returns:
        Intent resource with discovery results

    Raises:
        RuntimeError: If job is not completed
    """
    job_id = job_record["job_id"]
    status = job_record["status"]

    if status != JobStatus.COMPLETED.value:
        raise RuntimeError(f"Job {job_id} not completed (status: {status}). Intent not available.")

    # Parse result and extract intent
    result = json.loads(job_record["result"])
    workflow_state = result.get("workflow_state", {})
    intent = workflow_state.get("intent", {})

    # Build HATEOAS links
    links = {
        "self": f"job://{job_id}/intent",
        "status": f"job://{job_id}/status",
        "result": f"job://{job_id}/result",
    }

    resource = {
        "uri": f"job://{job_id}/intent",
        "type": "job_intent",
        "job_id": job_id,
        "intent": intent,
        "links": links,
    }

    logger.info(f"Job intent resource: {job_id}")
    return resource


def _read_job_data(job_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read job data generation resource.

    Returns data generation results from Dame Workflow.

    Args:
        job_record: Job record from storage

    Returns:
        Data resource with generation results

    Raises:
        RuntimeError: If job is not completed
    """
    job_id = job_record["job_id"]
    status = job_record["status"]

    if status != JobStatus.COMPLETED.value:
        raise RuntimeError(f"Job {job_id} not completed (status: {status}). Data not available.")

    # Parse result and extract data
    result = json.loads(job_record["result"])
    workflow_state = result.get("workflow_state", {})
    data_pack = workflow_state.get("data_pack", {})

    # Build HATEOAS links
    links = {
        "self": f"job://{job_id}/data",
        "status": f"job://{job_id}/status",
        "result": f"job://{job_id}/result",
    }

    resource = {
        "uri": f"job://{job_id}/data",
        "type": "job_data",
        "job_id": job_id,
        "data_pack": data_pack,
        "links": links,
    }

    logger.info(f"Job data resource: {job_id}")
    return resource


def _read_job_solver(job_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read job solver optimization resource.

    Returns solver results from Dame Workflow.

    Args:
        job_record: Job record from storage

    Returns:
        Solver resource with optimization results

    Raises:
        RuntimeError: If job is not completed
    """
    job_id = job_record["job_id"]
    status = job_record["status"]

    if status != JobStatus.COMPLETED.value:
        raise RuntimeError(f"Job {job_id} not completed (status: {status}). Solver results not available.")

    # Parse result and extract solver results
    result = json.loads(job_record["result"])
    workflow_state = result.get("workflow_state", {})
    solver_output = workflow_state.get("solver_output", {})

    # Build HATEOAS links
    links = {
        "self": f"job://{job_id}/solver",
        "status": f"job://{job_id}/status",
        "result": f"job://{job_id}/result",
    }

    resource = {
        "uri": f"job://{job_id}/solver",
        "type": "job_solver",
        "job_id": job_id,
        "solver_output": solver_output,
        "links": links,
    }

    logger.info(f"Job solver resource: {job_id}")
    return resource


def _read_job_explanation(job_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read job business explanation resource.

    Returns business explanation from Dame Workflow.

    Args:
        job_record: Job record from storage

    Returns:
        Explanation resource with business insights

    Raises:
        RuntimeError: If job is not completed
    """
    job_id = job_record["job_id"]
    status = job_record["status"]

    if status != JobStatus.COMPLETED.value:
        raise RuntimeError(f"Job {job_id} not completed (status: {status}). Explanation not available.")

    # Parse result and extract explanation
    result = json.loads(job_record["result"])
    workflow_state = result.get("workflow_state", {})
    explanation = workflow_state.get("explanation", {})

    # Build HATEOAS links
    links = {
        "self": f"job://{job_id}/explanation",
        "status": f"job://{job_id}/status",
        "result": f"job://{job_id}/result",
    }

    resource = {
        "uri": f"job://{job_id}/explanation",
        "type": "job_explanation",
        "job_id": job_id,
        "explanation": explanation,
        "links": links,
    }

    logger.info(f"Job explanation resource: {job_id}")
    return resource


def _read_job_progress(job_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read job progress resource.

    Returns current progress for running jobs.

    Args:
        job_record: Job record from storage

    Returns:
        Progress resource with current step and percentage
    """
    job_id = job_record["job_id"]
    status = job_record["status"]

    # Parse progress if available
    progress = None
    if job_record["progress"]:
        progress = json.loads(job_record["progress"])
    else:
        # Default progress for queued jobs
        progress = {
            "current_step": "queued",
            "progress_percentage": 0,
            "step_details": {},
            "updated_at": job_record["created_at"],
        }

    # Build HATEOAS links
    links = {
        "self": f"job://{job_id}/progress",
        "status": f"job://{job_id}/status",
    }

    resource = {
        "uri": f"job://{job_id}/progress",
        "type": "job_progress",
        "job_id": job_id,
        "status": status,
        "progress": progress,
        "links": links,
    }

    logger.info(f"Job progress resource: {job_id} -> {progress['current_step']} ({progress['progress_percentage']}%)")
    return resource


def list_job_resources(job_id: str) -> Dict[str, Any]:
    """
    List all available resources for a job.

    This is a convenience function for discovering available resources.

    Args:
        job_id: Job identifier

    Returns:
        Dictionary with available resource URIs

    Raises:
        KeyError: If job not found
    """
    job_record = get_job(job_id)
    if not job_record:
        raise KeyError(f"Job not found: {job_id}")

    status = job_record["status"]

    # Base resources (always available)
    resources = {
        "status": f"job://{job_id}/status",
        "progress": f"job://{job_id}/progress",
    }

    # Add result resources if completed
    if status == JobStatus.COMPLETED.value:
        resources["result"] = f"job://{job_id}/result"
        resources["intent"] = f"job://{job_id}/intent"
        resources["data"] = f"job://{job_id}/data"
        resources["solver"] = f"job://{job_id}/solver"
        resources["explanation"] = f"job://{job_id}/explanation"

    return {
        "job_id": job_id,
        "status": status,
        "resources": resources,
    }


if __name__ == "__main__":
    # Test resource handler
    from dcisionai_mcp_server.jobs.storage import create_job_record
    from dcisionai_mcp_server.jobs.schemas import JobPriority

    logger.info("Testing MCP resource handler...")

    # Create test job
    test_job_id = "test_resource_123"
    job = create_job_record(
        job_id=test_job_id,
        session_id="test_session",
        user_query="Test resource handler",
        priority=JobPriority.NORMAL,
    )

    # Test status resource
    status_uri = f"job://{test_job_id}/status"
    status_resource = read_job_resource(status_uri)
    print(f"Status resource: {json.dumps(status_resource, indent=2)}")

    # Test progress resource
    progress_uri = f"job://{test_job_id}/progress"
    progress_resource = read_job_resource(progress_uri)
    print(f"Progress resource: {json.dumps(progress_resource, indent=2)}")

    # List all resources
    all_resources = list_job_resources(test_job_id)
    print(f"All resources: {json.dumps(all_resources, indent=2)}")

    logger.info("✅ MCP resource handler test complete")
