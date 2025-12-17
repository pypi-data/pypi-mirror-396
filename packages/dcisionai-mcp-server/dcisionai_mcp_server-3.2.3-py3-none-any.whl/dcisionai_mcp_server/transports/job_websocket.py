"""
WebSocket Handler for Job-Based Streaming

Subscribes to Redis pub/sub channel `job_updates:{job_id}` and streams
real-time job updates to the client. This enables live progress updates,
thinking messages (CoT), and step-by-step workflow visibility.

Following MCP Protocol:
- WebSocket endpoint: /ws/job/{job_id}
- Message types: status, progress, thinking, completed, result, error
- Graceful connection handling and error recovery
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect

try:
    import redis.asyncio as aioredis
except ImportError:
    import redis as aioredis  # Fallback

from dcisionai_mcp_server.jobs.storage import get_job
from dcisionai_mcp_server.jobs.schemas import JobStatus

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


async def handle_job_websocket(websocket: WebSocket, job_id: str) -> None:
    """
    Handle WebSocket connection for job-based streaming.

    Protocol:
    1. Client connects to /ws/job/{job_id}
    2. Server sends initial job status
    3. Server subscribes to Redis pub/sub channel: job_updates:{job_id}
    4. Server streams updates as they arrive
    5. Connection closes when job completes or client disconnects

    Args:
        websocket: FastAPI WebSocket connection
        job_id: Job ID to stream updates for
    """
    await websocket.accept()
    logger.info(f"[JobWebSocket] Client connected for job {job_id}")

    # Initialize Redis pub/sub
    redis_client: Optional[aioredis.Redis] = None
    pubsub: Optional[aioredis.client.PubSub] = None

    try:
        # Connect to Redis
        redis_client = await aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info(f"[JobWebSocket] Redis connected for job {job_id}")

        # Verify job exists
        job = get_job(job_id)
        if not job:
            await websocket.send_json({
                "type": "error",
                "message": f"Job {job_id} not found"
            })
            await websocket.close(code=1008, reason="Job not found")
            return

        # Send initial job status
        # Also check if there's existing progress to replay
        import json as json_lib
        existing_progress = None
        if job.get("progress"):
            try:
                existing_progress = json_lib.loads(job.get("progress")) if isinstance(job.get("progress"), str) else job.get("progress")
            except:
                pass
        
        initial_status = {
            "type": "status",
            "job_id": job_id,
            "status": job.get("status"),
            "progress": existing_progress.get("progress_percentage", 0) if existing_progress else 0,
            "current_step": existing_progress.get("current_step", "Initializing") if existing_progress else "Initializing"
        }
        await websocket.send_json(initial_status)
        logger.info(f"[JobWebSocket] Sent initial status for job {job_id}: {job.get('status')}, progress={initial_status['progress']}%")
        
        # If there's existing progress, send it as a progress update too
        if existing_progress and job.get("status") == JobStatus.RUNNING.value:
            progress_replay = {
                "type": "progress",
                "job_id": job_id,
                "status": JobStatus.RUNNING.value,
                "step": existing_progress.get("current_step"),
                "progress": existing_progress.get("progress_percentage", 0),
                "current_step": existing_progress.get("current_step"),
                "progress_percentage": existing_progress.get("progress_percentage", 0),
                "step_details": existing_progress.get("step_details", {}),
                "updated_at": existing_progress.get("updated_at"),
            }
            await websocket.send_json(progress_replay)
            logger.info(f"[JobWebSocket] Replayed existing progress: {existing_progress.get('current_step')} ({existing_progress.get('progress_percentage', 0)}%)")

        # If job is already completed or failed, send final result and close
        if job.get("status") in [JobStatus.COMPLETED.value, JobStatus.FAILED.value]:
            logger.info(f"[JobWebSocket] Job {job_id} already {job.get('status')}, sending result")

            # Send final status
            await websocket.send_json({
                "type": "final_status",
                "status": job.get("status"),
                "progress": 100 if job.get("status") == JobStatus.COMPLETED.value else 0
            })

            # Send result if available
            if job.get("status") == JobStatus.COMPLETED.value:
                result = job.get("result")
                if result:
                    await websocket.send_json({
                        "type": "result",
                        "result": result
                    })

            # Send completed/error message
            await websocket.send_json({
                "type": "completed" if job.get("status") == JobStatus.COMPLETED.value else "error",
                "message": "Job completed" if job.get("status") == JobStatus.COMPLETED.value else job.get("error", "Job failed")
            })

            await websocket.close(code=1000, reason="Job already completed")
            return

        # Subscribe to Redis pub/sub channel
        pubsub = redis_client.pubsub()
        channel = f"job_updates:{job_id}"
        await pubsub.subscribe(channel)
        logger.info(f"[JobWebSocket] Subscribed to Redis channel: {channel}")

        # Stream updates from Redis pub/sub
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    # Parse update from Redis
                    update_str = message["data"]
                    update = json.loads(update_str) if isinstance(update_str, str) else update_str

                    logger.info(f"[JobWebSocket] Received update from Redis for job {job_id}: type={update.get('type')}, step={update.get('step', update.get('current_step', 'N/A'))}")

                    # Send update to client
                    await websocket.send_json(update)
                    logger.info(f"[JobWebSocket] Sent update to client: type={update.get('type')}, step={update.get('step', update.get('current_step', 'N/A'))}")

                    # Close connection if job completed or failed
                    if update.get("type") in ["completed", "error"]:
                        logger.info(f"[JobWebSocket] Job {job_id} {update.get('type')}, closing connection")
                        await websocket.close(code=1000, reason=f"Job {update.get('type')}")
                        break

                except json.JSONDecodeError as e:
                    logger.error(f"[JobWebSocket] Failed to decode Redis message: {e}")
                    continue
                except Exception as e:
                    logger.error(f"[JobWebSocket] Error processing update: {e}", exc_info=True)
                    continue

    except WebSocketDisconnect:
        logger.info(f"[JobWebSocket] Client disconnected from job {job_id}")

    except Exception as e:
        logger.error(f"[JobWebSocket] Error in job WebSocket handler: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"WebSocket error: {str(e)}"
            })
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass

    finally:
        # Cleanup Redis connection
        if pubsub:
            try:
                await pubsub.unsubscribe(f"job_updates:{job_id}")
                await pubsub.close()
            except Exception as e:
                logger.error(f"[JobWebSocket] Error closing pubsub: {e}")

        if redis_client:
            try:
                await redis_client.close()
            except Exception as e:
                logger.error(f"[JobWebSocket] Error closing Redis client: {e}")

        logger.info(f"[JobWebSocket] Connection closed for job {job_id}")
