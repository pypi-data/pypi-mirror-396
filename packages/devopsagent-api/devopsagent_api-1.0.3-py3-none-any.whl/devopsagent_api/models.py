"""
Pydantic data models for the DevOps Agent API.

This module provides type-safe Python models for all API operations,
enabling validation, serialization, and IDE autocomplete support.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING_START = "PENDING_START"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    CANCELLED_ALT = "CANCELLED"  # Alternative spelling
    TIMED_OUT = "TIMED_OUT"
    PENDING_CUSTOMER_APPROVAL = "PENDING_CUSTOMER_APPROVAL"


class TaskType(str, Enum):
    """Type of task."""

    INVESTIGATION = "INVESTIGATION"
    EVALUATION = "EVALUATION"


class TaskPriority(str, Enum):
    """Task priority level."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class GoalType(str, Enum):
    """Type of automated goal/workflow."""

    CUSTOMER_DEFINED = "CUSTOMER_DEFINED"
    ONCALL_REPORT = "ONCALL_REPORT"
    PREDEFINED = "PREDEFINED"


class GoalStatus(str, Enum):
    """Goal execution status."""

    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    PAUSED = "PAUSED"


class RecommendationStatus(str, Enum):
    """Recommendation status."""

    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"


class JournalRecordType(str, Enum):
    """Type of journal record."""

    MESSAGE = "message"
    PLAN = "plan"
    ACTIVITY = "activity"
    OBSERVATION = "observation"
    SYMPTOM = "symptom"
    FINDING = "finding"
    INVESTIGATION_SUMMARY = "investigation_summary"


class SortField(str, Enum):
    """Field to sort results by."""

    CREATED_AT = "CREATED_AT"
    UPDATED_AT = "UPDATED_AT"
    PRIORITY = "PRIORITY"


class SortOrder(str, Enum):
    """Sort direction."""

    ASC = "ASC"
    DESC = "DESC"


# =============================================================================
# Common Models
# =============================================================================


class Metadata(BaseModel):
    """Generic metadata container."""

    pass  # Flexible structure for additional metadata


class Reference(BaseModel):
    """Reference to external system."""

    system: Optional[str] = None
    id: Optional[str] = None


class SupportMetadata(BaseModel):
    """Support case metadata."""

    case_id: Optional[str] = None
    visual_id: Optional[str] = None
    case_url: Optional[str] = None


class PaginationInfo(BaseModel):
    """Pagination metadata."""

    next_token: Optional[str] = None
    has_more: bool = False
    total_count: Optional[int] = None


# =============================================================================
# Task Models
# =============================================================================


class Task(BaseModel):
    """Complete task representation."""

    agent_space_id: str = Field(..., description="Agent space UUID")
    task_id: str = Field(..., description="Task UUID")
    execution_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., max_length=5000)
    task_type: TaskType
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus
    created_at: str = Field(..., description="ISO 8601 timestamp")
    updated_at: str = Field(..., description="ISO 8601 timestamp")
    version: int = Field(..., ge=0)
    metadata: Optional[Metadata] = None
    reference: Optional[Reference] = None
    support_metadata: Optional[SupportMetadata] = None


class TaskFilter(BaseModel):
    """Filter criteria for task queries."""

    task_type: Optional[List[TaskType]] = None
    status: Optional[List[TaskStatus]] = None
    priority: Optional[List[TaskPriority]] = None
    created_after: Optional[str] = None
    created_before: Optional[str] = None
    updated_after: Optional[str] = None
    updated_before: Optional[str] = None


class TaskListRequest(BaseModel):
    """Request for listing tasks."""

    agent_space_id: str
    limit: Optional[int] = Field(None, ge=1, le=1000)
    next_token: Optional[str] = None
    sort_field: Optional[SortField] = SortField.CREATED_AT
    order: Optional[SortOrder] = SortOrder.DESC
    filter: Optional[TaskFilter] = None


class TaskListResponse(BaseModel):
    """Response from task listing."""

    tasks: List[Task] = Field(default_factory=list)
    next_token: Optional[str] = None


class TaskCreateRequest(BaseModel):
    """Request to create a new task."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., max_length=5000)
    task_type: TaskType
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    metadata: Optional[Metadata] = None


class TaskCreateResponse(BaseModel):
    """Response from task creation."""

    task: Task


class TaskUpdateRequest(BaseModel):
    """Request to update a task."""

    agent_space_id: str
    task_id: str
    task_status: Optional[TaskStatus] = None
    current_version: Optional[int] = None
    metadata: Optional[Metadata] = None
    support_metadata: Optional[SupportMetadata] = None


class TaskUpdateResponse(BaseModel):
    """Response from task update."""

    task: Task


# =============================================================================
# Goal Models
# =============================================================================


class Goal(BaseModel):
    """Automated goal/workflow representation."""

    goal_id: str = Field(..., description="Goal UUID")
    goal_type: GoalType
    title: str
    status: GoalStatus
    execution_status: Optional[str] = None
    last_task_id: Optional[str] = None
    last_evaluated_at: Optional[str] = None
    created_at: str = Field(..., description="ISO 8601 timestamp")
    updated_at: str = Field(..., description="ISO 8601 timestamp")


class GoalList(BaseModel):
    """List of goals."""

    goals: List[Goal] = Field(default_factory=list)
    next_token: Optional[str] = None


class GoalListRequest(BaseModel):
    """Request for listing goals."""

    agent_space_id: str
    limit: Optional[int] = Field(None, ge=1, le=100)
    next_token: Optional[str] = None
    goal_type: Optional[GoalType] = None
    status: Optional[GoalStatus] = None
    execution_status: Optional[str] = None


class GoalListResponse(BaseModel):
    """Response from goal listing."""

    goals: List[Goal] = Field(default_factory=list)
    next_token: Optional[str] = None


# =============================================================================
# Recommendation Models
# =============================================================================


class RecommendationSummary(BaseModel):
    """Recommendation summary content."""

    title: str
    category: str
    overview: str
    background: Optional[str] = None
    next_steps: Optional[str] = None
    considerations: Optional[str] = None
    action_plan: Optional[str] = None
    affected_incidents: Optional[List[str]] = None


class RecommendationContent(BaseModel):
    """Recommendation content structure."""

    summary: RecommendationSummary


class Recommendation(BaseModel):
    """Recommendation representation."""

    recommendation_id: str = Field(..., description="Recommendation UUID")
    title: str
    status: RecommendationStatus
    priority: TaskPriority
    content: RecommendationContent
    goal_id: Optional[str] = None
    goal_version: Optional[int] = None
    created_at: str = Field(..., description="ISO 8601 timestamp")
    updated_at: str = Field(..., description="ISO 8601 timestamp")
    version: int


class RecommendationList(BaseModel):
    """List of recommendations."""

    recommendations: List[Recommendation] = Field(default_factory=list)
    next_token: Optional[str] = None


class RecommendationListRequest(BaseModel):
    """Request for listing recommendations."""

    agent_space_id: str
    limit: Optional[int] = Field(None, ge=1, le=100)
    next_token: Optional[str] = None
    task_id: Optional[str] = None
    goal_id: Optional[str] = None
    status: Optional[RecommendationStatus] = None
    priority: Optional[TaskPriority] = None


class RecommendationListResponse(BaseModel):
    """Response from recommendation listing."""

    recommendations: List[Recommendation] = Field(default_factory=list)
    next_token: Optional[str] = None


class RecommendationUpdateRequest(BaseModel):
    """Request to update a recommendation."""

    agent_space_id: str
    recommendation_id: str
    client_token: Optional[str] = None
    status: RecommendationStatus
    additional_context: Optional[str] = None


class RecommendationUpdateResponse(BaseModel):
    """Response from recommendation update."""

    recommendation: Recommendation


# =============================================================================
# Journal Models
# =============================================================================


class JournalRecordContent(BaseModel):
    """Base class for journal record content."""

    type: str
    id: str


class MessageContent(JournalRecordContent):
    """Message record content."""

    type: str = "message"
    role: str  # "user" or "assistant"
    content: List[Dict[str, Any]]  # Message content blocks
    user_reference: Optional[str] = None


class PlanContent(JournalRecordContent):
    """Plan record content."""

    type: str = "plan"
    title: str
    description: str
    activity_ids: List[str] = Field(default_factory=list)


class ActivityContent(JournalRecordContent):
    """Activity record content."""

    type: str = "activity"
    title: str
    description: str
    status: str  # "IN_PROGRESS", "COMPLETED", "PENDING"
    child_activity_ids: List[str] = Field(default_factory=list)


class ObservationContent(JournalRecordContent):
    """Observation record content."""

    type: str = "observation"
    plan_id: Optional[str] = None
    activity_id: Optional[str] = None
    title: str
    analysis: str
    signals: List[Dict[str, Any]] = Field(default_factory=list)


class SymptomContent(JournalRecordContent):
    """Symptom record content."""

    type: str = "symptom"
    title: str
    description: str
    start_time: str  # ISO 8601
    end_time: Optional[str] = None


class FindingContent(JournalRecordContent):
    """Finding record content."""

    type: str = "finding"
    title: str
    description: str
    supporting_observations: List[Any] = Field(default_factory=list)
    cascaded_cause_ids: List[str] = Field(default_factory=list)
    related_resources: List[str] = Field(default_factory=list)  # ARNs


class InvestigationSummaryContent(JournalRecordContent):
    """Investigation summary content."""

    type: str = "investigation_summary"
    symptoms: List[Any] = Field(default_factory=list)
    findings: List[Any] = Field(default_factory=list)
    investigation_gaps: List[Any] = Field(default_factory=list)


class JournalRecord(BaseModel):
    """Journal record entry."""

    agent_space_id: str = Field(..., description="Agent space UUID")
    execution_id: str = Field(..., description="Execution identifier")
    record_id: str = Field(..., description="Record UUID")
    content: str = Field(..., description="JSON-encoded content")
    created_at: float = Field(..., description="Unix timestamp")
    record_type: JournalRecordType


class JournalRecordList(BaseModel):
    """List of journal records."""

    records: List[JournalRecord] = Field(default_factory=list)
    next_token: Optional[str] = None


class JournalRecordsRequest(BaseModel):
    """Request for journal records."""

    agent_space_id: str
    execution_id: str
    record_type: Optional[JournalRecordType] = None
    order: Optional[SortOrder] = SortOrder.ASC
    limit: Optional[int] = Field(None, ge=1, le=1000)
    next_token: Optional[str] = None


class JournalRecordsResponse(BaseModel):
    """Response from journal records query."""

    records: List[JournalRecord] = Field(default_factory=list)
    next_token: Optional[str] = None


# =============================================================================
# Execution Models
# =============================================================================


class Execution(BaseModel):
    """Execution metadata."""

    agent_space_id: str = Field(..., description="Agent space UUID")
    execution_id: str = Field(..., description="Execution identifier")
    agent_sub_task: str  # "oncall" or "task-chat"
    agent_type: str  # "ops1" or "taskChat"
    created_at: float = Field(..., description="Unix timestamp")
    updated_at: float = Field(..., description="Unix timestamp")
    execution_status: str  # Status values
    uid: Optional[str] = None


class ExecutionList(BaseModel):
    """List of executions."""

    executions: List[Execution] = Field(default_factory=list)
    next_token: Optional[str] = None


class ExecutionListRequest(BaseModel):
    """Request for execution list."""

    agent_space_id: str
    task_id: Optional[str] = None
    limit: Optional[int] = Field(None, ge=1, le=100)
    next_token: Optional[str] = None


class ExecutionListResponse(BaseModel):
    """Response from execution list."""

    executions: List[Execution] = Field(default_factory=list)
    next_token: Optional[str] = None


# =============================================================================
# Topology Models
# =============================================================================


class IdentifierMetadata(BaseModel):
    """Resource identifier metadata."""

    account_id: str
    region: str
    arn: Optional[str] = None
    name: Optional[str] = None


class TopologyNode(BaseModel):
    """Infrastructure resource node."""

    identifier: str = Field(..., description="Unique node identifier")
    node_metadata_id: str
    type: str = Field(..., description="Node type")
    resource_type: str = Field(..., description="AWS resource type")
    identifier_metadata: IdentifierMetadata


class TopologyEdge(BaseModel):
    """Relationship between topology nodes."""

    source: str = Field(..., description="Source node identifier")
    target: str = Field(..., description="Target node identifier")
    source_node_metadata: str
    target_node_metadata: str


class Topology(BaseModel):
    """Topology data structure."""

    nodes: List[TopologyNode] = Field(default_factory=list)
    edges: List[TopologyEdge] = Field(default_factory=list)


class TopologyData(BaseModel):
    """Topology query response data."""

    topology: Topology


class TopologyQueryRequest(BaseModel):
    """Request for topology query."""

    agent_space_id: str
    query: str = Field(..., description="GraphQL query string")
    variables: Optional[Dict[str, Any]] = None


class TopologyQueryResponse(BaseModel):
    """Response from topology query."""

    data: TopologyData


# =============================================================================
# Support Models
# =============================================================================


class SupportLevel(BaseModel):
    """AWS Support level information."""

    code: str  # "BASIC", "DEVELOPER", "BUSINESS", "ENTERPRISE"
    name: str


class SupportLevelRequest(BaseModel):
    """Request for support level."""

    agent_space_id: str
    task_id: str


class SupportLevelResponse(BaseModel):
    """Response with support level."""

    support_level: SupportLevel


class SupportChatRequest(BaseModel):
    """Request to create support chat."""

    agent_space_id: str
    task_id: str
    client_token: Optional[str] = None


class SupportChatResponse(BaseModel):
    """Response from support chat creation."""

    chat_id: str
    status: str
    created_at: str


class SupportChatEndRequest(BaseModel):
    """Request to end support chat."""

    agent_space_id: str
    task_id: str
    client_token: Optional[str] = None
    reason: Optional[str] = None
    requester: Optional[str] = None


class SupportChatEndResponse(BaseModel):
    """Response from support chat ending."""

    status: str
    ended_at: str


# =============================================================================
# Error Models
# =============================================================================


class ErrorResponse(BaseModel):
    """API error response."""

    error: str
    message: str
    status_code: int
    request_id: Optional[str] = None


# =============================================================================
# Utility Functions
# =============================================================================


def parse_journal_content(
    content: str,
) -> Union[
    MessageContent,
    PlanContent,
    ActivityContent,
    ObservationContent,
    SymptomContent,
    FindingContent,
    InvestigationSummaryContent,
    Dict[str, Any],
]:
    """
    Parse JSON-encoded journal record content.

    Args:
        content: JSON string from journal record

    Returns:
        Parsed content object or dict if unknown type
    """
    import json

    data = json.loads(content)

    content_type = data.get("type")
    if content_type == "message":
        return MessageContent(**data)
    elif content_type == "plan":
        return PlanContent(**data)
    elif content_type == "activity":
        return ActivityContent(**data)
    elif content_type == "observation":
        return ObservationContent(**data)
    elif content_type == "symptom":
        return SymptomContent(**data)
    elif content_type == "finding":
        return FindingContent(**data)
    elif content_type == "investigation_summary":
        return InvestigationSummaryContent(**data)
    else:
        return data  # Return raw dict for unknown types


# Export all models
__all__ = [
    # Enums
    "TaskStatus",
    "TaskType",
    "TaskPriority",
    "GoalType",
    "GoalStatus",
    "RecommendationStatus",
    "JournalRecordType",
    "SortField",
    "SortOrder",
    # Common models
    "Metadata",
    "Reference",
    "SupportMetadata",
    "PaginationInfo",
    # Task models
    "Task",
    "TaskFilter",
    "TaskListRequest",
    "TaskListResponse",
    "TaskCreateRequest",
    "TaskCreateResponse",
    "TaskUpdateRequest",
    "TaskUpdateResponse",
    # Goal models
    "Goal",
    "GoalList",
    "GoalListRequest",
    "GoalListResponse",
    # Recommendation models
    "RecommendationSummary",
    "RecommendationContent",
    "Recommendation",
    "RecommendationList",
    "RecommendationListRequest",
    "RecommendationListResponse",
    "RecommendationUpdateRequest",
    "RecommendationUpdateResponse",
    # Journal models
    "JournalRecordContent",
    "MessageContent",
    "PlanContent",
    "ActivityContent",
    "ObservationContent",
    "SymptomContent",
    "FindingContent",
    "InvestigationSummaryContent",
    "JournalRecord",
    "JournalRecordList",
    "JournalRecordsRequest",
    "JournalRecordsResponse",
    # Execution models
    "Execution",
    "ExecutionList",
    "ExecutionListRequest",
    "ExecutionListResponse",
    # Topology models
    "IdentifierMetadata",
    "TopologyNode",
    "TopologyEdge",
    "Topology",
    "TopologyData",
    "TopologyQueryRequest",
    "TopologyQueryResponse",
    # Support models
    "SupportLevel",
    "SupportLevelRequest",
    "SupportLevelResponse",
    "SupportChatRequest",
    "SupportChatResponse",
    "SupportChatEndRequest",
    "SupportChatEndResponse",
    # Error models
    "ErrorResponse",
    # Utility functions
    "parse_journal_content",
]
