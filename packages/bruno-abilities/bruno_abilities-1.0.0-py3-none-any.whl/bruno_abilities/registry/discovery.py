"""
Ability discovery through Python entry points.

This module provides automatic discovery of abilities registered
through Python package entry points.
"""

import importlib
import importlib.metadata

import structlog

from bruno_abilities.base.ability_base import BaseAbility

logger = structlog.get_logger(__name__)


class AbilityDiscovery:
    """
    Discovers abilities through Python entry points.

    Abilities can register themselves by declaring entry points
    in their package configuration (setup.py or pyproject.toml).
    """

    ENTRY_POINT_GROUP = "bruno.abilities"

    @staticmethod
    def discover_abilities() -> dict[str, type[BaseAbility]]:
        """
        Discover all abilities registered through entry points.

        Returns:
            Dictionary mapping ability names to ability classes
        """
        discovered = {}

        try:
            # Get all entry points for bruno.abilities
            entry_points = importlib.metadata.entry_points()

            # Handle different Python versions' entry_points return type
            if hasattr(entry_points, "select"):
                # Python 3.10+
                ability_eps = entry_points.select(group=AbilityDiscovery.ENTRY_POINT_GROUP)
            else:
                # Python 3.9
                ability_eps = entry_points.get(AbilityDiscovery.ENTRY_POINT_GROUP, [])

            for ep in ability_eps:
                try:
                    # Load the ability class
                    ability_class = ep.load()

                    # Validate it's a BaseAbility subclass
                    if not issubclass(ability_class, BaseAbility):
                        logger.warning(
                            "Entry point does not reference a BaseAbility subclass",
                            entry_point=ep.name,
                            class_name=ability_class.__name__,
                        )
                        continue

                    discovered[ep.name] = ability_class
                    logger.info(
                        "Discovered ability", name=ep.name, class_name=ability_class.__name__
                    )

                except Exception as e:
                    logger.error(
                        "Failed to load ability from entry point", entry_point=ep.name, error=str(e)
                    )

        except Exception as e:
            logger.error("Failed to discover abilities", error=str(e))

        return discovered

    @staticmethod
    def load_ability(module_path: str, class_name: str) -> type[BaseAbility]:
        """
        Load an ability class from a module path.

        Args:
            module_path: Python module path (e.g., 'bruno_abilities.abilities.timer_ability')
            class_name: Name of the ability class

        Returns:
            Ability class

        Raises:
            ImportError: If module cannot be imported
            AttributeError: If class doesn't exist in module
            TypeError: If class is not a BaseAbility subclass
        """
        try:
            module = importlib.import_module(module_path)
            ability_class = getattr(module, class_name)

            if not issubclass(ability_class, BaseAbility):
                raise TypeError(f"{class_name} is not a subclass of BaseAbility")

            logger.info("Loaded ability class", module=module_path, class_name=class_name)

            return ability_class

        except ImportError as e:
            logger.error("Failed to import module", module=module_path, error=str(e))
            raise

        except AttributeError as e:
            logger.error(
                "Class not found in module", module=module_path, class_name=class_name, error=str(e)
            )
            raise

    @staticmethod
    def instantiate_abilities(
        ability_classes: dict[str, type[BaseAbility]],
    ) -> dict[str, BaseAbility]:
        """
        Instantiate ability classes.

        Args:
            ability_classes: Dictionary of ability classes

        Returns:
            Dictionary of ability instances
        """
        instances = {}

        for name, ability_class in ability_classes.items():
            try:
                instance = ability_class()
                instances[name] = instance
                logger.info("Instantiated ability", name=name, class_name=ability_class.__name__)
            except Exception as e:
                logger.error(
                    "Failed to instantiate ability",
                    name=name,
                    class_name=ability_class.__name__,
                    error=str(e),
                )

        return instances

    @staticmethod
    def discover_and_instantiate() -> dict[str, BaseAbility]:
        """
        Discover and instantiate all abilities.

        Returns:
            Dictionary of ability instances
        """
        ability_classes = AbilityDiscovery.discover_abilities()
        return AbilityDiscovery.instantiate_abilities(ability_classes)
