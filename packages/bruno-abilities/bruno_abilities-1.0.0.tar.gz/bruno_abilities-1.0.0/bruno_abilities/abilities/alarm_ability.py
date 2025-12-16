"""
Alarm Ability - Scheduled alarms with one-time and recurring support.

This ability allows users to create and manage alarms that trigger at
specific times, with support for recurring schedules and timezone awareness.
"""

import asyncio
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import pytz
import structlog
from dateutil import parser as date_parser

from bruno_abilities.base.ability_base import AbilityContext, AbilityResult, BaseAbility
from bruno_abilities.base.metadata import (
    AbilityCapability,
    AbilityMetadata,
    ParameterMetadata,
    ParameterType,
)

logger = structlog.get_logger(__name__)


class AlarmState(str, Enum):
    """Alarm states."""

    ACTIVE = "active"
    DISABLED = "disabled"
    TRIGGERED = "triggered"
    MISSED = "missed"


class RecurrenceType(str, Enum):
    """Recurrence types for alarms."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    WEEKDAYS = "weekdays"
    WEEKENDS = "weekends"
    CUSTOM = "custom"


@dataclass
class Alarm:
    """Represents an alarm."""

    alarm_id: str
    name: str
    alarm_time: datetime
    user_id: str
    timezone: str = "UTC"
    state: AlarmState = AlarmState.ACTIVE
    recurrence: RecurrenceType = RecurrenceType.NONE
    recurrence_days: list[int] | None = None  # 0=Monday, 6=Sunday
    created_at: datetime = field(default_factory=datetime.now)
    last_triggered: datetime | None = None
    next_trigger: datetime | None = None
    callback: Callable | None = None
    task: asyncio.Task | None = None
    snooze_until: datetime | None = None

    def __post_init__(self) -> None:
        """Initialize next trigger time."""
        if self.next_trigger is None:
            self.next_trigger = self._calculate_next_trigger()

    def _calculate_next_trigger(self) -> datetime:
        """Calculate the next trigger time for this alarm."""
        now = datetime.now(pytz.timezone(self.timezone))
        alarm_dt = self.alarm_time

        # Make alarm_time timezone-aware if it isn't already
        if alarm_dt.tzinfo is None:
            tz = pytz.timezone(self.timezone)
            alarm_dt = tz.localize(alarm_dt)

        # If snoozed, return snooze time
        if self.snooze_until:
            return self.snooze_until

        # For one-time alarms
        if self.recurrence == RecurrenceType.NONE:
            return alarm_dt if alarm_dt > now else alarm_dt

        # For recurring alarms, find next occurrence
        next_time = alarm_dt

        # Start from today's time
        next_time = next_time.replace(year=now.year, month=now.month, day=now.day)

        # If the time has passed today, start from tomorrow
        if next_time <= now:
            next_time += timedelta(days=1)

        # Handle different recurrence types
        if self.recurrence == RecurrenceType.DAILY:
            return next_time

        elif self.recurrence == RecurrenceType.WEEKDAYS:
            # Monday to Friday (0-4)
            while next_time.weekday() >= 5:
                next_time += timedelta(days=1)
            return next_time

        elif self.recurrence == RecurrenceType.WEEKENDS:
            # Saturday and Sunday (5-6)
            while next_time.weekday() < 5:
                next_time += timedelta(days=1)
            return next_time

        elif self.recurrence == RecurrenceType.CUSTOM and self.recurrence_days:
            # Find next day that matches
            max_days = 7
            days_checked = 0
            while days_checked < max_days:
                if next_time.weekday() in self.recurrence_days:
                    return next_time
                next_time += timedelta(days=1)
                days_checked += 1
            return next_time

        return next_time


class AlarmAbility(BaseAbility):
    """
    Alarm ability for creating and managing scheduled alarms.

    Features:
    - One-time and recurring alarms
    - Timezone-aware scheduling
    - Multiple recurrence patterns (daily, weekly, weekdays, weekends, custom)
    - Snooze functionality
    - Missed alarm detection and handling
    - Alarm listing and status checking
    """

    def __init__(self) -> None:
        """Initialize the alarm ability."""
        super().__init__()
        self._alarms: dict[str, Alarm] = {}  # alarm_id -> Alarm
        self._user_alarms: dict[str, list[str]] = {}  # user_id -> [alarm_ids]
        self._alarm_counter = 0
        self._monitor_task: asyncio.Task | None = None

    @property
    def metadata(self) -> AbilityMetadata:
        """Return alarm ability metadata."""
        return AbilityMetadata(
            name="alarm",
            display_name="Alarm",
            description="Create and manage scheduled alarms with recurring patterns",
            category="time_management",
            version="1.0.0",
            tags=["alarm", "schedule", "time", "reminder", "recurring"],
            parameters=[
                ParameterMetadata(
                    name="action",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Action to perform: create, disable, enable, delete, snooze, list, status",
                    required=True,
                    examples=["create", "disable", "enable", "delete", "snooze", "list", "status"],
                ),
                ParameterMetadata(
                    name="time",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Alarm time in format 'HH:MM' or natural language (required for create)",
                    required=False,
                    examples=["07:30", "14:00", "tomorrow at 3pm"],
                ),
                ParameterMetadata(
                    name="name",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Alarm name for easy reference",
                    required=False,
                    examples=["Morning Alarm", "Workout Time", "Meeting Reminder"],
                ),
                ParameterMetadata(
                    name="alarm_id",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Alarm ID for disable/enable/delete/snooze/status actions",
                    required=False,
                ),
                ParameterMetadata(
                    name="recurrence",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Recurrence pattern: none, daily, weekly, weekdays, weekends",
                    required=False,
                    examples=["none", "daily", "weekdays"],
                ),
                ParameterMetadata(
                    name="timezone",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Timezone for the alarm (e.g., 'America/New_York', 'UTC')",
                    required=False,
                    default="UTC",
                    examples=["America/New_York", "Europe/London", "Asia/Tokyo"],
                ),
                ParameterMetadata(
                    name="snooze_minutes",
                    type=int,
                    parameter_type=ParameterType.INTEGER,
                    description="Number of minutes to snooze the alarm",
                    required=False,
                    default=10,
                    examples=[5, 10, 15],
                ),
            ],
            capabilities=[
                AbilityCapability.CANCELLABLE,
                AbilityCapability.BACKGROUND,
            ],
            aliases=["set alarm", "wake me up", "schedule alarm"],
            examples=[
                {
                    "description": "Create a morning alarm at 7:30 AM",
                    "parameters": {
                        "action": "create",
                        "time": "07:30",
                        "name": "Morning Alarm",
                        "recurrence": "daily",
                    },
                },
                {
                    "description": "List all active alarms",
                    "parameters": {"action": "list"},
                },
                {
                    "description": "Snooze an alarm for 10 minutes",
                    "parameters": {"action": "snooze", "alarm_id": "alarm_1", "snooze_minutes": 10},
                },
            ],
        )

    async def initialize(self) -> None:
        """Initialize and start alarm monitoring."""
        await super().initialize()
        self._monitor_task = asyncio.create_task(self._monitor_alarms())
        logger.info("Alarm monitoring started")

    async def _execute(self, parameters: dict[str, Any], context: AbilityContext) -> AbilityResult:
        """Execute alarm action."""
        action = parameters.get("action", "").lower()

        if action == "create":
            return await self._create_alarm(parameters, context)
        elif action == "disable":
            return await self._disable_alarm(parameters, context)
        elif action == "enable":
            return await self._enable_alarm(parameters, context)
        elif action == "delete":
            return await self._delete_alarm(parameters, context)
        elif action == "snooze":
            return await self._snooze_alarm(parameters, context)
        elif action == "list":
            return await self._list_alarms(parameters, context)
        elif action == "status":
            return await self._get_alarm_status(parameters, context)
        else:
            return AbilityResult(
                success=False,
                error=f"Unknown action: {action}. Valid actions: create, disable, enable, delete, snooze, list, status",
            )

    async def _create_alarm(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Create a new alarm."""
        time_str = parameters.get("time")
        if not time_str:
            return AbilityResult(
                success=False,
                error="Time is required for creating an alarm",
            )

        # Parse time
        try:
            alarm_time = self._parse_time(time_str)
        except ValueError as e:
            return AbilityResult(
                success=False,
                error=f"Invalid time format: {str(e)}",
            )

        # Get timezone
        timezone = parameters.get("timezone", "UTC")
        try:
            tz = pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            return AbilityResult(
                success=False,
                error=f"Unknown timezone: {timezone}",
            )

        # Make alarm_time timezone-aware
        if alarm_time.tzinfo is None:
            alarm_time = tz.localize(alarm_time)

        # Get recurrence
        recurrence_str = parameters.get("recurrence", "none").lower()
        try:
            recurrence = RecurrenceType(recurrence_str)
        except ValueError:
            return AbilityResult(
                success=False,
                error=f"Invalid recurrence: {recurrence_str}",
            )

        # Generate alarm ID
        self._alarm_counter += 1
        alarm_id = f"alarm_{self._alarm_counter}"

        # Create alarm
        alarm = Alarm(
            alarm_id=alarm_id,
            name=parameters.get("name", f"Alarm {self._alarm_counter}"),
            alarm_time=alarm_time,
            user_id=context.user_id,
            timezone=timezone,
            recurrence=recurrence,
        )

        # Store alarm
        self._alarms[alarm_id] = alarm

        if context.user_id not in self._user_alarms:
            self._user_alarms[context.user_id] = []
        self._user_alarms[context.user_id].append(alarm_id)

        logger.info(
            "Alarm created",
            alarm_id=alarm_id,
            name=alarm.name,
            time=alarm_time.isoformat(),
            recurrence=recurrence.value,
            user_id=context.user_id,
        )

        return AbilityResult(
            success=True,
            data={
                "alarm_id": alarm_id,
                "name": alarm.name,
                "alarm_time": alarm_time.isoformat(),
                "next_trigger": alarm.next_trigger.isoformat() if alarm.next_trigger else None,
                "recurrence": recurrence.value,
                "timezone": timezone,
                "state": alarm.state.value,
                "message": f"Alarm '{alarm.name}' set for {alarm_time.strftime('%H:%M')}",
            },
        )

    def _parse_time(self, time_str: str) -> datetime:
        """Parse time string into datetime."""
        # Try HH:MM format first
        time_pattern = re.compile(r"^(\d{1,2}):(\d{2})$")
        match = time_pattern.match(time_str.strip())

        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))

            if hour > 23 or minute > 59:
                raise ValueError("Invalid time: hours must be 0-23, minutes must be 0-59")

            now = datetime.now()
            alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # If time has passed today, set for tomorrow
            if alarm_time <= now:
                alarm_time += timedelta(days=1)

            return alarm_time

        # Try natural language parsing
        try:
            parsed = date_parser.parse(time_str, fuzzy=True)
            return parsed
        except (ValueError, TypeError):
            raise ValueError(f"Could not parse time: {time_str}") from None

    async def _monitor_alarms(self) -> None:
        """Monitor alarms and trigger them at the right time."""
        try:
            while not self.is_cancelled():
                now = datetime.now(pytz.UTC)

                for alarm in list(self._alarms.values()):
                    if alarm.state != AlarmState.ACTIVE:
                        continue

                    if alarm.next_trigger is None:
                        continue

                    # Make both timezone-aware for comparison
                    next_trigger = alarm.next_trigger
                    if next_trigger.tzinfo is None:
                        tz = pytz.timezone(alarm.timezone)
                        next_trigger = tz.localize(next_trigger)

                    # Convert to UTC for comparison
                    next_trigger_utc = next_trigger.astimezone(pytz.UTC)

                    if now >= next_trigger_utc:
                        await self._trigger_alarm(alarm)

                # Check every second
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("Alarm monitoring stopped")
            raise

        except Exception as e:
            logger.error("Alarm monitoring error", error=str(e))

    async def _trigger_alarm(self, alarm: Alarm) -> None:
        """Trigger an alarm."""
        alarm.state = AlarmState.TRIGGERED
        alarm.last_triggered = datetime.now()
        alarm.snooze_until = None

        logger.info(
            "Alarm triggered",
            alarm_id=alarm.alarm_id,
            name=alarm.name,
        )

        # Call notification callback if set
        if alarm.callback:
            try:
                await alarm.callback(alarm)
            except Exception as e:
                logger.error(
                    "Alarm callback failed",
                    alarm_id=alarm.alarm_id,
                    error=str(e),
                )

        # Handle recurrence
        if alarm.recurrence != RecurrenceType.NONE:
            # Reset to active and calculate next trigger
            alarm.state = AlarmState.ACTIVE
            alarm.next_trigger = alarm._calculate_next_trigger()
            logger.info(
                "Recurring alarm rescheduled",
                alarm_id=alarm.alarm_id,
                next_trigger=alarm.next_trigger.isoformat() if alarm.next_trigger else None,
            )

    async def _disable_alarm(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Disable an alarm."""
        alarm_id = parameters.get("alarm_id")
        if not alarm_id:
            return AbilityResult(
                success=False,
                error="alarm_id is required for disabling an alarm",
            )

        alarm = self._alarms.get(alarm_id)
        if not alarm:
            return AbilityResult(
                success=False,
                error=f"Alarm not found: {alarm_id}",
            )

        if alarm.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to disable this alarm",
            )

        alarm.state = AlarmState.DISABLED

        logger.info("Alarm disabled", alarm_id=alarm_id)

        return AbilityResult(
            success=True,
            data={
                "alarm_id": alarm_id,
                "name": alarm.name,
                "state": alarm.state.value,
                "message": f"Alarm '{alarm.name}' disabled",
            },
        )

    async def _enable_alarm(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Enable a disabled alarm."""
        alarm_id = parameters.get("alarm_id")
        if not alarm_id:
            return AbilityResult(
                success=False,
                error="alarm_id is required for enabling an alarm",
            )

        alarm = self._alarms.get(alarm_id)
        if not alarm:
            return AbilityResult(
                success=False,
                error=f"Alarm not found: {alarm_id}",
            )

        if alarm.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to enable this alarm",
            )

        alarm.state = AlarmState.ACTIVE
        alarm.next_trigger = alarm._calculate_next_trigger()

        logger.info("Alarm enabled", alarm_id=alarm_id)

        return AbilityResult(
            success=True,
            data={
                "alarm_id": alarm_id,
                "name": alarm.name,
                "state": alarm.state.value,
                "next_trigger": alarm.next_trigger.isoformat() if alarm.next_trigger else None,
                "message": f"Alarm '{alarm.name}' enabled",
            },
        )

    async def _delete_alarm(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Delete an alarm."""
        alarm_id = parameters.get("alarm_id")
        if not alarm_id:
            return AbilityResult(
                success=False,
                error="alarm_id is required for deleting an alarm",
            )

        alarm = self._alarms.get(alarm_id)
        if not alarm:
            return AbilityResult(
                success=False,
                error=f"Alarm not found: {alarm_id}",
            )

        if alarm.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to delete this alarm",
            )

        # Remove alarm
        del self._alarms[alarm_id]
        if context.user_id in self._user_alarms:
            self._user_alarms[context.user_id].remove(alarm_id)

        logger.info("Alarm deleted", alarm_id=alarm_id)

        return AbilityResult(
            success=True,
            data={
                "alarm_id": alarm_id,
                "message": f"Alarm '{alarm.name}' deleted",
            },
        )

    async def _snooze_alarm(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Snooze an alarm."""
        alarm_id = parameters.get("alarm_id")
        snooze_minutes = parameters.get("snooze_minutes", 10)

        if not alarm_id:
            return AbilityResult(
                success=False,
                error="alarm_id is required for snoozing an alarm",
            )

        alarm = self._alarms.get(alarm_id)
        if not alarm:
            return AbilityResult(
                success=False,
                error=f"Alarm not found: {alarm_id}",
            )

        if alarm.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to snooze this alarm",
            )

        # Set snooze time
        tz = pytz.timezone(alarm.timezone)
        snooze_until = datetime.now(tz) + timedelta(minutes=snooze_minutes)
        alarm.snooze_until = snooze_until
        alarm.next_trigger = snooze_until
        alarm.state = AlarmState.ACTIVE

        logger.info(
            "Alarm snoozed",
            alarm_id=alarm_id,
            snooze_minutes=snooze_minutes,
        )

        return AbilityResult(
            success=True,
            data={
                "alarm_id": alarm_id,
                "name": alarm.name,
                "snooze_until": snooze_until.isoformat(),
                "snooze_minutes": snooze_minutes,
                "message": f"Alarm '{alarm.name}' snoozed for {snooze_minutes} minutes",
            },
        )

    async def _list_alarms(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """List all alarms for the user."""
        user_alarm_ids = self._user_alarms.get(context.user_id, [])

        alarms_data = []
        for alarm_id in user_alarm_ids:
            alarm = self._alarms.get(alarm_id)
            if alarm:
                alarms_data.append(
                    {
                        "alarm_id": alarm.alarm_id,
                        "name": alarm.name,
                        "alarm_time": alarm.alarm_time.strftime("%H:%M"),
                        "next_trigger": (
                            alarm.next_trigger.isoformat() if alarm.next_trigger else None
                        ),
                        "state": alarm.state.value,
                        "recurrence": alarm.recurrence.value,
                        "timezone": alarm.timezone,
                    }
                )

        logger.info(
            "Alarms listed",
            user_id=context.user_id,
            count=len(alarms_data),
        )

        return AbilityResult(
            success=True,
            data={
                "alarms": alarms_data,
                "count": len(alarms_data),
                "message": f"Found {len(alarms_data)} alarm(s)",
            },
        )

    async def _get_alarm_status(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Get status of a specific alarm."""
        alarm_id = parameters.get("alarm_id")
        if not alarm_id:
            return AbilityResult(
                success=False,
                error="alarm_id is required for getting alarm status",
            )

        alarm = self._alarms.get(alarm_id)
        if not alarm:
            return AbilityResult(
                success=False,
                error=f"Alarm not found: {alarm_id}",
            )

        if alarm.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to view this alarm",
            )

        data = {
            "alarm_id": alarm.alarm_id,
            "name": alarm.name,
            "alarm_time": alarm.alarm_time.isoformat(),
            "next_trigger": alarm.next_trigger.isoformat() if alarm.next_trigger else None,
            "state": alarm.state.value,
            "recurrence": alarm.recurrence.value,
            "timezone": alarm.timezone,
            "created_at": alarm.created_at.isoformat(),
        }

        if alarm.last_triggered:
            data["last_triggered"] = alarm.last_triggered.isoformat()

        if alarm.snooze_until:
            data["snooze_until"] = alarm.snooze_until.isoformat()

        return AbilityResult(
            success=True,
            data=data,
        )

    async def _cleanup(self) -> None:
        """Clean up alarm monitoring."""
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        self._alarms.clear()
        self._user_alarms.clear()

        logger.info("Alarm ability cleaned up")
