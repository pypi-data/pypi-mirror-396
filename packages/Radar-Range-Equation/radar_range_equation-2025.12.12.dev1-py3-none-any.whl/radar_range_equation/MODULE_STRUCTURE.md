# Radar Range Equation - Module Structure

## Overview

The `radar_range_equation` package has been refactored from a single 2372-line `main.py` file into multiple focused modules for better readability and maintainability.

## Module Organization

### Core Modules

| Module | Lines | Description |
|--------|-------|-------------|
| `constants.py` | ~15 | Physical constants (c, k, pi, g, T_0) |
| `variables.py` | ~270 | Variable definitions for radar parameters |
| `equations.py` | 347 | Symbolic SymPy equations for all radar types |
| `solvable.py` | ~205 | Interactive Solvable class for parameter solving |
| `solvers.py` | 750 | Numeric solver functions and methods |
| `converters.py` | 293 | Unit conversion utilities |
| `analysis.py` | 537 | Analysis helpers for pulse parsing, integration, etc. |
| `main.py` | ~55 | Orchestration module that imports and re-exports all classes |

### Supporting Modules

| Module | Lines | Description |
|--------|-------|-------------|
| `plot.py` | 587 | Plotting utilities for radar signals |
| `__init__.py` | 49 | Package initialization and exports |

## Module Dependencies

```
main.py
├── constants.py (depends on: scipy)
├── variables.py (depends on: constants, sympy)
├── equations.py (depends on: sympy)
├── solvable.py (depends on: variables, sympy)
├── solvers.py (depends on: solvable, equations, variables, converters)
├── converters.py (depends on: numpy)
└── analysis.py (depends on: variables, converters, numpy)

plot.py (separate, depends on: matplotlib, numpy)
```

## Key Classes

### constants (from constants.py)
- Physical constants: c (speed of light), k (Boltzmann), pi, g (gravity), T_0
- Imported from scipy.constants where applicable

### vars (from variables.py)
- Container for all radar system variables
- Includes references to physical constants from constants module
- Organized by topic (Base, Doppler, CWFM, Pulsed, Direction Finding, etc.)

### equations (from equations.py)
- Symbolic SymPy representations of radar equations
- Supports all radar types and calculation scenarios

### Solvable (from solvable.py)
- Interactive, introspective solver for individual parameters
- Methods: `status()`, `solve()`, `__repr__()`, `__call__()`

### solve (from solvers.py)
- Container of Solvable instances and direct calculation methods
- Provides both interactive (Solvable) and functional (method-based) interfaces

### convert (from converters.py)
- Unit conversion utilities for angles, power, frequency, distance
- Supports dB conversions, metric conversions, etc.

### analysis (from analysis.py)
- Helper functions for pulse timing, integration gains, jammer analysis
- RGPO (Range Gate Pull-Off) analysis tools

## Backward Compatibility

All imports are re-exported through `main.py`, so existing code works unchanged:

```python
import radar_range_equation as RRE

# All of these still work exactly as before:
RRE.vars.c = 3e8
RRE.vars.f = 10e9
wavelength = RRE.solve.wavelength()
```

## Benefits of New Structure

1. **Readability**: Each module is focused and ~200-750 lines instead of 2372 lines
2. **Maintainability**: Related code is grouped together
3. **Testing**: Easier to test individual modules
4. **Documentation**: Each module has clear purpose and dependencies
5. **Extensibility**: New features can be added to specific modules
6. **Backward Compatible**: All existing code continues to work

## Import Examples

### Standard Usage (Recommended)
```python
import radar_range_equation as RRE

# Access all functionality through RRE
RRE.vars.f = 10e9
RRE.solve.wavelength()
RRE.convert.lin_to_db(1000)
```

### Direct Module Import (Advanced)
```python
from radar_range_equation.variables import vars
from radar_range_equation.solvable import Solvable
from radar_range_equation.solvers import solve

# Use directly
vars.f = 10e9
```

## Key Features

### Auto-Variable Definition
When using Solvable instances, the calculated result is automatically stored in the corresponding variable:

```python
RRE.vars.c = 3e8
RRE.vars.f = 10e9

# Before solving
print(RRE.vars.wavelength)  # lambda (symbolic)

# Solve
wavelength = RRE.solve.wavelength()

# After solving - automatically defined!
print(RRE.vars.wavelength)  # 0.03 (numeric)
```

This enables chaining calculations where one solve automatically provides input for the next.

## Development Guidelines

1. **Adding New Constants**: Edit `constants.py`
2. **Adding New Variables**: Edit `variables.py`
3. **Adding New Equations**: Edit `equations.py`
4. **Adding New Solvers**: Edit `solvers.py` and create Solvable instances
5. **Adding Conversions**: Edit `converters.py`
6. **Adding Analysis Tools**: Edit `analysis.py`

Always ensure `main.py` re-exports any new classes or functions for backward compatibility.
