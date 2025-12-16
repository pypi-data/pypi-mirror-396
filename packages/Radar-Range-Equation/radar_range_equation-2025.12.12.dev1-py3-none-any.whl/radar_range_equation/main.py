"""Radar Range Equation Package - Core Module.

This module provides a comprehensive toolkit for radar range equation calculations,
including symbolic and numeric solutions for various radar types (CW, CWFM, pulsed),
direction finding, and pulse compression techniques.

The module is organized into separate sub-modules:
    - variables: Container for physical constants and radar parameters
    - equations: Symbolic SymPy equations for radar calculations
    - solvable: Solvable class for interactive parameter solving
    - solvers: Numeric solver functions for radar problems
    - converters: Unit conversion utilities
    - analysis: Analysis helpers for pulse parsing, integration, etc.

Example:
    >>> import radar_range_equation as RRE
    >>> RRE.vars.f = 10e9  # 10 GHz
    >>> RRE.vars.wavelength = RRE.solve.wavelength()
    >>> print(RRE.vars.wavelength)
"""

# Import all classes from sub-modules
from . import constants
from .variables import vars, v
from .equations import equations
from .solvable import Solvable
from .solvers import solve
from .converters import convert, con
from .analysis import analysis


def redefine_variable(var_name, new_value):
    """
    Redefines a global variable within the 'vars' namespace.
    
    Args:
        var_name (str): The name of the variable to redefine (e.g., "lambda").
        new_value: The new value to assign to the variable.
    """
    setattr(vars, var_name, new_value)


# For backward compatibility - demonstration code if run directly
if __name__ == '__main__':
    # Only runs when the script is executed directly
    print("Radar Range Equation Package - Modular Structure")
    print("=" * 60)
    print("\nAvailable modules:")
    print("  - vars: Variable definitions")
    print("  - equations: Symbolic equations")
    print("  - Solvable: Interactive solver class")
    print("  - solve: Numeric solvers")
    print("  - convert: Unit conversions")
    print("  - analysis: Analysis helpers")
    print("\nUse 'import radar_range_equation as RRE' to access all modules")
