"""Schemas for music and playback data."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PlaybackState(str, Enum):
    """Playback state enum."""

    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class RepeatMode(str, Enum):
    """Repeat mode enum."""

    OFF = "off"
    ONE = "one"
    ALL = "all"


class Track(BaseModel):
    """Music track model."""

    track_id: str = Field(description="Unique track identifier")
    file_path: str = Field(description="Absolute path to audio file")
    title: str = Field(description="Track title")
    artist: str | None = Field(default=None, description="Artist name")
    album: str | None = Field(default=None, description="Album name")
    duration: float | None = Field(default=None, description="Duration in seconds")
    genre: str | None = Field(default=None, description="Genre")
    year: int | None = Field(default=None, description="Release year")
    track_number: int | None = Field(default=None, description="Track number")
    play_count: int = Field(default=0, description="Number of times played")
    last_played: datetime | None = Field(default=None, description="Last play timestamp")
    added_at: datetime = Field(description="When track was added to library")


class Playlist(BaseModel):
    """Playlist model."""

    playlist_id: str = Field(description="Unique playlist identifier")
    name: str = Field(description="Playlist name")
    description: str | None = Field(default=None, description="Playlist description")
    user_id: str = Field(description="Owner user ID")
    track_ids: list[str] = Field(default_factory=list, description="List of track IDs in order")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    play_count: int = Field(default=0, description="Times playlist was played")


class PlaybackSession(BaseModel):
    """Playback session for history tracking."""

    session_id: str = Field(description="Unique session identifier")
    user_id: str = Field(description="User ID")
    track_id: str = Field(description="Track being played")
    started_at: datetime = Field(description="Session start time")
    ended_at: datetime | None = Field(default=None, description="Session end time")
    duration_played: float = Field(default=0.0, description="Seconds of track actually played")
    completed: bool = Field(default=False, description="Whether track played to completion")
