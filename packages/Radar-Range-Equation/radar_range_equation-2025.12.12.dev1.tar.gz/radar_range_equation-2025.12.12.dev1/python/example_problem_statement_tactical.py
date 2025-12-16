#!/usr/bin/env python3
"""
Demonstration matching the exact problem statement example.

This script creates a tactical scenario plot that exactly matches the
code provided in the problem statement, but uses the new tactical_scenario()
function from the radar_range_equation package.
"""

import sys
sys.path.insert(0, 'python/src')  # For running from repo without installation
import radar_range_equation as RRE

print("="*70)
print("Tactical Scenario Plot - Problem Statement Example")
print("="*70)
print("\nThis example creates the exact plot from the problem statement:")
print("  - Radar at (10, 20) km - Blue 'x' marker")
print("  - Target at (50, -20) km - Green solid square marker")
print("  - Support jammer at (70, -10) km - Red hollow circle marker")
print("\nAxis configuration:")
print("  - X-axis: 0 to 75 km (ticks every 10 km)")
print("  - Y-axis: -25 to 25 km (ticks every 5 km)")
print("  - Grid: Dashed lines with 70% opacity")
print("  - Figure size: 8 x 6 inches")

# Create the exact plot from the problem statement using the new function
fig = RRE.plot.tactical_scenario(
    radar_pos=(10, 20),
    target_pos=(50, -20),
    jammer_pos=(70, -10),
    xlim=(0, 75),
    ylim=(-25, 25),
    figsize=(8, 6),
    show=False
)

print("\n✓ Tactical scenario plot generated successfully!")

# Save the figure
output_path = '/tmp/problem_statement_tactical_scenario.png'
fig.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"✓ Plot saved to {output_path}")

print("\n" + "="*70)
print("The implementation successfully reproduces the exact plot")
print("described in the problem statement using RRE.plot.tactical_scenario()!")
print("="*70)

print("\n" + "="*70)
print("Comparison with original problem statement code:")
print("="*70)
print("\nOriginal approach (from problem statement):")
print("  import matplotlib.pyplot as plt")
print("  import numpy as np")
print("  plt.figure(figsize=(8, 6))")
print("  plt.scatter(10, 20, marker='x', color='blue', s=80, label='Radar')")
print("  plt.scatter(50, -20, marker='s', color='green', s=60, label='Target')")
print("  plt.scatter(70, -10, marker='o', facecolors='none',")
print("              edgecolors='red', s=80, label='Support jammer')")
print("  # ... plus axis labels, limits, ticks, grid, legend, etc.")
print("  plt.show()")

print("\nNew approach (with radar_range_equation package):")
print("  import radar_range_equation as RRE")
print("  fig = RRE.plot.tactical_scenario()")
print("  # That's it! All configuration is handled automatically.")

print("\nBenefits of the new approach:")
print("  ✓ Much simpler and cleaner code")
print("  ✓ Consistent with other RRE plotting functions")
print("  ✓ Fully customizable with optional parameters")
print("  ✓ Returns matplotlib Figure for further customization")
print("  ✓ Can save to file or display interactively")
print("="*70)
