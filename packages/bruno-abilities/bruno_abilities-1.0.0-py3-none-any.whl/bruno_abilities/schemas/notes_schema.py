"""
Notes schema for bruno-memory integration.

This module defines the data structures for notes storage,
including versioning and metadata.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteVersion(BaseModel):
    """Represents a version of a note for edit history."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    version_id: str = Field(..., description="Unique version identifier")
    content: str = Field(..., description="Note content at this version")
    created_at: datetime = Field(..., description="When this version was created")
    created_by: str = Field(..., description="User who created this version")
    change_summary: str | None = Field(default=None, description="Summary of changes")


class Note(BaseModel):
    """
    Represents a note with rich metadata.

    Notes support Markdown formatting, tagging, categorization,
    and versioning for edit history.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    note_id: str = Field(..., description="Unique note identifier")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content (Markdown supported)")
    user_id: str = Field(..., description="User who owns the note")

    # Organization
    category: str | None = Field(default=None, description="Note category")
    tags: list[str] = Field(default_factory=list, description="Note tags")
    folder: str | None = Field(default=None, description="Folder/notebook path")

    # Metadata
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    archived: bool = Field(default=False, description="Whether note is archived")

    # Versioning
    current_version: int = Field(default=1, description="Current version number")
    versions: list[NoteVersion] = Field(default_factory=list, description="Version history")

    # Linking
    linked_notes: list[str] = Field(default_factory=list, description="IDs of linked notes")

    # Templates
    template_id: str | None = Field(default=None, description="Template used")

    # Attachments (references only)
    attachments: list[str] = Field(
        default_factory=list, description="Attachment file paths or URLs"
    )
