#!/usr/bin/env python3
"""
Example: Interactive Solver System for Radar Range Equation

This example demonstrates the new interactive, introspective solver system
that transforms static methods into dynamic, self-documenting objects.

The key feature: typing RRE.solve.G_t in a console shows what's needed,
and calling RRE.solve.G_t() executes the calculation.

Usage:
    python example_interactive_solver.py

For interactive exploration, open a Python REPL or Jupyter notebook and try:
    >>> import radar_range_equation as RRE
    >>> RRE.solve.G_t  # Shows status
    >>> RRE.solve.G_t()  # Executes calculation
"""

import radar_range_equation as RRE

def example_basic_workflow():
    """Demonstrate basic workflow: check status, set vars, calculate."""
    print("="*80)
    print("Example 1: Basic Workflow - Calculating Wavelength")
    print("="*80)
    
    print("\nStep 1: Check what's needed")
    print(">>> RRE.solve.wavelength")
    RRE.solve.wavelength.status()
    
    print("\nStep 2: Set the required variables")
    print(">>> RRE.vars.c = 3e8")
    print(">>> RRE.vars.f = 10e9")
    RRE.vars.c = 3e8
    RRE.vars.f = 10e9
    
    print("\nStep 3: Check status again")
    print(">>> RRE.solve.wavelength")
    RRE.solve.wavelength.status()
    
    print("\nStep 4: Calculate the result")
    print(">>> wavelength = RRE.solve.wavelength()")
    wavelength = RRE.solve.wavelength()
    print(f"    Result: {wavelength} m = {wavelength*100} cm")


def example_antenna_gain():
    """Demonstrate calculating antenna gain."""
    print("\n" + "="*80)
    print("Example 2: Antenna Gain Calculation")
    print("="*80)
    
    print("\nScenario: Design antenna for 10 GHz with 2 m² effective aperture")
    print("\nStep 1: What do we need for G_t?")
    print(">>> RRE.solve.G_t")
    RRE.solve.G_t.status()
    
    print("\nStep 2: Set effective aperture")
    print(">>> RRE.vars.A_e = 2.0  # 2 m² effective aperture")
    RRE.vars.A_e = 2.0
    
    print("\nStep 3: We need wavelength - let's calculate it first")
    print(">>> RRE.vars.c = 3e8")
    print(">>> RRE.vars.f = 10e9  # 10 GHz")
    RRE.vars.c = 3e8
    RRE.vars.f = 10e9
    print(">>> RRE.vars.wavelength = RRE.solve.wavelength()")
    RRE.vars.wavelength = RRE.solve.wavelength()
    print(f"    Wavelength: {RRE.vars.wavelength} m")
    
    print("\nStep 4: Now calculate gain")
    print(">>> RRE.solve.G_t")
    RRE.solve.G_t.status()
    print(">>> gain = RRE.solve.G_t()")
    gain = RRE.solve.G_t()
    gain_db = RRE.convert.lin_to_db(gain)
    print(f"    Gain: {gain:.2f} (linear) = {gain_db:.2f} dB")


def example_radar_range():
    """Demonstrate calculating maximum radar range."""
    print("\n" + "="*80)
    print("Example 3: Maximum Radar Range Calculation")
    print("="*80)
    
    print("\nScenario: Radar system design")
    print("  - Transmit power: 10 kW")
    print("  - Antenna gain: 40 dB")
    print("  - Target RCS: 5 m²")
    print("  - Minimum detectable signal: 1e-14 W")
    print("  - Wavelength: 3 cm")
    
    print("\nStep 1: Check what's needed for R_max")
    print(">>> RRE.solve.R_max")
    RRE.solve.R_max.status()
    
    print("\nStep 2: Set all required variables")
    print(">>> RRE.vars.P_t = 10000.0  # 10 kW")
    print(">>> RRE.vars.G_t = 10000.0  # 40 dB ≈ 10000 linear")
    print(">>> RRE.vars.wavelength = 0.03  # 3 cm")
    print(">>> RRE.vars.sigma = 5.0  # 5 m² RCS")
    print(">>> RRE.vars.S_min = 1e-14  # -140 dBW")
    RRE.vars.P_t = 10000.0
    RRE.vars.G_t = 10000.0
    RRE.vars.wavelength = 0.03
    RRE.vars.sigma = 5.0
    RRE.vars.S_min = 1e-14
    
    print("\nStep 3: Verify all variables are ready")
    print(">>> RRE.solve.R_max")
    RRE.solve.R_max.status()
    
    print("\nStep 4: Calculate maximum range")
    print(">>> r_max = RRE.solve.R_max()")
    r_max = RRE.solve.R_max()
    print(f"    Maximum Range: {r_max:.2f} m")
    print(f"                 = {r_max/1000:.2f} km")
    print(f"                 = {r_max/1852:.2f} nautical miles")


def example_doppler_radar():
    """Demonstrate Doppler radar calculations."""
    print("\n" + "="*80)
    print("Example 4: Doppler CW Radar Analysis")
    print("="*80)
    
    print("\nScenario: Target moving at 100 m/s closing")
    print("  - Wavelength: 3 cm (10 GHz)")
    
    print("\nStep 1: Calculate Doppler shift")
    print(">>> RRE.vars.v = -100  # negative for closing")
    print(">>> RRE.vars.wavelength = 0.03")
    RRE.vars.v = -100
    RRE.vars.wavelength = 0.03
    
    print(">>> RRE.solve.f_doppler")
    RRE.solve.f_doppler.status()
    
    print(">>> f_d = RRE.solve.f_doppler()")
    f_d = RRE.solve.f_doppler()
    print(f"    Doppler Shift: {f_d:.2f} Hz = {f_d/1000:.2f} kHz")
    
    print("\nStep 2: Calculate velocity resolution")
    print(">>> RRE.vars.T_cpi = 0.01  # 10 ms CPI")
    RRE.vars.T_cpi = 0.01
    
    print(">>> delta_v = RRE.solve.delta_v()")
    delta_v = RRE.solve.delta_v()
    print(f"    Velocity Resolution: {delta_v:.2f} m/s")


def example_error_handling():
    """Demonstrate error handling when variables are missing."""
    print("\n" + "="*80)
    print("Example 5: Error Handling - Missing Variables")
    print("="*80)
    
    print("\nWhat happens if we try to calculate without setting variables?")
    print(">>> # Create fresh instance by resetting a key variable")
    import sympy
    print(">>> RRE.vars.sigma = sympy.Symbol('sigma')")
    RRE.vars.sigma = sympy.Symbol('sigma')
    
    print(">>> # Try to calculate R_max")
    print(">>> r_max = RRE.solve.R_max()")
    r_max = RRE.solve.R_max()
    
    print(f"\nResult: {r_max}")
    print("The system automatically showed status and returned None!")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("INTERACTIVE RADAR SOLVER SYSTEM - EXAMPLES")
    print("="*80)
    print("\nThis demonstrates the new Solvable class that makes radar")
    print("analysis interactive, introspective, and self-documenting.")
    print("\nKey Features:")
    print("  • Type RRE.solve.<param> to see what's needed")
    print("  • Call RRE.solve.<param>() to calculate")
    print("  • Automatic error handling with helpful status reports")
    print("  • Works great in interactive consoles and Jupyter!")
    
    example_basic_workflow()
    example_antenna_gain()
    example_radar_range()
    example_doppler_radar()
    example_error_handling()
    
    print("\n" + "="*80)
    print("TIP: Try these examples in a Python REPL or Jupyter notebook")
    print("for the full interactive experience!")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
