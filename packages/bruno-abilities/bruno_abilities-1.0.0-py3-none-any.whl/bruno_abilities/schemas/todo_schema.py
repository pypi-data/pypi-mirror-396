"""
To-Do List schema for bruno-memory integration.

This module defines the data structures for task management,
including dependencies, priorities, and metrics.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    """Task status enumeration."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    """Task priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecurrencePattern(str, Enum):
    """Recurrence pattern enumeration."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class Task(BaseModel):
    """
    Represents a task with rich metadata.

    Tasks support dependencies, subtasks, priorities,
    due dates, recurring patterns, and completion tracking.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    task_id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: str | None = Field(default=None, description="Task description")
    user_id: str = Field(..., description="User who owns the task")

    # Status and Priority
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")

    # Organization
    project: str | None = Field(default=None, description="Project name")
    category: str | None = Field(default=None, description="Task category")
    tags: list[str] = Field(default_factory=list, description="Task tags")

    # Timing
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    due_date: datetime | None = Field(default=None, description="Due date")
    completed_at: datetime | None = Field(default=None, description="Completion timestamp")

    # Recurrence
    recurrence: RecurrencePattern = Field(
        default=RecurrencePattern.NONE, description="Recurrence pattern"
    )
    recurrence_interval: int = Field(
        default=1, description="Interval for recurrence (e.g., every N days)"
    )
    last_recurrence: datetime | None = Field(default=None, description="Last recurrence timestamp")

    # Dependencies and Hierarchy
    depends_on: list[str] = Field(default_factory=list, description="IDs of tasks this depends on")
    parent_task: str | None = Field(default=None, description="Parent task ID for subtasks")
    subtasks: list[str] = Field(default_factory=list, description="Subtask IDs")

    # Metrics
    estimated_minutes: int | None = Field(default=None, description="Estimated time to complete")
    actual_minutes: int | None = Field(default=None, description="Actual time spent")

    # History
    completion_count: int = Field(
        default=0, description="Number of times completed (for recurring)"
    )
    completion_history: list[datetime] = Field(
        default_factory=list, description="History of completion times"
    )
