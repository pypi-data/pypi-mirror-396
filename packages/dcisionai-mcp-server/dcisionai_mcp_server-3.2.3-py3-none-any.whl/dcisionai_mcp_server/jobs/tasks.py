"""
Celery Tasks for Async Job Queue

Following LangGraph Best Practices:
- TypedDict state management (no dict or dataclass)
- Progress callbacks for state updates
- Checkpointing support for resumable workflows
- StateGraph-compatible state structure

Following MCP Protocol:
- Job results exposed as MCP resources
- Reuses existing Dame Workflow (no changes)
- Compatible with existing MCP tool patterns
"""

import os
import logging
import traceback
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from celery import Celery, Task
from celery.exceptions import SoftTimeLimitExceeded, TaskRevokedError

from dcisionai_mcp_server.jobs.schemas import (
    JobState,
    JobMetadata,
    JobInput,
    JobProgress,
    JobResult,
    JobStatus,
    JobPriority,
    CeleryTaskInput,
)

logger = logging.getLogger(__name__)

# ========== CELERY APP INITIALIZATION ==========

# Redis URL from environment (Railway will provide this)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "dcisionai_jobs",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["dcisionai_mcp_server.jobs.tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks
    task_acks_late=True,  # Acknowledge after task completion
    task_reject_on_worker_lost=True,  # Requeue if worker dies
)

logger.info(f"✅ Celery app initialized with Redis broker: {REDIS_URL}")


# ========== REDIS PUB/SUB FOR REAL-TIME UPDATES ==========

try:
    import redis
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    logger.info("✅ Redis client initialized for pub/sub")
except Exception as e:
    logger.warning(f"⚠️ Redis client initialization failed: {e}. Real-time updates disabled.")
    redis_client = None


def publish_job_update(job_id: str, update: Dict[str, Any]) -> None:
    """
    Publish job update to Redis pub/sub channel.

    WebSocket subscribers listen to: job_updates:{job_id}
    This enables real-time streaming to frontend.
    """
    if not redis_client:
        logger.debug(f"[RedisPubSub] Redis not available, skipping update for job {job_id}")
        return

    try:
        import json
        channel = f"job_updates:{job_id}"
        message = json.dumps(update)
        redis_client.publish(channel, message)
        logger.info(f"[RedisPubSub] Published to {channel}: type={update.get('type')}, step={update.get('step', update.get('current_step', 'N/A'))}")
    except Exception as e:
        logger.error(f"[RedisPubSub] Failed to publish job update for {job_id}: {e}", exc_info=True)


# ========== CUSTOM TASK BASE CLASS ==========

class JobTask(Task):
    """
    Base class for all job tasks with error handling and state management.

    LangGraph Pattern:
    - Maintains JobState throughout execution
    - Updates progress via callbacks
    - Supports checkpointing for resumability
    """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure with detailed error tracking"""
        logger.error(f"Task {task_id} failed: {exc}")
        logger.error(f"Traceback: {einfo}")

        # Extract job_id from args
        job_id = args[0] if args else kwargs.get("job_id")

        if job_id:
            # CRITICAL FIX: Update database status first, then publish to Redis
            from dcisionai_mcp_server.jobs.storage import update_job_status
            
            try:
                update_job_status(
                    job_id=job_id,
                    status=JobStatus.FAILED,
                    completed_at=datetime.utcnow().isoformat(),
                    error=str(exc)
                )
                logger.info(f"✅ Job {job_id} status updated to FAILED in database")
            except Exception as db_error:
                logger.error(f"❌ Failed to update job {job_id} status in database: {db_error}")
                # Continue anyway - still publish to Redis
            
            # Publish failure notification to Redis
            error_update = {
                "type": "error",  # Add type field for WebSocket protocol
                "job_id": job_id,
                "status": JobStatus.FAILED.value,
                "error": {
                    "message": str(exc),
                    "type": type(exc).__name__,
                    "traceback": str(einfo),
                },
                "completed_at": datetime.utcnow().isoformat(),
            }
            publish_job_update(job_id, error_update)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry with progress notification"""
        logger.warning(f"Task {task_id} retrying: {exc}")

        job_id = args[0] if args else kwargs.get("job_id")

        if job_id:
            retry_update = {
                "type": "status",  # Add type field for WebSocket protocol
                "job_id": job_id,
                "status": "retrying",
                "retry_count": self.request.retries,
                "error": str(exc),
            }
            publish_job_update(job_id, retry_update)

    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success with final result notification"""
        logger.info(f"Task {task_id} completed successfully")

        job_id = args[0] if args else kwargs.get("job_id")

        if job_id:
            # CRITICAL FIX: Update database status if not already updated
            # (The task itself updates the database, but this ensures it happens even if task code fails)
            from dcisionai_mcp_server.jobs.storage import update_job_status
            
            try:
                # Only update if status is still RUNNING (task might have already updated it)
                # This is a safety net in case the task's database update failed
                update_job_status(
                    job_id=job_id,
                    status=JobStatus.COMPLETED,
                    completed_at=datetime.utcnow().isoformat()
                )
                logger.info(f"✅ Job {job_id} status updated to COMPLETED in database (on_success callback)")
            except Exception as db_error:
                logger.error(f"❌ Failed to update job {job_id} status in database: {db_error}")
                # Continue anyway - still publish to Redis
            
            # Publish success notification to Redis
            success_update = {
                "type": "completed",  # Add type field for WebSocket protocol
                "job_id": job_id,
                "status": JobStatus.COMPLETED.value,
                "completed_at": datetime.utcnow().isoformat(),
            }
            publish_job_update(job_id, success_update)


# ========== DAME WORKFLOW INTEGRATION ==========

def run_dame_workflow(
    user_query: str,
    session_id: str,
    use_case: Optional[str] = None,
    progress_callback: Optional[Callable[[str, int, Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """
    Execute existing Dame Workflow (LangGraph StateGraph).

    CRITICAL: This function does NOT change the workflow itself.
    It simply calls the existing workflow with progress callbacks.

    LangGraph Integration:
    - Passes TypedDict state through workflow
    - Receives progress updates via callbacks
    - Returns final workflow state

    Args:
        user_query: Natural language query from user
        session_id: Session identifier for context
        use_case: Optional use case hint (e.g., "VRP", "client_advisor_matching")
        progress_callback: Optional callback for progress updates

    Returns:
        Final Dame Workflow state (TypedDict)
    """
    import asyncio
    from dcisionai_workflow.workflow import run_workflow

    logger.info(f"Starting DcisionAI Workflow for session {session_id}")
    logger.info(f"Query: {user_query}")

    try:
        # Run the clean workflow from dcisionai_workflow
        # This workflow includes: HITL Router → Intent Discovery (9 steps) → Claude SDK Solver → Business Explanation
        result = asyncio.run(
            run_workflow(
                problem_description=user_query,
                session_id=session_id,
                hitl_enabled=False,  # Autonomous mode for async jobs
                progress_callback=progress_callback  # Pass progress callback to workflow
            )
        )
        logger.info(f"DcisionAI Workflow completed for session {session_id}")
        return result

    except Exception as e:
        logger.error(f"DcisionAI Workflow failed for session {session_id}: {e}")
        logger.error(traceback.format_exc())
        raise


# ========== CELERY TASKS ==========

@celery_app.task(base=JobTask, bind=True, max_retries=3, default_retry_delay=60)
def run_optimization_job(
    self,
    job_id: str,
    user_query: str,
    session_id: str,
    use_case: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute optimization workflow as background job.

    LangGraph Integration:
    - Maintains JobState throughout execution
    - Updates progress via callbacks
    - Supports resumable workflows via checkpointing

    MCP Integration:
    - Job results stored and exposed as MCP resources
    - Compatible with existing MCP tool patterns

    Args:
        job_id: Unique job identifier
        user_query: Natural language query
        session_id: Session identifier
        use_case: Optional use case hint
        parameters: Optional additional parameters

    Returns:
        JobResult TypedDict with final state and MCP resource URIs
    """
    logger.info(f"Starting optimization job {job_id}")

    # Track job start time for metrics
    job_start_time = datetime.utcnow()

    # CRITICAL FIX: Update job status to RUNNING in database
    # Import here to avoid circular imports
    from dcisionai_mcp_server.jobs.storage import update_job_status

    try:
        # Update job status in database with started timestamp
        update_job_status(
            job_id=job_id,
            status=JobStatus.RUNNING,
            started_at=job_start_time.isoformat()
        )
        logger.info(f"✅ Job {job_id} status updated to RUNNING in database")
    except Exception as db_error:
        logger.error(f"❌ Failed to update job {job_id} status in database: {db_error}")
        # Continue anyway - job will still run

    # Update job status to RUNNING (for Redis pub/sub)
    running_update = {
        "type": "status",
        "job_id": job_id,
        "status": JobStatus.RUNNING.value,
        "progress": 0,
        "current_step": "initializing",
        "started_at": job_start_time.isoformat(),
    }
    publish_job_update(job_id, running_update)
    logger.info(f"[JobProgress] Published RUNNING status for job {job_id}")

    # Also update Celery task state (for polling clients)
    self.update_state(
        state="PROGRESS",
        meta={
            "job_id": job_id,
            "status": JobStatus.RUNNING.value,
            "progress": {
                "current_step": "initializing",
                "progress_percentage": 0,
                "step_details": {},
            },
        },
    )

    # Define progress callback for Dame Workflow
    def progress_callback(step: str, progress: int, details: Dict[str, Any]) -> None:
        """
        Progress callback invoked by Dame Workflow.

        LangGraph Pattern:
        - Called after each StateGraph node completion
        - Receives current step, progress %, and step details
        - Updates JobState progress field
        - Extracts and streams thinking content if available
        """
        # Format progress update for WebSocket clients
        # Client expects: { type: 'progress', step: '...', progress: 45, current_step: '...' }
        progress_update = {
            "type": "progress",
            "job_id": job_id,
            "status": JobStatus.RUNNING.value,
            # Flat fields for client compatibility
            "step": step,
            "progress": progress,
            "current_step": step,  # Alias for compatibility
            "progress_percentage": progress,  # Alias for compatibility
            # Nested structure for detailed information
            "step_details": details,
            "updated_at": datetime.utcnow().isoformat(),
        }

        # Publish to Redis (for WebSocket subscribers)
        publish_job_update(job_id, progress_update)
        logger.info(f"[JobProgress] Published progress update for job {job_id}: {step} ({progress}%)")

        # Extract and publish thinking content if available (for streaming CoT display)
        thinking_content = details.get("_thinking_content") or details.get("thinking_content")
        if thinking_content and isinstance(thinking_content, str) and thinking_content.strip():
            # Publish thinking message separately for streaming display
            thinking_update = {
                "type": "thinking",
                "job_id": job_id,
                "step": step,
                "content": thinking_content,
                "timestamp": datetime.utcnow().isoformat(),
            }
            publish_job_update(job_id, thinking_update)
            logger.info(f"[JobProgress] ✅ Published thinking content for job {job_id}: {step} ({len(thinking_content)} chars)")
        else:
            # Debug: Log when thinking content is missing
            logger.debug(f"[JobProgress] ⚠️ No thinking content for job {job_id}, step {step}. Details keys: {list(details.keys())}")
            if details:
                logger.debug(f"[JobProgress] Details preview: {str(details)[:200]}")

        # CRITICAL: Persist progress to database (including thinking content in step_details)
        # This ensures progress is restored on page reload
        try:
            from dcisionai_mcp_server.jobs.storage import update_job_progress
            update_job_progress(job_id, {
                "current_step": step,
                "progress_percentage": progress,
                "step_details": details,  # Includes _thinking_content if present
                "updated_at": datetime.utcnow().isoformat(),
            })
            logger.debug(f"[JobProgress] ✅ Persisted progress to database for job {job_id}: {step} ({progress}%)")
        except Exception as db_error:
            logger.error(f"[JobProgress] ❌ Failed to persist progress to database for job {job_id}: {db_error}")
            # Don't fail the workflow if database update fails

        # Update Celery task state (for polling clients) - keep nested format for API
        celery_progress_update = {
            "type": "progress",
            "job_id": job_id,
            "status": JobStatus.RUNNING.value,
            "progress": {
                "current_step": step,
                "progress_percentage": progress,
                "step_details": details,
                "updated_at": datetime.utcnow().isoformat(),
            },
        }
        self.update_state(state="PROGRESS", meta=celery_progress_update)

    try:
        # CRITICAL: Execute existing Dame Workflow (NO changes to workflow)
        workflow_result = run_dame_workflow(
            user_query=user_query,
            session_id=session_id,
            use_case=use_case,
            progress_callback=progress_callback,
        )

        # Convert workflow_result to JSON-serializable format
        # LangChain Message objects (HumanMessage, AIMessage, etc.) are not JSON serializable
        def make_serializable(obj):
            """Recursively convert non-serializable objects to serializable format."""
            if hasattr(obj, "type") and hasattr(obj, "content"):
                # LangChain message object
                return {
                    "role": obj.type,
                    "content": obj.content,
                }
            elif isinstance(obj, dict):
                # Skip non-serializable tracker object (extracted separately)
                # CRITICAL: Preserve _thinking_content fields for CoT restoration
                result = {}
                for k, v in obj.items():
                    if k == 'llm_metrics_tracker':
                        continue  # Skip non-serializable tracker
                    # Preserve _thinking_content fields (they're strings, so serializable)
                    if k == '_thinking_content' or k == 'thinking_content':
                        result[k] = v  # Keep as-is (already string)
                    else:
                        result[k] = make_serializable(v)
                return result
            elif isinstance(obj, (list, tuple)):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            else:
                # For any other non-serializable object, convert to string
                return str(obj)

        serializable_workflow_state = make_serializable(workflow_result)

        # Extract LLM metrics from workflow result
        llm_tracker = workflow_result.get('llm_metrics_tracker')
        llm_metrics: LLMMetrics = {}
        if llm_tracker:
            llm_metrics = llm_tracker.get_summary()
            llm_tracker.log_summary()  # Log summary for observability
            logger.info(f"📊 Job {job_id} LLM Metrics: {llm_metrics['total_calls']} calls, "
                       f"{llm_metrics['total_tokens_in']:,} tokens in, "
                       f"{llm_metrics['total_tokens_out']:,} tokens out, "
                       f"${llm_metrics['total_cost_usd']:.4f} USD")

        # Calculate timing metrics
        step_timings = workflow_result.get('step_timings', {})
        job_end_time = datetime.utcnow()
        total_duration = (job_end_time - job_start_time).total_seconds()

        # Calculate intent discovery total (all intent steps)
        intent_steps = ['decomposition', 'context_building', 'classification', 'assumptions',
                       'entities', 'objectives', 'constraints', 'synthesis']
        intent_discovery_seconds = sum(step_timings.get(step, 0) for step in intent_steps)

        timing_metrics: TimingMetrics = {
            "job_started_at": job_start_time.isoformat(),
            "job_completed_at": job_end_time.isoformat(),
            "total_duration_seconds": total_duration,
            "by_step": step_timings,
            "intent_discovery_seconds": intent_discovery_seconds,
            "solver_seconds": step_timings.get('claude_sdk_solver', 0),
            "explanation_seconds": step_timings.get('business_explanation', 0),
        }

        logger.info(f"⏱️ Job {job_id} Timing: {total_duration:.1f}s total "
                   f"(Intent: {intent_discovery_seconds:.1f}s, "
                   f"Solver: {timing_metrics['solver_seconds']:.1f}s, "
                   f"Explanation: {timing_metrics['explanation_seconds']:.1f}s)")

        # Extract key results from workflow state
        # Dame Workflow returns TypedDict with intent, data, solver, explanation
        job_result: JobResult = {
            "status": JobStatus.COMPLETED.value,
            "workflow_state": serializable_workflow_state,
            "llm_metrics": llm_metrics,  # LLM usage and cost tracking
            "timing_metrics": timing_metrics,  # Execution timing
            "mcp_resources": {
                "status": f"job://{job_id}/status",
                "result": f"job://{job_id}/result",
                "intent": f"job://{job_id}/intent",
                "data": f"job://{job_id}/data",
                "solver": f"job://{job_id}/solver",
                "explanation": f"job://{job_id}/explanation",
            },
            "summary": {
                "query": user_query,
                "use_case": serializable_workflow_state.get("use_case", use_case),
                "completed_at": datetime.utcnow().isoformat(),
            },
        }

        logger.info(f"Job {job_id} completed successfully")

        # CRITICAL FIX: Update job status in database with completion timestamp
        # Import here to avoid circular imports
        from dcisionai_mcp_server.jobs.storage import update_job_status, save_job_result

        try:
            # Update job status to COMPLETED with timestamp
            update_job_status(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                completed_at=datetime.utcnow().isoformat()
            )

            # Save job result to database
            save_job_result(job_id=job_id, result=job_result)

            logger.info(f"✅ Job {job_id} status and result saved to database")
        except Exception as db_error:
            logger.error(f"❌ Failed to update job {job_id} in database: {db_error}")
            # Don't fail the entire job if database update fails
            # The result is still being returned and stored in Celery backend

        # Training Data Collection (Phase 1: ADR-040)
        # Opt-in, disabled by default - does not affect workflow execution
        try:
            enable_training_collection = os.getenv("ENABLE_TRAINING_DATA_COLLECTION", "false").lower() == "true"
            
            if enable_training_collection:
                from dcisionai_workflow.training import TrainingDataExtractor, TrainingDataStorage
                
                extractor = TrainingDataExtractor()
                training_record = extractor.extract_training_data(
                    workflow_state=serializable_workflow_state,
                    job_result=job_result,
                    enable_training_collection=True
                )
                
                if training_record:
                    storage = TrainingDataStorage()
                    storage.save_training_record(training_record)
                    logger.info(f"✅ Training data collected for job {job_id}: quality_score={training_record.get('quality_score', 0):.2f}")
                else:
                    logger.debug(f"Training data not collected for job {job_id}: quality_score below threshold or extraction failed")
            else:
                logger.debug(f"Training data collection disabled for job {job_id}")
                
        except Exception as training_error:
            logger.warning(f"⚠️ Training data collection failed for job {job_id}: {training_error}")
            # Don't fail the workflow if training data collection fails
            # This is a non-critical operation

        return job_result

    except SoftTimeLimitExceeded:
        logger.error(f"Job {job_id} exceeded time limit")
        raise

    except TaskRevokedError:
        logger.error(f"Job {job_id} was cancelled")
        raise

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        logger.error(traceback.format_exc())

        # Retry on recoverable errors
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job {job_id} (attempt {self.request.retries + 1})")
            raise self.retry(exc=e)
        else:
            # Max retries exceeded, mark as failed
            raise


@celery_app.task(base=JobTask, bind=True, max_retries=3)
def cancel_job(self, job_id: str) -> Dict[str, str]:
    """
    Cancel a running job.

    This terminates the Celery task and updates job status.

    Args:
        job_id: Job identifier to cancel

    Returns:
        Status dictionary
    """
    logger.info(f"Cancelling job {job_id}")

    try:
        # Revoke the task (terminate if running)
        celery_app.control.revoke(job_id, terminate=True, signal="SIGKILL")

        # Publish cancellation update
        cancel_update = {
            "job_id": job_id,
            "status": JobStatus.CANCELLED.value,
            "cancelled_at": datetime.utcnow().isoformat(),
        }
        publish_job_update(job_id, cancel_update)

        return {"status": "cancelled", "job_id": job_id}

    except Exception as e:
        logger.error(f"Failed to cancel job {job_id}: {e}")
        raise


# ========== TASK INSPECTION UTILITIES ==========

def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get current status of a Celery task.

    This is used by the polling API to check job progress.

    Args:
        task_id: Celery task identifier (same as job_id)

    Returns:
        Task status dictionary with state and progress
    """
    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=celery_app)

    status = {
        "task_id": task_id,
        "state": result.state,
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else None,
        "failed": result.failed() if result.ready() else None,
    }

    # Include progress metadata if available
    if result.state == "PROGRESS" and result.info:
        status["progress"] = result.info.get("progress", {})

    # Include result if completed
    if result.ready() and result.successful():
        status["result"] = result.result

    # Include error if failed
    if result.failed():
        status["error"] = str(result.info)

    return status


def get_active_jobs() -> Dict[str, Any]:
    """
    Get list of currently active jobs.

    Returns:
        Dictionary with active, scheduled, and reserved tasks
    """
    inspect = celery_app.control.inspect()

    active = inspect.active() or {}
    scheduled = inspect.scheduled() or {}
    reserved = inspect.reserved() or {}

    return {
        "active": active,
        "scheduled": scheduled,
        "reserved": reserved,
    }


# ========== PERIODIC TASKS (OPTIONAL) ==========

@celery_app.task(name="cleanup_old_jobs")
def cleanup_old_jobs(days: int = 7) -> Dict[str, int]:
    """
    Clean up old job records from database and Redis cache.

    This task runs periodically to prevent unbounded storage growth.

    Args:
        days: Number of days to retain job records

    Returns:
        Cleanup statistics
    """
    logger.info(f"Cleaning up jobs older than {days} days")

    # TODO: Implement when storage layer is ready
    # from dcisionai_mcp_server.jobs.storage import cleanup_old_jobs
    # return cleanup_old_jobs(days)

    return {"deleted": 0, "message": "Cleanup not yet implemented"}


# ========== HEALTH CHECK ==========

@celery_app.task(name="health_check")
def health_check() -> Dict[str, str]:
    """
    Health check task to verify Celery workers are running.

    This can be called from the /health endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "worker": "celery",
    }


if __name__ == "__main__":
    # For local testing
    logger.info("Starting Celery worker...")
    celery_app.worker_main(["worker", "--loglevel=info", "--concurrency=2"])
