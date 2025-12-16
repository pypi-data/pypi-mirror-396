"""Radar Range Equation Package.

A comprehensive Python package for radar range equation calculations, supporting
multiple radar types including CW, CWFM, pulsed radar, direction finding, and
pulse compression techniques.

Main Components:
    vars: Container for all radar-related variables and physical constants
    equations: Symbolic SymPy equations for radar calculations
    solve: Numeric solver functions for computing radar parameters
    convert: Unit conversion utilities (angles, power, frequency, distance)
    analysis: Analysis helpers for pulse parsing, integration gains, jammers
    plot: Plotting utilities for visualizing radar signals and equations
    redefine_variable: Helper function to set variables in the vars namespace

Example:
    >>> import radar_range_equation as RRE
    >>> RRE.vars.c = 3e8  # speed of light
    >>> RRE.vars.f = 10e9  # 10 GHz
    >>> RRE.vars.wavelength = RRE.solve.wavelength()
    >>> print(f"Wavelength: {RRE.vars.wavelength} m")
    >>> 
    >>> # Visualize a pulsed radar signal
    >>> RRE.plot.pulsed_radar_signal()
    >>> 
    >>> # Analyze pulse timing
    >>> pulse_intervals = [(0, 15), (50, 65), (100, 115)]
    >>> timing = RRE.analysis.pulse_timing(pulse_intervals)

For detailed documentation, see the individual module docstrings in main.py and plot.py.
"""

from .main import vars, \
                    equations, \
                    solve, \
                    convert, \
                    analysis, \
                    redefine_variable, \
                    Solvable
from . import plot

__all__ = ["vars",
           "equations",
           "solve",
           "convert",
           "analysis",
           "plot",
           "redefine_variable",
           "Solvable"
           ]