# ICSIA Proof of Concept - AI Planning for Intracytoplasmic Sperm Injection

## Overview

This proof of concept demonstrates the application of hierarchical AI planning to **Intracytoplasmic Sperm Injection Automation (ICSIA)**. The system uses **GTPyhop**, a Goal-Task-Network planner, to automatically generate step-by-step procedures for performing ICSI operations on oocytes.

ICSI is a specialized assisted reproductive technology where a single sperm is directly injected into an oocyte (egg cell) using precise micromanipulation. This process requires careful coordination of multiple instruments, computer vision, and precise positioning - making it an ideal candidate for AI-driven automation.

## System Architecture

The ICSIA planning system models the microscopic world of ICSI operations through:

- **Physical Elements**: Microscope (abstraction for X-Y stage movement), holding pipette, ICSI pipette
- **Locations**: Various droplets on the culture plate, parking positions
- **Oocyte Tracking**: Status, general droplet location, and precise computer vision position knowledge for each oocyte
- **State Management**: Current positions, held items, and operational status

### Key Components

1. **Actions** - Atomic operations (move elements, hold/release oocytes, inject sperm)
2. **Tasks** - Compound procedures (complete injection workflow, locate and focus)
3. **Goals** - Desired state changes (oocyte status, position knowledge, holding state)

## Modeling Assumptions

### Physical Environment
- **Culture Plate**: Contains multiple droplets (oocyte droplets, sperm droplet, PVP droplet)
- **Coordinate System**: Abstract locations rather than precise coordinates
- **Element Movement**: Simplified to discrete location changes
- **Microscope Movement**: Abstraction where "microscope" moves between locations - in reality, the X-Y motorized stage moves the culture plate while the microscope remains stationary
- **Fluid Dynamics**: Modeled as position invalidation after oocyte release

### Operational Assumptions
- **Computer Vision**: Mock implementation that can locate oocytes and determine position
- **Autofocus**: Simplified focus adjustment without detailed optical modeling  
- **Hardware Readiness**: All equipment assumed operational (placeholder for real status checking)
- **Timing**: No temporal constraints - focuses on logical sequencing

### Biological Assumptions
- **Oocyte States**: Fresh (available for injection) or Empty (no viable oocyte)
- **Position Knowledge**: Binary state (known/unknown) rather than precise coordinates
- **Sperm Viability**: Simplified to presence/absence in ICSI pipette
- **Success Rate**: 100% success for demonstration (no failure modes modeled)

## State Variables

The planner tracks the microscopic world through several state variables:

### Important Distinction: Location vs. Position

- **Oocyte Location**: Refers to the general droplet assignment (e.g., "l_droplet_01"). This is known from sample preparation and tells us which droplet contains the oocyte, but not where exactly within that droplet.

- **Oocyte Position**: Refers to the precise X,Y,Z coordinates within a droplet, determined through computer vision analysis. This fine-grained positioning is essential for accurate pipette targeting and is represented as "known" or "unknown" in the planner (actual coordinates are handled by the motor control subsystem).

### Element Positions
- `current_location`: Where each element (microscope, pipettes) is positioned
- `held_oocyte`: Which specific oocyte is currently held (None if none held)
- `icsi_p_has_sperm`: Whether the ICSI pipette contains sperm

### Oocyte Properties (by ID)
- `oocyte_location`: Which droplet each oocyte is in (general droplet assignment)
- `oocyte_status`: Current state (fresh, empty, injected)
- `oocyte_position`: Whether precise position within the droplet is known through computer vision analysis (known/unknown)

## Example Scenarios

The proof of concept includes four test scenarios that demonstrate different planning capabilities:

### Test 1: Standard ICSI Procedure
**Goal**: Inject sperm into oocyte_001
**Context**: Starting from initial state (no sperm captured, no oocytes held)
**Plan**: Complete 10-step procedure including positioning, computer vision, sperm capture, oocyte manipulation, and injection

### Test 2: Computer Vision Position Detection
**Goal**: Determine precise position of oocyte_001 within its droplet using computer vision
**Context**: Simpler task focusing on microscope positioning and imaging analysis
**Plan**: 3-step procedure for locate-and-focus workflow (move microscope to droplet, perform CV analysis, focus on detected oocyte)

### Test 3: Optimized Injection (Sperm Pre-captured)
**Goal**: Inject sperm into oocyte_001 with sperm already in ICSI pipette
**Context**: Demonstrates conditional planning - skips unnecessary sperm capture
**Plan**: Efficient 8-step procedure (saves 2 steps by skipping sperm capture)

### Test 4: Oocyte Switching
**Goal**: Inject oocyte_001 while currently holding a different oocyte (oocyte_002)
**Context**: Complex scenario requiring safe oocyte management
**Plan**: 10-step procedure including safe release of wrong oocyte before capturing target

## Planning Intelligence Demonstrated

### Adaptive Behavior
- **Conditional Actions**: Only performs necessary operations based on current state
- **Safe Operations**: Never releases oocytes in unsafe locations (parking positions)
- **Resource Management**: Efficiently handles equipment and biological materials

### Hierarchical Decomposition
- **High-level Goals**: Abstract objectives like "inject oocyte"
- **Task Decomposition**: Breaking complex procedures into manageable steps
- **Action Sequencing**: Proper ordering of atomic operations

### State-Aware Planning
- **Precondition Checking**: Ensures operations are valid in current state
- **Effect Prediction**: Updates world model after each action
- **Goal Verification**: Confirms objectives are achieved

## Technical Benefits

### For Laboratory Automation
- **Standardization**: Consistent procedures across different operators/sessions
- **Optimization**: Automatically finds efficient action sequences
- **Adaptability**: Handles variations in starting conditions
- **Safety**: Built-in constraints prevent unsafe operations

### For Research and Development
- **Rapid Prototyping**: Easy to modify procedures and test new workflows
- **Documentation**: Plans serve as detailed procedure documentation  
- **Training**: Generated plans can guide human operators
- **Analysis**: Can analyze optimal sequences and identify bottlenecks

## Future Extensions

This proof of concept provides a foundation for more sophisticated ICSIA systems:

- **Temporal Planning**: Adding timing constraints and scheduling
- **Uncertainty Handling**: Dealing with equipment failures and success rates
- **Multi-oocyte Workflows**: Parallel processing of multiple oocytes
- **Quality Assessment**: Integrating outcome prediction and optimization
- **Real Hardware Integration**: Connecting to actual microscopy and manipulation equipment

## Running the Examples

Execute the proof of concept with:
```bash
python3 icsia_poc.py [verbosity_level]
```

Where `verbosity_level` controls planning output detail (0=silent, 1=basic, 2=detailed, 3=verbose).

The system will display formatted results showing the generated plans for each test scenario, demonstrating the planner's ability to adapt to different initial conditions while maintaining safe and efficient operations.