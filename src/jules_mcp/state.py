"""Data models for worker state, activities, and state machine"""

from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WorkerState(str, Enum):
    """State of a worker Jules session"""
    PLANNING = "PLANNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ActivityType(str, Enum):
    """Type of Jules activity"""
    PLAN_GENERATED = "PLAN_GENERATED"
    PLAN_APPROVED = "PLAN_APPROVED"
    PROGRESS_UPDATED = "PROGRESS_UPDATED"
    SESSION_COMPLETED = "SESSION_COMPLETED"
    MESSAGE = "MESSAGE"
    UNKNOWN = "UNKNOWN"


class Activity(BaseModel):
    """Represents a Jules activity"""
    id: str
    name: str
    create_time: str
    originator: str
    type: ActivityType
    title: Optional[str] = None
    description: Optional[str] = None
    raw_data: dict

    @classmethod
    def from_api_response(cls, data: dict) -> "Activity":
        """Parse activity from Jules API response"""
        from .utils import detect_activity_type

        activity_id = data.get("name", "").split("/")[-1]
        activity_type = detect_activity_type(data)

        # Extract title and description based on activity type
        title = None
        description = None

        if "planGenerated" in data:
            plan = data["planGenerated"].get("plan", {})
            title = plan.get("title")
            description = plan.get("description")
        elif "progressUpdated" in data:
            progress = data["progressUpdated"]
            title = progress.get("title")
            description = progress.get("description")
        elif "userMessage" in data:
            title = "User Message"
            description = data["userMessage"].get("message")
        elif "agentMessage" in data:
            title = "Agent Message"
            description = data["agentMessage"].get("message")

        return cls(
            id=activity_id,
            name=data.get("name", ""),
            create_time=data.get("createTime", ""),
            originator=data.get("originator", "unknown"),
            type=activity_type,
            title=title,
            description=description,
            raw_data=data
        )


class WorkerSession(BaseModel):
    """Represents a worker Jules session with state tracking"""
    session_id: str
    task_description: str
    source: str
    state: WorkerState
    created_at: datetime
    last_activity_time: datetime
    activities_buffer: list[Activity] = Field(default_factory=list)
    pending_plan_id: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def update_from_activities(self, activities: list[Activity], stuck_timeout: int = 300) -> None:
        """Update worker state based on new activities"""
        if not activities:
            return

        # Update activities buffer (keep last 10)
        self.activities_buffer = activities[-10:]

        # Update last activity time
        if activities:
            self.last_activity_time = datetime.now()

        # Detect new state
        new_state = self.detect_state()

        # Check for errors
        from .utils import extract_error_from_activity
        for activity in activities:
            error = extract_error_from_activity(activity.raw_data)
            if error:
                self.state = WorkerState.FAILED
                self.error_message = error
                return

        # Update state
        self.state = new_state

        # Check for pending plan
        latest = activities[-1] if activities else None
        if latest and latest.type == ActivityType.PLAN_GENERATED:
            self.pending_plan_id = latest.id
        elif latest and latest.type == ActivityType.PLAN_APPROVED:
            self.pending_plan_id = None

    def detect_state(self) -> WorkerState:
        """Determine current state from activities"""
        if not self.activities_buffer:
            return WorkerState.PLANNING

        latest = self.activities_buffer[-1]

        # State transitions based on latest activity
        if latest.type == ActivityType.SESSION_COMPLETED:
            return WorkerState.COMPLETED
        elif latest.type == ActivityType.PLAN_GENERATED:
            return WorkerState.WAITING_APPROVAL
        elif latest.type == ActivityType.PLAN_APPROVED:
            return WorkerState.EXECUTING
        elif latest.type == ActivityType.PROGRESS_UPDATED:
            return WorkerState.EXECUTING

        # Default to PLANNING if no clear state
        return WorkerState.PLANNING

    def is_blocked(self) -> bool:
        """Check if worker needs human intervention"""
        # Blocked if waiting for plan approval
        if self.state == WorkerState.WAITING_APPROVAL:
            return True

        # Blocked if failed
        if self.state == WorkerState.FAILED:
            return True

        # Potentially stuck if no activity for too long (5 minutes)
        if self.state == WorkerState.EXECUTING:
            time_since_activity = (datetime.now() - self.last_activity_time).total_seconds()
            if time_since_activity > 300:  # 5 minutes
                return True

        return False

    def get_blocker_reason(self) -> Optional[str]:
        """Describe why worker is blocked"""
        if self.state == WorkerState.WAITING_APPROVAL:
            return "Plan generated, waiting for approval"

        if self.state == WorkerState.FAILED:
            return f"Failed: {self.error_message or 'Unknown error'}"

        if self.state == WorkerState.EXECUTING:
            time_since_activity = (datetime.now() - self.last_activity_time).total_seconds()
            if time_since_activity > 300:
                return f"No activity for {int(time_since_activity / 60)} minutes (potentially stuck)"

        return None
