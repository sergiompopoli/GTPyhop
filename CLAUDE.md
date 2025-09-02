# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GTPyhop is an automated planning system written in Python that uses hierarchical planning techniques to construct plans of action for tasks and goals. It can plan for both tasks (like Pyhop) and goals (inspired by GDP algorithm) in a unified framework called Goal-Task-Network (GTN) planning.

## Key Components and Architecture

### Core Architecture
- **gtpyhop.py**: Main planner implementation with classes for `State`, `Domain`, planning algorithms
- **test_harness.py**: Debugging utilities with `check_result()`, `pause()` functions for testing domains
- **Examples/**: Directory containing various domain implementations demonstrating different planning approaches

### Domain Structure Pattern
Each domain follows a consistent pattern:
1. Import gtpyhop and create a Domain object: `gtpyhop.Domain(domain_name)`
2. Define rigid relations using `gtpyhop.State('rigid relations')`
3. Declare actions using `gtpyhop.declare_actions()`
4. Declare task methods using `gtpyhop.declare_task_methods()`
5. Declare goal methods using `gtpyhop.declare_unigoal_methods()` or `gtpyhop.declare_multigoal_methods()`

### Planning Types
- **HTN (Hierarchical Task Network)**: Only uses tasks - see blocks_htn/, simple_htn.py
- **HGN (Hierarchical Goal Network)**: Only uses goals - see blocks_hgn/, simple_hgn.py  
- **GTN (Goal-Task Network)**: Uses both tasks and goals - see blocks_gtn/

## Running Examples

Navigate to the Examples directory and import any example module:

```python
# In Examples/ directory
import simple_htn                   # Simple task-planning examples
import simple_hgn                   # Simple goal-planning examples  
import backtracking_htn             # Backtracking demonstration
import logistics_hgn                # Goal-planning logistics domain
import blocks_gtn                   # Goal-task blocks world
import blocks_htn                   # Task-planning blocks world
import blocks_hgn                   # Goal-planning blocks world
import blocks_goal_splitting        # Sequential goal solving
import pyhop_simple_travel_example  # Pyhop backward-compatibility
```

## Testing and Debugging

- **test_harness.py** provides debugging utilities:
  - `th.check_result(actual, expected)` - Verify function results
  - `th.pause()` - Interactive debugging breaks
- **Examples/regression_tests.py** - Regression testing for examples
- Set `gtpyhop.verbose` to control debug output (0=none, 1=basic, 2=calls, 3=detailed)

## Development Notes

- Python 3 required (not compatible with Python 2)
- No external dependencies beyond standard Python libraries
- Actions and methods can return lists containing actions, tasks, and goals
- Goal verification can be disabled with `verify_goals = False`
- Each example domain is self-contained in its own module/package

## ICSIA POC Implementation (icsia-poc/icsia_poc.py)

### Project Description
The ICSIA (Intracytoplasmic Sperm Injection Assistant) POC demonstrates GTPyhop planning applied to automated laboratory procedures. This implementation models the complex process of ICSI in reproductive biology using hierarchical task networks and goal-oriented planning.

### Architecture Overview

**Actions vs Commands Pattern:**
- **Actions** (`move_element_to`, `hold_oocyte`, etc.): Pure planning functions that model state transitions for the planner
- **Commands** (`c_move_element_to`, `c_hold_oocyte`, etc.): Real-world execution functions that interface with hardware/CV systems
- **Separation Benefits**: Enables testing without hardware, modular implementation, and clean domain logic

### Key Components

**State Variables:**
- `current_location`: Positions of microscope, holding pipette, ICSI pipette
- `held_oocyte`: Which oocyte (if any) is currently held by holding pipette
- `icsi_p_has_sperm`: Whether ICSI pipette contains sperm
- `oocyte_location`: Physical location of each oocyte (which droplet)
- `oocyte_status`: Status of each oocyte ('fresh', 'injected', 'empty', 'damaged')
- `oocyte_position`: Whether oocyte position is 'known' or 'unknown' (for CV tracking)

**Core Actions:**
- `move_element_to(element, location)`: Move hardware components
- `hold_oocyte()`, `release_oocyte()`: Manipulate oocyte with holding pipette
- `capture_sperm()`, `release_sperm()`: Handle sperm with ICSI pipette
- `locate_oocyte_in_droplet(droplet)`: Computer vision localization
- `focus_on_oocyte(oocyte_id)`: Microscope autofocus
- `inject_sperm_into_oocyte()`: Perform sperm injection

**Task Methods:**
- `m_perform_icsi_injection_*`: High-level injection workflows
- `m_locate_and_focus`: Combined CV localization and focusing
- `m_prepare_for_injection`: Setup phase including sperm capture and oocyte handling
- `m_complete_injection`: Injection and cleanup phase

**Goal Methods:**
- `achieve_oocyte_status_goal`: Change oocyte status (fresh → injected)
- `achieve_oocyte_position_goal`: Localize oocyte position (unknown → known)
- `achieve_held_oocyte_goal`: Control which oocyte is held
- `achieve_icsi_has_sperm`: Control sperm capture state

### Error Simulation & Execution

**Realistic Hardware Failures:**
- Movement failures (10% hardware failure, 15% microscope positioning errors)
- Pipette issues (20% suction failure, 5-8% release mechanism failures)
- Computer vision failures (15% detection failure)
- Sperm handling problems (25% no viable sperm, 10% pipette blockage)
- Injection complications (18% membrane penetration failure, 12% oocyte damage)
- Autofocus failures (12% focus mechanism failure)

**Error Handling Strategy:**
- **Recoverable errors**: Return `False` to trigger replanning (e.g., movement failures, CV failures)
- **State-changing errors**: Update state and continue (e.g., oocyte position becomes 'unknown')
- **Terminal errors**: Complete failures for irreversible damage (e.g., oocyte destruction)

**Plan Execution:**
- Uses `run_lazy_lookahead()` for execution with automatic replanning on failures
- Commands provide detailed error messages for debugging and monitoring
- Precondition checking in commands prevents logical inconsistencies

### Key Implementation Features

**Precondition Enforcement:**
- Focus requires oocyte position to be 'known' (prevents focusing on unlocalized oocytes)
- Hold oocyte requires 'fresh' status and 'known' position
- Injection requires both pipettes at same location with proper states

**Logical Dependencies:**
- Computer vision must succeed → oocyte position becomes 'known' → focusing becomes possible
- Sperm must be captured → injection becomes possible
- Oocyte must be held → injection can proceed

**Testing Framework:**
- 4 comprehensive test cases covering different initial conditions
- Planning tests demonstrate goal achievement under various scenarios
- Execution tests show error handling and replanning capabilities
- Formatted output with clear success/failure reporting

### Usage Examples

**Basic Planning:**
```python
state = create_initial_state()
goal = [('oocyte_status', 'oocyte_001', 'injected')]
plan = gtpyhop.find_plan(state, goal)
```

**Plan Execution with Error Handling:**
```python
final_state = gtpyhop.run_lazy_lookahead(state, goal)
# Automatically handles hardware failures and replanning
```

**Custom Verbosity:**
```bash
python icsia_poc.py 2  # Verbosity level 2 for detailed output
```

### Development Session Achievements

1. **Implemented complete ICSIA domain** with 8 actions, 4 task methods, 5 goal methods
2. **Created command layer** with realistic error simulation for hardware interface
3. **Added comprehensive error handling** with 15+ different failure scenarios
4. **Fixed logical inconsistencies** in precondition checking and state management
5. **Established clean separation** between planning (actions) and execution (commands)
6. **Implemented robust test suite** with multiple scenarios and formatted output
7. **Demonstrated adaptive replanning** in face of realistic hardware failures
8. **Refactored codebase into modular architecture** with separate files for different components

### Code Architecture and Organization

**Modular File Structure:**
- `icsia_poc.py` - Main entry point with domain registration, test framework, and execution
- `icsia_poc_state.py` - State management functions and helper utilities
- `icsia_poc_actions.py` - Action definitions (planning) and command implementations (execution)
- `icsia_poc_tasks.py` - Task method definitions for hierarchical planning
- `icsia_poc_goals.py` - Goal method definitions for state-based planning

**Benefits of Modular Design:**
- **Maintainability**: Each component has focused responsibility and clear boundaries
- **Reusability**: Functions can be imported individually across different modules
- **Testability**: Individual components can be developed and tested in isolation
- **Scalability**: Easy to extend with new actions, tasks, or goals without affecting existing code
- **Clarity**: Separates different types of planning knowledge (state, actions, tasks, goals)

**Import Structure:**
- All modules follow "icsia_poc_" naming convention for consistency
- Clean import statements in main file show dependencies clearly
- Proper separation between planning logic and hardware execution layer

The implementation showcases GTPyhop's capabilities for complex real-world planning problems with realistic failure modes and recovery strategies, now organized in a maintainable modular architecture.