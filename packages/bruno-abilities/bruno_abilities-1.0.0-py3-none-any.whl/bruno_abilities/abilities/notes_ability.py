"""
Notes Ability - Rich note-taking with Markdown support.

This ability allows users to create and manage notes with Markdown formatting,
tagging, categorization, search, versioning, templates, and organization.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

import pytz
import structlog

from bruno_abilities.base.ability_base import AbilityContext, AbilityResult, BaseAbility
from bruno_abilities.base.metadata import (
    AbilityCapability,
    AbilityMetadata,
    ParameterMetadata,
    ParameterType,
)
from bruno_abilities.schemas.notes_schema import Note, NoteVersion

logger = structlog.get_logger(__name__)


class NotesAbility(BaseAbility):
    """
    Notes ability for creating and managing rich notes.

    Features:
    - Markdown formatting support
    - Tagging and categorization
    - Full-text search
    - Version history
    - Note templates
    - Hierarchical organization (folders/notebooks)
    - Note linking for knowledge graphs
    - Archive functionality
    """

    def __init__(self) -> None:
        """Initialize the notes ability."""
        super().__init__()
        self._notes: dict[str, Note] = {}  # note_id -> Note
        self._user_notes: dict[str, list[str]] = {}  # user_id -> [note_ids]
        self._templates: dict[str, str] = {}  # template_id -> template_content
        self._setup_default_templates()

    def _setup_default_templates(self) -> None:
        """Set up default note templates."""
        self._templates["meeting"] = """# Meeting Notes - {title}

**Date**: {date}
**Attendees**:

## Agenda


## Discussion


## Action Items
- [ ]

## Next Steps

"""

        self._templates["daily"] = """# Daily Note - {date}

## Tasks
- [ ]

## Notes


## Reflections

"""

        self._templates["blank"] = """# {title}

"""

    @property
    def metadata(self) -> AbilityMetadata:
        """Return notes ability metadata."""
        return AbilityMetadata(
            name="notes",
            display_name="Notes",
            description="Create and manage rich notes with Markdown, tagging, and organization",
            category="information_storage",
            version="1.0.0",
            tags=["notes", "markdown", "knowledge", "organization"],
            parameters=[
                ParameterMetadata(
                    name="action",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Action: create, update, read, delete, search, list, archive, link, list_templates",
                    required=True,
                    examples=[
                        "create",
                        "update",
                        "read",
                        "delete",
                        "search",
                        "list",
                        "archive",
                        "link",
                    ],
                ),
                ParameterMetadata(
                    name="note_id",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Note ID for update/read/delete/archive/link actions",
                    required=False,
                ),
                ParameterMetadata(
                    name="title",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Note title (required for create)",
                    required=False,
                    examples=["Meeting Notes", "Project Ideas", "Research"],
                ),
                ParameterMetadata(
                    name="content",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Note content (Markdown supported)",
                    required=False,
                ),
                ParameterMetadata(
                    name="category",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Note category",
                    required=False,
                    examples=["work", "personal", "research", "ideas"],
                ),
                ParameterMetadata(
                    name="tags",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Comma-separated tags",
                    required=False,
                    examples=["important,urgent", "project,planning"],
                ),
                ParameterMetadata(
                    name="folder",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Folder/notebook path (e.g., 'Work/Projects')",
                    required=False,
                ),
                ParameterMetadata(
                    name="template",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Template to use: blank, meeting, daily",
                    required=False,
                    examples=["blank", "meeting", "daily"],
                ),
                ParameterMetadata(
                    name="search_query",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Search query for finding notes",
                    required=False,
                ),
                ParameterMetadata(
                    name="linked_note_id",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Note ID to link to",
                    required=False,
                ),
                ParameterMetadata(
                    name="show_archived",
                    type=bool,
                    parameter_type=ParameterType.BOOLEAN,
                    description="Include archived notes in results",
                    required=False,
                    default=False,
                ),
            ],
            capabilities=[
                AbilityCapability.CANCELLABLE,
            ],
            aliases=["note", "create note", "take notes"],
            examples=[
                {
                    "description": "Create a new note",
                    "parameters": {
                        "action": "create",
                        "title": "Project Ideas",
                        "content": "# Ideas\\n\\n- Idea 1\\n- Idea 2",
                        "tags": "ideas,project",
                    },
                },
                {
                    "description": "Search for notes",
                    "parameters": {"action": "search", "search_query": "project"},
                },
                {
                    "description": "Create note from template",
                    "parameters": {
                        "action": "create",
                        "title": "Team Sync",
                        "template": "meeting",
                    },
                },
            ],
        )

    async def _execute(self, parameters: dict[str, Any], context: AbilityContext) -> AbilityResult:
        """Execute notes action."""
        action = parameters.get("action", "").lower()

        if action == "create":
            return await self._create_note(parameters, context)
        elif action == "update":
            return await self._update_note(parameters, context)
        elif action == "read":
            return await self._read_note(parameters, context)
        elif action == "delete":
            return await self._delete_note(parameters, context)
        elif action == "search":
            return await self._search_notes(parameters, context)
        elif action == "list":
            return await self._list_notes(parameters, context)
        elif action == "archive":
            return await self._archive_note(parameters, context)
        elif action == "link":
            return await self._link_notes(parameters, context)
        elif action == "list_templates":
            return await self._list_templates(parameters, context)
        else:
            return AbilityResult(
                success=False,
                error=f"Unknown action: {action}. Valid: create, update, read, delete, search, list, archive, link, list_templates",
            )

    async def _create_note(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Create a new note."""
        title = parameters.get("title")
        if not title:
            return AbilityResult(
                success=False,
                error="Title is required for creating a note",
            )

        # Get template content if specified
        template_name = parameters.get("template", "blank")
        if template_name not in self._templates:
            return AbilityResult(
                success=False,
                error=f"Unknown template: {template_name}. Available: {', '.join(self._templates.keys())}",
            )

        # Apply template
        template_content = self._templates[template_name]
        now = datetime.now(pytz.UTC)
        content = parameters.get("content")

        if not content:
            # Use template with placeholders
            content = template_content.format(title=title, date=now.strftime("%Y-%m-%d"))

        # Parse tags
        tags = []
        if parameters.get("tags"):
            tags = [t.strip() for t in parameters["tags"].split(",")]

        # Generate note ID
        note_id = f"note_{uuid4().hex[:12]}"

        # Create initial version
        version = NoteVersion(
            version_id=f"{note_id}_v1",
            content=content,
            created_at=now,
            created_by=context.user_id,
            change_summary="Initial creation",
        )

        # Create note
        note = Note(
            note_id=note_id,
            title=title,
            content=content,
            user_id=context.user_id,
            category=parameters.get("category"),
            tags=tags,
            folder=parameters.get("folder"),
            created_at=now,
            updated_at=now,
            current_version=1,
            versions=[version],
            template_id=template_name if template_name != "blank" else None,
        )

        # Store note
        self._notes[note_id] = note

        if context.user_id not in self._user_notes:
            self._user_notes[context.user_id] = []
        self._user_notes[context.user_id].append(note_id)

        logger.info(
            "Note created",
            note_id=note_id,
            title=title,
            user_id=context.user_id,
            template=template_name,
        )

        return AbilityResult(
            success=True,
            data={
                "note_id": note_id,
                "title": title,
                "category": note.category,
                "tags": tags,
                "folder": note.folder,
                "created_at": now.isoformat(),
                "message": f"Note '{title}' created successfully",
            },
        )

    async def _update_note(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Update an existing note."""
        note_id = parameters.get("note_id")
        if not note_id:
            return AbilityResult(
                success=False,
                error="note_id is required for updating a note",
            )

        note = self._notes.get(note_id)
        if not note:
            return AbilityResult(
                success=False,
                error=f"Note not found: {note_id}",
            )

        if note.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to update this note",
            )

        # Track changes for version
        changes = []
        now = datetime.now(pytz.UTC)

        # Update content
        if "content" in parameters:
            note.content = parameters["content"]
            changes.append("content")

            # Create new version
            note.current_version += 1
            version = NoteVersion(
                version_id=f"{note_id}_v{note.current_version}",
                content=note.content,
                created_at=now,
                created_by=context.user_id,
                change_summary=f"Updated {', '.join(changes)}",
            )
            note.versions.append(version)

        # Update title
        if "title" in parameters:
            note.title = parameters["title"]
            changes.append("title")

        # Update category
        if "category" in parameters:
            note.category = parameters["category"]
            changes.append("category")

        # Update tags
        if "tags" in parameters:
            note.tags = [t.strip() for t in parameters["tags"].split(",")]
            changes.append("tags")

        # Update folder
        if "folder" in parameters:
            note.folder = parameters["folder"]
            changes.append("folder")

        note.updated_at = now

        logger.info(
            "Note updated",
            note_id=note_id,
            changes=changes,
            version=note.current_version,
        )

        return AbilityResult(
            success=True,
            data={
                "note_id": note_id,
                "title": note.title,
                "version": note.current_version,
                "updated_at": now.isoformat(),
                "changes": changes,
                "message": f"Note '{note.title}' updated successfully",
            },
        )

    async def _read_note(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Read a note."""
        note_id = parameters.get("note_id")
        if not note_id:
            return AbilityResult(
                success=False,
                error="note_id is required for reading a note",
            )

        note = self._notes.get(note_id)
        if not note:
            return AbilityResult(
                success=False,
                error=f"Note not found: {note_id}",
            )

        if note.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to read this note",
            )

        return AbilityResult(
            success=True,
            data={
                "note_id": note.note_id,
                "title": note.title,
                "content": note.content,
                "category": note.category,
                "tags": note.tags,
                "folder": note.folder,
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat(),
                "version": note.current_version,
                "archived": note.archived,
                "linked_notes": note.linked_notes,
            },
        )

    async def _delete_note(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Delete a note."""
        note_id = parameters.get("note_id")
        if not note_id:
            return AbilityResult(
                success=False,
                error="note_id is required for deleting a note",
            )

        note = self._notes.get(note_id)
        if not note:
            return AbilityResult(
                success=False,
                error=f"Note not found: {note_id}",
            )

        if note.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to delete this note",
            )

        # Remove from storage
        del self._notes[note_id]
        if context.user_id in self._user_notes:
            self._user_notes[context.user_id].remove(note_id)

        logger.info("Note deleted", note_id=note_id, title=note.title)

        return AbilityResult(
            success=True,
            data={
                "note_id": note_id,
                "message": f"Note '{note.title}' deleted successfully",
            },
        )

    async def _search_notes(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Search for notes."""
        search_query = parameters.get("search_query", "").lower()
        if not search_query:
            return AbilityResult(
                success=False,
                error="search_query is required for searching notes",
            )

        show_archived = parameters.get("show_archived", False)
        user_note_ids = self._user_notes.get(context.user_id, [])

        matching_notes = []
        for note_id in user_note_ids:
            note = self._notes.get(note_id)
            if not note:
                continue

            # Skip archived notes unless requested
            if note.archived and not show_archived:
                continue

            # Search in title, content, category, tags, and folder
            search_fields = [
                note.title.lower(),
                note.content.lower(),
                (note.category or "").lower(),
                (note.folder or "").lower(),
            ] + [tag.lower() for tag in note.tags]

            if any(search_query in field for field in search_fields):
                matching_notes.append(
                    {
                        "note_id": note.note_id,
                        "title": note.title,
                        "category": note.category,
                        "tags": note.tags,
                        "folder": note.folder,
                        "created_at": note.created_at.isoformat(),
                        "updated_at": note.updated_at.isoformat(),
                        "archived": note.archived,
                        # Include snippet of content
                        "snippet": note.content[:150] + "..."
                        if len(note.content) > 150
                        else note.content,
                    }
                )

        # Sort by updated_at
        matching_notes.sort(key=lambda n: n["updated_at"], reverse=True)

        logger.info(
            "Notes searched",
            user_id=context.user_id,
            query=search_query,
            count=len(matching_notes),
        )

        return AbilityResult(
            success=True,
            data={
                "notes": matching_notes,
                "count": len(matching_notes),
                "query": search_query,
                "message": f"Found {len(matching_notes)} note(s) matching '{search_query}'",
            },
        )

    async def _list_notes(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """List all notes for the user."""
        show_archived = parameters.get("show_archived", False)
        user_note_ids = self._user_notes.get(context.user_id, [])

        notes_data = []
        for note_id in user_note_ids:
            note = self._notes.get(note_id)
            if not note:
                continue

            # Skip archived notes unless requested
            if note.archived and not show_archived:
                continue

            notes_data.append(
                {
                    "note_id": note.note_id,
                    "title": note.title,
                    "category": note.category,
                    "tags": note.tags,
                    "folder": note.folder,
                    "created_at": note.created_at.isoformat(),
                    "updated_at": note.updated_at.isoformat(),
                    "archived": note.archived,
                }
            )

        # Sort by updated_at
        notes_data.sort(key=lambda n: n["updated_at"], reverse=True)

        logger.info(
            "Notes listed",
            user_id=context.user_id,
            count=len(notes_data),
        )

        return AbilityResult(
            success=True,
            data={
                "notes": notes_data,
                "count": len(notes_data),
                "message": f"Found {len(notes_data)} note(s)",
            },
        )

    async def _archive_note(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Archive or unarchive a note."""
        note_id = parameters.get("note_id")
        if not note_id:
            return AbilityResult(
                success=False,
                error="note_id is required for archiving a note",
            )

        note = self._notes.get(note_id)
        if not note:
            return AbilityResult(
                success=False,
                error=f"Note not found: {note_id}",
            )

        if note.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to archive this note",
            )

        # Toggle archive status
        note.archived = not note.archived
        note.updated_at = datetime.now(pytz.UTC)

        status = "archived" if note.archived else "unarchived"
        logger.info("Note archived", note_id=note_id, archived=note.archived)

        return AbilityResult(
            success=True,
            data={
                "note_id": note_id,
                "title": note.title,
                "archived": note.archived,
                "message": f"Note '{note.title}' {status} successfully",
            },
        )

    async def _link_notes(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """Link two notes together."""
        note_id = parameters.get("note_id")
        linked_note_id = parameters.get("linked_note_id")

        if not note_id or not linked_note_id:
            return AbilityResult(
                success=False,
                error="Both note_id and linked_note_id are required for linking notes",
            )

        note = self._notes.get(note_id)
        linked_note = self._notes.get(linked_note_id)

        if not note:
            return AbilityResult(
                success=False,
                error=f"Note not found: {note_id}",
            )

        if not linked_note:
            return AbilityResult(
                success=False,
                error=f"Linked note not found: {linked_note_id}",
            )

        if note.user_id != context.user_id or linked_note.user_id != context.user_id:
            return AbilityResult(
                success=False,
                error="You don't have permission to link these notes",
            )

        # Add bidirectional link
        if linked_note_id not in note.linked_notes:
            note.linked_notes.append(linked_note_id)
            note.updated_at = datetime.now(pytz.UTC)

        if note_id not in linked_note.linked_notes:
            linked_note.linked_notes.append(note_id)
            linked_note.updated_at = datetime.now(pytz.UTC)

        logger.info(
            "Notes linked",
            note_id=note_id,
            linked_note_id=linked_note_id,
        )

        return AbilityResult(
            success=True,
            data={
                "note_id": note_id,
                "linked_note_id": linked_note_id,
                "message": f"Notes '{note.title}' and '{linked_note.title}' linked successfully",
            },
        )

    async def _list_templates(
        self, parameters: dict[str, Any], context: AbilityContext
    ) -> AbilityResult:
        """List available note templates."""
        templates_data = []
        for template_id, content in self._templates.items():
            # Get first line as description
            first_line = content.split("\n")[0].strip()
            templates_data.append(
                {
                    "template_id": template_id,
                    "description": first_line,
                }
            )

        return AbilityResult(
            success=True,
            data={
                "templates": templates_data,
                "count": len(templates_data),
                "message": f"Found {len(templates_data)} template(s)",
            },
        )

    async def _cleanup(self) -> None:
        """Clean up notes storage."""
        self._notes.clear()
        self._user_notes.clear()
        logger.info("Notes ability cleaned up")
