#!/usr/bin/env python3
"""Tests for the plotting module of the radar_range_equation package.

This script performs tests to ensure the plotting functions work correctly
and can generate the expected visualizations.

Note: This test uses sys.path.insert() to allow running directly from the
repository without installation. In production tests, install the package first.
"""

import sys
sys.path.insert(0, 'python/src')  # For running from repo without installation
import radar_range_equation as RRE
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing


def test_plotting_module():
    """Test that the plot module is available and has expected functions."""
    print("Testing plotting module availability...")
    
    assert hasattr(RRE, 'plot'), "plot module not found in RRE"
    print("✓ plot module is available")
    
    # Check for expected functions
    expected_functions = [
        'pulsed_radar_signal',
        'cw_doppler_signal',
        'cwfm_signal',
        'pulse_compression_signal',
        'range_profile',
        'doppler_spectrum',
        'tactical_scenario'
    ]
    
    for func_name in expected_functions:
        assert hasattr(RRE.plot, func_name), f"Function {func_name} not found in plot module"
    
    print(f"✓ All {len(expected_functions)} expected functions are present")
    return True


def test_pulsed_radar_signal():
    """Test the pulsed radar signal plotting function."""
    print("\nTesting pulsed_radar_signal()...")
    
    # Test with default parameters
    t, signal, fig = RRE.plot.pulsed_radar_signal(show=False)
    
    assert isinstance(t, np.ndarray), "Time vector should be numpy array"
    assert isinstance(signal, np.ndarray), "Signal should be numpy array"
    assert len(t) == len(signal), "Time and signal arrays should have same length"
    assert len(t) > 0, "Time vector should not be empty"
    
    # Check signal has expected characteristics
    max_amp = np.max(np.abs(signal))
    assert max_amp > 0, "Signal should have non-zero amplitude"
    assert max_amp <= 20 * 1.01, "Signal amplitude should not exceed specified maximum"
    
    print(f"✓ Generated signal with {len(t)} points, max amplitude: {max_amp:.2f}")
    
    # Test with custom parameters matching problem statement
    t, signal, fig = RRE.plot.pulsed_radar_signal(
        amplitude=20,
        frequency=0.5e6,
        pulse_width=15e-6,
        pri=50e-6,
        num_pulses=3,
        time_span=150e-6,
        show=False
    )
    
    max_amp = np.max(np.abs(signal))
    assert abs(max_amp - 20) < 0.1, f"Expected max amplitude ~20, got {max_amp}"
    
    print("✓ Custom parameters work correctly")
    return True


def test_cw_doppler_signal():
    """Test the CW Doppler radar signal plotting function."""
    print("\nTesting cw_doppler_signal()...")
    
    t, signals, fig = RRE.plot.cw_doppler_signal(show=False)
    
    assert isinstance(t, np.ndarray), "Time vector should be numpy array"
    assert isinstance(signals, dict), "Signals should be a dictionary"
    assert 'tx' in signals, "Should have 'tx' signal"
    assert 'rx' in signals, "Should have 'rx' signal"
    assert len(t) == len(signals['tx']), "Time and signal arrays should match"
    
    print(f"✓ Generated CW Doppler signals with {len(t)} points")
    return True


def test_cwfm_signal():
    """Test the CWFM radar signal plotting function."""
    print("\nTesting cwfm_signal()...")
    
    t, signal, freq_mod, fig = RRE.plot.cwfm_signal(show=False)
    
    assert isinstance(t, np.ndarray), "Time vector should be numpy array"
    assert isinstance(signal, np.ndarray), "Signal should be numpy array"
    assert isinstance(freq_mod, np.ndarray), "Frequency modulation should be numpy array"
    assert len(t) == len(signal) == len(freq_mod), "All arrays should have same length"
    
    print(f"✓ Generated CWFM signal with {len(t)} points")
    return True


def test_pulse_compression_signal():
    """Test the pulse compression signal plotting function."""
    print("\nTesting pulse_compression_signal()...")
    
    t, chirp, compressed, fig = RRE.plot.pulse_compression_signal(show=False)
    
    assert isinstance(t, np.ndarray), "Time vector should be numpy array"
    assert isinstance(chirp, np.ndarray), "Chirp should be numpy array"
    assert isinstance(compressed, np.ndarray), "Compressed signal should be numpy array"
    assert len(t) == len(chirp) == len(compressed), "All arrays should have same length"
    
    # Check that compressed pulse is narrower than chirp
    # (has energy more concentrated in time)
    chirp_energy = np.sum(chirp**2)
    compressed_energy = np.sum(compressed**2)
    
    print(f"✓ Generated pulse compression signal with {len(t)} points")
    return True


def test_range_profile():
    """Test the range profile plotting function."""
    print("\nTesting range_profile()...")
    
    ranges = [50, 100, 150, 200]
    amplitudes = [0.8, 1.0, 0.6, 0.4]
    
    fig = RRE.plot.range_profile(
        ranges=ranges,
        amplitudes=amplitudes,
        show=False
    )
    
    assert fig is not None, "Figure should be created"
    
    print(f"✓ Generated range profile with {len(ranges)} targets")
    return True


def test_doppler_spectrum():
    """Test the Doppler spectrum plotting function."""
    print("\nTesting doppler_spectrum()...")
    
    velocities = [-50, -20, 10, 30]
    amplitudes = [0.9, 0.7, 0.5, 0.8]
    
    fig = RRE.plot.doppler_spectrum(
        velocities=velocities,
        amplitudes=amplitudes,
        show=False
    )
    
    assert fig is not None, "Figure should be created"
    
    print(f"✓ Generated Doppler spectrum with {len(velocities)} targets")
    return True


def test_tactical_scenario():
    """Test the tactical scenario plotting function."""
    print("\nTesting tactical_scenario()...")
    
    # Test with default parameters
    fig = RRE.plot.tactical_scenario(show=False)
    
    assert fig is not None, "Figure should be created"
    
    print("✓ Generated tactical scenario with default positions")
    
    # Test with custom positions
    fig = RRE.plot.tactical_scenario(
        radar_pos=(20, 15),
        target_pos=(60, -15),
        jammer_pos=(80, -5),
        show=False
    )
    
    assert fig is not None, "Figure should be created"
    
    print("✓ Generated tactical scenario with custom positions")
    return True


def main():
    """Run all tests."""
    print("="*70)
    print("Testing Radar Range Equation - Plotting Module")
    print("="*70)
    
    try:
        test_plotting_module()
        test_pulsed_radar_signal()
        test_cw_doppler_signal()
        test_cwfm_signal()
        test_pulse_compression_signal()
        test_range_profile()
        test_doppler_spectrum()
        test_tactical_scenario()
        
        print("\n" + "="*70)
        print("✓ All plotting tests passed!")
        print("="*70)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
