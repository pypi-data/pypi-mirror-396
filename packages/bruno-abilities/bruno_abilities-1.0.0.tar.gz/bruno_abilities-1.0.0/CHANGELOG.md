# Changelog

All notable changes to bruno-abilities will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-12

### Added
-

### Changed
-

### Fixed
-


## [Unreleased]

## [0.1.0] - 2025-12-12

### Added

#### Core Framework (29 tests, 84-93% coverage)
- **BaseAbility** - Abstract base class extending bruno-core's AbilityInterface
- **ParameterExtractor** - Natural language parameter extraction from user messages
- **Decorators** - Retry logic, timeout handling, and rate limiting decorators
- **Metadata System** - Comprehensive ability metadata with parameters, examples, and version info
- **Validation Framework** - Pydantic-based parameter validation with user-friendly error messages

#### Time Management Abilities (49 tests, 82-88% coverage)
- **TimerAbility** - Countdown timers with callbacks, pause/resume, and cancellation
  - Actions: `set_timer`, `cancel_timer`, `list_timers`, `pause_timer`, `resume_timer`
  - Features: Multiple concurrent timers, labels, callback support

- **AlarmAbility** - Scheduled alarms with audio playback and recurrence
  - Actions: `set_alarm`, `cancel_alarm`, `list_alarms`, `snooze_alarm`, `dismiss_alarm`
  - Features: Recurring alarms, audio playback, snooze functionality

- **ReminderAbility** - Text-based reminders with persistence
  - Actions: `create_reminder`, `list_reminders`, `complete_reminder`, `delete_reminder`, `search_reminders`
  - Features: Flexible time formats, completion tracking, search by date/text

#### Information Storage Abilities (53 tests, 81-90% coverage)
- **NotesAbility** - Full CRUD operations on notes
  - Actions: `create_note`, `read_note`, `update_note`, `delete_note`, `list_notes`, `search_notes`
  - Features: Tags, search, timestamps, metadata

- **TodoAbility** - Task management with priorities and due dates
  - Actions: `create_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`, `search_tasks`
  - Features: Priority levels (low/normal/high/urgent), due dates, status tracking

#### Entertainment Abilities (33 tests, 88% coverage)
- **MusicAbility** - Local music playback control
  - Actions: `play`, `pause`, `stop`, `next`, `previous`, `set_volume`, `get_status`
  - Features: Playlist support, volume control, playback status

#### Infrastructure
- **StateManager** - Persistent state management for long-running operations
- **AbilityRegistry** - Dynamic ability discovery and loading via entry points
- **LifecycleManager** - Ability lifecycle management (initialize, shutdown, health checks)

#### Packaging & CI/CD
- **PyPI Package** - Complete pyproject.toml with 6 ability entry points
- **GitHub Actions Workflows**:
  - Multi-OS testing (Ubuntu, Windows, macOS)
  - Multi-Python testing (3.10, 3.11, 3.12)
  - Automated linting and code quality checks
  - Automated PyPI publishing on release
- **Pre-commit Hooks** - Ruff formatting, linting, and validation
- **Dependabot** - Weekly dependency updates for pip and GitHub Actions
- **Release Script** - Automated version bumping and release preparation

#### Documentation
- **README.md** - Comprehensive guide with installation, examples, and API reference
- **CONTRIBUTING.md** - Developer guide with setup, workflow, testing, and PR guidelines
- **API Documentation** - Complete docstrings for all public APIs (Google style)
- **Usage Examples** - Practical examples for all 6 abilities

### Technical Details

#### Requirements
- **Python**: 3.10, 3.11, 3.12
- **Core Dependencies**: bruno-core >= 0.1.0, bruno-llm >= 0.1.0, bruno-memory >= 0.1.0
- **Validation**: pydantic >= 2.0.0
- **Logging**: structlog >= 23.0.0
- **Date/Time**: python-dateutil >= 2.8.0, dateparser >= 1.1.0, pytz >= 2023.3
- **Audio** (optional): pygame >= 2.5.0

#### Testing
- **164 tests passing** - Full test coverage for all abilities
- **67% code coverage** - Abilities at 81-93%, infrastructure at 18-26%
- **Test organization**: Unit, integration, and slow test markers
- **Async testing**: Complete pytest-asyncio support

#### Code Quality
- **Type hints**: 100% type coverage with mypy validation
- **Formatting**: Ruff (100-char lines, consistent style)
- **Linting**: Ruff with pyupgrade, bugbear, comprehensions
- **Security**: Bandit security checks
- **Pre-commit**: Automated quality checks on every commit

#### Architecture
- **Async-first**: Built with asyncio for efficient concurrent operations
- **Event-driven**: Full integration with bruno-core EventBus
- **Type-safe**: Pydantic v2 models throughout
- **Extensible**: Easy custom ability creation via BaseAbility
- **Discoverable**: Entry point-based ability registration

### Known Limitations

1. **Infrastructure Coverage** - StateManager and registry modules at 18-26% coverage (planned for v0.2.0)
2. **Music Playback** - Local files only, no streaming support yet
3. **Natural Language** - Basic pattern matching for parameter extraction (LLM integration planned)
4. **Documentation** - API reference not yet published to ReadTheDocs

### Breaking Changes

None - this is the initial release.

### Contributors

- Meggy AI Team

[Unreleased]: https://github.com/meggy-ai/bruno-abilities/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/meggy-ai/bruno-abilities/releases/tag/v0.1.0
