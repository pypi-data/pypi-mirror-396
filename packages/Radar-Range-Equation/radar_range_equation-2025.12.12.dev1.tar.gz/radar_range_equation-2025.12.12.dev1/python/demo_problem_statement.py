#!/usr/bin/env python3
"""
Demonstration that matches the exact problem statement example.

This script creates a pulsed radar transmit signal that matches the 
parameters provided in the problem statement.

Note: This demo uses sys.path.insert() to allow running directly from the
repository without installation. In production code, install the package first.
"""

import sys
sys.path.insert(0, 'python/src')  # For running from repo without installation
import radar_range_equation as RRE

print("="*70)
print("Pulsed Radar Transmit Signal - Problem Statement Example")
print("="*70)
print("\nThis example matches the exact parameters from the problem statement:")
print("  - Amplitude (A) = 20")
print("  - Period (T) = 2 µs")
print("  - Frequency (f) = 1 / T = 0.5 MHz")
print("  - Angular frequency (ω) = 2π * f = π rad/µs")
print("\nThree pulses:")
print("  - Pulse 1: 0 µs to 15 µs")
print("  - Pulse 2: 50 µs to 65 µs")
print("  - Pulse 3: 100 µs to 115 µs")
print("\nTotal time span: 0 to 150 µs")

# Create the exact signal from the problem statement
t, signal, fig = RRE.plot.pulsed_radar_signal(
    amplitude=20,           # Amplitude A = 20
    frequency=0.5e6,        # f = 0.5 MHz (period T = 2 µs)
    pulse_width=15e-6,      # 15 microseconds (0 to 15, 50 to 65, 100 to 115)
    pri=50e-6,              # PRI = 50 µs (pulses at 0, 50, 100)
    num_pulses=3,           # 3 pulses
    time_span=150e-6,       # 150 microseconds
    num_points=10000        # High resolution for smooth plotting
)

print("\n✓ Signal generated successfully!")
print(f"  - Time vector has {len(t)} points")
print(f"  - Time range: {t[0]:.1f} to {t[-1]:.1f} µs")
print(f"  - Signal peak amplitude: {max(abs(signal)):.2f}")

# Save the figure
fig.savefig('/tmp/problem_statement_pulsed_radar.png', dpi=150, bbox_inches='tight')
print(f"\n✓ Plot saved to /tmp/problem_statement_pulsed_radar.png")

print("\n" + "="*70)
print("The implementation successfully reproduces the exact signal")
print("described in the problem statement using the new plot module!")
print("="*70)
