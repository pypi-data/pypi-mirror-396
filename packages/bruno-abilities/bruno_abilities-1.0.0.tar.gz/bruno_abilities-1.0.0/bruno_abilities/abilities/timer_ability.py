"""
Timer Ability - Countdown timers with pause/resume functionality.

This ability allows users to create and manage multiple countdown timers
with support for pausing, resuming, extending, and notification callbacks.
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import structlog

from bruno_abilities.base.ability_base import AbilityContext, AbilityResult, BaseAbility
from bruno_abilities.base.metadata import (
    AbilityCapability,
    AbilityMetadata,
    ParameterMetadata,
    ParameterType,
)

logger = structlog.get_logger(__name__)


class TimerState(str, Enum):
    """Timer states."""

    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Timer:
    """Represents a countdown timer."""

    timer_id: str
    name: str
    duration: timedelta
    user_id: str
    state: TimerState = TimerState.RUNNING
    remaining: timedelta = field(default_factory=lambda: timedelta(0))
    started_at: datetime = field(default_factory=datetime.now)
    paused_at: datetime | None = None
    completed_at: datetime | None = None
    callback: Callable | None = None
    task: asyncio.Task | None = None

    def __post_init__(self) -> None:
        """Initialize remaining time if not set."""
        if self.remaining == timedelta(0):
            self.remaining = self.duration


class TimerAbility(BaseAbility):
    """
    Timer ability for creating and managing countdown timers.

    Features:
    - Multiple concurrent timers per user
    - Named timers for easy reference
    - Pause and resume functionality
    - Timer extension while running
    - Notification callbacks on completion
    - Timer listing and status checking
    """

    def __init__(self) -> None:
        """Initialize the timer ability."""
        super().__init__()
        self._timers: dict[str, Timer] = {}  # timer_id -> Timer
        self._user_timers: dict[str, list[str]] = {}  # user_id -> [timer_ids]
        self._timer_counter = 0

    @property
    def metadata(self) -> AbilityMetadata:
        """Return timer ability metadata."""
        return AbilityMetadata(
            name="timer",
            display_name="Timer",
            description="Create and manage countdown timers with pause/resume support",
            category="time_management",
            version="1.0.0",
            tags=["timer", "countdown", "time", "alarm"],
            parameters=[
                ParameterMetadata(
                    name="action",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Action to perform: create, pause, resume, cancel, extend, list, status",
                    required=True,
                    examples=["create", "pause", "resume", "cancel", "extend", "list", "status"],
                ),
                ParameterMetadata(
                    name="duration",
                    type=int,
                    parameter_type=ParameterType.INTEGER,
                    description="Timer duration in seconds (required for create action)",
                    required=False,
                    examples=[60, 300, 3600],
                ),
                ParameterMetadata(
                    name="name",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Timer name for easy reference",
                    required=False,
                    examples=["Coffee Timer", "Workout", "Meeting Reminder"],
                ),
                ParameterMetadata(
                    name="timer_id",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Timer ID for pause/resume/cancel/status actions",
                    required=False,
                ),
                ParameterMetadata(
                    name="extend_seconds",
                    type=int,
                    parameter_type=ParameterType.INTEGER,
                    description="Number of seconds to extend the timer (for extend action)",
                    required=False,
                    examples=[60, 300],
                ),
            ],
            capabilities=[
                AbilityCapability.CANCELLABLE,
                AbilityCapability.BACKGROUND,
            ],
            aliases=["countdown", "set timer", "start timer"],
            examples=[
                {
                    "description": "Create a 5-minute timer",
                    "parameters": {"action": "create", "duration": 300, "name": "Coffee Break"},
                },
                {
                    "description": "List all active timers",
                    "parameters": {"action": "list"},
                },
                {
                    "description": "Pause a timer",
                    "parameters": {"action": "pause", "timer_id": "timer_1"},
                },
            ],
        )

    async def _execute(self, parameters: dict[str, Any], context: AbilityContext) -> AbilityResult:
        """Execute timer action."""
        action = parameters.get("action", "").lower()

        if action == "create":
            return await self._create_timer(parameters, context)
        elif action == "pause":
            return await self._pause_timer(parameters, context)
        elif action == "resume":
            return await self._resume_timer(parameters, context)
        elif action == "cancel":
            return await self._cancel_timer(parameters, context)
        elif action == "extend":
            return await self._extend_timer(parameters, context)
        elif action == "list":
            return await self._list_timers(parameters, context)
        elif action == "status":
            return await self._get_timer_status(parameters, context)
        else:
            return AbilityResult(
                success=False,
                error=f"Unknown action: {action}. Valid actions: create, pause, resume, cancel, extend, list, status",
            )

    async def _create_timer(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Create a new timer."""
        duration_seconds = parameters.get("duration")
        if duration_seconds is None:
            return AbilityResult(
                success=False,
                error="Duration is required for creating a timer",
            )

        if duration_seconds <= 0:
            return AbilityResult(
                success=False,
                error="Duration must be greater than 0",
            )

        # Generate timer ID
        self._timer_counter += 1
        timer_id = f"timer_{self._timer_counter}"

        # Create timer
        timer = Timer(
            timer_id=timer_id,
            name=parameters.get("name", f"Timer {self._timer_counter}"),
            duration=timedelta(seconds=duration_seconds),
            user_id=context.user_id,
        )

        # Store timer
        self._timers[timer_id] = timer

        if context.user_id not in self._user_timers:
            self._user_timers[context.user_id] = []
        self._user_timers[context.user_id].append(timer_id)

        # Start timer task
        timer.task = asyncio.create_task(self._run_timer(timer))

        logger.info(
            "Timer created",
            timer_id=timer_id,
            name=timer.name,
            duration=duration_seconds,
            user_id=context.user_id,
        )

        return AbilityResult(
            success=True,
            data={
                "timer_id": timer_id,
                "name": timer.name,
                "duration_seconds": duration_seconds,
                "state": timer.state.value,
                "message": f"Timer '{timer.name}' created for {duration_seconds} seconds",
            },
        )

    async def _run_timer(self, timer: Timer) -> None:
        """Run a timer to completion."""
        try:
            end_time = datetime.now() + timer.remaining

            while datetime.now() < end_time:
                if self.is_cancelled():
                    timer.state = TimerState.CANCELLED
                    logger.info("Timer cancelled", timer_id=timer.timer_id)
                    return

                # Check if paused
                if timer.state == TimerState.PAUSED:
                    await asyncio.sleep(0.1)
                    continue

                # Update remaining time
                timer.remaining = end_time - datetime.now()

                # Small sleep to prevent tight loop
                await asyncio.sleep(0.1)

            # Timer completed
            timer.state = TimerState.COMPLETED
            timer.completed_at = datetime.now()
            timer.remaining = timedelta(0)

            logger.info(
                "Timer completed",
                timer_id=timer.timer_id,
                name=timer.name,
            )

            # Call notification callback if set
            if timer.callback:
                try:
                    await timer.callback(timer)
                except Exception as e:
                    logger.error(
                        "Timer callback failed",
                        timer_id=timer.timer_id,
                        error=str(e),
                    )

        except asyncio.CancelledError:
            timer.state = TimerState.CANCELLED
            logger.info("Timer task cancelled", timer_id=timer.timer_id)
            raise

        except Exception as e:
            logger.error(
                "Timer error",
                timer_id=timer.timer_id,
                error=str(e),
            )

    async def _pause_timer(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Pause a running timer."""
        timer_id = parameters.get("timer_id")
        if not timer_id:
            return AbilityResult(
                success=False,
                error="timer_id is required for pausing a timer",
            )

        timer = self._timers.get(timer_id)
        if not timer:
            return AbilityResult(
                success=False,
                error=f"Timer not found: {timer_id}",
            )

        if timer.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to pause this timer",
            )

        if timer.state != TimerState.RUNNING:
            return AbilityResult(
                success=False,
                error=f"Timer is not running (current state: {timer.state.value})",
            )

        timer.state = TimerState.PAUSED
        timer.paused_at = datetime.now()

        logger.info("Timer paused", timer_id=timer_id)

        return AbilityResult(
            success=True,
            data={
                "timer_id": timer_id,
                "name": timer.name,
                "state": timer.state.value,
                "remaining_seconds": int(timer.remaining.total_seconds()),
                "message": f"Timer '{timer.name}' paused",
            },
        )

    async def _resume_timer(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Resume a paused timer."""
        timer_id = parameters.get("timer_id")
        if not timer_id:
            return AbilityResult(
                success=False,
                error="timer_id is required for resuming a timer",
            )

        timer = self._timers.get(timer_id)
        if not timer:
            return AbilityResult(
                success=False,
                error=f"Timer not found: {timer_id}",
            )

        if timer.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to resume this timer",
            )

        if timer.state != TimerState.PAUSED:
            return AbilityResult(
                success=False,
                error=f"Timer is not paused (current state: {timer.state.value})",
            )

        timer.state = TimerState.RUNNING
        timer.paused_at = None

        logger.info("Timer resumed", timer_id=timer_id)

        return AbilityResult(
            success=True,
            data={
                "timer_id": timer_id,
                "name": timer.name,
                "state": timer.state.value,
                "remaining_seconds": int(timer.remaining.total_seconds()),
                "message": f"Timer '{timer.name}' resumed",
            },
        )

    async def _cancel_timer(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Cancel a timer."""
        timer_id = parameters.get("timer_id")
        if not timer_id:
            return AbilityResult(
                success=False,
                error="timer_id is required for cancelling a timer",
            )

        timer = self._timers.get(timer_id)
        if not timer:
            return AbilityResult(
                success=False,
                error=f"Timer not found: {timer_id}",
            )

        if timer.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to cancel this timer",
            )

        # Cancel the timer task
        if timer.task and not timer.task.done():
            timer.task.cancel()

        timer.state = TimerState.CANCELLED

        logger.info("Timer cancelled", timer_id=timer_id)

        return AbilityResult(
            success=True,
            data={
                "timer_id": timer_id,
                "name": timer.name,
                "state": timer.state.value,
                "message": f"Timer '{timer.name}' cancelled",
            },
        )

    async def _extend_timer(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Extend a running timer."""
        timer_id = parameters.get("timer_id")
        extend_seconds = parameters.get("extend_seconds")

        if not timer_id:
            return AbilityResult(
                success=False,
                error="timer_id is required for extending a timer",
            )

        if not extend_seconds:
            return AbilityResult(
                success=False,
                error="extend_seconds is required for extending a timer",
            )

        timer = self._timers.get(timer_id)
        if not timer:
            return AbilityResult(
                success=False,
                error=f"Timer not found: {timer_id}",
            )

        if timer.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to extend this timer",
            )

        if timer.state not in [TimerState.RUNNING, TimerState.PAUSED]:
            return AbilityResult(
                success=False,
                error=f"Timer cannot be extended (current state: {timer.state.value})",
            )

        # Extend the timer
        timer.remaining += timedelta(seconds=extend_seconds)
        timer.duration += timedelta(seconds=extend_seconds)

        logger.info(
            "Timer extended",
            timer_id=timer_id,
            extend_seconds=extend_seconds,
        )

        return AbilityResult(
            success=True,
            data={
                "timer_id": timer_id,
                "name": timer.name,
                "state": timer.state.value,
                "remaining_seconds": int(timer.remaining.total_seconds()),
                "message": f"Timer '{timer.name}' extended by {extend_seconds} seconds",
            },
        )

    async def _list_timers(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """List all timers for the user."""
        user_timer_ids = self._user_timers.get(context.user_id, [])

        timers_data = []
        for timer_id in user_timer_ids:
            timer = self._timers.get(timer_id)
            if timer and timer.state in [TimerState.RUNNING, TimerState.PAUSED]:
                timers_data.append(
                    {
                        "timer_id": timer.timer_id,
                        "name": timer.name,
                        "state": timer.state.value,
                        "duration_seconds": int(timer.duration.total_seconds()),
                        "remaining_seconds": int(timer.remaining.total_seconds()),
                        "started_at": timer.started_at.isoformat(),
                    }
                )

        logger.info(
            "Timers listed",
            user_id=context.user_id,
            count=len(timers_data),
        )

        return AbilityResult(
            success=True,
            data={
                "timers": timers_data,
                "count": len(timers_data),
                "message": f"Found {len(timers_data)} active timer(s)",
            },
        )

    async def _get_timer_status(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Get status of a specific timer."""
        timer_id = parameters.get("timer_id")
        if not timer_id:
            return AbilityResult(
                success=False,
                error="timer_id is required for getting timer status",
            )

        timer = self._timers.get(timer_id)
        if not timer:
            return AbilityResult(
                success=False,
                error=f"Timer not found: {timer_id}",
            )

        if timer.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to view this timer",
            )

        data = {
            "timer_id": timer.timer_id,
            "name": timer.name,
            "state": timer.state.value,
            "duration_seconds": int(timer.duration.total_seconds()),
            "remaining_seconds": int(timer.remaining.total_seconds()),
            "started_at": timer.started_at.isoformat(),
        }

        if timer.paused_at:
            data["paused_at"] = timer.paused_at.isoformat()

        if timer.completed_at:
            data["completed_at"] = timer.completed_at.isoformat()

        return AbilityResult(
            success=True,
            data=data,
        )

    async def _cleanup(self) -> None:
        """Clean up all timer tasks."""
        for timer in self._timers.values():
            if timer.task and not timer.task.done():
                timer.task.cancel()

        # Wait for all tasks to complete
        tasks = [t.task for t in self._timers.values() if t.task and not t.task.done()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self._timers.clear()
        self._user_timers.clear()

        logger.info("Timer ability cleaned up")
