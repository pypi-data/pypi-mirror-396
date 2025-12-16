"""
State management for abilities.

This module provides utilities for persisting and managing ability state
across invocations, including different state scopes and persistence strategies.
"""

import asyncio
import json
import pickle
from enum import Enum
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class StateScope(str, Enum):
    """Scope for state persistence."""

    SESSION = "session"  # Per-session state (cleared when session ends)
    USER = "user"  # Per-user state (persists across sessions)
    GLOBAL = "global"  # Global state (shared across all users)
    ABILITY = "ability"  # Per-ability state (shared by ability instances)


class StateEntry(BaseModel):
    """Represents a state entry."""

    key: str = Field(..., description="State key")
    value: Any = Field(..., description="State value")
    scope: StateScope = Field(..., description="State scope")
    ability_name: str | None = Field(default=None, description="Associated ability")
    user_id: str | None = Field(default=None, description="Associated user")
    session_id: str | None = Field(default=None, description="Associated session")
    created_at: float = Field(..., description="Creation timestamp")
    updated_at: float = Field(..., description="Last update timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class StateManager:
    """
    Manages state persistence for abilities.

    Provides scoped state storage with different persistence levels,
    from ephemeral session state to persistent user/global state.
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        """
        Initialize the state manager.

        Args:
            storage_path: Path for persistent state storage
        """
        self._storage_path = storage_path or Path.home() / ".bruno" / "ability_state"
        self._state: dict[str, dict[str, StateEntry]] = {
            "session": {},
            "user": {},
            "global": {},
            "ability": {},
        }
        self._lock = asyncio.Lock()

        # Ensure storage directory exists
        if storage_path:
            self._storage_path.mkdir(parents=True, exist_ok=True)

        logger.info("State manager initialized", storage_path=str(self._storage_path))

    def _get_state_key(
        self,
        key: str,
        scope: StateScope,
        ability_name: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> str:
        """Generate a unique state key based on scope and identifiers."""
        parts = [key]

        if scope == StateScope.SESSION and session_id:
            parts.append(f"session:{session_id}")
        elif scope == StateScope.USER and user_id:
            parts.append(f"user:{user_id}")
        elif scope == StateScope.ABILITY and ability_name:
            parts.append(f"ability:{ability_name}")

        if ability_name and scope != StateScope.ABILITY:
            parts.append(f"ability:{ability_name}")

        return ":".join(parts)

    async def set(
        self,
        key: str,
        value: Any,
        scope: StateScope = StateScope.SESSION,
        ability_name: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Set a state value.

        Args:
            key: State key
            value: State value
            scope: State scope
            ability_name: Associated ability name
            user_id: Associated user ID
            session_id: Associated session ID
            metadata: Additional metadata
        """
        import time

        state_key = self._get_state_key(key, scope, ability_name, user_id, session_id)

        async with self._lock:
            # Get or create entry
            existing = self._state[scope.value].get(state_key)

            if existing:
                existing.value = value
                existing.updated_at = time.time()
                if metadata:
                    existing.metadata.update(metadata)
            else:
                entry = StateEntry(
                    key=key,
                    value=value,
                    scope=scope,
                    ability_name=ability_name,
                    user_id=user_id,
                    session_id=session_id,
                    created_at=time.time(),
                    updated_at=time.time(),
                    metadata=metadata or {},
                )
                self._state[scope.value][state_key] = entry

            # Persist if not session scope
            if scope in (StateScope.USER, StateScope.GLOBAL, StateScope.ABILITY):
                await self._persist_entry(state_key, self._state[scope.value][state_key])

        logger.debug(
            "State set",
            key=key,
            scope=scope.value,
            ability=ability_name,
            user=user_id,
        )

    async def get(
        self,
        key: str,
        scope: StateScope = StateScope.SESSION,
        ability_name: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        default: Any = None,
    ) -> Any:
        """
        Get a state value.

        Args:
            key: State key
            scope: State scope
            ability_name: Associated ability name
            user_id: Associated user ID
            session_id: Associated session ID
            default: Default value if not found

        Returns:
            State value or default
        """
        state_key = self._get_state_key(key, scope, ability_name, user_id, session_id)

        async with self._lock:
            entry = self._state[scope.value].get(state_key)

            if entry:
                return entry.value

            # Try to load from persistent storage
            if scope in (StateScope.USER, StateScope.GLOBAL, StateScope.ABILITY):
                entry = await self._load_entry(state_key, scope)
                if entry:
                    self._state[scope.value][state_key] = entry
                    return entry.value

        return default

    async def delete(
        self,
        key: str,
        scope: StateScope = StateScope.SESSION,
        ability_name: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> bool:
        """
        Delete a state value.

        Args:
            key: State key
            scope: State scope
            ability_name: Associated ability name
            user_id: Associated user ID
            session_id: Associated session ID

        Returns:
            True if deleted, False if not found
        """
        state_key = self._get_state_key(key, scope, ability_name, user_id, session_id)

        async with self._lock:
            entry = self._state[scope.value].pop(state_key, None)

            if entry:
                # Delete from persistent storage
                if scope in (StateScope.USER, StateScope.GLOBAL, StateScope.ABILITY):
                    await self._delete_entry(state_key, scope)

                logger.debug(
                    "State deleted",
                    key=key,
                    scope=scope.value,
                    ability=ability_name,
                    user=user_id,
                )
                return True

        return False

    async def clear_scope(
        self,
        scope: StateScope,
        ability_name: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> int:
        """
        Clear all state in a scope.

        Args:
            scope: State scope to clear
            ability_name: Filter by ability name
            user_id: Filter by user ID
            session_id: Filter by session ID

        Returns:
            Number of entries cleared
        """
        count = 0

        async with self._lock:
            entries_to_remove = []

            for state_key, entry in self._state[scope.value].items():
                # Check filters
                if ability_name and entry.ability_name != ability_name:
                    continue
                if user_id and entry.user_id != user_id:
                    continue
                if session_id and entry.session_id != session_id:
                    continue

                entries_to_remove.append(state_key)

            # Remove entries
            for state_key in entries_to_remove:
                self._state[scope.value].pop(state_key, None)
                count += 1

                # Delete from persistent storage
                if scope in (StateScope.USER, StateScope.GLOBAL, StateScope.ABILITY):
                    await self._delete_entry(state_key, scope)

        logger.info(
            "Scope cleared",
            scope=scope.value,
            count=count,
            ability=ability_name,
            user=user_id,
        )

        return count

    async def _persist_entry(self, state_key: str, entry: StateEntry) -> None:
        """Persist a state entry to disk."""
        try:
            scope_dir = self._storage_path / entry.scope.value
            scope_dir.mkdir(parents=True, exist_ok=True)

            file_path = scope_dir / f"{state_key.replace(':', '_')}.json"

            # Try JSON serialization first
            try:
                data = {
                    "key": entry.key,
                    "value": entry.value,
                    "scope": entry.scope.value,
                    "ability_name": entry.ability_name,
                    "user_id": entry.user_id,
                    "session_id": entry.session_id,
                    "created_at": entry.created_at,
                    "updated_at": entry.updated_at,
                    "metadata": entry.metadata,
                }

                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)

            except (TypeError, ValueError):
                # Fall back to pickle for non-JSON-serializable data
                file_path = scope_dir / f"{state_key.replace(':', '_')}.pkl"
                with open(file_path, "wb") as f:
                    pickle.dump(entry.model_dump(), f)

            logger.debug("State persisted", state_key=state_key, file=str(file_path))

        except Exception as e:
            logger.error(
                "Failed to persist state", state_key=state_key, error=str(e), exc_info=True
            )

    async def _load_entry(self, state_key: str, scope: StateScope) -> StateEntry | None:
        """Load a state entry from disk."""
        try:
            scope_dir = self._storage_path / scope.value

            # Try JSON first
            json_path = scope_dir / f"{state_key.replace(':', '_')}.json"
            if json_path.exists():
                with open(json_path) as f:
                    data = json.load(f)
                    return StateEntry(**data)

            # Try pickle
            pkl_path = scope_dir / f"{state_key.replace(':', '_')}.pkl"
            if pkl_path.exists():
                with open(pkl_path, "rb") as f:
                    data = pickle.load(f)
                    return StateEntry(**data)

            return None

        except Exception as e:
            logger.error("Failed to load state", state_key=state_key, error=str(e), exc_info=True)
            return None

    async def _delete_entry(self, state_key: str, scope: StateScope) -> None:
        """Delete a persisted state entry."""
        try:
            scope_dir = self._storage_path / scope.value
            safe_key = state_key.replace(":", "_")

            for ext in [".json", ".pkl"]:
                file_path = scope_dir / f"{safe_key}{ext}"
                if file_path.exists():
                    file_path.unlink()
                    logger.debug("State file deleted", file=str(file_path))

        except Exception as e:
            logger.error("Failed to delete state", state_key=state_key, error=str(e), exc_info=True)

    def get_stats(self) -> dict[str, Any]:
        """Get state manager statistics."""
        return {
            "session_entries": len(self._state["session"]),
            "user_entries": len(self._state["user"]),
            "global_entries": len(self._state["global"]),
            "ability_entries": len(self._state["ability"]),
            "total_entries": sum(len(entries) for entries in self._state.values()),
            "storage_path": str(self._storage_path),
        }
