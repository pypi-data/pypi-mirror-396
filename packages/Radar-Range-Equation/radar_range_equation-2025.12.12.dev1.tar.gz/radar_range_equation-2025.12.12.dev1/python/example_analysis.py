#!/usr/bin/env python3
"""
Example demonstrating the analysis capabilities of the Radar_Range_Equation package.

This example shows how to use the analysis helpers for:
- Pulse timing calculations
- Integration gains
- Effective independent looks
- Fluctuation loss
- Jammer and burnthrough analysis

Note: This example uses sys.path.insert() to allow running directly from the
repository without installation. In production code, install the package and
import normally: `import radar_range_equation as RRE`
"""

import sys
sys.path.insert(0, 'python/src')  # For running from repo without installation
import radar_range_equation as RRE
import numpy as np


def example_pulse_analysis():
    """Demonstrate pulse timing and integration gain analysis."""
    print("\n" + "="*70)
    print("Example 1: Pulse Timing and Integration Gain Analysis")
    print("="*70)
    print("\nScenario: Pulsed radar with 3 pulses")
    print("  - Pulse 1: 0 to 15 µs")
    print("  - Pulse 2: 50 to 65 µs")
    print("  - Pulse 3: 100 to 115 µs")
    print("  - Amplitude: 20")
    
    # Define pulse intervals
    pulse_intervals = [(0, 15), (50, 65), (100, 115)]
    amplitude = 20
    
    # Calculate pulse timing
    timing = RRE.analysis.pulse_timing(pulse_intervals)
    
    print("\nPulse Timing Analysis:")
    print(f"  ✓ Pulse width: {timing['pulse_width_s']*1e6:.1f} µs")
    print(f"  ✓ PRI (Pulse Repetition Interval): {timing['PRI_s']*1e6:.1f} µs")
    print(f"  ✓ PRF (Pulse Repetition Frequency): {timing['PRF_hz']/1000:.1f} kHz")
    print(f"  ✓ Duty cycle: {timing['duty_cycle']*100:.1f}%")
    print(f"  ✓ Number of pulses: {timing['n_p']}")
    
    # Calculate power and integration gains
    coh_result = RRE.analysis.power_and_integration(amplitude, pulse_intervals, use='coherent')
    noncoh_result = RRE.analysis.power_and_integration(amplitude, pulse_intervals, use='noncoherent')
    
    print("\nPower Analysis:")
    print(f"  ✓ Peak power: {coh_result['P_peak']:.1f} (arbitrary units)")
    print(f"  ✓ Average power: {coh_result['P_avg']:.1f} (arbitrary units)")
    
    print("\nIntegration Gains:")
    print(f"  ✓ Coherent integration:")
    print(f"    - Linear gain: {coh_result['gain_linear']:.1f}x")
    print(f"    - dB gain: {coh_result['gain_db']:.2f} dB")
    print(f"  ✓ Non-coherent integration:")
    print(f"    - Linear gain: {noncoh_result['gain_linear']:.2f}x")
    print(f"    - dB gain: {noncoh_result['gain_db']:.2f} dB")
    
    print("\n💡 Interpretation:")
    print("   Coherent integration provides 3x gain (3 pulses)")
    print("   Non-coherent integration provides √3 ≈ 1.73x gain")
    
    return timing, coh_result, noncoh_result


def example_independent_looks():
    """Demonstrate effective independent looks calculation."""
    print("\n" + "="*70)
    print("Example 2: Effective Independent Looks Analysis")
    print("="*70)
    print("\nScenario: Target with correlation time of 15 µs")
    print("  Pulses at: 0, 50, 100, 110, 120 µs")
    
    pulse_starts = [0, 50, 100, 110, 120]
    correlation_time = 15
    
    result = RRE.analysis.effective_independent_looks(pulse_starts, correlation_time)
    
    print(f"\nAnalysis Results:")
    print(f"  ✓ Correlation time: {correlation_time} µs")
    print(f"  ✓ Number of effective independent looks: {result['n_e']}")
    print(f"  ✓ Pulse clusters:")
    for i, cluster in enumerate(result['clusters'], 1):
        print(f"    - Cluster {i}: {cluster} µs")
    
    print("\n💡 Interpretation:")
    print("   Pulses within correlation time of ANY pulse in a cluster are grouped")
    print("   Pulse 110 is correlated with 100 (10 µs apart)")
    print("   Pulse 120 is correlated with 110 (10 µs apart)")
    print("   Therefore, 100, 110, and 120 form one cluster")
    
    # Demonstrate fluctuation loss calculation
    L_single_db = 5.0
    L_total_db = RRE.analysis.fluctuation_loss_total(L_single_db, result['n_e'])
    
    print(f"\nFluctuation Loss with {result['n_e']} independent looks:")
    print(f"  ✓ Single-look loss: {L_single_db} dB")
    print(f"  ✓ Total loss: {L_total_db:.2f} dB")
    print(f"  ✓ Improvement: {L_single_db - L_total_db:.2f} dB")
    
    return result


def example_jammer_analysis():
    """Demonstrate jammer and burnthrough calculations."""
    print("\n" + "="*70)
    print("Example 3: Jammer and Burnthrough Analysis")
    print("="*70)
    
    # Setup radar parameters
    print("\nRadar System Configuration:")
    RRE.vars.f = RRE.convert.hz_from(10, 'ghz')  # 10 GHz
    RRE.vars.wavelength = RRE.solve.wavelength()
    print(f"  - Frequency: {RRE.convert.hz_to(RRE.vars.f, 'ghz')} GHz")
    print(f"  - Wavelength: {RRE.vars.wavelength*1000:.1f} mm")
    
    # Radar transmit parameters
    Pt = 10000  # 10 kW
    Gt_db = 40  # 40 dB
    Gr_db = 40  # 40 dB
    Gt_linear = RRE.convert.db_to_lin(Gt_db)
    Gr_linear = RRE.convert.db_to_lin(Gr_db)
    
    print(f"\nRadar Parameters:")
    print(f"  - Transmit power: {Pt/1000} kW")
    print(f"  - Transmit gain: {Gt_db} dB")
    print(f"  - Receive gain: {Gr_db} dB")
    
    # Target parameters
    sigma = 5.0  # 5 m² RCS
    R_target = 50000  # 50 km
    
    print(f"\nTarget Parameters:")
    print(f"  - Range: {R_target/1000} km")
    print(f"  - RCS: {sigma} m²")
    
    # Calculate received power from target
    Pr_single = RRE.analysis.monostatic_received_power(
        Pt, Gt_linear, Gr_linear, RRE.vars.wavelength, sigma, R_target
    )
    
    print(f"\nReceived Signal Power (single pulse):")
    print(f"  ✓ {Pr_single:.2e} W ({RRE.convert.lin_to_db(Pr_single):.1f} dBW)")
    
    # Apply integration and pulse compression
    n_p = 10  # 10 pulses integrated
    PCR_db = 40  # 40 dB pulse compression ratio
    
    S_processed = RRE.analysis.processed_signal_power(Pr_single, n_p, PCR_db)
    
    print(f"\nProcessed Signal Power:")
    print(f"  - Number of pulses: {n_p}")
    print(f"  - Pulse compression ratio: {PCR_db} dB")
    print(f"  ✓ Processed power: {S_processed:.2e} W ({RRE.convert.lin_to_db(S_processed):.1f} dBW)")
    
    # Jammer parameters
    Pj = 5000  # 5 kW jammer power
    G_j_tx_db = 30  # 30 dB jammer gain
    G_radar_on_jam_db = 20  # 20 dB radar gain toward jammer
    R_jr = 80000  # 80 km jammer range
    band_ratio = 50  # Jammer bandwidth / radar bandwidth
    
    print(f"\nJammer Configuration:")
    print(f"  - Jammer power: {Pj/1000} kW")
    print(f"  - Jammer gain: {G_j_tx_db} dB")
    print(f"  - Radar gain on jammer: {G_radar_on_jam_db} dB")
    print(f"  - Jammer range: {R_jr/1000} km")
    print(f"  - Bandwidth ratio: {band_ratio}")
    
    # Calculate jammer received power
    P_jr = RRE.analysis.jammer_received_power(
        Pj, G_j_tx_db, G_radar_on_jam_db, RRE.vars.wavelength, R_jr, band_ratio
    )
    
    print(f"\nJammer Received Power:")
    print(f"  ✓ {P_jr:.2e} W ({RRE.convert.lin_to_db(P_jr):.1f} dBW)")
    
    # Calculate signal-to-jammer ratio
    sjr = RRE.analysis.signal_to_jammer(S_processed, P_jr)
    
    print(f"\nSignal-to-Jammer Ratio (S/J):")
    print(f"  ✓ Linear: {sjr['SJR_linear']:.2e}")
    print(f"  ✓ dB: {sjr['SJR_db']:.2f} dB")
    
    if sjr['SJR_db'] > 0:
        print("  📊 Status: Signal dominates - Target detected")
    else:
        print("  📊 Status: Jammer dominates - Target masked")
    
    # Calculate burnthrough range
    R_bt = RRE.analysis.burnthrough_range(
        Pj, G_j_tx_db, G_radar_on_jam_db, RRE.vars.wavelength, band_ratio, S_processed
    )
    
    print(f"\nBurnthrough Range:")
    print(f"  ✓ {R_bt/1000:.1f} km")
    
    if R_target < R_bt:
        print(f"  📊 Target at {R_target/1000} km is within burnthrough range")
    else:
        print(f"  📊 Target at {R_target/1000} km is beyond burnthrough range")
    
    return S_processed, P_jr, sjr, R_bt


def example_comprehensive_scenario():
    """Demonstrate a comprehensive radar scenario analysis."""
    print("\n" + "="*70)
    print("Example 4: Comprehensive Scenario Analysis")
    print("="*70)
    print("\nMission: Air defense radar tracking aircraft in presence of jammer")
    
    # Mission parameters
    print("\n📋 Mission Parameters:")
    print("  - Radar: S-band (3 GHz)")
    print("  - Target: Fighter aircraft at 40 km")
    print("  - Jammer: Escort jammer at 60 km")
    print("  - Target RCS: 2 m²")
    print("  - Weather: Clear sky")
    
    # Setup
    RRE.vars.f = RRE.convert.hz_from(3, 'ghz')
    RRE.vars.wavelength = RRE.solve.wavelength()
    
    # Pulse configuration
    pulse_intervals = [(0, 20), (100, 120), (200, 220), (300, 320), (400, 420)]
    amplitude = 30
    
    timing = RRE.analysis.pulse_timing(pulse_intervals)
    power = RRE.analysis.power_and_integration(amplitude, pulse_intervals, use='coherent')
    
    print("\n⚡ Waveform Configuration:")
    print(f"  - Pulse width: {timing['pulse_width_s']*1e6:.0f} µs")
    print(f"  - PRF: {timing['PRF_hz']/1000:.1f} kHz")
    print(f"  - Pulses integrated: {timing['n_p']}")
    print(f"  - Integration gain: {power['gain_db']:.1f} dB")
    
    # Calculate signal powers
    Pt = 50000  # 50 kW
    Gt_linear = RRE.convert.db_to_lin(45)  # 45 dB
    Gr_linear = Gt_linear
    sigma = 2.0
    R_target = 40000
    
    Pr = RRE.analysis.monostatic_received_power(
        Pt, Gt_linear, Gr_linear, RRE.vars.wavelength, sigma, R_target
    )
    
    S_proc = RRE.analysis.processed_signal_power(Pr, timing['n_p'], 30)  # 30 dB PCR
    
    print(f"\n📡 Signal Analysis:")
    print(f"  - Single pulse received power: {Pr:.2e} W")
    print(f"  - Processed signal power: {S_proc:.2e} W")
    print(f"  - Signal power (dB): {RRE.convert.lin_to_db(S_proc):.1f} dBW")
    
    # Jammer analysis
    Pj = 2000  # 2 kW
    R_jr = 60000
    P_jr = RRE.analysis.jammer_received_power(
        Pj, 25, 15, RRE.vars.wavelength, R_jr, 20
    )
    
    sjr = RRE.analysis.signal_to_jammer(S_proc, P_jr)
    
    print(f"\n🚫 Jammer Analysis:")
    print(f"  - Jammer power: {Pj/1000} kW at {R_jr/1000} km")
    print(f"  - Jammer received power: {P_jr:.2e} W")
    print(f"  - S/J ratio: {sjr['SJR_db']:.1f} dB")
    
    # Mission outcome
    print(f"\n✅ Mission Outcome:")
    if sjr['SJR_db'] > 0:
        print(f"  SUCCESS: Target detected with S/J = {sjr['SJR_db']:.1f} dB")
        print(f"  Radar overcomes jamming through:")
        print(f"    • Coherent integration ({timing['n_p']} pulses)")
        print(f"    • Pulse compression (30 dB)")
        print(f"    • High antenna gain (45 dB)")
    else:
        print(f"  DEGRADED: Jammer dominates by {abs(sjr['SJR_db']):.1f} dB")
        print(f"  Recommendations:")
        print(f"    • Increase transmit power")
        print(f"    • Use more pulse integration")
        print(f"    • Apply sidelobe cancellation")


def main():
    """Run all analysis examples."""
    print("\n" + "="*70)
    print("Radar Range Equation - Analysis Examples")
    print("="*70)
    print("This script demonstrates the analysis capabilities of the")
    print("radar_range_equation package.")
    
    try:
        # Run all examples
        example_pulse_analysis()
        example_independent_looks()
        example_jammer_analysis()
        example_comprehensive_scenario()
        
        print("\n" + "="*70)
        print("✓ All analysis examples completed successfully!")
        print("="*70)
        print("\n📚 Key Capabilities Demonstrated:")
        print("  ✓ Pulse timing and integration gain analysis")
        print("  ✓ Effective independent looks calculation")
        print("  ✓ Fluctuation loss estimation")
        print("  ✓ Monostatic radar equation")
        print("  ✓ Pulse compression processing")
        print("  ✓ Jammer power calculations")
        print("  ✓ Signal-to-jammer ratio analysis")
        print("  ✓ Burnthrough range estimation")
        print("\n🎯 Use Cases:")
        print("  • Radar system design and analysis")
        print("  • EW (Electronic Warfare) studies")
        print("  • Mission planning and feasibility analysis")
        print("  • Performance prediction in jamming environments")
        print("="*70)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
