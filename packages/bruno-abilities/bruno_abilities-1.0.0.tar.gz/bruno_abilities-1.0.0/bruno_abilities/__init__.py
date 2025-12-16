"""
Bruno Abilities - Action execution layer for Bruno Personal Assistant.

This package provides the ability system that enables Bruno to perform
discrete, executable actions beyond conversation.
"""

__version__ = "0.1.0"
__author__ = "Meggy AI"

from bruno_abilities.base.ability_base import BaseAbility
from bruno_abilities.base.metadata import AbilityMetadata, ParameterMetadata
from bruno_abilities.infrastructure import StateManager, StateScope
from bruno_abilities.registry.lifecycle import LifecycleManager, LifecycleState
from bruno_abilities.registry.registry import AbilityRegistry

__all__ = [
    "BaseAbility",
    "AbilityMetadata",
    "ParameterMetadata",
    "AbilityRegistry",
    "LifecycleManager",
    "LifecycleState",
    "StateManager",
    "StateScope",
]
