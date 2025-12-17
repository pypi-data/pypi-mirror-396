"""
Async Job Queue for DcisionAI MCP Server

This module provides asynchronous job processing with Celery + Redis.

Architecture:
- Celery tasks execute Dame Workflow in background
- SQLite database for job persistence
- Redis for caching and pub/sub updates
- WebSocket streaming for real-time progress
- MCP resources for job results (job://job_id/*)

Following LangGraph Best Practices:
- TypedDict state management
- Progress callbacks for workflow updates
- Checkpointing for resumable workflows

Following MCP Protocol:
- Job results exposed as MCP resources
- Compatible with existing MCP tool patterns
- HATEOAS links for REST API navigation
"""

from dcisionai_mcp_server.jobs.schemas import (
    JobStatus,
    JobPriority,
    JobMetadata,
    JobInput,
    JobProgress,
    JobResult,
    JobState,
    JobResourceSchema,
    JobRecord,
)

from dcisionai_mcp_server.jobs.tasks import (
    celery_app,
    run_optimization_job,
    cancel_job,
    get_task_status,
    get_active_jobs,
    health_check,
)

from dcisionai_mcp_server.jobs.storage import (
    create_job_record,
    get_job,
    update_job_status,
    update_job_progress,
    save_job_result,
    save_checkpoint,
    get_checkpoint,
    get_all_jobs,
    get_jobs_by_session,
    get_jobs_by_status,
    get_active_jobs as get_active_jobs_from_db,
    cleanup_old_jobs,
    get_job_statistics,
)

__all__ = [
    # Schemas
    "JobStatus",
    "JobPriority",
    "JobMetadata",
    "JobInput",
    "JobProgress",
    "JobResult",
    "JobState",
    "JobResourceSchema",
    "JobRecord",
    # Tasks
    "celery_app",
    "run_optimization_job",
    "cancel_job",
    "get_task_status",
    "get_active_jobs",
    "health_check",
    # Storage
    "create_job_record",
    "get_job",
    "update_job_status",
    "update_job_progress",
    "save_job_result",
    "save_checkpoint",
    "get_checkpoint",
    "get_all_jobs",
    "get_jobs_by_session",
    "get_jobs_by_status",
    "get_active_jobs_from_db",
    "cleanup_old_jobs",
    "get_job_statistics",
]
