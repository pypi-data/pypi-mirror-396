"""
Job Queue State Schemas

Following LangGraph best practices with TypedDict for state management.
Integrates with MCP protocol for tool invocation and resource management.
"""

from typing import TypedDict, Optional, Literal, Any, Dict, List
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job execution status following MCP protocol status patterns"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(str, Enum):
    """Job priority levels for queue management"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# LangGraph State: Job Metadata
class JobMetadata(TypedDict, total=False):
    """
    Job metadata following LangGraph state management patterns.

    TypedDict ensures type safety and IDE autocomplete.
    total=False allows optional fields for flexibility.
    """
    job_id: str
    user_id: Optional[str]
    session_id: str
    use_case: str  # vrp, wealth_management, etc.
    priority: JobPriority
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_duration_seconds: Optional[int]


# LangGraph State: Job Input
class JobInput(TypedDict, total=False):
    """
    Job input parameters following MCP tool invocation patterns.

    Mirrors dcisionai_solve tool parameters for consistency.
    """
    user_query: str
    session_id: str
    use_case: Optional[str]
    data_context: Optional[Dict[str, Any]]
    constraints: Optional[Dict[str, Any]]
    # MCP protocol: Additional tool-specific parameters
    tool_parameters: Optional[Dict[str, Any]]


# LangGraph State: Job Progress
class JobProgress(TypedDict, total=False):
    """
    Job progress tracking following LangGraph state update patterns.

    Designed for streaming updates via Redis pub/sub and WebSocket.
    """
    current_step: str  # intent_discovery, data_generation, solver, etc.
    total_steps: int
    completed_steps: int
    progress_percentage: int  # 0-100
    step_details: Optional[Dict[str, Any]]
    thinking_content: Optional[str]  # CoT from current step
    # MCP protocol: Resource references for intermediate results
    resource_uris: Optional[List[str]]


# LangGraph State: LLM Metrics (for observability)
class LLMMetrics(TypedDict, total=False):
    """
    LLM usage metrics for cost tracking and observability.

    Tracks token usage and cost for each LLM call in the workflow.
    """
    total_calls: int  # Total number of LLM calls
    total_tokens_in: int  # Total input tokens across all calls
    total_tokens_out: int  # Total output tokens across all calls
    total_cost_usd: float  # Total cost in USD
    # Per-step breakdown
    by_step: Dict[str, Dict[str, Any]]  # {step_name: {calls, tokens_in, tokens_out, cost, model}}
    # Per-model breakdown
    by_model: Dict[str, Dict[str, Any]]  # {model_name: {calls, tokens_in, tokens_out, cost}}


# LangGraph State: Timing Metrics
class TimingMetrics(TypedDict, total=False):
    """
    Timing metrics for performance tracking.

    Tracks execution time for the job and individual steps.
    """
    job_started_at: str  # ISO timestamp
    job_completed_at: Optional[str]  # ISO timestamp
    total_duration_seconds: Optional[float]  # Total job duration
    # Per-step timing
    by_step: Dict[str, float]  # {step_name: duration_seconds}
    # Workflow stage timing
    intent_discovery_seconds: Optional[float]
    solver_seconds: Optional[float]
    explanation_seconds: Optional[float]


# LangGraph State: Job Result
class JobResult(TypedDict, total=False):
    """
    Job result following MCP resource pattern.

    Results are stored as MCP resources for retrieval via read_resource.
    """
    status: JobStatus
    result_data: Optional[Dict[str, Any]]
    business_explanation: Optional[str]
    solver_summary: Optional[str]
    generated_files: Optional[List[str]]
    metrics: Optional[Dict[str, Any]]  # DEPRECATED: Use llm_metrics and timing_metrics instead
    llm_metrics: Optional[LLMMetrics]  # NEW: LLM usage and cost metrics
    timing_metrics: Optional[TimingMetrics]  # NEW: Execution timing metrics
    # MCP protocol: Resource URI for full result
    result_resource_uri: str  # e.g., "job://job_abc123/result"
    error: Optional[str]
    error_traceback: Optional[str]


# LangGraph State: Complete Job State (StateGraph node state)
class JobState(TypedDict, total=False):
    """
    Complete job state for LangGraph StateGraph nodes.

    This is the state passed between workflow nodes.
    Follows LangGraph pattern: single TypedDict for entire state.
    """
    # Core metadata
    metadata: JobMetadata

    # Input (immutable after creation)
    input: JobInput

    # Progress (updated during execution)
    progress: JobProgress

    # Result (populated on completion)
    result: Optional[JobResult]

    # LangGraph state: Workflow control
    next_node: Optional[str]  # For conditional routing
    checkpoint_id: Optional[str]  # For resumable workflows

    # LangGraph state: Messages (for LLM interaction tracking)
    messages: Optional[List[Dict[str, Any]]]

    # Dame Workflow state (passed through to workflow)
    dame_state: Optional[Dict[str, Any]]


# MCP Protocol: Job Resource Schema
class JobResourceSchema(TypedDict):
    """
    MCP resource schema for job status and results.

    Follows MCP protocol: resources are identified by URI and have MIME types.
    """
    uri: str  # job://job_abc123 or job://job_abc123/result
    name: str
    description: str
    mimeType: str  # application/json
    content: JobState


# Celery Task: Input Schema
class CeleryTaskInput(TypedDict):
    """
    Input schema for Celery task invocation.

    Minimal serializable data for Redis queue.
    """
    job_id: str
    user_query: str
    session_id: str
    use_case: Optional[str]
    priority: JobPriority
    # MCP protocol: Tool name to invoke
    mcp_tool_name: str  # dcisionai_solve, dcisionai_adhoc_optimize


# Database: Job Record Schema (for persistence)
class JobRecord(TypedDict):
    """
    Database record schema for job persistence.

    Flat structure optimized for SQL queries and indexing.
    """
    id: str  # job_id
    user_id: Optional[str]
    session_id: str
    use_case: str
    status: JobStatus
    priority: JobPriority

    # Timestamps
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    # Progress tracking
    current_step: Optional[str]
    progress_percentage: int

    # Celery task tracking
    celery_task_id: str

    # Input/output (JSON serialized)
    input_json: str  # JSON serialized JobInput
    result_json: Optional[str]  # JSON serialized JobResult

    # Error tracking
    error_message: Optional[str]
    retry_count: int
    max_retries: int


# WebSocket: Progress Update Message
class ProgressUpdateMessage(TypedDict):
    """
    WebSocket message schema for real-time progress updates.

    Follows existing WebSocket transport pattern in transports/websocket.py
    """
    type: Literal["job_progress"]
    job_id: str
    progress: JobProgress
    timestamp: str  # ISO format


# WebSocket: Job Complete Message
class JobCompleteMessage(TypedDict):
    """
    WebSocket message schema for job completion notification.
    """
    type: Literal["job_complete"]
    job_id: str
    status: JobStatus
    result_uri: str  # MCP resource URI
    timestamp: str


# API Response: Job Submission
class JobSubmissionResponse(TypedDict):
    """
    API response schema for job submission endpoint.

    Follows REST API best practices with HATEOAS links.
    """
    job_id: str
    status: JobStatus
    created_at: str  # ISO format
    estimated_duration_seconds: Optional[int]
    # HATEOAS links
    _links: Dict[str, str]  # {status: /api/jobs/{id}/status, stream: ws://...}


# API Response: Job Status
class JobStatusResponse(TypedDict):
    """
    API response schema for job status endpoint.
    """
    job_id: str
    status: JobStatus
    progress: JobProgress
    created_at: str
    started_at: Optional[str]
    elapsed_seconds: Optional[int]
    estimated_remaining_seconds: Optional[int]
    # Links to resources
    result_uri: Optional[str]  # Available when status=COMPLETED
    _links: Dict[str, str]
