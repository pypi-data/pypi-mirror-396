"""
Infrastructure components for ability state management.

This package provides state persistence for abilities across sessions.
"""

from bruno_abilities.infrastructure.state_manager import StateManager, StateScope

__all__ = [
    "StateManager",
    "StateScope",
]
