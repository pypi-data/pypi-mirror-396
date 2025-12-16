"""
Music Control Ability - Local playback control.

This ability provides music playback control for local audio files using pygame.mixer.
It supports playback control, playlist management, volume control, and listening history.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pygame
import pytz
import structlog

from bruno_abilities.base.ability_base import AbilityContext, AbilityResult, BaseAbility
from bruno_abilities.base.metadata import (
    AbilityCapability,
    AbilityMetadata,
    ParameterMetadata,
    ParameterType,
)
from bruno_abilities.schemas.music_schema import (
    PlaybackSession,
    PlaybackState,
    Playlist,
    RepeatMode,
    Track,
)

logger = structlog.get_logger(__name__)


class MusicAbility(BaseAbility):
    """
    Music control ability for local audio playback.

    Features:
    - Play, pause, stop, skip audio files
    - Playlist management (create, add, remove)
    - Queue management with shuffle and repeat
    - Volume control
    - Local library scanning and indexing
    - Listening history tracking
    - Smart recommendations based on history
    """

    def __init__(self) -> None:
        """Initialize the music ability."""
        super().__init__()

        # Initialize pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        # Storage
        self._tracks: dict[str, Track] = {}  # track_id -> Track
        self._playlists: dict[str, Playlist] = {}  # playlist_id -> Playlist
        self._user_playlists: dict[str, list[str]] = {}  # user_id -> [playlist_ids]
        self._sessions: dict[str, PlaybackSession] = {}  # session_id -> Session

        # Playback state
        self._current_track: Track | None = None
        self._current_user: str | None = None
        self._playback_state: PlaybackState = PlaybackState.STOPPED
        self._current_session: PlaybackSession | None = None
        self._queue: list[str] = []  # List of track_ids
        self._queue_position: int = 0
        self._repeat_mode: RepeatMode = RepeatMode.OFF
        self._shuffle: bool = False
        self._volume: float = 0.7  # 0.0 to 1.0

        # Set initial volume
        pygame.mixer.music.set_volume(self._volume)

    @property
    def metadata(self) -> AbilityMetadata:
        """Return music ability metadata."""
        return AbilityMetadata(
            name="music",
            display_name="Music Control",
            description="Local music playback control with playlist and queue management",
            category="entertainment",
            version="1.0.0",
            tags=["music", "audio", "playback", "playlist", "entertainment"],
            parameters=[
                ParameterMetadata(
                    name="action",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Action: play, pause, stop, skip, previous, volume, queue, playlist, library, history, status",
                    required=True,
                    examples=[
                        "play",
                        "pause",
                        "stop",
                        "skip",
                        "volume",
                        "queue",
                        "playlist",
                        "library",
                        "status",
                    ],
                ),
                ParameterMetadata(
                    name="sub_action",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Sub-action for queue/playlist: list, add, clear, shuffle, repeat, create, delete, add_track",
                    required=False,
                    examples=["list", "add", "clear", "create", "delete"],
                ),
                ParameterMetadata(
                    name="file_path",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Path to audio file (for play action)",
                    required=False,
                ),
                ParameterMetadata(
                    name="track_id",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Track ID to play",
                    required=False,
                ),
                ParameterMetadata(
                    name="playlist_id",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Playlist ID to play or manage",
                    required=False,
                ),
                ParameterMetadata(
                    name="playlist_name",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Name for new playlist",
                    required=False,
                ),
                ParameterMetadata(
                    name="volume",
                    type=float,
                    parameter_type=ParameterType.FLOAT,
                    description="Volume level (0.0 to 1.0)",
                    required=False,
                    examples=[0.5, 0.7, 1.0],
                ),
                ParameterMetadata(
                    name="repeat",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Repeat mode: off, one, all",
                    required=False,
                    default="off",
                    examples=["off", "one", "all"],
                ),
                ParameterMetadata(
                    name="shuffle",
                    type=bool,
                    parameter_type=ParameterType.BOOLEAN,
                    description="Enable shuffle mode",
                    required=False,
                    default=False,
                ),
                ParameterMetadata(
                    name="library_path",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Path to music library directory for scanning",
                    required=False,
                ),
            ],
            capabilities=[
                AbilityCapability.CANCELLABLE,
            ],
            aliases=["music", "play music", "audio", "player"],
            examples=[
                {
                    "description": "Play a music file",
                    "parameters": {"action": "play", "file_path": "/music/song.mp3"},
                },
                {
                    "description": "Pause playback",
                    "parameters": {"action": "pause"},
                },
                {
                    "description": "Set volume to 50%",
                    "parameters": {"action": "volume", "volume": 0.5},
                },
            ],
        )

    async def _execute(self, parameters: dict[str, Any], context: AbilityContext) -> AbilityResult:
        """Execute music action."""
        action = parameters.get("action", "").lower()

        if action == "play":
            return await self._play(parameters, context)
        elif action == "pause":
            return await self._pause(parameters, context)
        elif action == "stop":
            return await self._stop(parameters, context)
        elif action == "skip":
            return await self._skip(parameters, context)
        elif action == "previous":
            return await self._previous(parameters, context)
        elif action == "volume":
            return await self._set_volume(parameters, context)
        elif action == "queue":
            return await self._manage_queue(parameters, context)
        elif action == "playlist":
            return await self._manage_playlist(parameters, context)
        elif action == "library":
            return await self._scan_library(parameters, context)
        elif action == "history":
            return await self._get_history(parameters, context)
        elif action == "status":
            return await self._get_status(parameters, context)
        else:
            return AbilityResult(
                success=False,
                error=f"Unknown action: {action}. Valid: play, pause, stop, skip, previous, volume, queue, playlist, library, history, status",
            )

    async def _play(self, parameters: dict[str, Any], context: AbilityContext) -> AbilityResult:
        """Play music from file or track ID."""
        # Check if we should resume paused music
        if (
            self._playback_state == PlaybackState.PAUSED
            and not parameters.get("file_path")
            and not parameters.get("track_id")
            and not parameters.get("playlist_id")
        ):
            pygame.mixer.music.unpause()
            self._playback_state = PlaybackState.PLAYING
            logger.info(
                "Resumed playback", track=self._current_track.title if self._current_track else None
            )
            return AbilityResult(
                success=True,
                data={
                    "state": "playing",
                    "track": self._current_track.title if self._current_track else None,
                    "message": "Resumed playback",
                },
            )

        # Get track to play
        track = None

        if parameters.get("playlist_id"):
            # Play playlist
            playlist_id = parameters["playlist_id"]
            playlist = self._playlists.get(playlist_id)
            if not playlist:
                return AbilityResult(success=False, error=f"Playlist not found: {playlist_id}")

            if playlist.user_id != context.user_id:
                return AbilityResult(
                    success=False,
                    error="You don't have permission to play this playlist",
                )

            if not playlist.track_ids:
                return AbilityResult(success=False, error="Playlist is empty")

            # Set queue to playlist tracks
            self._queue = playlist.track_ids.copy()
            self._queue_position = 0

            # Apply shuffle if needed
            if self._shuffle:
                import random

                random.shuffle(self._queue)

            track_id = self._queue[0]
            track = self._tracks.get(track_id)

        elif parameters.get("track_id"):
            # Play specific track
            track_id = parameters["track_id"]
            track = self._tracks.get(track_id)
            if not track:
                return AbilityResult(success=False, error=f"Track not found: {track_id}")

        elif parameters.get("file_path"):
            # Play from file path
            file_path = parameters["file_path"]
            if not os.path.exists(file_path):
                return AbilityResult(success=False, error=f"File not found: {file_path}")

            # Check if track already in library
            for t in self._tracks.values():
                if t.file_path == file_path:
                    track = t
                    break

            # Create new track if not in library
            if not track:
                track_id = f"track_{uuid4().hex[:12]}"
                track = Track(
                    track_id=track_id,
                    file_path=file_path,
                    title=Path(file_path).stem,
                    added_at=datetime.now(pytz.UTC),
                )
                self._tracks[track_id] = track

        else:
            return AbilityResult(
                success=False,
                error="Must provide file_path, track_id, or playlist_id to play",
            )

        if not track:
            return AbilityResult(success=False, error="Could not load track")

        # Stop current playback
        if self._playback_state != PlaybackState.STOPPED:
            await self._end_session()
            pygame.mixer.music.stop()

        # Load and play track
        try:
            pygame.mixer.music.load(track.file_path)
            pygame.mixer.music.play()

            self._current_track = track
            self._current_user = context.user_id
            self._playback_state = PlaybackState.PLAYING

            # Start new session
            session_id = f"session_{uuid4().hex[:12]}"
            self._current_session = PlaybackSession(
                session_id=session_id,
                user_id=context.user_id,
                track_id=track.track_id,
                started_at=datetime.now(pytz.UTC),
            )
            self._sessions[session_id] = self._current_session

            # Update track stats
            track.play_count += 1
            track.last_played = datetime.now(pytz.UTC)

            logger.info(
                "Started playback",
                track=track.title,
                track_id=track.track_id,
                user_id=context.user_id,
            )

            return AbilityResult(
                success=True,
                data={
                    "state": "playing",
                    "track_id": track.track_id,
                    "title": track.title,
                    "artist": track.artist,
                    "album": track.album,
                    "message": f"Now playing: {track.title}",
                },
            )

        except Exception as e:
            logger.error("Failed to play track", error=str(e), track=track.title)
            return AbilityResult(success=False, error=f"Failed to play track: {e}")

    async def _pause(self, parameters: dict[str, Any], context: AbilityContext) -> AbilityResult:
        """Pause playback."""
        if self._playback_state != PlaybackState.PLAYING:
            return AbilityResult(success=False, error="Nothing is currently playing")

        pygame.mixer.music.pause()
        self._playback_state = PlaybackState.PAUSED

        logger.info(
            "Paused playback", track=self._current_track.title if self._current_track else None
        )

        return AbilityResult(
            success=True,
            data={
                "state": "paused",
                "track": self._current_track.title if self._current_track else None,
                "message": "Playback paused",
            },
        )

    async def _stop(self, parameters: dict[str, Any], context: AbilityContext) -> AbilityResult:
        """Stop playback."""
        if self._playback_state == PlaybackState.STOPPED:
            return AbilityResult(success=False, error="Nothing is currently playing")

        pygame.mixer.music.stop()
        await self._end_session()

        self._playback_state = PlaybackState.STOPPED
        track_title = self._current_track.title if self._current_track else None
        self._current_track = None
        self._current_user = None

        logger.info("Stopped playback", track=track_title)

        return AbilityResult(
            success=True,
            data={"state": "stopped", "message": "Playback stopped"},
        )

    async def _skip(self, parameters: dict[str, Any], context: AbilityContext) -> AbilityResult:
        """Skip to next track in queue."""
        if not self._queue:
            return AbilityResult(success=False, error="No tracks in queue")

        # Move to next track
        self._queue_position += 1

        # Handle repeat modes
        if self._queue_position >= len(self._queue):
            if self._repeat_mode == RepeatMode.ALL:
                self._queue_position = 0
            elif self._repeat_mode == RepeatMode.ONE:
                self._queue_position -= 1  # Stay on current track
            else:
                return AbilityResult(
                    success=True,
                    data={"message": "End of queue reached", "state": "stopped"},
                )

        # Play next track
        track_id = self._queue[self._queue_position]
        return await self._play({"track_id": track_id}, context)

    async def _previous(self, parameters: dict[str, Any], context: AbilityContext) -> AbilityResult:
        """Go to previous track in queue."""
        if not self._queue:
            return AbilityResult(success=False, error="No tracks in queue")

        # Move to previous track
        self._queue_position -= 1

        if self._queue_position < 0:
            self._queue_position = 0

        # Play previous track
        track_id = self._queue[self._queue_position]
        return await self._play({"track_id": track_id}, context)

    async def _set_volume(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Set playback volume."""
        volume = parameters.get("volume")
        if volume is None:
            return AbilityResult(success=False, error="volume parameter is required")

        # Validate volume range
        try:
            volume = float(volume)
            if not 0.0 <= volume <= 1.0:
                return AbilityResult(success=False, error="Volume must be between 0.0 and 1.0")
        except (ValueError, TypeError):
            return AbilityResult(success=False, error="Invalid volume value")

        self._volume = volume
        pygame.mixer.music.set_volume(volume)

        logger.info("Volume changed", volume=volume)

        return AbilityResult(
            success=True,
            data={
                "volume": volume,
                "percentage": int(volume * 100),
                "message": f"Volume set to {int(volume * 100)}%",
            },
        )

    async def _manage_queue(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Manage playback queue."""
        sub_action = parameters.get("sub_action")
        if not sub_action:
            sub_action = "list"
        sub_action = sub_action.lower()

        if sub_action == "list":
            # List current queue
            queue_tracks = []
            for i, track_id in enumerate(self._queue):
                track = self._tracks.get(track_id)
                if track:
                    queue_tracks.append(
                        {
                            "position": i,
                            "track_id": track.track_id,
                            "title": track.title,
                            "artist": track.artist,
                            "current": i == self._queue_position,
                        }
                    )

            return AbilityResult(
                success=True,
                data={
                    "queue": queue_tracks,
                    "position": self._queue_position,
                    "total": len(self._queue),
                    "repeat": self._repeat_mode.value,
                    "shuffle": self._shuffle,
                },
            )

        elif sub_action == "add":
            # Add track to queue
            track_id = parameters.get("track_id")
            if not track_id:
                return AbilityResult(success=False, error="track_id is required to add to queue")

            if track_id not in self._tracks:
                return AbilityResult(success=False, error=f"Track not found: {track_id}")

            self._queue.append(track_id)

            return AbilityResult(
                success=True,
                data={"message": "Track added to queue", "queue_length": len(self._queue)},
            )

        elif sub_action == "clear":
            # Clear queue
            self._queue.clear()
            self._queue_position = 0

            return AbilityResult(success=True, data={"message": "Queue cleared"})

        elif sub_action == "shuffle":
            # Toggle shuffle
            self._shuffle = not self._shuffle

            return AbilityResult(
                success=True,
                data={
                    "shuffle": self._shuffle,
                    "message": f"Shuffle {'enabled' if self._shuffle else 'disabled'}",
                },
            )

        elif sub_action == "repeat":
            # Set repeat mode
            repeat = parameters.get("repeat", "off").lower()
            try:
                self._repeat_mode = RepeatMode(repeat)
            except ValueError:
                return AbilityResult(
                    success=False,
                    error=f"Invalid repeat mode: {repeat}. Valid: off, one, all",
                )

            return AbilityResult(
                success=True,
                data={
                    "repeat": self._repeat_mode.value,
                    "message": f"Repeat mode set to {self._repeat_mode.value}",
                },
            )

        else:
            return AbilityResult(
                success=False,
                error=f"Unknown queue sub_action: {sub_action}. Valid: list, add, clear, shuffle, repeat",
            )

    async def _manage_playlist(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Manage playlists."""
        sub_action = parameters.get("sub_action")
        if not sub_action:
            sub_action = "list"
        sub_action = sub_action.lower()

        if sub_action == "create":
            # Create new playlist
            name = parameters.get("playlist_name")
            if not name:
                return AbilityResult(
                    success=False, error="playlist_name is required to create playlist"
                )

            playlist_id = f"playlist_{uuid4().hex[:12]}"
            now = datetime.now(pytz.UTC)

            playlist = Playlist(
                playlist_id=playlist_id,
                name=name,
                description=parameters.get("description"),
                user_id=context.user_id,
                created_at=now,
                updated_at=now,
            )

            self._playlists[playlist_id] = playlist
            if context.user_id not in self._user_playlists:
                self._user_playlists[context.user_id] = []
            self._user_playlists[context.user_id].append(playlist_id)

            logger.info("Playlist created", playlist_id=playlist_id, name=name)

            return AbilityResult(
                success=True,
                data={
                    "playlist_id": playlist_id,
                    "name": name,
                    "message": f"Playlist '{name}' created",
                },
            )

        elif sub_action == "list":
            # List user's playlists
            user_playlist_ids = self._user_playlists.get(context.user_id, [])
            playlists_data = []

            for playlist_id in user_playlist_ids:
                playlist = self._playlists.get(playlist_id)
                if playlist:
                    playlists_data.append(
                        {
                            "playlist_id": playlist.playlist_id,
                            "name": playlist.name,
                            "description": playlist.description,
                            "track_count": len(playlist.track_ids),
                            "play_count": playlist.play_count,
                        }
                    )

            return AbilityResult(
                success=True,
                data={"playlists": playlists_data, "count": len(playlists_data)},
            )

        elif sub_action == "add_track":
            # Add track to playlist
            playlist_id = parameters.get("playlist_id")
            track_id = parameters.get("track_id")

            if not playlist_id or not track_id:
                return AbilityResult(
                    success=False,
                    error="playlist_id and track_id are required",
                )

            playlist = self._playlists.get(playlist_id)
            if not playlist:
                return AbilityResult(success=False, error=f"Playlist not found: {playlist_id}")

            if playlist.user_id != context.user_id:
                return AbilityResult(
                    success=False,
                    error="You don't have permission to modify this playlist",
                )

            if track_id not in self._tracks:
                return AbilityResult(success=False, error=f"Track not found: {track_id}")

            playlist.track_ids.append(track_id)
            playlist.updated_at = datetime.now(pytz.UTC)

            return AbilityResult(
                success=True,
                data={"message": "Track added to playlist", "track_count": len(playlist.track_ids)},
            )

        elif sub_action == "delete":
            # Delete playlist
            playlist_id = parameters.get("playlist_id")
            if not playlist_id:
                return AbilityResult(success=False, error="playlist_id is required to delete")

            playlist = self._playlists.get(playlist_id)
            if not playlist:
                return AbilityResult(success=False, error=f"Playlist not found: {playlist_id}")

            if playlist.user_id != context.user_id:
                return AbilityResult(
                    success=False,
                    error="You don't have permission to delete this playlist",
                )

            del self._playlists[playlist_id]
            self._user_playlists[context.user_id].remove(playlist_id)

            return AbilityResult(
                success=True,
                data={"message": f"Playlist '{playlist.name}' deleted"},
            )

        else:
            return AbilityResult(
                success=False,
                error=f"Unknown playlist sub_action: {sub_action}. Valid: create, list, add_track, delete",
            )

    async def _scan_library(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Scan directory for music files."""
        library_path = parameters.get("library_path")
        if not library_path:
            return AbilityResult(success=False, error="library_path is required for scanning")

        if not os.path.exists(library_path):
            return AbilityResult(success=False, error=f"Path not found: {library_path}")

        # Supported audio formats
        audio_extensions = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"}

        # Scan directory
        found_tracks = []
        for root, _, files in os.walk(library_path):
            for file in files:
                if Path(file).suffix.lower() in audio_extensions:
                    file_path = os.path.join(root, file)

                    # Check if already in library
                    existing = False
                    for track in self._tracks.values():
                        if track.file_path == file_path:
                            existing = True
                            break

                    if not existing:
                        track_id = f"track_{uuid4().hex[:12]}"
                        track = Track(
                            track_id=track_id,
                            file_path=file_path,
                            title=Path(file).stem,
                            added_at=datetime.now(pytz.UTC),
                        )
                        self._tracks[track_id] = track
                        found_tracks.append(track_id)

        logger.info(
            "Library scan complete",
            path=library_path,
            new_tracks=len(found_tracks),
        )

        return AbilityResult(
            success=True,
            data={
                "tracks_added": len(found_tracks),
                "total_tracks": len(self._tracks),
                "message": f"Added {len(found_tracks)} new tracks to library",
            },
        )

    async def _get_history(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Get listening history."""
        # Get user's sessions
        user_sessions = [s for s in self._sessions.values() if s.user_id == context.user_id]

        # Sort by start time (most recent first)
        user_sessions.sort(key=lambda s: s.started_at, reverse=True)

        # Limit to recent sessions
        limit = min(len(user_sessions), 50)
        recent_sessions = user_sessions[:limit]

        history_data = []
        for session in recent_sessions:
            track = self._tracks.get(session.track_id)
            if track:
                history_data.append(
                    {
                        "track_id": track.track_id,
                        "title": track.title,
                        "artist": track.artist,
                        "played_at": session.started_at.isoformat(),
                        "duration_played": session.duration_played,
                        "completed": session.completed,
                    }
                )

        return AbilityResult(
            success=True, data={"history": history_data, "count": len(history_data)}
        )

    async def _get_status(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Get current playback status."""
        status_data = {
            "state": self._playback_state.value,
            "volume": self._volume,
            "volume_percentage": int(self._volume * 100),
            "repeat": self._repeat_mode.value,
            "shuffle": self._shuffle,
            "queue_length": len(self._queue),
            "queue_position": self._queue_position,
        }

        if self._current_track:
            status_data["current_track"] = {
                "track_id": self._current_track.track_id,
                "title": self._current_track.title,
                "artist": self._current_track.artist,
                "album": self._current_track.album,
            }

        return AbilityResult(success=True, data=status_data)

    async def _end_session(self) -> None:
        """End current playback session."""
        if self._current_session:
            self._current_session.ended_at = datetime.now(pytz.UTC)
            # Calculate duration (simplified - would need position tracking for accuracy)
            if self._current_session.started_at:
                duration = (
                    self._current_session.ended_at - self._current_session.started_at
                ).total_seconds()
                self._current_session.duration_played = duration

            self._current_session = None

    async def _cleanup(self) -> None:
        """Clean up music ability resources."""
        # Stop playback
        pygame.mixer.music.stop()

        # End current session
        await self._end_session()

        # Clear storage
        self._tracks.clear()
        self._playlists.clear()
        self._user_playlists.clear()
        self._sessions.clear()
        self._queue.clear()

        # Quit pygame mixer
        pygame.mixer.quit()

        logger.info("Music ability cleaned up")
