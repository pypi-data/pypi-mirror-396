"""
Job Storage Layer with Supabase Database and Redis Cache

Following MCP Protocol:
- Jobs stored in Supabase for persistence
- Jobs cached in Redis for fast access (24h TTL)
- Job results exposed as MCP resources (job://job_id/*)
- HATEOAS links for REST API navigation

Following LangGraph Patterns:
- JobState persisted as JSON (TypedDict serialization)
- Checkpoint support for resumable workflows
- Progress updates persisted for recovery
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

from supabase import create_client, Client

from dcisionai_mcp_server.jobs.schemas import (
    JobState,
    JobMetadata,
    JobInput,
    JobProgress,
    JobResult,
    JobStatus,
    JobPriority,
    JobRecord,
)

logger = logging.getLogger(__name__)

# ========== DATABASE CONFIGURATION ==========

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_TTL_SECONDS = 24 * 60 * 60  # 24 hours

# Initialize Supabase client
supabase_client: Optional[Client] = None
try:
    if SUPABASE_URL and SUPABASE_API_KEY:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_API_KEY)
        logger.info(f"✅ Supabase client initialized: {SUPABASE_URL}")
    else:
        logger.warning("⚠️ Supabase credentials not found. Set SUPABASE_URL and SUPABASE_API_KEY environment variables.")
except Exception as e:
    logger.error(f"❌ Supabase client initialization failed: {e}")
    supabase_client = None

# Initialize Redis client
try:
    import redis
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    logger.info(f"✅ Redis cache initialized: {REDIS_URL}")
except Exception as e:
    logger.warning(f"⚠️ Redis cache initialization failed: {e}. Using database only.")
    redis_client = None


# ========== DATABASE INITIALIZATION ==========

def init_database() -> None:
    """
    Verify Supabase tables exist.

    Tables should be created via Supabase Dashboard or setup script:
    - async_jobs: Main job records with metadata and state
    - async_job_checkpoints: LangGraph checkpoints for resumable workflows
    """
    if not supabase_client:
        logger.warning("⚠️ Supabase client not initialized. Skipping table verification.")
        return

    try:
        # Verify async_jobs table exists by attempting a simple query
        supabase_client.table("async_jobs").select("job_id").limit(1).execute()
        logger.info("✅ Supabase table 'async_jobs' verified")
    except Exception as e:
        logger.error(f"❌ Supabase table 'async_jobs' not found: {e}")
        logger.error("Please create tables using docs/implementation/SUPABASE_ASYNC_JOBS_SETUP.md")
        raise

    try:
        # Verify async_job_checkpoints table exists
        supabase_client.table("async_job_checkpoints").select("checkpoint_id").limit(1).execute()
        logger.info("✅ Supabase table 'async_job_checkpoints' verified")
    except Exception as e:
        logger.error(f"❌ Supabase table 'async_job_checkpoints' not found: {e}")
        logger.error("Please create tables using docs/implementation/SUPABASE_ASYNC_JOBS_SETUP.md")
        raise


# Initialize database on module import
init_database()


# ========== REDIS CACHE LAYER ==========

def cache_get(key: str) -> Optional[Dict[str, Any]]:
    """Get job from Redis cache"""
    if not redis_client:
        return None

    try:
        cached = redis_client.get(key)
        if cached:
            logger.debug(f"Cache HIT: {key}")
            return json.loads(cached)
        logger.debug(f"Cache MISS: {key}")
        return None
    except Exception as e:
        logger.error(f"Cache get error for {key}: {e}")
        return None


def cache_set(key: str, value: Dict[str, Any], ttl: int = REDIS_TTL_SECONDS) -> None:
    """Store job in Redis cache with TTL"""
    if not redis_client:
        return

    try:
        redis_client.setex(key, ttl, json.dumps(value))
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    except Exception as e:
        logger.error(f"Cache set error for {key}: {e}")


def cache_delete(key: str) -> None:
    """Remove job from Redis cache"""
    if not redis_client:
        return

    try:
        redis_client.delete(key)
        logger.debug(f"Cache DELETE: {key}")
    except Exception as e:
        logger.error(f"Cache delete error for {key}: {e}")


def cache_key(job_id: str) -> str:
    """Generate cache key for job"""
    return f"job:{job_id}"


# ========== JOB CRUD OPERATIONS ==========

def create_job_record(
    job_id: str,
    session_id: str,
    user_query: str,
    priority: JobPriority = JobPriority.NORMAL,
    use_case: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
) -> JobRecord:
    """
    Create a new job record in database.

    Args:
        job_id: Unique job identifier (same as Celery task ID)
        session_id: Session identifier for context
        user_query: Natural language query from user
        priority: Job priority (low, normal, high, urgent)
        use_case: Optional use case hint
        parameters: Optional additional parameters

    Returns:
        JobRecord TypedDict with initial state
    """
    logger.info(f"Creating job record: {job_id}")

    # Create job record
    job_data = {
        "job_id": job_id,
        "session_id": session_id,
        "status": JobStatus.QUEUED.value,
        "priority": priority.value,
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "user_query": user_query,
        "use_case": use_case,
        "parameters": parameters,  # Supabase stores as JSONB
        "progress": None,
        "result": None,
        "error": None,
        "checkpoint_id": None,
    }

    # Insert into Supabase
    if supabase_client:
        try:
            supabase_client.table("async_jobs").insert(job_data).execute()
        except Exception as e:
            logger.error(f"❌ Failed to insert job into Supabase: {e}")
            raise

    # Convert to JobRecord format (parameters as JSON string for compatibility)
    job_record: JobRecord = {
        **job_data,
        "parameters": json.dumps(parameters) if parameters else None,
    }

    # Cache the job record
    cache_set(cache_key(job_id), job_record)

    logger.info(f"✅ Job record created: {job_id}")
    return job_record


def get_job(job_id: str) -> Optional[JobRecord]:
    """
    Get job record by ID.

    First checks Redis cache, then falls back to database.

    Args:
        job_id: Job identifier

    Returns:
        JobRecord if found, None otherwise
    """
    # Try cache first
    cached = cache_get(cache_key(job_id))
    if cached:
        return cached

    # Fall back to Supabase
    if not supabase_client:
        logger.error("Supabase client not initialized")
        return None

    try:
        response = supabase_client.table("async_jobs").select("*").eq("job_id", job_id).execute()

        if not response.data or len(response.data) == 0:
            logger.warning(f"Job not found: {job_id}")
            return None

        row = response.data[0]

        # Convert Supabase row to JobRecord
        job_record: JobRecord = {
            "job_id": row["job_id"],
            "session_id": row["session_id"],
            "status": row["status"],
            "priority": row["priority"],
            "created_at": row["created_at"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
            "user_query": row["user_query"],
            "use_case": row["use_case"],
            "parameters": json.dumps(row["parameters"]) if row["parameters"] else None,
            "progress": json.dumps(row["progress"]) if row["progress"] else None,
            "result": json.dumps(row["result"]) if row["result"] else None,
            "error": row["error"],
            "checkpoint_id": row["checkpoint_id"],
        }

        # Cache for next time
        cache_set(cache_key(job_id), job_record)

        return job_record

    except Exception as e:
        logger.error(f"❌ Failed to get job from Supabase: {e}")
        return None


def delete_job(job_id: str) -> None:
    """
    Delete a job from the database and cache.

    Args:
        job_id: Unique job identifier
    """
    logger.info(f"Deleting job: {job_id}")

    if not supabase_client:
        logger.error("Supabase client not initialized")
        raise RuntimeError("Database not available")

    try:
        # Delete from Supabase
        supabase_client.table("async_jobs").delete().eq("job_id", job_id).execute()

        # Invalidate cache
        cache_delete(cache_key(job_id))

        logger.info(f"✅ Deleted job: {job_id}")
    except Exception as e:
        logger.error(f"❌ Failed to delete job {job_id}: {e}")
        raise


def update_job_status(
    job_id: str,
    status: JobStatus,
    started_at: Optional[str] = None,
    completed_at: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    """
    Update job status in database and cache.

    Args:
        job_id: Job identifier
        status: New status
        started_at: Optional start timestamp
        completed_at: Optional completion timestamp
        error: Optional error message
    """
    logger.info(f"Updating job {job_id} status: {status.value}")

    if not supabase_client:
        logger.error("Supabase client not initialized")
        return

    # Build update data
    update_data = {"status": status.value}

    if started_at:
        update_data["started_at"] = started_at

    if completed_at:
        update_data["completed_at"] = completed_at

    if error:
        update_data["error"] = error

    try:
        supabase_client.table("async_jobs").update(update_data).eq("job_id", job_id).execute()
    except Exception as e:
        logger.error(f"❌ Failed to update job status in Supabase: {e}")
        raise

    # Invalidate cache
    cache_delete(cache_key(job_id))

    logger.info(f"✅ Job status updated: {job_id} -> {status.value}")


def update_job_progress(job_id: str, progress: JobProgress) -> None:
    """
    Update job progress in database and cache.

    Args:
        job_id: Job identifier
        progress: JobProgress TypedDict with current step and percentage
    """
    logger.debug(f"Updating job {job_id} progress: {progress['current_step']} ({progress['progress_percentage']}%)")

    if not supabase_client:
        logger.error("Supabase client not initialized")
        return

    try:
        supabase_client.table("async_jobs").update({"progress": progress}).eq("job_id", job_id).execute()
    except Exception as e:
        logger.error(f"❌ Failed to update job progress in Supabase: {e}")
        raise

    # Invalidate cache (progress updates frequently, so we don't cache)
    cache_delete(cache_key(job_id))


def save_job_result(job_id: str, result: JobResult) -> None:
    """
    Save job result to database and cache.

    Args:
        job_id: Job identifier
        result: JobResult TypedDict with final workflow state and MCP resource URIs
    """
    logger.info(f"Saving job result: {job_id}")

    if not supabase_client:
        logger.error("Supabase client not initialized")
        return

    update_data = {
        "result": result,
        "completed_at": datetime.utcnow().isoformat(),
    }

    try:
        supabase_client.table("async_jobs").update(update_data).eq("job_id", job_id).execute()
    except Exception as e:
        logger.error(f"❌ Failed to save job result in Supabase: {e}")
        raise

    # Invalidate cache
    cache_delete(cache_key(job_id))

    logger.info(f"✅ Job result saved: {job_id}")


# ========== CHECKPOINT SUPPORT (LANGGRAPH RESUMABILITY) ==========

def save_checkpoint(job_id: str, checkpoint_id: str, checkpoint_data: Dict[str, Any]) -> None:
    """
    Save LangGraph checkpoint for resumable workflows.

    This allows workflows to be paused and resumed later.

    Args:
        job_id: Job identifier
        checkpoint_id: Unique checkpoint identifier
        checkpoint_data: LangGraph StateGraph checkpoint data
    """
    logger.info(f"Saving checkpoint {checkpoint_id} for job {job_id}")

    if not supabase_client:
        logger.error("Supabase client not initialized")
        return

    # Insert checkpoint
    checkpoint_record = {
        "checkpoint_id": checkpoint_id,
        "job_id": job_id,
        "checkpoint_data": checkpoint_data,  # Supabase stores as JSONB
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        supabase_client.table("async_job_checkpoints").insert(checkpoint_record).execute()

        # Update job record with latest checkpoint
        supabase_client.table("async_jobs").update({"checkpoint_id": checkpoint_id}).eq("job_id", job_id).execute()
    except Exception as e:
        logger.error(f"❌ Failed to save checkpoint in Supabase: {e}")
        raise

    logger.info(f"✅ Checkpoint saved: {checkpoint_id}")


def get_checkpoint(checkpoint_id: str) -> Optional[Dict[str, Any]]:
    """
    Get LangGraph checkpoint by ID.

    Args:
        checkpoint_id: Checkpoint identifier

    Returns:
        Checkpoint data if found, None otherwise
    """
    if not supabase_client:
        logger.error("Supabase client not initialized")
        return None

    try:
        response = supabase_client.table("async_job_checkpoints").select("*").eq("checkpoint_id", checkpoint_id).execute()

        if not response.data or len(response.data) == 0:
            logger.warning(f"Checkpoint not found: {checkpoint_id}")
            return None

        row = response.data[0]
        return row["checkpoint_data"]

    except Exception as e:
        logger.error(f"❌ Failed to get checkpoint from Supabase: {e}")
        return None


# ========== QUERY OPERATIONS ==========

def get_jobs_by_session(session_id: str, limit: int = 100) -> List[JobRecord]:
    """
    Get all jobs for a session.

    Args:
        session_id: Session identifier
        limit: Maximum number of jobs to return

    Returns:
        List of JobRecord Typedicts
    """
    if not supabase_client:
        logger.error("Supabase client not initialized")
        return []

    try:
        response = supabase_client.table("async_jobs").select("*").eq("session_id", session_id).order("created_at", desc=True).limit(limit).execute()

        return [
            {
                "job_id": row["job_id"],
                "session_id": row["session_id"],
                "status": row["status"],
                "priority": row["priority"],
                "created_at": row["created_at"],
                "started_at": row["started_at"],
                "completed_at": row["completed_at"],
                "user_query": row["user_query"],
                "use_case": row["use_case"],
                "parameters": json.dumps(row["parameters"]) if row["parameters"] else None,
                "progress": json.dumps(row["progress"]) if row["progress"] else None,
                "result": json.dumps(row["result"]) if row["result"] else None,
                "error": row["error"],
                "checkpoint_id": row["checkpoint_id"],
            }
            for row in response.data
        ]

    except Exception as e:
        logger.error(f"❌ Failed to get jobs by session from Supabase: {e}")
        return []


def get_jobs_by_status(status: JobStatus, limit: int = 100) -> List[JobRecord]:
    """
    Get all jobs with a specific status.

    Args:
        status: Job status to filter by
        limit: Maximum number of jobs to return

    Returns:
        List of JobRecord Typedicts
    """
    if not supabase_client:
        logger.error("Supabase client not initialized")
        return []

    try:
        response = supabase_client.table("async_jobs").select("*").eq("status", status.value).order("created_at", desc=True).limit(limit).execute()

        return [
            {
                "job_id": row["job_id"],
                "session_id": row["session_id"],
                "status": row["status"],
                "priority": row["priority"],
                "created_at": row["created_at"],
                "started_at": row["started_at"],
                "completed_at": row["completed_at"],
                "user_query": row["user_query"],
                "use_case": row["use_case"],
                "parameters": json.dumps(row["parameters"]) if row["parameters"] else None,
                "progress": json.dumps(row["progress"]) if row["progress"] else None,
                "result": json.dumps(row["result"]) if row["result"] else None,
                "error": row["error"],
                "checkpoint_id": row["checkpoint_id"],
            }
            for row in response.data
        ]

    except Exception as e:
        logger.error(f"❌ Failed to get jobs by status from Supabase: {e}")
        return []


def get_all_jobs(limit: int = 100) -> List[JobRecord]:
    """
    Get all jobs (no filtering).

    Args:
        limit: Maximum number of jobs to return

    Returns:
        List of JobRecord Typedicts
    """
    if not supabase_client:
        logger.error("Supabase client not initialized")
        return []

    try:
        response = supabase_client.table("async_jobs").select("*").order("created_at", desc=True).limit(limit).execute()

        return [
            {
                "job_id": row["job_id"],
                "session_id": row["session_id"],
                "status": row["status"],
                "priority": row["priority"],
                "created_at": row["created_at"],
                "started_at": row["started_at"],
                "completed_at": row["completed_at"],
                "user_query": row["user_query"],
                "use_case": row["use_case"],
                "parameters": json.dumps(row["parameters"]) if row["parameters"] else None,
                "progress": json.dumps(row["progress"]) if row["progress"] else None,
                "result": json.dumps(row["result"]) if row["result"] else None,
                "error": row["error"],
                "checkpoint_id": row["checkpoint_id"],
            }
            for row in response.data
        ]

    except Exception as e:
        logger.error(f"❌ Failed to get all jobs from Supabase: {e}")
        return []


def get_active_jobs() -> List[JobRecord]:
    """
    Get all active jobs (queued or running).

    Returns:
        List of JobRecord Typedicts
    """
    if not supabase_client:
        logger.error("Supabase client not initialized")
        return []

    try:
        response = supabase_client.table("async_jobs").select("*").in_("status", [JobStatus.QUEUED.value, JobStatus.RUNNING.value]).order("created_at", desc=True).execute()

        return [
            {
                "job_id": row["job_id"],
                "session_id": row["session_id"],
                "status": row["status"],
                "priority": row["priority"],
                "created_at": row["created_at"],
                "started_at": row["started_at"],
                "completed_at": row["completed_at"],
                "user_query": row["user_query"],
                "use_case": row["use_case"],
                "parameters": json.dumps(row["parameters"]) if row["parameters"] else None,
                "progress": json.dumps(row["progress"]) if row["progress"] else None,
                "result": json.dumps(row["result"]) if row["result"] else None,
                "error": row["error"],
                "checkpoint_id": row["checkpoint_id"],
            }
            for row in response.data
        ]

    except Exception as e:
        logger.error(f"❌ Failed to get active jobs from Supabase: {e}")
        return []


# ========== CLEANUP OPERATIONS ==========

def cleanup_old_jobs(days: int = 7) -> Dict[str, int]:
    """
    Clean up old job records from database and cache.

    Deletes jobs older than specified days (excluding RUNNING jobs).

    Args:
        days: Number of days to retain job records

    Returns:
        Cleanup statistics
    """
    logger.info(f"Cleaning up jobs older than {days} days")

    if not supabase_client:
        logger.error("Supabase client not initialized")
        return {"jobs_deleted": 0, "checkpoints_deleted": 0}

    cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

    try:
        # Get old job IDs first (excluding RUNNING jobs)
        old_jobs_response = supabase_client.table("async_jobs").select("job_id").lt("created_at", cutoff_date).neq("status", JobStatus.RUNNING.value).execute()
        old_job_ids = [row["job_id"] for row in old_jobs_response.data]

        if not old_job_ids:
            logger.info("No old jobs to clean up")
            return {"jobs_deleted": 0, "checkpoints_deleted": 0}

        # Delete old checkpoints first (foreign key constraint)
        checkpoints_response = supabase_client.table("async_job_checkpoints").delete().in_("job_id", old_job_ids).execute()
        checkpoints_deleted = len(checkpoints_response.data) if checkpoints_response.data else 0

        # Delete old jobs
        jobs_response = supabase_client.table("async_jobs").delete().in_("job_id", old_job_ids).execute()
        jobs_deleted = len(jobs_response.data) if jobs_response.data else 0

        logger.info(f"✅ Cleanup complete: {jobs_deleted} jobs, {checkpoints_deleted} checkpoints")

        return {
            "jobs_deleted": jobs_deleted,
            "checkpoints_deleted": checkpoints_deleted,
        }

    except Exception as e:
        logger.error(f"❌ Failed to cleanup old jobs in Supabase: {e}")
        return {"jobs_deleted": 0, "checkpoints_deleted": 0}


def cleanup_failed_jobs(days: int = 3) -> int:
    """
    Clean up failed job records.

    Deletes failed jobs older than specified days.

    Args:
        days: Number of days to retain failed job records

    Returns:
        Number of jobs deleted
    """
    logger.info(f"Cleaning up failed jobs older than {days} days")

    if not supabase_client:
        logger.error("Supabase client not initialized")
        return 0

    cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

    try:
        response = supabase_client.table("async_jobs").delete().lt("created_at", cutoff_date).eq("status", JobStatus.FAILED.value).execute()
        deleted = len(response.data) if response.data else 0

        logger.info(f"✅ Deleted {deleted} failed jobs")
        return deleted

    except Exception as e:
        logger.error(f"❌ Failed to cleanup failed jobs in Supabase: {e}")
        return 0


# ========== STATISTICS ==========

def get_job_statistics() -> Dict[str, Any]:
    """
    Get job statistics across all statuses.

    Returns:
        Statistics dictionary with counts by status
    """
    if not supabase_client:
        logger.error("Supabase client not initialized")
        return {
            "total_jobs": 0,
            "by_status": {},
            "avg_completion_time_seconds": None,
        }

    try:
        # Get all jobs for statistics
        all_jobs_response = supabase_client.table("async_jobs").select("status, started_at, completed_at").execute()
        all_jobs = all_jobs_response.data

        # Count by status
        status_counts = {}
        for job in all_jobs:
            status = job["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        # Calculate average completion time
        completed_jobs = [
            job for job in all_jobs
            if job["status"] == JobStatus.COMPLETED.value
            and job["started_at"]
            and job["completed_at"]
        ]

        avg_duration = None
        if completed_jobs:
            total_duration = 0
            for job in completed_jobs:
                started = datetime.fromisoformat(job["started_at"].replace("Z", "+00:00"))
                completed = datetime.fromisoformat(job["completed_at"].replace("Z", "+00:00"))
                duration = (completed - started).total_seconds()
                total_duration += duration
            avg_duration = total_duration / len(completed_jobs)

        return {
            "total_jobs": len(all_jobs),
            "by_status": status_counts,
            "avg_completion_time_seconds": avg_duration,
        }

    except Exception as e:
        logger.error(f"❌ Failed to get job statistics from Supabase: {e}")
        return {
            "total_jobs": 0,
            "by_status": {},
            "avg_completion_time_seconds": None,
        }


if __name__ == "__main__":
    # Test storage layer
    logger.info("Testing storage layer...")

    # Create test job
    test_job_id = "test_job_123"
    job = create_job_record(
        job_id=test_job_id,
        session_id="test_session",
        user_query="Test query",
        priority=JobPriority.NORMAL,
    )
    print(f"Created job: {job}")

    # Get job
    retrieved = get_job(test_job_id)
    print(f"Retrieved job: {retrieved}")

    # Update progress
    update_job_progress(test_job_id, {
        "current_step": "data_generation",
        "progress_percentage": 50,
        "step_details": {"tables": 3},
        "updated_at": datetime.utcnow().isoformat(),
    })

    # Get statistics
    stats = get_job_statistics()
    print(f"Statistics: {stats}")

    logger.info("✅ Storage layer test complete")
