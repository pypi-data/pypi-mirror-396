"""
Ability registry for managing and discovering abilities.

This module provides the central registry for all abilities,
handling registration, lookup, and lifecycle management.
"""

import asyncio
from collections import defaultdict

import structlog

from bruno_abilities.base.ability_base import BaseAbility
from bruno_abilities.base.metadata import AbilityMetadata

logger = structlog.get_logger(__name__)


class AbilityRegistry:
    """
    Central registry for managing abilities.

    The registry maintains a collection of registered abilities,
    handles their lifecycle, and provides lookup and discovery functionality.
    """

    def __init__(self) -> None:
        """Initialize the ability registry."""
        self._abilities: dict[str, BaseAbility] = {}
        self._aliases: dict[str, str] = {}  # alias -> ability_name
        self._categories: dict[str, set[str]] = defaultdict(set)  # category -> ability_names
        self._tags: dict[str, set[str]] = defaultdict(set)  # tag -> ability_names
        self._enabled: dict[str, bool] = {}  # ability_name -> enabled
        self._dependencies: dict[str, list[str]] = {}  # ability_name -> dependencies
        self._lock = asyncio.Lock()

        logger.info("Ability registry initialized")

    async def register(
        self, ability: BaseAbility, enabled: bool = True, dependencies: list[str] | None = None
    ) -> None:
        """
        Register an ability with the registry.

        Args:
            ability: Ability instance to register
            enabled: Whether ability should be enabled by default
            dependencies: List of ability names this ability depends on

        Raises:
            ValueError: If ability name is already registered
        """
        async with self._lock:
            metadata = ability.metadata
            name = metadata.name

            if name in self._abilities:
                logger.warning("Ability already registered", ability=name)
                raise ValueError(f"Ability '{name}' is already registered")

            # Validate interface
            if not isinstance(ability, BaseAbility):
                raise TypeError(f"Ability must extend BaseAbility, got {type(ability)}")

            # Register the ability
            self._abilities[name] = ability
            self._enabled[name] = enabled

            # Register aliases
            for alias in metadata.aliases:
                self._aliases[alias.lower()] = name

            # Register category
            if metadata.category:
                self._categories[metadata.category].add(name)

            # Register tags
            for tag in metadata.tags:
                self._tags[tag.lower()].add(name)

            # Register dependencies
            if dependencies:
                self._dependencies[name] = dependencies

            logger.info(
                "Ability registered", ability=name, category=metadata.category, enabled=enabled
            )

    async def unregister(self, name: str) -> None:
        """
        Unregister an ability from the registry.

        Args:
            name: Name of ability to unregister

        Raises:
            KeyError: If ability is not registered
        """
        async with self._lock:
            if name not in self._abilities:
                raise KeyError(f"Ability '{name}' is not registered")

            ability = self._abilities[name]
            metadata = ability.metadata

            # Cleanup ability
            await ability.cleanup()

            # Remove from registry
            del self._abilities[name]
            del self._enabled[name]

            # Remove aliases
            for alias in metadata.aliases:
                self._aliases.pop(alias.lower(), None)

            # Remove from category
            if metadata.category:
                self._categories[metadata.category].discard(name)

            # Remove from tags
            for tag in metadata.tags:
                self._tags[tag.lower()].discard(name)

            # Remove dependencies
            self._dependencies.pop(name, None)

            logger.info("Ability unregistered", ability=name)

    def get(self, name_or_alias: str) -> BaseAbility | None:
        """
        Get an ability by name or alias.

        Args:
            name_or_alias: Ability name or alias

        Returns:
            Ability instance or None if not found
        """
        # Try direct lookup
        if name_or_alias in self._abilities:
            return self._abilities[name_or_alias]

        # Try alias lookup
        actual_name = self._aliases.get(name_or_alias.lower())
        if actual_name:
            return self._abilities.get(actual_name)

        return None

    def is_enabled(self, name: str) -> bool:
        """
        Check if an ability is enabled.

        Args:
            name: Ability name

        Returns:
            True if enabled, False otherwise
        """
        return self._enabled.get(name, False)

    async def enable(self, name: str) -> None:
        """
        Enable an ability.

        Args:
            name: Ability name

        Raises:
            KeyError: If ability is not registered
        """
        async with self._lock:
            if name not in self._abilities:
                raise KeyError(f"Ability '{name}' is not registered")

            self._enabled[name] = True
            logger.info("Ability enabled", ability=name)

    async def disable(self, name: str) -> None:
        """
        Disable an ability.

        Args:
            name: Ability name

        Raises:
            KeyError: If ability is not registered
        """
        async with self._lock:
            if name not in self._abilities:
                raise KeyError(f"Ability '{name}' is not registered")

            self._enabled[name] = False
            logger.info("Ability disabled", ability=name)

    def list_abilities(
        self, category: str | None = None, tag: str | None = None, enabled_only: bool = False
    ) -> list[str]:
        """
        List abilities matching criteria.

        Args:
            category: Filter by category
            tag: Filter by tag
            enabled_only: Only include enabled abilities

        Returns:
            List of ability names
        """
        abilities = set(self._abilities.keys())

        # Filter by category
        if category:
            abilities &= self._categories.get(category, set())

        # Filter by tag
        if tag:
            abilities &= self._tags.get(tag.lower(), set())

        # Filter by enabled status
        if enabled_only:
            abilities = {name for name in abilities if self._enabled.get(name, False)}

        return sorted(abilities)

    def search(self, query: str, enabled_only: bool = False) -> list[BaseAbility]:
        """
        Search for abilities matching a query.

        Args:
            query: Search query
            enabled_only: Only search enabled abilities

        Returns:
            List of matching abilities
        """
        results = []

        for name, ability in self._abilities.items():
            # Skip disabled if filtering
            if enabled_only and not self._enabled.get(name, False):
                continue

            # Check if metadata matches query
            if ability.metadata.matches_query(query):
                results.append(ability)

        return results

    def get_by_category(self, category: str) -> list[BaseAbility]:
        """
        Get all abilities in a category.

        Args:
            category: Category name

        Returns:
            List of abilities
        """
        ability_names = self._categories.get(category, set())
        return [self._abilities[name] for name in ability_names if name in self._abilities]

    def get_by_tag(self, tag: str) -> list[BaseAbility]:
        """
        Get all abilities with a tag.

        Args:
            tag: Tag name

        Returns:
            List of abilities
        """
        ability_names = self._tags.get(tag.lower(), set())
        return [self._abilities[name] for name in ability_names if name in self._abilities]

    def get_dependencies(self, name: str) -> list[str]:
        """
        Get dependencies for an ability.

        Args:
            name: Ability name

        Returns:
            List of dependency names
        """
        return self._dependencies.get(name, [])

    def check_dependencies(self, name: str) -> bool:
        """
        Check if all dependencies for an ability are satisfied.

        Args:
            name: Ability name

        Returns:
            True if all dependencies are registered and enabled
        """
        dependencies = self._dependencies.get(name, [])

        for dep in dependencies:
            if dep not in self._abilities:
                logger.warning("Missing dependency", ability=name, dependency=dep)
                return False

            if not self._enabled.get(dep, False):
                logger.warning("Dependency not enabled", ability=name, dependency=dep)
                return False

        return True

    async def initialize_all(self) -> None:
        """Initialize all registered abilities."""
        for name, ability in self._abilities.items():
            if self._enabled.get(name, False):
                try:
                    await ability.initialize()
                except Exception as e:
                    logger.error("Failed to initialize ability", ability=name, error=str(e))

    async def cleanup_all(self) -> None:
        """Cleanup all registered abilities."""
        for name, ability in self._abilities.items():
            try:
                await ability.cleanup()
            except Exception as e:
                logger.error("Failed to cleanup ability", ability=name, error=str(e))

    def get_all_metadata(self) -> list[AbilityMetadata]:
        """
        Get metadata for all registered abilities.

        Returns:
            List of ability metadata
        """
        return [ability.metadata for ability in self._abilities.values()]


# Global registry instance
_global_registry: AbilityRegistry | None = None


def get_registry() -> AbilityRegistry:
    """
    Get the global ability registry instance.

    Returns:
        Global registry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = AbilityRegistry()
    return _global_registry
