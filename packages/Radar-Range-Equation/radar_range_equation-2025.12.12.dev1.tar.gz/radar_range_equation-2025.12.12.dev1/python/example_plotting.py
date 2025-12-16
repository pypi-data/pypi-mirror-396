#!/usr/bin/env python3
"""
Example demonstrating the plotting capabilities of the Radar_Range_Equation package.

This example shows how to visualize various radar signals including:
- Pulsed radar transmit signals
- CW Doppler radar signals
- CWFM radar signals
- Pulse compression signals
- Range profiles
- Doppler spectra

Note: This example uses sys.path.insert() to allow running directly from the
repository without installation. In production code, install the package and
import normally: `import radar_range_equation as RRE`
"""

import sys
sys.path.insert(0, 'python/src')  # For running from repo without installation
import radar_range_equation as RRE
import numpy as np

def example_pulsed_radar():
    """Demonstrate pulsed radar signal plotting."""
    print("\n" + "="*70)
    print("Example 1: Pulsed Radar Transmit Signal")
    print("="*70)
    print("Creating a pulsed radar signal with the following parameters:")
    print("  - Amplitude: 20")
    print("  - Carrier frequency: 0.5 MHz (period = 2 µs)")
    print("  - Pulse width: 15 µs")
    print("  - Pulse Repetition Interval (PRI): 50 µs")
    print("  - Number of pulses: 3")
    print("  - Total time span: 150 µs")
    
    # Create the pulsed radar signal (matches the problem statement example)
    t, signal, fig = RRE.plot.pulsed_radar_signal(
        amplitude=20,
        frequency=0.5e6,  # 0.5 MHz
        pulse_width=15e-6,  # 15 microseconds
        pri=50e-6,  # 50 microseconds
        num_pulses=3,
        time_span=150e-6,  # 150 microseconds
        show=False
    )
    
    print(f"✓ Generated signal with {len(t)} points")
    print(f"  Signal peak amplitude: {np.max(np.abs(signal)):.2f}")
    
    # Save the figure
    fig.savefig('/tmp/pulsed_radar_signal.png', dpi=150, bbox_inches='tight')
    print("✓ Saved plot to /tmp/pulsed_radar_signal.png")
    
    return fig


def example_cw_doppler():
    """Demonstrate CW Doppler radar signal plotting."""
    print("\n" + "="*70)
    print("Example 2: CW Doppler Radar Signal")
    print("="*70)
    print("Creating CW Doppler radar signals:")
    print("  - Carrier frequency: 10 GHz")
    print("  - Doppler shift: 6667 Hz (from moving target)")
    
    t, signals, fig = RRE.plot.cw_doppler_signal(
        carrier_freq=10e9,
        doppler_shift=6667,
        show=False
    )
    
    print(f"✓ Generated TX and RX signals")
    
    # Save the figure
    fig.savefig('/tmp/cw_doppler_signal.png', dpi=150, bbox_inches='tight')
    print("✓ Saved plot to /tmp/cw_doppler_signal.png")
    
    return fig


def example_cwfm():
    """Demonstrate CWFM radar signal plotting."""
    print("\n" + "="*70)
    print("Example 3: CWFM Radar Signal")
    print("="*70)
    print("Creating CWFM radar signal:")
    print("  - Carrier frequency: 35 GHz")
    print("  - Modulation frequency: 100 Hz")
    print("  - Frequency deviation: 30 MHz")
    
    t, signal, freq_mod, fig = RRE.plot.cwfm_signal(
        carrier_freq=35e9,
        modulation_freq=100,
        frequency_deviation=30e6,
        show=False
    )
    
    print(f"✓ Generated CWFM signal")
    
    # Save the figure
    fig.savefig('/tmp/cwfm_signal.png', dpi=150, bbox_inches='tight')
    print("✓ Saved plot to /tmp/cwfm_signal.png")
    
    return fig


def example_pulse_compression():
    """Demonstrate pulse compression signal plotting."""
    print("\n" + "="*70)
    print("Example 4: Pulse Compression Signal")
    print("="*70)
    print("Creating pulse compression visualization:")
    print("  - Pulse width: 20 µs")
    print("  - Bandwidth: 200 MHz")
    print("  - Pulse Compression Ratio (PCR): 4000")
    
    t, chirp, compressed, fig = RRE.plot.pulse_compression_signal(
        pulse_width=20e-6,
        bandwidth=200e6,
        show=False
    )
    
    print(f"✓ Generated chirp and compressed pulse")
    pcr = 20e-6 * 200e6
    print(f"  PCR = {pcr:.0f}")
    
    # Save the figure
    fig.savefig('/tmp/pulse_compression_signal.png', dpi=150, bbox_inches='tight')
    print("✓ Saved plot to /tmp/pulse_compression_signal.png")
    
    return fig


def example_range_profile():
    """Demonstrate range profile plotting."""
    print("\n" + "="*70)
    print("Example 5: Radar Range Profile")
    print("="*70)
    print("Creating range profile with multiple targets:")
    
    # Define some target ranges and amplitudes
    ranges = [50, 120, 180, 240]
    amplitudes = [0.8, 1.0, 0.6, 0.4]
    
    print(f"  Number of targets: {len(ranges)}")
    for i, (r, a) in enumerate(zip(ranges, amplitudes), 1):
        print(f"  Target {i}: Range = {r} m, Amplitude = {a}")
    
    fig = RRE.plot.range_profile(
        ranges=ranges,
        amplitudes=amplitudes,
        max_range=300,
        show=False
    )
    
    print(f"✓ Generated range profile")
    
    # Save the figure
    fig.savefig('/tmp/range_profile.png', dpi=150, bbox_inches='tight')
    print("✓ Saved plot to /tmp/range_profile.png")
    
    return fig


def example_doppler_spectrum():
    """Demonstrate Doppler spectrum plotting."""
    print("\n" + "="*70)
    print("Example 6: Doppler Spectrum")
    print("="*70)
    print("Creating Doppler spectrum with multiple targets:")
    
    # Define target velocities and amplitudes
    velocities = [-50, -20, 10, 30]  # negative = approaching
    amplitudes = [0.9, 0.7, 0.5, 0.8]
    
    print(f"  Number of targets: {len(velocities)}")
    for i, (v, a) in enumerate(zip(velocities, amplitudes), 1):
        direction = "approaching" if v < 0 else "receding"
        print(f"  Target {i}: Velocity = {v} m/s ({direction}), Amplitude = {a}")
    
    fig = RRE.plot.doppler_spectrum(
        velocities=velocities,
        amplitudes=amplitudes,
        max_velocity=100,
        show=False
    )
    
    print(f"✓ Generated Doppler spectrum")
    
    # Save the figure
    fig.savefig('/tmp/doppler_spectrum.png', dpi=150, bbox_inches='tight')
    print("✓ Saved plot to /tmp/doppler_spectrum.png")
    
    return fig


def example_tactical_scenario():
    """Demonstrate tactical scenario plotting."""
    print("\n" + "="*70)
    print("Example 7: Tactical Scenario")
    print("="*70)
    print("Creating tactical scenario plot with:")
    print("  - Radar at (10, 20) km")
    print("  - Target at (50, -20) km")
    print("  - Support jammer at (70, -10) km")
    
    fig = RRE.plot.tactical_scenario(
        radar_pos=(10, 20),
        target_pos=(50, -20),
        jammer_pos=(70, -10),
        show=False
    )
    
    print(f"✓ Generated tactical scenario plot")
    
    # Save the figure
    fig.savefig('/tmp/tactical_scenario.png', dpi=150, bbox_inches='tight')
    print("✓ Saved plot to /tmp/tactical_scenario.png")
    
    return fig


def main():
    """Run all plotting examples."""
    print("\n" + "="*70)
    print("Radar Range Equation - Plotting Examples")
    print("="*70)
    print("This script demonstrates the plotting capabilities of the")
    print("radar_range_equation package.")
    
    try:
        # Run all examples
        example_pulsed_radar()
        example_cw_doppler()
        example_cwfm()
        example_pulse_compression()
        example_range_profile()
        example_doppler_spectrum()
        example_tactical_scenario()
        
        print("\n" + "="*70)
        print("✓ All examples completed successfully!")
        print("="*70)
        print("\nGenerated plots saved to /tmp/:")
        print("  - pulsed_radar_signal.png")
        print("  - cw_doppler_signal.png")
        print("  - cwfm_signal.png")
        print("  - pulse_compression_signal.png")
        print("  - range_profile.png")
        print("  - doppler_spectrum.png")
        print("  - tactical_scenario.png")
        print("\nYou can view these plots or integrate them into your application.")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
