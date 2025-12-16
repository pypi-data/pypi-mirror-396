# artificer-workflows Architecture

## Core Principles

- **Simplicity over features**: We prioritize clean architecture over feature richness. Every addition should simplify or remove something.
- **Workflow as state machine**: Workflows are linear or branching state machines where each step returns the next step class.
- **Minimal persistence**: Use simple JSON-based storage. No database until absolutely necessary.
- **Per-workflow state tracking**: Track executed steps per workflow instance, not globally.
- **MCP-native**: Workflows expose themselves as MCP tools and prompts for natural AI interaction.

## System Overview

artificer-workflows is a Python framework for defining multi-step workflows that AI agents can execute. Workflows are defined as classes with nested Step classes. Each step provides instructions (via templates) and validates output (via Pydantic models). The framework integrates with FastMCP to expose workflows as tools.

## Components

### Settings Module

**Responsibility**: Centralized configuration for the application.

**Key Design Decisions**:
- Single source of truth for application-wide constants
- Simple module with constants, no complex configuration management
- Imported by other modules as needed

**Interactions**: Imported by store.py and other modules requiring configuration

### Workflow Class

**Responsibility**: Base class for defining workflows. Manages workflow lifecycle, step registration, and MCP tool registration.

**Key Design Decisions**:
- Uses `__init_subclass__` to auto-register workflows and set up infrastructure (Jinja2 env, Step base class)
- Each workflow gets its own Step base class via factory function to avoid cross-contamination
- Stores only `_start_step` (the step class to begin with), not a dict of all steps
- Instance attribute `steps` tracks executed step instances per workflow execution

**Interactions**: Creates Step base class, registers with MCP, manages workflow execution

### Step Class (Factory-Created)

**Responsibility**: Base class for workflow steps. Each workflow gets its own Step class via `create_step_class()`.

**Key Design Decisions**:
- Steps are classes, not instances, until workflow execution
- Uses `__init_subclass__` to register steps and create MCP tools
- `start()` returns instructions (string)
- `complete(output)` validates output and returns next step class (or None to end)
- Steps access `previous_result` to get output from prior step

**Interactions**: Registered by workflow, instantiated during execution, chains to next step

### WorkflowsStore

**Responsibility**: Persist workflow execution state using JSON.

**Key Design Decisions**:
- Uses JSON for robustness and debuggability (pickle was too fragile)
- Stored in project directory (`.artificer/workflow_executions.json`)
- Tracks workflows by `workflow_id`
- Simple dict-based storage: `{workflow_id: workflow_dict}`
- Workflows serialize via `to_dict()` / deserialize via `from_dict()`
- Configuration imported from settings module

**Interactions**: Called by Workflow.start_workflow() and Workflow.complete_step()

### MCP Integration

**Responsibility**: Expose workflows as MCP tools and prompts.

**Key Design Decisions**:
- Each workflow gets two tools: `{WorkflowName}__start_workflow` and `{WorkflowName}__complete_step`
- Each step gets a tool: `{WorkflowName}__{StepName}`
- Workflows are also exposed as prompts for quick access
- Uses FastMCP for tool registration

**Interactions**: Workflows register themselves via `Workflow.register(mcp)`

## What We DON'T Do

- ❌ **Complex state machines** - No parallel steps, no dynamic routing beyond step.complete() returning next class
- ❌ **Database persistence** - No SQL, no ORM. JSON is sufficient for now.
- ❌ **Global step registry** - Steps are per-workflow. No shared `_steps` dict.
- ❌ **Artifact file management** - Workflows track artifact metadata, but don't manage files (that's the agent's job)
- ❌ **Retry logic beyond step level** - If a step fails max_retries, workflow fails. No fancy recovery.
- ❌ **Validation at class definition time** - Type hints use strings and `# type: ignore` to avoid circular imports
- ❌ **Complex configuration management** - Simple constants in settings.py, no config files or env var loading (yet)

## Data Flow

1. **Workflow Start**: User/agent calls `start_workflow()` MCP tool
   - Workflow instantiates `_start_step` class
   - Calls `step.render()` to generate prompt
   - Saves workflow to store
   - Returns prompt to agent

2. **Step Execution**: Agent reads prompt, performs work, calls `complete_step()` with output
   - Workflow validates output using Pydantic model from `complete()` signature
   - Calls `step.complete(output)` to get next step class
   - If next step exists: instantiate it, render prompt, save workflow, return prompt
   - If no next step: mark workflow complete

3. **Step Chaining**: Each step's `complete()` method returns the next step class
   - Can return different classes based on output (branching logic)
   - Returns `None` to end workflow

## Extension Points

- **Custom Workflows**: Subclass `Workflow`, set `templates_dir`, define `Step` subclasses
- **Custom Templates**: Override `step_template` or use Jinja2 templates in `templates_dir`
- **Output Models**: Define Pydantic models for step output validation
- **Branching Logic**: Return different step classes from `complete()` based on output

## Recent Changes

### 2025-11-26 - Settings Module for Configuration

**What changed**: Created `settings.py` module and moved `APP_NAME` constant from `store.py` to centralize configuration.

**Why**: Establishes a clear separation of concerns. The store module should focus on persistence, not configuration. Having a dedicated settings module makes configuration discoverable and extensible.

**What was removed/simplified**:
- ✅ Removed configuration constants from business logic modules
- ✅ Store module now has single responsibility (persistence only)

**Architecture changes**:
- Add new `artificer_workflows/settings.py` module
- Define `APP_NAME = "artificer"` in settings.py
- Update `store.py` to import `APP_NAME` from settings

**Components affected**:
- `artificer_workflows/settings.py`: New module for application configuration
- `artificer_workflows/store.py`: Updated to import APP_NAME from settings

**Rationale**:
- Follows separation of concerns principle
- Makes configuration easily discoverable and maintainable
- Sets pattern for future configuration needs
- Minimal change with clear architectural benefit

### 2025-11-26 - Workflow Inspection Tool

**What changed**: Adding `inspect_workflow()` classmethod to the `Workflow` base class. This tool provides runtime visibility into workflow execution state by exposing the `workflow.steps` attribute.

**Why**: Enable agents to inspect workflow execution history for debugging, progress tracking, and error investigation. This addresses the gap between starting a workflow and understanding what has happened during its execution.

**What was removed/simplified**:
- ✅ The commented-out Mermaid diagram generator in `inspect.py` will be removed or reconsidered - it served a similar inspection purpose but was more complex and static
- ✅ No need for separate documentation or logging systems - inspection data comes directly from the workflow state

**Architecture changes**:
- Add `inspect_workflow(workflow_id: str)` classmethod to `Workflow` base class
- Returns JSON-serializable dict with all step details: ID, name, status, timestamps, results
- Registered as MCP tool with pattern `{WorkflowName}__inspect_workflow`
- Reads workflow from `WorkflowsStore` and serializes `steps` dict
- No changes to persistence layer - uses existing workflow state

**Components affected**:
- `artificer_workflows/workflow.py`: Add `inspect_workflow()` method and tool registration
- `artificer_workflows/inspect.py`: Remove or archive commented-out code

**Rationale**:
- Maintains simplicity by reusing existing state tracking (`workflow.steps`)
- Follows MCP-native pattern by exposing as a tool
- Provides debugging capability without adding complexity
- Enables agents to self-diagnose workflow issues

### 2025-11-26 - Architecture Review Step

**What changed**: Added `ArchitectureReviewStep` to the AddFeature workflow, positioned between CollectRequirements and CreatePlan.

**Why**: To enforce architectural discipline and prevent complexity creep. Forces developers/agents to review ARCHITECTURE.md and identify simplifications before implementing features.

**What was removed/simplified**: None (this is an addition, but future features using this workflow will be required to identify simplifications)

**Components affected**:
- `examples/basic_workflow.py`: Added `ArchitectureReviewOutput` model and `ArchitectureReviewStep` class
- `examples/templates/add_feature/`: Added `review_architecture.md` template

### 2025-11-26 - Removed `_steps` Class Dict

**What changed**: Removed `_steps` class-level dict. Now `_start_step` stores the step class directly instead of the step name.

**Why**: Simpler design. No need for intermediate lookup. Reduces class-level state.

**What was removed/simplified**:
- ❌ `_steps` dict
- ❌ String-based step lookup
- ❌ Step registration in `_steps`

**Components affected**:
- `artificer_workflows/workflow.py`: Removed `_steps` initialization and registration

### 2025-11-26 - Removed `from __future__ import annotations`

**What changed**: Replaced `|` union syntax with `Union` and `Optional` from `typing`.

**Why**: The future import is unnecessary baggage. Using `Union`/`Optional` is more explicit and compatible.

**What was removed/simplified**:
- ❌ `from __future__ import annotations`
- ✅ Added `Union` and `Optional` imports
- Changed `type["Step"] | None` → `Optional[type["Step"]]`
- Changed `BaseModel | dict` → `Union[BaseModel, dict]`

**Components affected**:
- `artificer_workflows/workflow.py`
- `artificer_workflows/store.py`

### 2025-11-26 - Fixed Refactoring Bugs

**What changed**: Fixed 9 bugs introduced during refactoring (pickle file mode, missing step lookup, etc.)

**Why**: Refactor had good architectural vision but introduced runtime errors.

**What was removed/simplified**: N/A (bug fixes)

**Components affected**: `artificer_workflows/workflow.py`, `artificer_workflows/store.py`

## Recent Changes

### 2025-11-28 - Move Basic Workflow to Dev MCP Server

**What changed**: Moving `examples/basic_workflow.py` to `.mcp/server.py` and its templates to `.mcp/templates/add_feature/`.

**Why**: The basic_workflow.py implements the AddFeature workflow which is useful for developing features on the project itself. This fits the "dev MCP" pattern - an MCP server that provides development tools for the project. Moving it to `.mcp/server.py` makes it clear this is development infrastructure, not just an example.

**What was removed/simplified**:
- ✅ Removed `examples/` directory entirely (was only housing one workflow)
- ✅ Simplified project structure by having one clear location for dev tooling (`.mcp/`)
- ✅ Eliminated confusion about whether basic_workflow.py is an example or production tooling

**Architecture changes**:
- Create `.mcp/` directory for development MCP server
- Move `examples/basic_workflow.py` → `.mcp/server.py`
- Move `examples/templates/add_feature/` → `.mcp/templates/add_feature/`
- Remove `examples/` directory
- Update CLAUDE.md to reference new location

**Components affected**:
- `.mcp/server.py`: Dev MCP server with AddFeature workflow (moved from examples/)
- `.mcp/templates/add_feature/`: Workflow templates (moved from examples/templates/)
- `CLAUDE.md`: Update documentation to reflect new structure

**Rationale**:
- Establishes clear separation: `.mcp/` for dev tooling, future directories for production code
- Follows simplicity principle by removing unnecessary directory structure
- Makes it obvious that this workflow is for developing the project itself
- Aligns with the "dev MCP" pattern mentioned in project documentation

### 2025-11-28 - Workflow Diagram Generation Tool

**What changed**: Adding a diagram generation module (`artificer_workflows/diagram.py`) and MCP tool to generate Mermaid diagrams from workflow class definitions.

**Why**: Enable visual understanding of workflow structure for documentation, debugging, and development. Using type hint introspection aligns with our "no magic" principle - the diagram is derived directly from the code structure.

**What was removed/simplified**:
- ✅ No changes to workflow class definitions required - uses pure introspection
- ✅ Eliminates need for manual diagram maintenance - diagrams are always in sync with code
- ✅ Simpler than commented-out Mermaid generator in old `inspect.py` - focuses only on structure, not runtime state

**Architecture changes**:
- Add `artificer_workflows/diagram.py` module with `generate_workflow_diagram(workflow_class)` function
- Function inspects workflow steps using Python's `inspect` and `typing` modules
- Extracts graph structure from `complete()` method return type hints
- Handles union types for branching (e.g., `type["StepA"] | type["StepB"]`)
- Handles `None` return type for terminal steps
- Generates Mermaid flowchart syntax
- Register as MCP tool in `.mcp/server.py` for easy access during development

**Components affected**:
- `artificer_workflows/diagram.py`: New module for diagram generation (pure utility, no dependencies on workflow execution)
- `.mcp/server.py`: Add tool to expose diagram generation for AddFeature workflow

**Rationale**:
- Maintains simplicity by being a pure inspection utility - no changes to core workflow framework
- Follows MCP-native pattern by exposing as a development tool
- Leverages Python's introspection capabilities instead of requiring explicit graph definition
- Diagrams are always accurate since they're derived from source code
- Useful for documentation, onboarding, and understanding complex workflows

### 2025-11-29 - Test Feature (Workflow Debug Test)

**What changed**: Testing the AddFeature workflow execution to debug serialization issues.

**Why**: To verify workflow state transitions and artifact passing work correctly after fixing pickle deserialization bug.

**What was removed/simplified**:
- ✅ Cleared old pickled workflow data that referenced non-existent classes

**Architecture changes**: None - this is a test execution to verify framework functionality.

**Components affected**: None - testing only

**Rationale**: Ensure workflow framework is stable before adding more features.

### 2025-11-29 - Configurable Local Storage Path

**What changed**: Moving workflow storage from `~/.config/artificer` to `.artificer/` in the project directory, with environment variable override support.

**Why**: Project-local storage is more appropriate for development workflows. Each project should have its own workflow history. Users can override with `ARTIFICER_WORKFLOWS_DIR` environment variable for custom locations.

**What was removed/simplified**:
- ✅ Removed `appdirs` dependency - no longer needed for simple local directory
- ✅ Removed module-level path computation from `store.py` - moved to settings module
- ✅ Storage logic consolidated in settings module (single responsibility)

**Architecture changes**:
- Update `artificer_workflows/settings.py`:
  - Add `WORKFLOWS_DIR` setting with `.artificer/` default
  - Check `ARTIFICER_WORKFLOWS_DIR` environment variable first
  - Fall back to `.artificer/` if env var not set
- Update `artificer_workflows/store.py`:
  - Import `WORKFLOWS_DIR` from settings instead of computing path
  - Remove `appdirs` import and usage
  - Simplify module-level initialization
- Remove `appdirs` from project dependencies

**Components affected**:
- `artificer_workflows/settings.py`: Add storage path configuration
- `artificer_workflows/store.py`: Use settings instead of appdirs
- `pyproject.toml`: Remove appdirs dependency

**Rationale**:
- Project-local storage is more intuitive for development workflows
- Simpler codebase with one less dependency
- Follows existing pattern of centralizing configuration in settings module
- Environment variable provides flexibility for custom locations
- Maintains backward compatibility through WorkflowsStore constructor parameter

### 2025-11-29 - Package Namespace Refactoring

**What changed**: Refactoring from `artificer_workflows` package to `artificer.workflows` namespace structure for cleaner, more pythonic imports.

**Why**: Python convention favors dot notation for hierarchical packages. The current `artificer_workflows` name with underscore is less intuitive and doesn't scale well if we want to add other submodules under the `artificer` namespace. This change improves the developer experience and aligns with Python best practices.

**What was removed/simplified**:
- ✅ Simplified import syntax - from `from artificer_workflows.workflow import Workflow` to `from artificer.workflows.workflow import Workflow`
- ✅ Better namespace organization - enables future expansion with other `artificer.*` submodules
- ✅ Cleaner package structure aligned with Python conventions

**Architecture changes**:
- Rename `artificer_workflows/` directory to `artificer/workflows/`
- Create `artificer/__init__.py` as top-level package entry point
- Keep existing modules under `artificer/workflows/`:
  - `workflow.py`, `operations.py`, `store.py`, `settings.py`, `types.py`
- Update `pyproject.toml`:
  - Change packages from `["artificer_workflows"]` to `["artificer"]`
  - Keep distribution name as `artificer-workflows` for PyPI (no breaking change)
- Update all imports in:
  - `.mcp/server.py` (dev MCP server)
  - `artificer/workflows/__init__.py` (internal imports)
  - `README.md` (documentation examples)
  - `CLAUDE.md` (if needed)

**Components affected**:
- All files in `artificer_workflows/` → moved to `artificer/workflows/`
- `.mcp/server.py` - update imports to use new namespace
- `pyproject.toml` - update package configuration
- `README.md` - update example code
- Internal imports within workflow modules

**Refactoring approach**:
1. Create new directory structure: `artificer/workflows/`
2. Move all files from `artificer_workflows/` to `artificer/workflows/`
3. Create proper `__init__.py` files for both `artificer/` and `artificer/workflows/`
4. Update all import statements throughout codebase
5. Update `pyproject.toml` package configuration
6. Delete old `artificer_workflows/` directory
7. Test that imports work correctly

**Rationale**:
- Follows Python naming conventions (PEP 8)
- Enables future modular expansion under `artificer.*` namespace
- Improves code readability and developer experience
- No functional changes - pure structural refactoring
- Clean break acceptable since project is in alpha stage (0.1.0a5)

**Architectural principles maintained**:
- Simplicity: Pure rename/move, no logic changes
- MCP-native: All MCP integrations remain unchanged
- Minimal persistence: No changes to storage logic
- Workflow state machine: Core workflow logic untouched

### 2025-12-07 - JSON-based Workflow Persistence

**What changed**: Replacing pickle-based workflow serialization with JSON for robustness and debuggability.

**Why**: Pickle is fragile - when class definitions change or are removed, deserialization fails with cryptic errors (e.g., "Can't get attribute 'TestWorkflow'"). JSON provides human-readable storage that survives class changes.

**What was removed/simplified**:
- ✅ Remove `pickle` dependency from store.py
- ✅ Human-readable workflow state (can inspect `.artificer/workflow_executions.json`)
- ✅ More robust deserialization - class lookup happens explicitly

**Architecture changes**:
- Update `store.py` to use JSON instead of pickle
- Add `to_dict()` method to serialize workflows (workflow_id, status, steps, etc.)
- Add `from_dict()` classmethod to deserialize workflows
- Store step class names as strings, resolve them on load via workflow's Step subclasses
- Pydantic models serialize naturally to dicts via `.model_dump()`
- Change file extension from `.pkl` to `.json`

**Components affected**:
- `artificer/workflows/store.py`: JSON serialization/deserialization
- `artificer/workflows/workflow.py`: Add to_dict/from_dict methods

**Rationale**:
- Robustness: Class changes don't break existing workflow state
- Debuggability: Can inspect workflow state in any text editor
- Simplicity: JSON is more straightforward than pickle magic
- No external dependencies: json is stdlib

### 2025-12-08 - Add Examples Directory with Banana Catcher Game

**What changed**: Creating an `examples/` directory to house standalone example files that demonstrate workflow capabilities or serve as test artifacts.

**Why**: The AddFeature workflow needed a location to output a self-contained HTML game example. Unlike the `.mcp/` directory (which contains development tooling), `examples/` is for standalone demonstrations.

**What was removed/simplified**:
- No removals needed - this is a clean addition to an empty location

**Architecture changes**:
- Create `examples/` directory for standalone example files
- Add `banana_catcher.html` - a self-contained 2D game with inline JS/CSS

**Components affected**:
- `examples/banana_catcher.html`: New standalone HTML game

**Rationale**:
- Separates development tooling (`.mcp/`) from examples/demonstrations
- Self-contained HTML files are good for quick demos without dependencies
- Provides a location for future standalone examples

### 2025-12-08 - Add Wizard Blaster Game

**What changed**: Adding a second example game `wizard_blaster.html` to the `examples/` directory.

**Why**: Another standalone HTML game to demonstrate workflow output capabilities. This game has more complex mechanics (projectiles, enemies, waves) compared to the banana catcher.

**What was removed/simplified**:
- No removals needed - follows established pattern for examples

**Architecture changes**:
- Add `examples/wizard_blaster.html` - top-down shooter with fireballs and enemies

**Components affected**:
- `examples/wizard_blaster.html`: New standalone HTML game

**Rationale**:
- Follows existing pattern established by banana_catcher.html
- Demonstrates workflow can produce varied outputs
- Self-contained with no dependencies

### 2025-12-08 - CLI Integration via WorkflowModule

**What changed**: Adding `WorkflowModule` class to integrate artificer-workflows with artificer-cli. This creates a `workflows` command group with subcommands: `list`, `start`, `resume`, `pause`.

**Why**: Enable CLI-based workflow management alongside MCP-based management. Users should be able to interact with workflows via terminal when not using an AI agent.

**What was removed/simplified**:
- ✅ Reuse existing `operations.py` functions (list_workflows, resume_workflow, pause_workflow) - no duplication
- ✅ No changes to core Workflow class - CLI wraps existing functionality
- ✅ Leverage existing workflow store and serialization

**Architecture changes**:
- Add `artificer/workflows/module.py` with `WorkflowModule` class
- WorkflowModule implements `ArtificerModule.register(cli, config)` interface
- Creates `workflows` Click group with subcommands
- Commands wrap existing operations from `operations.py`
- Workflow discovery via `[tool.artificer.workflows]` config in pyproject.toml

**Components affected**:
- `artificer/workflows/module.py`: New module implementing CLI integration
- `pyproject.toml`: Update to include click as optional dependency for CLI

**Rationale**:
- Follows principle of wrapping existing functionality, not duplicating
- Maintains MCP-native pattern (MCP tools remain primary interface)
- CLI provides alternative interface for direct user interaction
- Uses existing operations module - single source of truth for workflow operations

### 2025-12-08 - Workflow-Specific Configuration

**What changed**: WorkflowModule reads `[tool.artificer.workflows]` section from pyproject.toml to discover workflow entrypoints. Also adding `[tool.artificer]` config to artificer-workflows project itself.

**Why**: Enable `artificer workflows start AddFeature` to work in the artificer-workflows project for development. The general `entrypoint` in `[tool.artificer]` is for custom modules, but workflows need their own entrypoint to import workflow definitions.

**What was removed/simplified**:
- ✅ WorkflowModule reads config directly instead of relying on artificer-cli to pass it
- ✅ Self-contained configuration - no changes needed to artificer-cli

**Architecture changes**:
- WorkflowModule reads pyproject.toml directly for `[tool.artificer.workflows].entrypoint`
- Add `[tool.artificer]` section to artificer-workflows pyproject.toml
- Add `[tool.artificer.workflows]` section pointing to `.mcp.server`

**Components affected**:
- `artificer/workflows/module.py`: Add config reading for workflow-specific settings
- `pyproject.toml`: Add artificer configuration sections

**Rationale**:
- Keeps workflow config self-contained in artificer-workflows package
- No changes required to artificer-cli for workflow-specific settings
- Follows existing pattern of reading pyproject.toml for configuration

### 2025-12-08 - Agent TUI Launch from CLI

**What changed**: Modifying the `workflows start` command to launch an agent TUI instead of just printing the workflow prompt.

**Why**: Enable a seamless workflow experience where `artificer workflows start <name>` immediately opens an AI agent with context about the workflow, rather than requiring the user to manually copy/paste the prompt to an agent.

**What was removed/simplified**:
- No removals - this extends existing `start_cmd` functionality
- ✅ Reuses existing workflow lookup and validation logic
- ✅ No changes to core workflow framework - purely CLI layer modification

**Architecture changes**:
- Modify `artificer/workflows/module.py`:
  - `start_cmd` reads `AGENT_COMMAND` env var (required, no default)
  - If `AGENT_COMMAND` not set, display helpful error message
  - Construct initial prompt: "Starting a `<workflow_name>` workflow via the `<mcp_server>` MCP server. Start the first step."
  - Launch agent command via subprocess with the prompt
  - Assumes agent already has access to MCP server (pre-configured)

**Components affected**:
- `artificer/workflows/module.py`: Modify `start_cmd` to launch agent TUI

**Rationale**:
- Follows principle of minimal change - only modifies the CLI command, not workflow logic
- Uses environment variable for configuration (consistent with `ARTIFICER_WORKFLOWS_DIR` pattern)
- Assumes pre-configured MCP connection to keep complexity low
- No default agent command prevents surprising behavior

### 2025-12-09 - 3D Zombie Shooter Game Example

**What changed**: Adding `examples/zombie-shooter.html` - a 3D first-person shooter zombie survival game using Three.js.

**Why**: Demonstrates workflow capability to produce complex, self-contained interactive content. This is the most ambitious example yet, featuring 3D graphics, wave-based gameplay, weapon systems, and a boss fight.

**What was removed/simplified**:
- No removals - follows established pattern for examples directory
- Uses CDN-hosted Three.js to keep file self-contained

**Architecture changes**:
- Add `examples/zombie-shooter.html` - self-contained 3D FPS game

**Components affected**:
- `examples/zombie-shooter.html`: New standalone HTML game

**Rationale**:
- Follows existing pattern established by banana_catcher.html
- Demonstrates workflow can produce sophisticated 3D interactive content
- Self-contained with CDN dependencies only
- Showcases the full AddFeature workflow from requirements to implementation

### 2025-12-09 - Zombie City Game Enhancements

**What changed**: Major enhancement to `examples/zombie-shooter.html` adding faster zombies, unique wave bosses, diverse zombie types, more weapons, and progressive difficulty.

**Why**: User requested gameplay improvements to increase difficulty, variety, and replayability.

**What was removed/simplified**:
- ✅ Consolidate zombie creation into factory function `createZombie(type)` instead of hardcoded mesh construction
- ✅ Unify boss and mini-boss logic into single `createBoss(type)` factory with config objects
- ✅ Move hardcoded values into CONFIG object for centralized tuning
- ✅ Simplify weapon switching logic with consistent ammo drop system

**Architecture changes (zombie-shooter.html)**:
- Refactor zombie spawning: Extract `ZOMBIE_TYPES` config object with stats and visual properties
- Refactor boss system: Add `BOSS_TYPES` config object, each wave 3+ can have a mini-boss
- Add weapon types: Extend `WEAPONS` array with SMG, Sniper Rifle, Flamethrower
- Unify spawn logic: Single `spawnEnemy(type, isBoss)` function handles all enemy types
- Progressive difficulty: Scale spawn rate and stats per wave in CONFIG calculations

**Components affected**:
- `examples/zombie-shooter.html`: Complete game enhancement

**Refactorings before implementation**:
1. Extract `createZombieMesh(type)` factory function from `spawnZombie()`
2. Extract `ZOMBIE_TYPES` config object with speed/health/damage/color properties
3. Extract `BOSS_TYPES` config object with wave number, name, stats, abilities
4. Move all magic numbers into CONFIG section at top of file
5. Create unified `spawnEnemy()` function used by both zombie and boss spawning

**Rationale**:
- Config-driven approach makes balancing easier without code changes
- Factory functions reduce code duplication between enemy types
- Centralized CONFIG enables rapid iteration on game feel
- Follows simplicity principle: configuration over conditional logic

### 2025-12-09 - Visual and Audio Enhancements

**What changed**: Adding immersive audio system, first-person weapon rendering, bullet tracers, and powerup icons to `examples/zombie-shooter.html`.

**Why**: User requested visual polish and audio feedback to create a more atmospheric and polished gameplay experience.

**What was removed/simplified**:
- ✅ Consolidate audio generation into `AudioManager` class instead of scattered audio calls
- ✅ Centralize weapon visual configs alongside existing `WEAPONS` array
- ✅ Use object pooling for tracers to avoid GC pressure
- ✅ Reuse existing powerup indicator system with icon additions

**Architecture changes (zombie-shooter.html)**:
- Add `AudioManager` class encapsulating Web Audio API for all sound generation
- Add `WeaponRenderer` system for first-person gun model management
- Add `TracerManager` for bullet trail visualization with pooling
- Extend powerup CSS with icon support using Unicode symbols
- Add `WEAPON_VISUALS` config for gun model definitions

**Components affected**:
- `examples/zombie-shooter.html`: Audio, visual weapon, and UI enhancements

**New modules/systems**:
1. `AudioManager`: Handles all procedural sound generation via Web Audio API
   - Weapon sounds (per-weapon type)
   - Ambient music generation
   - Game event sounds (damage, powerup, wave start)
2. `WeaponRenderer`: Manages first-person weapon display
   - Gun model creation per weapon type
   - Idle bob animation
   - Recoil animation on fire
3. `TracerManager`: Bullet trail visualization
   - Object pooling for performance
   - Fade-out animation
   - Weapon-specific colors

**Rationale**:
- Encapsulated systems prevent audio/visual code from polluting game logic
- Config-driven approach continues pattern from previous enhancement
- Object pooling for tracers prevents frame drops from GC
- Web Audio API allows no-dependency audio generation

### 2025-12-09 - Vertical Gameplay and Difficulty Increase

**What changed**: Adding jumping mechanics, elevated platforms, zombie climbing/jumping, and doubling zombie counts in `examples/zombie-shooter.html`.

**Why**: User requested more vertical gameplay to add tactical depth and significantly increased difficulty.

**What was removed/simplified**:
- ✅ Consolidate physics into simple velocity/gravity system (no physics engine needed)
- ✅ Reuse existing collision detection with height checks added
- ✅ Extend existing zombie AI state machine with climbing/jumping states
- ✅ Platform generation reuses existing building placement logic patterns

**Architecture changes (zombie-shooter.html)**:
- Add `PhysicsState` to player: velocityY, isGrounded, canJump
- Add `PLATFORM_TYPES` config for crates, vehicles, barriers, rooftop access points
- Extend zombie state machine with `climbing` and `jumping` states
- Add height-aware pathfinding: zombies detect player elevation and choose climb/jump
- Double zombie counts in CONFIG: `baseZombiesPerWave: 16`, `zombiesPerWaveScale: 10`

**Components affected**:
- `examples/zombie-shooter.html`: Jumping, platforms, zombie AI, difficulty tuning

**New systems**:
1. `PlayerPhysics`: Simple gravity/jump velocity system
   - SPACEBAR triggers jump if grounded
   - Gravity applied each frame
   - Ground/platform detection for landing
2. `PlatformManager`: Manages elevated surfaces
   - Crates, vehicles, barriers, rooftop ledges
   - Collision boxes for landing detection
   - Visual mesh generation
3. `ZombieVerticalAI`: Extended zombie behaviors
   - Climbing state for scaling platforms (slower movement)
   - Jump ability for runner-type zombies
   - Height-aware target tracking

**Rationale**:
- Simple physics keeps code maintainable (no external physics engine)
- Extends existing patterns rather than replacing them
- Config-driven platform and difficulty tuning
- Zombie AI extension preserves existing behavior as base case

## Future Considerations

- **Better Error Handling**: More structured error types instead of generic exceptions
- **Async Support**: If workflows need to wait for external processes
- **Multi-tenancy**: If workflows need to support multiple users/projects
