"""
Lifecycle management for abilities.

This module provides utilities for managing ability lifecycle,
including initialization, state management, and cleanup.
"""

import asyncio
from enum import Enum

import structlog

from bruno_abilities.base.ability_base import BaseAbility

logger = structlog.get_logger(__name__)


class LifecycleState(str, Enum):
    """Lifecycle states for abilities."""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class LifecycleManager:
    """
    Manages the lifecycle of abilities.

    Handles initialization, state transitions, and cleanup
    for abilities in a coordinated manner.
    """

    def __init__(self) -> None:
        """Initialize the lifecycle manager."""
        self._states: dict[str, LifecycleState] = {}
        self._errors: dict[str, str] = {}
        self._dependencies: dict[str, list[str]] = {}
        self._lock = asyncio.Lock()

        logger.info("Lifecycle manager initialized")

    async def initialize_ability(
        self, ability: BaseAbility, dependencies: list[str] | None = None
    ) -> bool:
        """
        Initialize an ability with dependency handling.

        Args:
            ability: Ability to initialize
            dependencies: List of dependency ability names

        Returns:
            True if initialization successful, False otherwise
        """
        name = ability.metadata.name

        async with self._lock:
            # Check current state
            current_state = self._states.get(name, LifecycleState.UNINITIALIZED)

            if current_state == LifecycleState.READY:
                logger.info("Ability already initialized", ability=name)
                return True

            if current_state == LifecycleState.INITIALIZING:
                logger.warning("Ability is already initializing", ability=name)
                return False

            # Set initializing state
            self._states[name] = LifecycleState.INITIALIZING

            if dependencies:
                self._dependencies[name] = dependencies

        try:
            # Initialize the ability
            await ability.initialize()

            async with self._lock:
                self._states[name] = LifecycleState.READY
                self._errors.pop(name, None)

            logger.info("Ability initialized successfully", ability=name)
            return True

        except Exception as e:
            error_msg = f"Initialization failed: {str(e)}"

            async with self._lock:
                self._states[name] = LifecycleState.ERROR
                self._errors[name] = error_msg

            logger.error("Failed to initialize ability", ability=name, error=error_msg)
            return False

    async def cleanup_ability(self, ability: BaseAbility) -> bool:
        """
        Cleanup an ability.

        Args:
            ability: Ability to cleanup

        Returns:
            True if cleanup successful, False otherwise
        """
        name = ability.metadata.name

        async with self._lock:
            current_state = self._states.get(name, LifecycleState.UNINITIALIZED)

            if current_state == LifecycleState.UNINITIALIZED:
                logger.info("Ability not initialized, skipping cleanup", ability=name)
                return True

            self._states[name] = LifecycleState.STOPPING

        try:
            await ability.cleanup()

            async with self._lock:
                self._states[name] = LifecycleState.STOPPED
                self._errors.pop(name, None)
                self._dependencies.pop(name, None)

            logger.info("Ability cleaned up successfully", ability=name)
            return True

        except Exception as e:
            error_msg = f"Cleanup failed: {str(e)}"

            async with self._lock:
                self._states[name] = LifecycleState.ERROR
                self._errors[name] = error_msg

            logger.error("Failed to cleanup ability", ability=name, error=error_msg)
            return False

    def get_state(self, ability_name: str) -> LifecycleState:
        """
        Get the current lifecycle state of an ability.

        Args:
            ability_name: Name of the ability

        Returns:
            Current lifecycle state
        """
        return self._states.get(ability_name, LifecycleState.UNINITIALIZED)

    def get_error(self, ability_name: str) -> str | None:
        """
        Get the last error message for an ability.

        Args:
            ability_name: Name of the ability

        Returns:
            Error message or None
        """
        return self._errors.get(ability_name)

    def is_ready(self, ability_name: str) -> bool:
        """
        Check if an ability is ready for use.

        Args:
            ability_name: Name of the ability

        Returns:
            True if ready, False otherwise
        """
        return self._states.get(ability_name) == LifecycleState.READY

    def get_dependencies(self, ability_name: str) -> list[str]:
        """
        Get dependencies for an ability.

        Args:
            ability_name: Name of the ability

        Returns:
            List of dependency names
        """
        return self._dependencies.get(ability_name, [])

    async def initialize_with_dependencies(
        self, abilities: dict[str, BaseAbility], dependencies: dict[str, list[str]]
    ) -> dict[str, bool]:
        """
        Initialize multiple abilities respecting dependencies.

        Args:
            abilities: Dictionary of ability instances
            dependencies: Dictionary of dependencies for each ability

        Returns:
            Dictionary of initialization results
        """
        results = {}
        initialized: set[str] = set()
        failed: set[str] = set()

        # Build dependency graph
        remaining = set(abilities.keys())

        while remaining:
            # Find abilities with satisfied dependencies
            ready = []

            for name in remaining:
                deps = dependencies.get(name, [])

                # Check if all dependencies are satisfied
                if all(dep in initialized for dep in deps):
                    ready.append(name)

            if not ready:
                # Circular dependency or missing dependencies
                logger.error("Cannot satisfy dependencies", remaining=list(remaining))
                for name in remaining:
                    results[name] = False
                    failed.add(name)
                break

            # Initialize ready abilities in parallel
            tasks = [
                self.initialize_ability(abilities[name], dependencies.get(name)) for name in ready
            ]

            init_results = await asyncio.gather(*tasks, return_exceptions=True)

            for name, result in zip(ready, init_results, strict=False):
                if isinstance(result, Exception):
                    results[name] = False
                    failed.add(name)
                    logger.error("Failed to initialize ability", ability=name, error=str(result))
                elif result:
                    results[name] = True
                    initialized.add(name)
                else:
                    results[name] = False
                    failed.add(name)

                remaining.discard(name)

        return results

    async def health_check(self, ability: BaseAbility) -> bool:
        """
        Perform health check on an ability.

        Args:
            ability: Ability to check

        Returns:
            True if healthy, False otherwise
        """
        name = ability.metadata.name

        # Check lifecycle state
        state = self.get_state(name)
        if state != LifecycleState.READY:
            logger.warning("Ability not in ready state", ability=name, state=state.value)
            return False

        # Perform ability health check
        try:
            is_healthy = await ability.health_check()

            if not is_healthy:
                logger.warning("Ability health check failed", ability=name)
                async with self._lock:
                    self._states[name] = LifecycleState.ERROR
                    self._errors[name] = "Health check failed"

            return is_healthy

        except Exception as e:
            logger.error("Health check error", ability=name, error=str(e))

            async with self._lock:
                self._states[name] = LifecycleState.ERROR
                self._errors[name] = f"Health check error: {str(e)}"

            return False
