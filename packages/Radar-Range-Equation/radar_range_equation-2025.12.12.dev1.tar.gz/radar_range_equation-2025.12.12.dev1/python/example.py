#!/usr/bin/env python3
"""
Example demonstrating the usage of the Radar_Range_Equation package
as described in the problem statement.

This example shows:
- Setting c (speed of light)
- Setting f (frequency)
- Calculating lambda (wavelength) = c/f
- Printing the result
"""

import radar_range_equation as RRE

# Set the speed of light (m/s)
RRE.vars.c = 3.00 * 10**8
print(f"RRE.vars.c = {RRE.vars.c}")

# Set the frequency (Hz)
RRE.vars.f = 10
print(f"RRE.vars.f = {RRE.vars.f}")

# Calculate and set wavelength (m)
# Note: 'lambda' is a reserved keyword in Python, so we use setattr/getattr to set/access it
setattr(RRE.vars, 'lambda', RRE.vars.c / RRE.vars.f)

# Print the wavelength
print(f"RRE.vars.lambda = {getattr(RRE.vars, 'lambda')}")
