"""
Base ability class that all abilities must extend.

This module provides the abstract base class for all Bruno abilities,
implementing bruno-core's AbilityInterface with common functionality.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import structlog
from pydantic import BaseModel, ConfigDict
from pydantic import ValidationError as PydanticValidationError

from bruno_abilities.base.metadata import AbilityMetadata

logger = structlog.get_logger(__name__)


class AbilityResult(BaseModel):
    """Result returned from ability execution."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool
    data: Any | None = None
    error: str | None = None
    metadata: dict[str, Any] = {}
    timestamp: datetime = datetime.now()


class AbilityContext(BaseModel):
    """Context information for ability execution."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: str
    session_id: str | None = None
    conversation_id: str | None = None
    metadata: dict[str, Any] = {}


class BaseAbility(ABC):
    """
    Abstract base class for all Bruno abilities.

    This class extends bruno-core's AbilityInterface and provides common
    functionality including parameter validation, error handling, logging,
    state management, and cancellation support.

    Attributes:
        metadata: Ability metadata describing capabilities and parameters
        _is_initialized: Whether the ability has been initialized
        _state: Current state dictionary for the ability
        _cancellation_token: Token for cancelling long-running operations
    """

    def __init__(self) -> None:
        """Initialize the base ability."""
        self._is_initialized = False
        self._state: dict[str, Any] = {}
        self._cancellation_token = asyncio.Event()
        self._logger = structlog.get_logger(self.__class__.__name__)

    @property
    @abstractmethod
    def metadata(self) -> AbilityMetadata:
        """
        Return metadata describing this ability.

        Returns:
            AbilityMetadata instance with ability information
        """
        pass

    async def initialize(self) -> None:
        """
        Initialize the ability.

        Called once before the ability is used. Override to perform
        setup operations like loading resources or establishing connections.
        """
        if self._is_initialized:
            self._logger.warning("Ability already initialized")
            return

        self._logger.info("Initializing ability", ability=self.metadata.name)
        await self._initialize()
        self._is_initialized = True
        self._logger.info("Ability initialized successfully", ability=self.metadata.name)

    async def _initialize(self) -> None:
        """
        Internal initialization hook for subclasses.

        Override this method to perform ability-specific initialization.
        """
        pass

    async def cleanup(self) -> None:
        """
        Clean up ability resources.

        Called when the ability is no longer needed. Override to perform
        cleanup operations like releasing resources or closing connections.
        """
        if not self._is_initialized:
            self._logger.warning("Ability not initialized, skipping cleanup")
            return

        self._logger.info("Cleaning up ability", ability=self.metadata.name)
        await self._cleanup()
        self._is_initialized = False
        self._state.clear()
        self._logger.info("Ability cleaned up successfully", ability=self.metadata.name)

    async def _cleanup(self) -> None:
        """
        Internal cleanup hook for subclasses.

        Override this method to perform ability-specific cleanup.
        """
        pass

    async def execute(self, parameters: dict[str, Any], context: AbilityContext) -> AbilityResult:
        """
        Execute the ability with the given parameters and context.

        This method handles validation, logging, error handling, and
        delegates to the _execute method for actual implementation.

        Args:
            parameters: Dictionary of parameters for the ability
            context: Execution context with user and session information

        Returns:
            AbilityResult with execution outcome
        """
        if not self._is_initialized:
            await self.initialize()

        self._logger.info(
            "Executing ability",
            ability=self.metadata.name,
            user_id=context.user_id,
            parameters=parameters,
        )

        start_time = datetime.now()

        try:
            # Validate parameters
            validated_params = await self._validate_parameters(parameters)

            # Check if operation should be cancelled
            if self._cancellation_token.is_set():
                return AbilityResult(success=False, error="Operation was cancelled")

            # Execute the ability
            result = await self._execute(validated_params, context)

            execution_time = (datetime.now() - start_time).total_seconds()
            self._logger.info(
                "Ability executed successfully",
                ability=self.metadata.name,
                execution_time=execution_time,
            )

            return result

        except (ValueError, TypeError) as e:
            error_msg = f"Parameter validation failed: {str(e)}"
            self._logger.error(
                "Ability validation error", ability=self.metadata.name, error=error_msg
            )
            return AbilityResult(success=False, error=error_msg)

        except PydanticValidationError as e:
            error_msg = f"Parameter validation failed: {str(e)}"
            self._logger.error(
                "Ability validation error", ability=self.metadata.name, error=error_msg
            )
            return AbilityResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Ability execution failed: {str(e)}"
            self._logger.exception(
                "Ability execution error", ability=self.metadata.name, error=error_msg
            )
            return AbilityResult(success=False, error=error_msg)

    @abstractmethod
    async def _execute(self, parameters: dict[str, Any], context: AbilityContext) -> AbilityResult:
        """
        Internal execution method to be implemented by subclasses.

        Args:
            parameters: Validated parameters for the ability
            context: Execution context

        Returns:
            AbilityResult with execution outcome
        """
        pass

    async def _validate_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """
        Validate parameters against ability metadata.

        Args:
            parameters: Raw parameters to validate

        Returns:
            Validated parue dictionary

        Raises:
            ValidationError: If parameters are invalid
        """
        validated = {}

        # Check required parameters
        for param in self.metadata.parameters:
            param_name = param.name

            if param.required and param_name not in parameters:
                raise ValueError(f"Required parameter '{param_name}' is missing")

            if param_name in parameters:
                value = parameters[param_name]

                # Perform basic type validation if specified
                if param.type and not isinstance(value, param.type):
                    try:
                        # Attempt type coercion
                        value = param.type(value)
                    except (ValueError, TypeError):
                        raise TypeError(
                            f"Parameter '{param_name}' must be of type {param.type.__name__}"
                        ) from None

                validated[param_name] = value
            elif param.default is not None:
                validated[param_name] = param.default

        return validated

    async def cancel(self) -> None:
        """
        Cancel any ongoing operations.

        Sets the cancellation token to signal that operations should stop.
        """
        self._logger.info("Cancelling ability operations", ability=self.metadata.name)
        self._cancellation_token.set()

    async def reset_cancellation(self) -> None:
        """Reset the cancellation token for new operations."""
        self._cancellation_token.clear()

    def is_cancelled(self) -> bool:
        """
        Check if the ability has been cancelled.

        Returns:
            True if cancelled, False otherwise
        """
        return self._cancellation_token.is_set()

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the ability's state.

        Args:
            key: State key to retrieve
            default: Default value if key doesn't exist

        Returns:
            State value or default
        """
        return self._state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """
        Set a value in the ability's state.

        Args:
            key: State key to set
            value: Value to store
        """
        self._state[key] = value

    def clear_state(self) -> None:
        """Clear all state data."""
        self._state.clear()

    async def health_check(self) -> bool:
        """
        Perform a health check on the ability.

        Returns:
            True if healthy, False otherwise
        """
        try:
            return self._is_initialized and await self._health_check()
        except Exception as e:
            self._logger.error("Health check failed", error=str(e))
            return False

    async def _health_check(self) -> bool:
        """
        Internal health check hook for subclasses.

        Override this to implement ability-specific health checks.

        Returns:
            True if healthy, False otherwise
        """
        return True
