"""
Reminder Ability - Contextual reminders with natural language parsing.

This ability allows users to create reminders using natural language,
with support for categorization, priorities, snoozing, and recurring schedules.
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

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

logger = structlog.get_logger(__name__)


class ReminderState(str, Enum):
    """Reminder states."""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SNOOZED = "snoozed"


class Priority(str, Enum):
    """Reminder priorities."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Reminder:
    """Represents a reminder."""

    reminder_id: str
    title: str
    remind_at: datetime
    user_id: str
    description: str | None = None
    category: str | None = None
    priority: Priority = Priority.MEDIUM
    state: ReminderState = ReminderState.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    snoozed_until: datetime | None = None
    callback: Callable | None = None
    tags: list[str] = field(default_factory=list)
    recurring_days: int | None = None  # Recur every N days

    def __post_init__(self) -> None:
        """Validate reminder data."""
        if self.remind_at.tzinfo is None:
            # Make timezone-aware (UTC)
            self.remind_at = pytz.UTC.localize(self.remind_at)


class ReminderAbility(BaseAbility):
    """
    Reminder ability for creating contextual reminders.

    Features:
    - Natural language date/time parsing ("tomorrow at 3pm", "in 2 hours")
    - Categorization and tagging
    - Priority levels
    - Snooze functionality
    - Recurring reminders
    - Context and description
    - Search and filtering
    """

    def __init__(self) -> None:
        """Initialize the reminder ability."""
        super().__init__()
        self._reminders: dict[str, Reminder] = {}  # reminder_id -> Reminder
        self._user_reminders: dict[str, list[str]] = {}  # user_id -> [reminder_ids]
        self._reminder_counter = 0
        self._monitor_task: asyncio.Task | None = None

    @property
    def metadata(self) -> AbilityMetadata:
        """Return reminder ability metadata."""
        return AbilityMetadata(
            name="reminder",
            display_name="Reminder",
            description="Create and manage reminders with natural language and smart scheduling",
            category="time_management",
            version="1.0.0",
            tags=["reminder", "schedule", "notification", "task"],
            parameters=[
                ParameterMetadata(
                    name="action",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Action to perform: create, complete, cancel, snooze, list, search, status",
                    required=True,
                    examples=["create", "complete", "cancel", "snooze", "list", "search", "status"],
                ),
                ParameterMetadata(
                    name="title",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Reminder title (required for create)",
                    required=False,
                    examples=["Call dentist", "Buy groceries", "Submit report"],
                ),
                ParameterMetadata(
                    name="when",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="When to remind in natural language (required for create)",
                    required=False,
                    examples=["tomorrow at 3pm", "in 2 hours", "next Monday at 9am"],
                ),
                ParameterMetadata(
                    name="description",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Additional context or notes",
                    required=False,
                ),
                ParameterMetadata(
                    name="category",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Reminder category",
                    required=False,
                    examples=["work", "personal", "health", "shopping"],
                ),
                ParameterMetadata(
                    name="priority",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Priority level: low, medium, high, urgent",
                    required=False,
                    default="medium",
                    examples=["low", "medium", "high", "urgent"],
                ),
                ParameterMetadata(
                    name="tags",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Comma-separated tags",
                    required=False,
                    examples=["important,urgent", "work,project"],
                ),
                ParameterMetadata(
                    name="reminder_id",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Reminder ID for complete/cancel/snooze/status actions",
                    required=False,
                ),
                ParameterMetadata(
                    name="snooze_minutes",
                    type=int,
                    parameter_type=ParameterType.INTEGER,
                    description="Minutes to snooze the reminder",
                    required=False,
                    default=10,
                    examples=[5, 10, 30, 60],
                ),
                ParameterMetadata(
                    name="recurring_days",
                    type=int,
                    parameter_type=ParameterType.INTEGER,
                    description="Recur every N days (0 for no recurrence)",
                    required=False,
                    default=0,
                ),
                ParameterMetadata(
                    name="search_query",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Search query for finding reminders",
                    required=False,
                ),
            ],
            capabilities=[
                AbilityCapability.CANCELLABLE,
                AbilityCapability.BACKGROUND,
            ],
            aliases=["remind me", "set reminder", "reminder"],
            examples=[
                {
                    "description": "Remind me to call dentist tomorrow at 3pm",
                    "parameters": {
                        "action": "create",
                        "title": "Call dentist",
                        "when": "tomorrow at 3pm",
                        "category": "health",
                        "priority": "high",
                    },
                },
                {
                    "description": "List all active reminders",
                    "parameters": {"action": "list"},
                },
                {
                    "description": "Search for work reminders",
                    "parameters": {"action": "search", "search_query": "work"},
                },
            ],
        )

    async def initialize(self) -> None:
        """Initialize and start reminder monitoring."""
        await super().initialize()
        self._monitor_task = asyncio.create_task(self._monitor_reminders())
        logger.info("Reminder monitoring started")

    async def _execute(self, parameters: dict[str, Any], context: AbilityContext) -> AbilityResult:
        """Execute reminder action."""
        action = parameters.get("action", "").lower()

        if action == "create":
            return await self._create_reminder(parameters, context)
        elif action == "complete":
            return await self._complete_reminder(parameters, context)
        elif action == "cancel":
            return await self._cancel_reminder(parameters, context)
        elif action == "snooze":
            return await self._snooze_reminder(parameters, context)
        elif action == "list":
            return await self._list_reminders(parameters, context)
        elif action == "search":
            return await self._search_reminders(parameters, context)
        elif action == "status":
            return await self._get_reminder_status(parameters, context)
        else:
            return AbilityResult(
                success=False,
                error=f"Unknown action: {action}. Valid actions: create, complete, cancel, snooze, list, search, status",
            )

    async def _create_reminder(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Create a new reminder."""
        title = parameters.get("title")
        when = parameters.get("when")

        if not title:
            return AbilityResult(
                success=False,
                error="Title is required for creating a reminder",
            )

        if not when:
            return AbilityResult(
                success=False,
                error="When (time) is required for creating a reminder",
            )

        # Parse time using dateparser (better for natural language than dateutil)
        settings = {"PREFER_DATES_FROM": "future", "RELATIVE_BASE": datetime.now()}
        remind_at = dateparser.parse(when, settings=settings)
        if not remind_at:
            return AbilityResult(
                success=False,
                error=f"Could not parse time: {when}",
            )

        # Validate time is in the future
        now = datetime.now(pytz.UTC)
        if remind_at.tzinfo is None:
            remind_at = pytz.UTC.localize(remind_at)

        if remind_at <= now:
            return AbilityResult(
                success=False,
                error="Reminder time must be in the future",
            )

        # Parse priority
        priority_str = parameters.get("priority", "medium").lower()
        try:
            priority = Priority(priority_str)
        except ValueError:
            return AbilityResult(
                success=False,
                error=f"Invalid priority: {priority_str}. Valid: low, medium, high, urgent",
            )

        # Parse tags
        tags = []
        if parameters.get("tags"):
            tags = [t.strip() for t in parameters["tags"].split(",")]

        # Parse recurring
        recurring_days = parameters.get("recurring_days", 0)
        if recurring_days and recurring_days < 0:
            return AbilityResult(
                success=False,
                error="Recurring days must be 0 or positive",
            )

        # Generate reminder ID
        self._reminder_counter += 1
        reminder_id = f"reminder_{self._reminder_counter}"

        # Create reminder
        reminder = Reminder(
            reminder_id=reminder_id,
            title=title,
            remind_at=remind_at,
            user_id=context.user_id,
            description=parameters.get("description"),
            category=parameters.get("category"),
            priority=priority,
            tags=tags,
            recurring_days=recurring_days if recurring_days > 0 else None,
        )

        # Store reminder
        self._reminders[reminder_id] = reminder

        if context.user_id not in self._user_reminders:
            self._user_reminders[context.user_id] = []
        self._user_reminders[context.user_id].append(reminder_id)

        logger.info(
            "Reminder created",
            reminder_id=reminder_id,
            title=title,
            remind_at=remind_at.isoformat(),
            priority=priority.value,
            user_id=context.user_id,
        )

        return AbilityResult(
            success=True,
            data={
                "reminder_id": reminder_id,
                "title": title,
                "remind_at": remind_at.isoformat(),
                "priority": priority.value,
                "category": reminder.category,
                "tags": tags,
                "recurring": bool(reminder.recurring_days),
                "message": f"Reminder created: '{title}' for {remind_at.strftime('%Y-%m-%d %H:%M')}",
            },
        )

    async def _monitor_reminders(self) -> None:
        """Monitor reminders and trigger them at the right time."""
        try:
            while not self.is_cancelled():
                now = datetime.now(pytz.UTC)

                for reminder in list(self._reminders.values()):
                    if reminder.state != ReminderState.ACTIVE:
                        continue

                    # Check if snoozed
                    trigger_time = (
                        reminder.snoozed_until if reminder.snoozed_until else reminder.remind_at
                    )

                    # Make timezone-aware if needed
                    if trigger_time.tzinfo is None:
                        trigger_time = pytz.UTC.localize(trigger_time)

                    if now >= trigger_time:
                        await self._trigger_reminder(reminder)

                # Check every second
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("Reminder monitoring stopped")
            raise

        except Exception as e:
            logger.error("Reminder monitoring error", error=str(e))

    async def _trigger_reminder(self, reminder: Reminder) -> None:
        """Trigger a reminder."""
        logger.info(
            "Reminder triggered",
            reminder_id=reminder.reminder_id,
            title=reminder.title,
        )

        # Call notification callback if set
        if reminder.callback:
            try:
                await reminder.callback(reminder)
            except Exception as e:
                logger.error(
                    "Reminder callback failed",
                    reminder_id=reminder.reminder_id,
                    error=str(e),
                )

        # Handle recurrence
        if reminder.recurring_days:
            # Reset and reschedule
            reminder.remind_at = reminder.remind_at + timedelta(days=reminder.recurring_days)
            reminder.snoozed_until = None
            logger.info(
                "Recurring reminder rescheduled",
                reminder_id=reminder.reminder_id,
                next_time=reminder.remind_at.isoformat(),
            )
        else:
            # Mark as completed
            reminder.state = ReminderState.COMPLETED
            reminder.completed_at = datetime.now()

    async def _complete_reminder(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Mark a reminder as completed."""
        reminder_id = parameters.get("reminder_id")
        if not reminder_id:
            return AbilityResult(
                success=False,
                error="reminder_id is required for completing a reminder",
            )

        reminder = self._reminders.get(reminder_id)
        if not reminder:
            return AbilityResult(
                success=False,
                error=f"Reminder not found: {reminder_id}",
            )

        if reminder.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to complete this reminder",
            )

        reminder.state = ReminderState.COMPLETED
        reminder.completed_at = datetime.now()

        logger.info("Reminder completed", reminder_id=reminder_id)

        return AbilityResult(
            success=True,
            data={
                "reminder_id": reminder_id,
                "title": reminder.title,
                "state": reminder.state.value,
                "message": f"Reminder '{reminder.title}' marked as completed",
            },
        )

    async def _cancel_reminder(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Cancel a reminder."""
        reminder_id = parameters.get("reminder_id")
        if not reminder_id:
            return AbilityResult(
                success=False,
                error="reminder_id is required for cancelling a reminder",
            )

        reminder = self._reminders.get(reminder_id)
        if not reminder:
            return AbilityResult(
                success=False,
                error=f"Reminder not found: {reminder_id}",
            )

        if reminder.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to cancel this reminder",
            )

        reminder.state = ReminderState.CANCELLED

        logger.info("Reminder cancelled", reminder_id=reminder_id)

        return AbilityResult(
            success=True,
            data={
                "reminder_id": reminder_id,
                "title": reminder.title,
                "state": reminder.state.value,
                "message": f"Reminder '{reminder.title}' cancelled",
            },
        )

    async def _snooze_reminder(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Snooze a reminder."""
        reminder_id = parameters.get("reminder_id")
        snooze_minutes = parameters.get("snooze_minutes", 10)

        if not reminder_id:
            return AbilityResult(
                success=False,
                error="reminder_id is required for snoozing a reminder",
            )

        reminder = self._reminders.get(reminder_id)
        if not reminder:
            return AbilityResult(
                success=False,
                error=f"Reminder not found: {reminder_id}",
            )

        if reminder.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to snooze this reminder",
            )

        # Set snooze time
        snooze_until = datetime.now(pytz.UTC) + timedelta(minutes=snooze_minutes)
        reminder.snoozed_until = snooze_until
        reminder.state = ReminderState.SNOOZED

        logger.info(
            "Reminder snoozed",
            reminder_id=reminder_id,
            snooze_minutes=snooze_minutes,
        )

        return AbilityResult(
            success=True,
            data={
                "reminder_id": reminder_id,
                "title": reminder.title,
                "snoozed_until": snooze_until.isoformat(),
                "snooze_minutes": snooze_minutes,
                "message": f"Reminder '{reminder.title}' snoozed for {snooze_minutes} minutes",
            },
        )

    async def _list_reminders(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """List all active reminders for the user."""
        user_reminder_ids = self._user_reminders.get(context.user_id, [])

        reminders_data = []
        for reminder_id in user_reminder_ids:
            reminder = self._reminders.get(reminder_id)
            if reminder and reminder.state == ReminderState.ACTIVE:
                reminders_data.append(
                    {
                        "reminder_id": reminder.reminder_id,
                        "title": reminder.title,
                        "remind_at": reminder.remind_at.isoformat(),
                        "priority": reminder.priority.value,
                        "category": reminder.category,
                        "tags": reminder.tags,
                        "recurring": bool(reminder.recurring_days),
                    }
                )

        # Sort by remind_at
        reminders_data.sort(key=lambda r: r["remind_at"])

        logger.info(
            "Reminders listed",
            user_id=context.user_id,
            count=len(reminders_data),
        )

        return AbilityResult(
            success=True,
            data={
                "reminders": reminders_data,
                "count": len(reminders_data),
                "message": f"Found {len(reminders_data)} active reminder(s)",
            },
        )

    async def _search_reminders(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Search reminders by query."""
        search_query = parameters.get("search_query", "").lower()

        if not search_query:
            return AbilityResult(
                success=False,
                error="search_query is required for searching reminders",
            )

        user_reminder_ids = self._user_reminders.get(context.user_id, [])

        matching_reminders = []
        for reminder_id in user_reminder_ids:
            reminder = self._reminders.get(reminder_id)
            if not reminder or reminder.state == ReminderState.CANCELLED:
                continue

            # Search in title, description, category, and tags
            search_fields = [
                reminder.title.lower(),
                (reminder.description or "").lower(),
                (reminder.category or "").lower(),
            ] + [tag.lower() for tag in reminder.tags]

            if any(search_query in field for field in search_fields):
                matching_reminders.append(
                    {
                        "reminder_id": reminder.reminder_id,
                        "title": reminder.title,
                        "remind_at": reminder.remind_at.isoformat(),
                        "priority": reminder.priority.value,
                        "category": reminder.category,
                        "state": reminder.state.value,
                        "tags": reminder.tags,
                    }
                )

        logger.info(
            "Reminders searched",
            user_id=context.user_id,
            query=search_query,
            count=len(matching_reminders),
        )

        return AbilityResult(
            success=True,
            data={
                "reminders": matching_reminders,
                "count": len(matching_reminders),
                "query": search_query,
                "message": f"Found {len(matching_reminders)} reminder(s) matching '{search_query}'",
            },
        )

    async def _get_reminder_status(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Get status of a specific reminder."""
        reminder_id = parameters.get("reminder_id")
        if not reminder_id:
            return AbilityResult(
                success=False,
                error="reminder_id is required for getting reminder status",
            )

        reminder = self._reminders.get(reminder_id)
        if not reminder:
            return AbilityResult(
                success=False,
                error=f"Reminder not found: {reminder_id}",
            )

        if reminder.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to view this reminder",
            )

        data = {
            "reminder_id": reminder.reminder_id,
            "title": reminder.title,
            "remind_at": reminder.remind_at.isoformat(),
            "priority": reminder.priority.value,
            "state": reminder.state.value,
            "created_at": reminder.created_at.isoformat(),
        }

        if reminder.description:
            data["description"] = reminder.description

        if reminder.category:
            data["category"] = reminder.category

        if reminder.tags:
            data["tags"] = reminder.tags

        if reminder.completed_at:
            data["completed_at"] = reminder.completed_at.isoformat()

        if reminder.snoozed_until:
            data["snoozed_until"] = reminder.snoozed_until.isoformat()

        if reminder.recurring_days:
            data["recurring_days"] = reminder.recurring_days

        return AbilityResult(
            success=True,
            data=data,
        )

    async def _cleanup(self) -> None:
        """Clean up reminder monitoring."""
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        self._reminders.clear()
        self._user_reminders.clear()

        logger.info("Reminder ability cleaned up")
