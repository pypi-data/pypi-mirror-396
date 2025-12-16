"""
To-Do List Ability - Comprehensive task management.

This ability allows users to create and manage tasks with dependencies,
subtasks, priorities, due dates, recurring patterns, and productivity metrics.
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

import dateparser
import pytz
import structlog

from bruno_abilities.base.ability_base import AbilityContext, AbilityResult, BaseAbility
from bruno_abilities.base.metadata import (
    AbilityCapability,
    AbilityMetadata,
    ParameterMetadata,
    ParameterType,
)
from bruno_abilities.schemas.todo_schema import (
    RecurrencePattern,
    Task,
    TaskPriority,
    TaskStatus,
)

logger = structlog.get_logger(__name__)


class TodoAbility(BaseAbility):
    """
    To-Do List ability for comprehensive task management.

    Features:
    - Task creation with due dates and priorities
    - Task dependencies and subtasks
    - Task categories and projects
    - Completion tracking with history
    - Recurring tasks with flexible schedules
    - Task search and filtering
    - Productivity metrics and statistics
    - Task import/export support
    """

    def __init__(self) -> None:
        """Initialize the todo ability."""
        super().__init__()
        self._tasks: dict[str, Task] = {}  # task_id -> Task
        self._user_tasks: dict[str, list[str]] = {}  # user_id -> [task_ids]

    @property
    def metadata(self) -> AbilityMetadata:
        """Return todo ability metadata."""
        return AbilityMetadata(
            name="todo",
            display_name="To-Do List",
            description="Comprehensive task management with dependencies, priorities, and metrics",
            category="information_storage",
            version="1.0.0",
            tags=["todo", "tasks", "productivity", "project"],
            parameters=[
                ParameterMetadata(
                    name="action",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Action: create, update, complete, cancel, delete, list, search, stats, add_subtask",
                    required=True,
                    examples=[
                        "create",
                        "update",
                        "complete",
                        "cancel",
                        "delete",
                        "list",
                        "search",
                        "stats",
                    ],
                ),
                ParameterMetadata(
                    name="task_id",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Task ID for update/complete/cancel/delete actions",
                    required=False,
                ),
                ParameterMetadata(
                    name="title",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Task title (required for create)",
                    required=False,
                    examples=["Complete project report", "Buy groceries", "Call dentist"],
                ),
                ParameterMetadata(
                    name="description",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Task description",
                    required=False,
                ),
                ParameterMetadata(
                    name="priority",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Task priority: low, medium, high, urgent",
                    required=False,
                    default="medium",
                    examples=["low", "medium", "high", "urgent"],
                ),
                ParameterMetadata(
                    name="due_date",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Due date in natural language",
                    required=False,
                    examples=["tomorrow", "next Friday", "in 3 days"],
                ),
                ParameterMetadata(
                    name="project",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Project name",
                    required=False,
                    examples=["Website Redesign", "Q4 Planning"],
                ),
                ParameterMetadata(
                    name="category",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Task category",
                    required=False,
                    examples=["work", "personal", "shopping", "health"],
                ),
                ParameterMetadata(
                    name="tags",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Comma-separated tags",
                    required=False,
                    examples=["important,urgent", "review,draft"],
                ),
                ParameterMetadata(
                    name="depends_on",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Comma-separated task IDs this task depends on",
                    required=False,
                ),
                ParameterMetadata(
                    name="parent_task",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Parent task ID for subtasks",
                    required=False,
                ),
                ParameterMetadata(
                    name="recurrence",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Recurrence pattern: none, daily, weekly, monthly",
                    required=False,
                    default="none",
                    examples=["none", "daily", "weekly", "monthly"],
                ),
                ParameterMetadata(
                    name="estimated_minutes",
                    type=int,
                    parameter_type=ParameterType.INTEGER,
                    description="Estimated time in minutes",
                    required=False,
                    examples=[15, 30, 60, 120],
                ),
                ParameterMetadata(
                    name="search_query",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Search query for finding tasks",
                    required=False,
                ),
                ParameterMetadata(
                    name="status",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Filter by status: todo, in_progress, completed, cancelled, blocked",
                    required=False,
                ),
            ],
            capabilities=[
                AbilityCapability.CANCELLABLE,
            ],
            aliases=["task", "todo list", "tasks"],
            examples=[
                {
                    "description": "Create a task with due date",
                    "parameters": {
                        "action": "create",
                        "title": "Submit report",
                        "priority": "high",
                        "due_date": "Friday",
                        "project": "Q4 Review",
                    },
                },
                {
                    "description": "Create recurring task",
                    "parameters": {
                        "action": "create",
                        "title": "Weekly team sync",
                        "recurrence": "weekly",
                    },
                },
                {
                    "description": "Complete a task",
                    "parameters": {"action": "complete", "task_id": "task_abc123"},
                },
            ],
        )

    async def _execute(self, parameters: dict[str, Any], context: AbilityContext) -> AbilityResult:
        """Execute todo action."""
        action = parameters.get("action", "").lower()

        if action == "create":
            return await self._create_task(parameters, context)
        elif action == "update":
            return await self._update_task(parameters, context)
        elif action == "complete":
            return await self._complete_task(parameters, context)
        elif action == "cancel":
            return await self._cancel_task(parameters, context)
        elif action == "delete":
            return await self._delete_task(parameters, context)
        elif action == "list":
            return await self._list_tasks(parameters, context)
        elif action == "search":
            return await self._search_tasks(parameters, context)
        elif action == "stats":
            return await self._get_stats(parameters, context)
        elif action == "add_subtask":
            return await self._add_subtask(parameters, context)
        else:
            return AbilityResult(
                success=False,
                error=f"Unknown action: {action}. Valid: create, update, complete, cancel, delete, list, search, stats, add_subtask",
            )

    async def _create_task(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Create a new task."""
        title = parameters.get("title")
        if not title:
            return AbilityResult(
                success=False,
                error="Title is required for creating a task",
            )

        # Parse priority
        priority_str = parameters.get("priority", "medium").lower()
        try:
            priority = TaskPriority(priority_str)
        except ValueError:
            return AbilityResult(
                success=False,
                error=f"Invalid priority: {priority_str}. Valid: low, medium, high, urgent",
            )

        # Parse due date if provided
        due_date = None
        if parameters.get("due_date"):
            settings = {"PREFER_DATES_FROM": "future", "RELATIVE_BASE": datetime.now()}
            due_date = dateparser.parse(parameters["due_date"], settings=settings)
            if not due_date:
                return AbilityResult(
                    success=False,
                    error=f"Could not parse due date: {parameters['due_date']}",
                )
            # Make timezone-aware
            if due_date.tzinfo is None:
                due_date = pytz.UTC.localize(due_date)

        # Parse recurrence
        recurrence_str = parameters.get("recurrence", "none").lower()
        try:
            recurrence = RecurrencePattern(recurrence_str)
        except ValueError:
            return AbilityResult(
                success=False,
                error=f"Invalid recurrence: {recurrence_str}. Valid: none, daily, weekly, monthly",
            )

        # Parse tags
        tags = []
        if parameters.get("tags"):
            tags = [t.strip() for t in parameters["tags"].split(",")]

        # Parse dependencies
        depends_on = []
        if parameters.get("depends_on"):
            depends_on = [t.strip() for t in parameters["depends_on"].split(",")]
            # Validate dependencies exist
            for dep_id in depends_on:
                if dep_id not in self._tasks:
                    return AbilityResult(
                        success=False,
                        error=f"Dependency task not found: {dep_id}",
                    )

        # Generate task ID
        task_id = f"task_{uuid4().hex[:12]}"

        # Create task
        now = datetime.now(pytz.UTC)
        task = Task(
            task_id=task_id,
            title=title,
            description=parameters.get("description"),
            user_id=context.user_id,
            priority=priority,
            project=parameters.get("project"),
            category=parameters.get("category"),
            tags=tags,
            created_at=now,
            updated_at=now,
            due_date=due_date,
            recurrence=recurrence,
            depends_on=depends_on,
            parent_task=parameters.get("parent_task"),
            estimated_minutes=parameters.get("estimated_minutes"),
        )

        # Store task
        self._tasks[task_id] = task

        if context.user_id not in self._user_tasks:
            self._user_tasks[context.user_id] = []
        self._user_tasks[context.user_id].append(task_id)

        # If this is a subtask, add to parent
        if task.parent_task:
            parent = self._tasks.get(task.parent_task)
            if parent:
                parent.subtasks.append(task_id)

        logger.info(
            "Task created",
            task_id=task_id,
            title=title,
            priority=priority.value,
            user_id=context.user_id,
        )

        return AbilityResult(
            success=True,
            data={
                "task_id": task_id,
                "title": title,
                "priority": priority.value,
                "due_date": due_date.isoformat() if due_date else None,
                "recurrence": recurrence.value,
                "depends_on": depends_on,
                "message": f"Task '{title}' created successfully",
            },
        )

    async def _update_task(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Update an existing task."""
        task_id = parameters.get("task_id")
        if not task_id:
            return AbilityResult(
                success=False,
                error="task_id is required for updating a task",
            )

        task = self._tasks.get(task_id)
        if not task:
            return AbilityResult(
                success=False,
                error=f"Task not found: {task_id}",
            )

        if task.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to update this task",
            )

        # Track changes
        changes = []
        now = datetime.now(pytz.UTC)

        # Update title
        if "title" in parameters:
            task.title = parameters["title"]
            changes.append("title")

        # Update description
        if "description" in parameters:
            task.description = parameters["description"]
            changes.append("description")

        # Update priority
        if "priority" in parameters:
            try:
                task.priority = TaskPriority(parameters["priority"].lower())
                changes.append("priority")
            except ValueError:
                pass

        # Update due date
        if "due_date" in parameters:
            settings = {"PREFER_DATES_FROM": "future", "RELATIVE_BASE": datetime.now()}
            due_date = dateparser.parse(parameters["due_date"], settings=settings)
            if due_date:
                if due_date.tzinfo is None:
                    due_date = pytz.UTC.localize(due_date)
                task.due_date = due_date
                changes.append("due_date")

        # Update project/category/tags
        if "project" in parameters:
            task.project = parameters["project"]
            changes.append("project")

        if "category" in parameters:
            task.category = parameters["category"]
            changes.append("category")

        if "tags" in parameters:
            task.tags = [t.strip() for t in parameters["tags"].split(",")]
            changes.append("tags")

        # Update status
        if "status" in parameters:
            try:
                task.status = TaskStatus(parameters["status"].lower())
                changes.append("status")
            except ValueError:
                pass

        task.updated_at = now

        logger.info(
            "Task updated",
            task_id=task_id,
            changes=changes,
        )

        return AbilityResult(
            success=True,
            data={
                "task_id": task_id,
                "title": task.title,
                "updated_at": now.isoformat(),
                "changes": changes,
                "message": f"Task '{task.title}' updated successfully",
            },
        )

    async def _complete_task(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Mark a task as completed."""
        task_id = parameters.get("task_id")
        if not task_id:
            return AbilityResult(
                success=False,
                error="task_id is required for completing a task",
            )

        task = self._tasks.get(task_id)
        if not task:
            return AbilityResult(
                success=False,
                error=f"Task not found: {task_id}",
            )

        if task.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to complete this task",
            )

        # Check if dependencies are met
        for dep_id in task.depends_on:
            dep_task = self._tasks.get(dep_id)
            if dep_task and dep_task.status != TaskStatus.COMPLETED:
                return AbilityResult(
                    success=False,
                    error=f"Cannot complete task: dependency '{dep_task.title}' not completed",
                )

        now = datetime.now(pytz.UTC)
        task.status = TaskStatus.COMPLETED
        task.completed_at = now
        task.updated_at = now
        task.completion_count += 1
        task.completion_history.append(now)

        # Handle recurring tasks
        if task.recurrence != RecurrencePattern.NONE:
            # Reset for next occurrence
            task.status = TaskStatus.TODO
            task.completed_at = None
            task.last_recurrence = now

            # Calculate next due date
            if task.due_date:
                if task.recurrence == RecurrencePattern.DAILY:
                    task.due_date += timedelta(days=task.recurrence_interval)
                elif task.recurrence == RecurrencePattern.WEEKLY:
                    task.due_date += timedelta(weeks=task.recurrence_interval)
                elif task.recurrence == RecurrencePattern.MONTHLY:
                    # Approximate monthly
                    task.due_date += timedelta(days=30 * task.recurrence_interval)

            logger.info(
                "Recurring task completed and reset",
                task_id=task_id,
                next_due=task.due_date.isoformat() if task.due_date else None,
            )
        else:
            logger.info("Task completed", task_id=task_id)

        return AbilityResult(
            success=True,
            data={
                "task_id": task_id,
                "title": task.title,
                "completed_at": now.isoformat(),
                "status": task.status.value,
                "recurring": task.recurrence != RecurrencePattern.NONE,
                "completion_count": task.completion_count,
                "message": f"Task '{task.title}' completed successfully",
            },
        )

    async def _cancel_task(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Cancel a task."""
        task_id = parameters.get("task_id")
        if not task_id:
            return AbilityResult(
                success=False,
                error="task_id is required for cancelling a task",
            )

        task = self._tasks.get(task_id)
        if not task:
            return AbilityResult(
                success=False,
                error=f"Task not found: {task_id}",
            )

        if task.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to cancel this task",
            )

        task.status = TaskStatus.CANCELLED
        task.updated_at = datetime.now(pytz.UTC)

        logger.info("Task cancelled", task_id=task_id)

        return AbilityResult(
            success=True,
            data={
                "task_id": task_id,
                "title": task.title,
                "status": task.status.value,
                "message": f"Task '{task.title}' cancelled successfully",
            },
        )

    async def _delete_task(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Delete a task."""
        task_id = parameters.get("task_id")
        if not task_id:
            return AbilityResult(
                success=False,
                error="task_id is required for deleting a task",
            )

        task = self._tasks.get(task_id)
        if not task:
            return AbilityResult(
                success=False,
                error=f"Task not found: {task_id}",
            )

        if task.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to delete this task",
            )

        # Remove from storage
        del self._tasks[task_id]
        if context.user_id in self._user_tasks:
            self._user_tasks[context.user_id].remove(task_id)

        # Remove from parent's subtasks
        if task.parent_task:
            parent = self._tasks.get(task.parent_task)
            if parent and task_id in parent.subtasks:
                parent.subtasks.remove(task_id)

        logger.info("Task deleted", task_id=task_id)

        return AbilityResult(
            success=True,
            data={
                "task_id": task_id,
                "message": f"Task '{task.title}' deleted successfully",
            },
        )

    async def _list_tasks(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """List tasks with optional filtering."""
        user_task_ids = self._user_tasks.get(context.user_id, [])

        # Get status filter
        status_filter = None
        if parameters.get("status"):
            try:
                status_filter = TaskStatus(parameters["status"].lower())
            except ValueError:
                pass

        tasks_data = []
        for task_id in user_task_ids:
            task = self._tasks.get(task_id)
            if not task:
                continue

            # Apply status filter
            if status_filter and task.status != status_filter:
                continue

            # Calculate if task is blocked by dependencies
            is_blocked = False
            if task.depends_on:
                for dep_id in task.depends_on:
                    dep_task = self._tasks.get(dep_id)
                    if dep_task and dep_task.status != TaskStatus.COMPLETED:
                        is_blocked = True
                        break

            tasks_data.append(
                {
                    "task_id": task.task_id,
                    "title": task.title,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "project": task.project,
                    "category": task.category,
                    "tags": task.tags,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat(),
                    "is_blocked": is_blocked,
                    "subtasks_count": len(task.subtasks),
                }
            )

        # Sort by priority and due date
        def sort_key(t):
            priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
            return (
                priority_order.get(t["priority"], 4),
                t["due_date"] or "9999-12-31",
            )

        tasks_data.sort(key=sort_key)

        logger.info(
            "Tasks listed",
            user_id=context.user_id,
            count=len(tasks_data),
        )

        return AbilityResult(
            success=True,
            data={
                "tasks": tasks_data,
                "count": len(tasks_data),
                "message": f"Found {len(tasks_data)} task(s)",
            },
        )

    async def _search_tasks(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Search for tasks."""
        search_query = parameters.get("search_query", "").lower()
        if not search_query:
            return AbilityResult(
                success=False,
                error="search_query is required for searching tasks",
            )

        user_task_ids = self._user_tasks.get(context.user_id, [])

        matching_tasks = []
        for task_id in user_task_ids:
            task = self._tasks.get(task_id)
            if not task:
                continue

            # Search in title, description, project, category, and tags
            search_fields = [
                task.title.lower(),
                (task.description or "").lower(),
                (task.project or "").lower(),
                (task.category or "").lower(),
            ] + [tag.lower() for tag in task.tags]

            if any(search_query in field for field in search_fields):
                matching_tasks.append(
                    {
                        "task_id": task.task_id,
                        "title": task.title,
                        "status": task.status.value,
                        "priority": task.priority.value,
                        "project": task.project,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                    }
                )

        logger.info(
            "Tasks searched",
            user_id=context.user_id,
            query=search_query,
            count=len(matching_tasks),
        )

        return AbilityResult(
            success=True,
            data={
                "tasks": matching_tasks,
                "count": len(matching_tasks),
                "query": search_query,
                "message": f"Found {len(matching_tasks)} task(s) matching '{search_query}'",
            },
        )

    async def _get_stats(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Get productivity statistics."""
        user_task_ids = self._user_tasks.get(context.user_id, [])

        stats = {
            "total_tasks": 0,
            "todo": 0,
            "in_progress": 0,
            "completed": 0,
            "cancelled": 0,
            "overdue": 0,
            "due_today": 0,
            "due_this_week": 0,
            "by_priority": {"low": 0, "medium": 0, "high": 0, "urgent": 0},
            "by_project": {},
            "completion_rate": 0.0,
            "average_completion_time": None,
        }

        now = datetime.now(pytz.UTC)
        today = now.date()
        week_end = today + timedelta(days=7)

        completed_times = []

        for task_id in user_task_ids:
            task = self._tasks.get(task_id)
            if not task:
                continue

            stats["total_tasks"] += 1

            # Count by status
            if task.status == TaskStatus.TODO:
                stats["todo"] += 1
            elif task.status == TaskStatus.IN_PROGRESS:
                stats["in_progress"] += 1
            elif task.status == TaskStatus.COMPLETED:
                stats["completed"] += 1
                # Calculate completion time
                if task.completed_at:
                    completion_time = (task.completed_at - task.created_at).total_seconds() / 60
                    completed_times.append(completion_time)
            elif task.status == TaskStatus.CANCELLED:
                stats["cancelled"] += 1

            # Count by priority
            stats["by_priority"][task.priority.value] += 1

            # Count by project
            if task.project:
                stats["by_project"][task.project] = stats["by_project"].get(task.project, 0) + 1

            # Check due dates
            if task.due_date and task.status not in [
                TaskStatus.COMPLETED,
                TaskStatus.CANCELLED,
            ]:
                due_date = task.due_date.date() if task.due_date.tzinfo else task.due_date.date()

                if due_date < today:
                    stats["overdue"] += 1
                elif due_date == today:
                    stats["due_today"] += 1
                elif due_date <= week_end:
                    stats["due_this_week"] += 1

        # Calculate completion rate
        if stats["total_tasks"] > 0:
            stats["completion_rate"] = round((stats["completed"] / stats["total_tasks"]) * 100, 1)

        # Calculate average completion time
        if completed_times:
            avg_minutes = sum(completed_times) / len(completed_times)
            stats["average_completion_time"] = f"{int(avg_minutes)} minutes"

        logger.info(
            "Stats retrieved",
            user_id=context.user_id,
            total_tasks=stats["total_tasks"],
        )

        return AbilityResult(
            success=True,
            data=stats,
        )

    async def _add_subtask(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Add a subtask to a parent task."""
        parent_id = parameters.get("parent_task")
        if not parent_id:
            return AbilityResult(
                success=False,
                error="parent_task is required for adding a subtask",
            )

        parent = self._tasks.get(parent_id)
        if not parent:
            return AbilityResult(
                success=False,
                error=f"Parent task not found: {parent_id}",
            )

        if parent.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to add subtask to this task",
            )

        # Create subtask using regular create logic
        return await self._create_task(parameters, context)

    async def _cleanup(self) -> None:
        """Clean up tasks storage."""
        self._tasks.clear()
        self._user_tasks.clear()
        logger.info("Todo ability cleaned up")
