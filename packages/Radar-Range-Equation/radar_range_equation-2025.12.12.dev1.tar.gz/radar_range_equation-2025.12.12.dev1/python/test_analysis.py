#!/usr/bin/env python3
"""Tests for the analysis module of the radar_range_equation package.

This script performs tests to ensure the analysis functions work correctly
and provide accurate results for pulse timing, integration gains, and
jammer calculations.

Note: This test uses sys.path.insert() to allow running directly from the
repository without installation. In production tests, install the package first.
"""

import sys
sys.path.insert(0, 'python/src')  # For running from repo without installation
import radar_range_equation as RRE
import numpy as np


def test_analysis_module():
    """Test that the analysis module is available and has expected functions."""
    print("Testing analysis module availability...")
    
    assert hasattr(RRE, 'analysis'), "analysis module not found in RRE"
    print("✓ analysis module is available")
    
    # Check for expected functions
    expected_functions = [
        'pulse_timing',
        'power_and_integration',
        'effective_independent_looks',
        'fluctuation_loss_total',
        'monostatic_received_power',
        'processed_signal_power',
        'jammer_received_power',
        'signal_to_jammer',
        'burnthrough_range'
    ]
    
    for func_name in expected_functions:
        assert hasattr(RRE.analysis, func_name), f"Function {func_name} not found in analysis module"
    
    print(f"✓ All {len(expected_functions)} expected functions are present")
    return True


def test_pulse_timing():
    """Test the pulse_timing function."""
    print("\nTesting pulse_timing()...")
    
    # Example: three pulses from problem statement
    # Pulse 1: 0 to 15 µs
    # Pulse 2: 50 to 65 µs
    # Pulse 3: 100 to 115 µs
    pulse_intervals = [(0, 15), (50, 65), (100, 115)]
    
    result = RRE.analysis.pulse_timing(pulse_intervals)
    
    assert 'pulse_width_s' in result, "Should have pulse_width_s"
    assert 'PRI_s' in result, "Should have PRI_s"
    assert 'PRF_hz' in result, "Should have PRF_hz"
    assert 'duty_cycle' in result, "Should have duty_cycle"
    assert 'n_p' in result, "Should have n_p"
    
    # Check values
    assert result['n_p'] == 3, f"Expected 3 pulses, got {result['n_p']}"
    assert abs(result['pulse_width_s'] - 15e-6) < 1e-9, "Pulse width should be 15 µs"
    assert abs(result['PRI_s'] - 50e-6) < 1e-9, "PRI should be 50 µs"
    assert abs(result['PRF_hz'] - 20000) < 1, "PRF should be 20 kHz"
    assert abs(result['duty_cycle'] - 0.3) < 0.01, "Duty cycle should be 30%"
    
    print(f"✓ Pulse timing calculated correctly:")
    print(f"  - Pulse width: {result['pulse_width_s']*1e6:.1f} µs")
    print(f"  - PRI: {result['PRI_s']*1e6:.1f} µs")
    print(f"  - PRF: {result['PRF_hz']/1000:.1f} kHz")
    print(f"  - Duty cycle: {result['duty_cycle']*100:.1f}%")
    print(f"  - Number of pulses: {result['n_p']}")
    
    return True


def test_power_and_integration():
    """Test the power_and_integration function."""
    print("\nTesting power_and_integration()...")
    
    amplitude = 20  # From problem statement
    pulse_intervals = [(0, 15), (50, 65), (100, 115)]
    
    # Test coherent integration
    result_coh = RRE.analysis.power_and_integration(amplitude, pulse_intervals, use='coherent')
    
    assert 'P_peak' in result_coh, "Should have P_peak"
    assert 'P_avg' in result_coh, "Should have P_avg"
    assert 'gain_linear' in result_coh, "Should have gain_linear"
    assert 'gain_db' in result_coh, "Should have gain_db"
    
    # Check peak power (A^2 / 2)
    expected_P_peak = (20 ** 2) / 2.0
    assert abs(result_coh['P_peak'] - expected_P_peak) < 0.1, f"Expected P_peak={expected_P_peak}"
    
    # Check coherent gain (should be n_p = 3)
    assert abs(result_coh['gain_linear'] - 3.0) < 0.01, "Coherent gain should be 3"
    expected_gain_db = 10 * np.log10(3)
    assert abs(result_coh['gain_db'] - expected_gain_db) < 0.1, f"Coherent gain should be ~4.77 dB"
    
    print(f"✓ Coherent integration calculated correctly:")
    print(f"  - P_peak: {result_coh['P_peak']:.1f}")
    print(f"  - P_avg: {result_coh['P_avg']:.1f}")
    print(f"  - Gain (linear): {result_coh['gain_linear']:.1f}")
    print(f"  - Gain (dB): {result_coh['gain_db']:.2f} dB")
    
    # Test non-coherent integration
    result_noncoh = RRE.analysis.power_and_integration(amplitude, pulse_intervals, use='noncoherent')
    
    # Check non-coherent gain (should be sqrt(n_p) = sqrt(3))
    expected_gain_noncoh = np.sqrt(3)
    assert abs(result_noncoh['gain_linear'] - expected_gain_noncoh) < 0.01, "Non-coherent gain should be sqrt(3)"
    
    print(f"✓ Non-coherent integration calculated correctly:")
    print(f"  - Gain (linear): {result_noncoh['gain_linear']:.2f}")
    print(f"  - Gain (dB): {result_noncoh['gain_db']:.2f} dB")
    
    return True


def test_effective_independent_looks():
    """Test the effective_independent_looks function."""
    print("\nTesting effective_independent_looks()...")
    
    # Pulses at 0, 50, 100, 110, 120 µs
    # With correlation time of 15 µs:
    # - 0: independent (first pulse)
    # - 50: independent (50-0=50 > 15)
    # - 100: independent (100-50=50 > 15)
    # - 110: correlated with 100 (110-100=10 < 15)
    # - 120: correlated with 110 (120-110=10 < 15), so also correlated with 100
    # Expected: 3 independent looks: [0], [50], [100, 110, 120]
    pulse_starts = [0, 50, 100, 110, 120]
    correlation_time = 15
    
    result = RRE.analysis.effective_independent_looks(pulse_starts, correlation_time)
    
    assert 'clusters' in result, "Should have clusters"
    assert 'n_e' in result, "Should have n_e"
    
    # With improved clustering (checks all cluster elements), pulses 100, 110, 120 are all correlated
    assert result['n_e'] == 3, f"Expected 3 independent looks with correlation time {correlation_time}"
    
    print(f"✓ Effective independent looks calculated correctly:")
    print(f"  - Pulse starts: {pulse_starts} µs")
    print(f"  - Correlation time: {correlation_time} µs")
    print(f"  - Number of independent looks: {result['n_e']}")
    print(f"  - Clusters: {result['clusters']}")
    
    return True


def test_fluctuation_loss():
    """Test the fluctuation_loss_total function."""
    print("\nTesting fluctuation_loss_total()...")
    
    L_single_db = 5.0  # 5 dB single-look loss
    n_e = 3  # 3 independent looks (updated to match improved clustering)
    
    result = RRE.analysis.fluctuation_loss_total(L_single_db, n_e)
    
    # L_total = L_single - 10*log10(n_e)
    expected = L_single_db - 10 * np.log10(n_e)
    assert abs(result - expected) < 0.01, f"Expected {expected:.2f} dB, got {result:.2f} dB"
    
    print(f"✓ Fluctuation loss calculated correctly:")
    print(f"  - Single-look loss: {L_single_db} dB")
    print(f"  - Independent looks: {n_e}")
    print(f"  - Total loss: {result:.2f} dB")
    
    return True


def test_monostatic_received_power():
    """Test the monostatic_received_power function."""
    print("\nTesting monostatic_received_power()...")
    
    Pt = 1000  # 1 kW transmit power
    Gt = 1000  # Transmit gain
    Gr = 1000  # Receive gain
    wavelength = 0.03  # 30 mm (10 GHz)
    sigma = 1.0  # 1 m^2 RCS
    R = 10000  # 10 km range
    
    Pr = RRE.analysis.monostatic_received_power(Pt, Gt, Gr, wavelength, sigma, R)
    
    assert Pr > 0, "Received power should be positive"
    
    print(f"✓ Monostatic received power calculated:")
    print(f"  - Transmit power: {Pt} W")
    print(f"  - Range: {R/1000} km")
    print(f"  - Received power: {Pr:.2e} W")
    
    return True


def test_jammer_calculations():
    """Test jammer-related functions."""
    print("\nTesting jammer calculations...")
    
    # Setup parameters
    Pj = 1000  # 1 kW jammer power
    G_j_tx_db = 30  # 30 dB jammer transmit gain
    G_radar_on_jam_db = 20  # 20 dB radar gain toward jammer
    wavelength = 0.03  # 30 mm
    R_jr = 50000  # 50 km jammer range
    band_ratio = 10.0  # Jammer 10x wider than radar bandwidth
    
    # Test jammer received power
    P_jr = RRE.analysis.jammer_received_power(Pj, G_j_tx_db, G_radar_on_jam_db, 
                                               wavelength, R_jr, band_ratio)
    
    assert P_jr > 0, "Jammer power should be positive"
    print(f"✓ Jammer received power: {P_jr:.2e} W")
    
    # Test signal-to-jammer ratio
    S_processed = 1e-10  # Example processed signal power
    sjr = RRE.analysis.signal_to_jammer(S_processed, P_jr)
    
    assert 'SJR_linear' in sjr, "Should have SJR_linear"
    assert 'SJR_db' in sjr, "Should have SJR_db"
    print(f"✓ Signal-to-jammer ratio: {sjr['SJR_db']:.2f} dB")
    
    # Test burnthrough range
    R_bt = RRE.analysis.burnthrough_range(Pj, G_j_tx_db, G_radar_on_jam_db, 
                                           wavelength, band_ratio, S_processed)
    
    assert R_bt > 0, "Burnthrough range should be positive"
    print(f"✓ Burnthrough range: {R_bt/1000:.1f} km")
    
    return True


def main():
    """Run all tests."""
    print("="*70)
    print("Testing Radar Range Equation - Analysis Module")
    print("="*70)
    
    try:
        test_analysis_module()
        test_pulse_timing()
        test_power_and_integration()
        test_effective_independent_looks()
        test_fluctuation_loss()
        test_monostatic_received_power()
        test_jammer_calculations()
        
        print("\n" + "="*70)
        print("✓ All analysis tests passed!")
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
