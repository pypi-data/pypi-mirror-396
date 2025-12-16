"""
Metadata system for describing ability capabilities and parameters.

This module provides classes for defining rich metadata about abilities
that feeds into the LLM's function calling mechanism.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ParameterType(str, Enum):
    """Enumeration of supported parameter types."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    DATETIME = "datetime"
    DURATION = "duration"


class ParameterMetadata(BaseModel):
    """Metadata describing an ability parameter."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(..., description="Parameter name")
    type: Optional[type] = Field(default=None, description="Python type for validation")
    parameter_type: ParameterType = Field(
        default=ParameterType.STRING, description="Type category for LLM understanding"
    )
    description: str = Field(..., description="Human-readable description")
    required: bool = Field(default=True, description="Whether parameter is required")
    default: Optional[Any] = Field(default=None, description="Default value if not provided")
    examples: list[Any] = Field(default_factory=list, description="Example values")
    constraints: dict[str, Any] = Field(
        default_factory=dict, description="Validation constraints (min, max, pattern, etc.)"
    )


class AbilityCapability(str, Enum):
    """Capability flags for abilities."""

    STREAMING = "streaming"
    CANCELLABLE = "cancellable"
    PROGRESS_REPORTING = "progress_reporting"
    BACKGROUND = "background"
    PERSISTENT = "persistent"


class PermissionLevel(str, Enum):
    """Permission levels for abilities."""

    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class AbilityMetadata(BaseModel):
    """
    Rich metadata describing an ability's capabilities.

    This metadata is used by the LLM to understand when and how to
    invoke the ability, and what parameters it requires.
    """

    name: str = Field(..., description="Unique ability name")
    display_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="What the ability does")
    version: str = Field(default="1.0.0", description="Ability version (semver)")

    category: str = Field(..., description="Ability category")
    tags: list[str] = Field(default_factory=list, description="Searchable tags")

    parameters: list[ParameterMetadata] = Field(
        default_factory=list, description="Parameter definitions"
    )

    examples: list[dict[str, Any]] = Field(
        default_factory=list, description="Example invocations with parameters"
    )

    capabilities: list[AbilityCapability] = Field(
        default_factory=list, description="Supported capabilities"
    )

    dependencies: list[str] = Field(
        default_factory=list, description="Required packages or services"
    )

    permission_level: PermissionLevel = Field(
        default=PermissionLevel.NONE, description="Required permission level"
    )

    aliases: list[str] = Field(
        default_factory=list, description="Alternative names for natural language"
    )

    returns: dict[str, Any] = Field(
        default_factory=dict, description="Description of return value structure"
    )

    error_codes: dict[str, str] = Field(
        default_factory=dict, description="Possible error codes and their meanings"
    )

    model_config = ConfigDict(use_enum_values=True)

    def to_function_schema(self) -> dict[str, Any]:
        """
        Convert metadata to OpenAI function calling schema.

        Returns:
            Function schema dictionary compatible with OpenAI API
        """
        properties = {}
        required = []

        for param in self.parameters:
            param_schema = {
                "type": param.parameter_type.value,
                "description": param.description,
            }

            if param.examples:
                param_schema["examples"] = param.examples

            if param.constraints:
                param_schema.update(param.constraints)

            properties[param.name] = param_schema

            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def has_capability(self, capability: AbilityCapability) -> bool:
        """
        Check if the ability has a specific capability.

        Args:
            capability: Capability to check

        Returns:
            True if capability is supported
        """
        return capability in self.capabilities

    def matches_query(self, query: str) -> bool:
        """
        Check if the ability matches a search query.

        Args:
            query: Search query string

        Returns:
            True if ability matches the query
        """
        query_lower = query.lower()

        # Check name and aliases
        if query_lower in self.name.lower():
            return True

        for alias in self.aliases:
            if query_lower in alias.lower():
                return True

        # Check description and tags
        if query_lower in self.description.lower():
            return True

        for tag in self.tags:
            if query_lower in tag.lower():
                return True

        return False
