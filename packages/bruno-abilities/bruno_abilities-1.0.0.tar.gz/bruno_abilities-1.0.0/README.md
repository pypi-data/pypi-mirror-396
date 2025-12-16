# bruno-abilities

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://github.com/meggy-ai/bruno-abilities/workflows/Tests/badge.svg)](https://github.com/meggy-ai/bruno-abilities/actions)
[![Code Quality](https://github.com/meggy-ai/bruno-abilities/workflows/Code%20Quality/badge.svg)](https://github.com/meggy-ai/bruno-abilities/actions)
[![Coverage](https://img.shields.io/badge/coverage-67%25-yellow)](htmlcov/index.html)

**Action execution layer for Bruno Personal Assistant** - Transform Bruno from a conversational AI into a functional personal assistant with pre-built, production-ready abilities.

## ✨ Features

- **6 Production-Ready Abilities**: Timer, Alarm, Reminder, Notes, Todo, Music
- **Async-First Design**: Built with asyncio for efficient concurrent operations
- **Type-Safe**: Full Pydantic v2 validation and type hints
- **Natural Language Extraction**: Automatic parameter extraction from user messages
- **State Management**: Persistent state for long-running operations
- **Event Integration**: Full bruno-core event bus integration
- **Extensible**: Easy to create custom abilities using BaseAbility
- **Well-Tested**: 164 tests with 67% coverage

---

## 📦 Installation

```bash
# Core installation
pip install bruno-abilities

# With music playback support
pip install bruno-abilities[music]

# Development installation
pip install bruno-abilities[dev]
```

### From Source

```bash
git clone https://github.com/meggy-ai/bruno-abilities.git
cd bruno-abilities
pip install -e ".[dev]"
```

---

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from bruno_abilities.abilities import TimerAbility, NotesAbility
from bruno_core.models import AbilityRequest

async def main():
    # Create abilities
    timer = TimerAbility()
    notes = NotesAbility()

    # Initialize
    await timer.initialize()
    await notes.initialize()

    # Set a timer
    timer_request = AbilityRequest(
        action="set_timer",
        parameters={"duration_seconds": 60, "label": "Tea"}
    )
    response = await timer.execute(timer_request)
    print(f"Timer set: {response.data}")

    # Create a note
    note_request = AbilityRequest(
        action="create_note",
        parameters={
            "title": "Meeting Notes",
            "content": "Discuss Q1 goals"
        }
    )
    response = await notes.execute(note_request)
    print(f"Note created: {response.data}")

    # Cleanup
    await timer.shutdown()
    await notes.shutdown()

asyncio.run(main())
```

### Using Ability Registry

```python
from bruno_abilities.registry import AbilityRegistry

async def main():
    # Discover and load all abilities
    registry = AbilityRegistry()
    await registry.discover_abilities()

    # Get an ability
    timer = await registry.get_ability("timer")

    # Execute action
    response = await timer.execute_action("set_timer", duration_seconds=300)
    print(response)

asyncio.run(main())
```

---

## 🎯 Available Abilities

### ⏱️ Timer Ability

Countdown timers with callbacks and cancellation support.

```python
from bruno_abilities.abilities import TimerAbility

timer = TimerAbility()
await timer.initialize()

# Set a timer
response = await timer.execute_action(
    "set_timer",
    duration_seconds=60,
    label="Pomodoro"
)

# List active timers
response = await timer.execute_action("list_timers")

# Cancel a timer
response = await timer.execute_action("cancel_timer", timer_id="timer_123")
```

**Actions**: `set_timer`, `cancel_timer`, `list_timers`, `pause_timer`, `resume_timer`

---

### ⏰ Alarm Ability

Scheduled alarms with audio playback and recurrence.

```python
from bruno_abilities.abilities import AlarmAbility

alarm = AlarmAbility()
await alarm.initialize()

# Set an alarm
response = await alarm.execute_action(
    "set_alarm",
    time="07:00",
    label="Wake up",
    repeat_days=["monday", "tuesday", "wednesday"]
)

# List alarms
response = await alarm.execute_action("list_alarms")

# Delete an alarm
response = await alarm.execute_action("delete_alarm", alarm_id="alarm_456")
```

**Actions**: `set_alarm`, `cancel_alarm`, `list_alarms`, `snooze_alarm`, `dismiss_alarm`

---

### 🔔 Reminder Ability

Text-based reminders with persistence and retrieval.

```python
from bruno_abilities.abilities import ReminderAbility

reminder = ReminderAbility()
await reminder.initialize()

# Create a reminder
response = await reminder.execute_action(
    "create_reminder",
    text="Call dentist",
    remind_at="2025-12-15 14:00"
)

# List reminders
response = await reminder.execute_action("list_reminders")

# Complete a reminder
response = await reminder.execute_action("complete_reminder", reminder_id="rem_789")
```

**Actions**: `create_reminder`, `list_reminders`, `complete_reminder`, `delete_reminder`, `search_reminders`

---

### 📝 Notes Ability

Full CRUD operations on notes with search and tagging.

```python
from bruno_abilities.abilities import NotesAbility

notes = NotesAbility()
await notes.initialize()

# Create a note
response = await notes.execute_action(
    "create_note",
    title="Project Ideas",
    content="1. AI assistant\n2. Task automation",
    tags=["work", "ideas"]
)

# Search notes
response = await notes.execute_action("search_notes", query="project")

# Update a note
response = await notes.execute_action(
    "update_note",
    note_id="note_101",
    content="Updated content"
)

# Delete a note
response = await notes.execute_action("delete_note", note_id="note_101")
```

**Actions**: `create_note`, `read_note`, `update_note`, `delete_note`, `list_notes`, `search_notes`

---

### ✅ Todo Ability

Task management with priorities, due dates, and completion tracking.

```python
from bruno_abilities.abilities import TodoAbility

todo = TodoAbility()
await todo.initialize()

# Create a task
response = await todo.execute_action(
    "create_task",
    title="Deploy v1.0",
    description="Deploy to production",
    priority="high",
    due_date="2025-12-20"
)

# List tasks
response = await todo.execute_action("list_tasks", status="pending")

# Complete a task
response = await todo.execute_action("complete_task", task_id="task_202")

# Update priority
response = await todo.execute_action(
    "update_task",
    task_id="task_202",
    priority="urgent"
)
```

**Actions**: `create_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`, `search_tasks`

---

### 🎵 Music Ability

Local music playback with playlist support.

```python
from bruno_abilities.abilities import MusicAbility

music = MusicAbility()
await music.initialize()

# Play a track
response = await music.execute_action(
    "play",
    track_path="/music/favorite-song.mp3"
)

# Pause playback
response = await music.execute_action("pause")

# Set volume
response = await music.execute_action("set_volume", level=75)

# Get playback status
response = await music.execute_action("get_status")
```

**Actions**: `play`, `pause`, `stop`, `next`, `previous`, `set_volume`, `get_status`

---

## 🛠️ Creating Custom Abilities

```python
from bruno_abilities.base import BaseAbility
from bruno_core.models import AbilityMetadata, AbilityRequest, AbilityResponse
from pydantic import Field

class WeatherAbility(BaseAbility):
    """Custom weather ability."""

    def get_metadata(self) -> AbilityMetadata:
        return AbilityMetadata(
            name="weather",
            description="Get weather information",
            version="1.0.0",
            author="Your Name",
            parameters=[
                {
                    "name": "location",
                    "type": "string",
                    "description": "City name",
                    "required": True
                }
            ],
            examples=["What's the weather in London?"]
        )

    async def execute_action(
        self,
        request: AbilityRequest
    ) -> AbilityResponse:
        location = request.parameters["location"]

        # Your weather API logic here
        weather_data = await self._fetch_weather(location)

        return AbilityResponse(
            request_id=request.id,
            ability_name="weather",
            success=True,
            data=weather_data
        )

    async def _fetch_weather(self, location: str):
        # Implement your weather API call
        return {"temperature": 20, "condition": "sunny"}
```

### Register Custom Ability

In your `pyproject.toml`:

```toml
[project.entry-points."bruno.abilities"]
weather = "my_package.abilities:WeatherAbility"
```

---

## 📚 Integration with Bruno Ecosystem

### With Bruno Core

```python
from bruno_core.base import BaseAssistant
from bruno_core.events import EventBus
from bruno_abilities.registry import AbilityRegistry

class MyAssistant(BaseAssistant):
    def __init__(self):
        self.event_bus = EventBus()
        self.ability_registry = AbilityRegistry()

    async def initialize(self):
        # Discover abilities
        await self.ability_registry.discover_abilities()

        # Subscribe to ability events
        self.event_bus.subscribe(
            "ability.completed",
            self.on_ability_completed
        )

    async def on_ability_completed(self, event):
        print(f"Ability {event.data['ability']} completed")
```

### With Bruno LLM

```python
from bruno_llm import LLMFactory
from bruno_abilities.base import ParameterExtractor

async def process_user_message(message: str):
    # Extract intent and parameters using LLM
    llm = LLMFactory.create("openai", model="gpt-4")

    # Use parameter extractor
    extractor = ParameterExtractor()
    params = extractor.extract_from_text(
        message,
        expected_params=["duration", "label"]
    )

    # Execute ability
    timer = TimerAbility()
    response = await timer.execute_action("set_timer", **params)
    return response
```

### With Bruno Memory

```python
from bruno_memory import MemoryFactory
from bruno_abilities.infrastructure import StateManager

# Use persistent state storage
memory = MemoryFactory.create("sqlite", database="bruno.db")
state_manager = StateManager(memory_backend=memory)

# Abilities automatically use state manager for persistence
timer = TimerAbility(state_manager=state_manager)
await timer.initialize()
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bruno_abilities --cov-report=html

# Run specific ability tests
pytest tests/abilities/test_timer_ability.py -v

# Run only unit tests
pytest -m unit

# Run integration tests
pytest -m integration
```

---

## 📊 Project Status

- **Version**: 0.1.0 (Alpha)
- **Python**: 3.10, 3.11, 3.12
- **Test Coverage**: 67% (164 tests passing)
- **Abilities**: 6 production-ready
- **Status**: Ready for PyPI publication

### Coverage by Module

| Module | Coverage |
|--------|----------|
| Timer Ability | 87% |
| Alarm Ability | 81% |
| Reminder Ability | 88% |
| Notes Ability | 90% |
| Todo Ability | 81% |
| Music Ability | 88% |
| Base Framework | 84-93% |
| Infrastructure | 18-26% (in progress) |

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/meggy-ai/bruno-abilities.git
cd bruno-abilities

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy bruno_abilities

# Run all pre-commit hooks
pre-commit run --all-files
```

---

## 📖 Documentation

- **API Reference**: [https://bruno-abilities.readthedocs.io](https://bruno-abilities.readthedocs.io)
- **User Guide**: [docs/user-guide.md](docs/user-guide.md)
- **Examples**: [examples/](examples/)
- **Architecture**: [docs/architecture.md](docs/architecture.md)

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Related Projects

- **[bruno-core](https://github.com/meggy-ai/bruno-core)** - Foundation framework
- **[bruno-llm](https://github.com/meggy-ai/bruno-llm)** - LLM provider implementations
- **[bruno-memory](https://github.com/meggy-ai/bruno-memory)** - Memory backends
- **[bruno-pa](https://github.com/meggy-ai/bruno-pa)** - Complete personal assistant

---

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/meggy-ai/bruno-abilities/issues)
- **Discussions**: [GitHub Discussions](https://github.com/meggy-ai/bruno-abilities/discussions)
- **Email**: contact@meggy-ai.com

---

## 🙏 Acknowledgments

Built with ❤️ by the Meggy AI team as part of the Bruno AI Assistant ecosystem.

**Made possible by**:
- [Pydantic](https://pydantic.dev/) - Data validation
- [structlog](https://www.structlog.org/) - Structured logging
- [pygame](https://www.pygame.org/) - Audio playback
- [dateparser](https://dateparser.readthedocs.io/) - Natural date parsing
