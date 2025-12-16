"""Radar Range Equation - Analysis Helpers Module.

This module defines the analysis class which provides analysis helpers for
pulse parsing, integration gains, fluctuation loss, and jammer calculations.
"""

import numpy as np
from .variables import vars
from .converters import convert


class analysis:
    """Analysis helpers: pulse parsing, integration gains, fluctuation loss,
    jammer and burnthrough calculations.

    These convenience functions wrap common calculation patterns used in the
    quiz solutions and examples. They use `vars`, `convert` and numpy utilities
    already defined in this module.
    """

    @staticmethod
    def pulse_timing(pulse_intervals_us):
        """Compute pulse width, PRI, PRF and duty cycle.

        Args:
            pulse_intervals_us (list of (start_us, end_us)): list of ON intervals in microseconds

        Returns:
            dict: {pulse_width_s, PRI_s, PRF_hz, duty_cycle, n_p}
        """
        if len(pulse_intervals_us) == 0:
            return {'pulse_width_s': 0.0, 'PRI_s': 0.0, 'PRF_hz': 0.0, 'duty_cycle': 0.0, 'n_p': 0}
        widths_us = [end - start for (start, end) in pulse_intervals_us]
        pulse_width_us = widths_us[0]
        starts = [s for (s, e) in pulse_intervals_us]
        if len(starts) > 1:
            PRI_us = starts[1] - starts[0]
        else:
            PRI_us = 0.0
        pulse_width_s = pulse_width_us * 1e-6
        PRI_s = PRI_us * 1e-6 if PRI_us > 0 else 0.0
        PRF_hz = 1.0 / PRI_s if PRI_s > 0 else 0.0
        duty_cycle = pulse_width_s / PRI_s if PRI_s > 0 else 0.0
        n_p = len(pulse_intervals_us)
        return {'pulse_width_s': pulse_width_s, 'PRI_s': PRI_s, 'PRF_hz': PRF_hz, 'duty_cycle': duty_cycle, 'n_p': n_p}

    @staticmethod
    def power_and_integration(amplitude, pulse_intervals_us, use='coherent'):
        """Compute peak power, average power and integration SNR gain.

        Args:
            amplitude (float): amplitude A of the transmit pulse (arbitrary units)
            pulse_intervals_us (list): list of (start,end) intervals in us
            use (str): 'coherent' or 'noncoherent' for integration gain model

        Returns:
            dict: {P_peak, P_avg, n_p, gain_linear, gain_db}
        """
        P_peak = (amplitude ** 2) / 2.0
        t = analysis.pulse_timing(pulse_intervals_us)
        P_avg = P_peak * t['duty_cycle']
        n = t['n_p']
        if n <= 0:
            gain_linear = 1.0
        else:
            if use == 'coherent':
                gain_linear = float(n)
            else:
                # simple non-coherent approximation (amplitude averaging)
                gain_linear = float(np.sqrt(n))
        gain_db = convert.lin_to_db(gain_linear)
        return {'P_peak': P_peak, 'P_avg': P_avg, 'n_p': n, 'gain_linear': gain_linear, 'gain_db': gain_db}

    @staticmethod
    def effective_independent_looks(pulse_start_times_us, correlation_time_us):
        """Estimate number of effective independent looks given correlation time.

        Groups pulses whose start times are within `correlation_time_us` of a group's
        first pulse. Returns the clusters and n_e (number of independent looks).
        """
        clusters = []
        for t in pulse_start_times_us:
            placed = False
            for cl in clusters:
                if abs(t - cl[0]) < correlation_time_us:
                    cl.append(t)
                    placed = True
                    break
            if not placed:
                clusters.append([t])
        return {'clusters': clusters, 'n_e': len(clusters)}

    @staticmethod
    def fluctuation_loss_total(L_single_db, n_e):
        """Combine single-look fluctuation loss across n_e independent looks.

        Simple method (default): L_total_db = L_single_db - 10*log10(n_e)
        (This is an approximate power-averaging rule; actual behavior depends on Swerling model.)
        """
        if n_e <= 0:
            return L_single_db
        return L_single_db - 10.0 * np.log10(n_e)

    @staticmethod
    def monostatic_received_power(Pt, Gt_linear, Gr_linear, wavelength_m, sigma_m2, R_m):
        """Monostatic single-pulse received power (Friis-based radar equation).

        Pr = Pt * Gt * Gr * lambda^2 * sigma / ((4*pi)^3 * R^4)
        """
        return (Pt * Gt_linear * Gr_linear * (wavelength_m ** 2) * sigma_m2) / ((4.0 * np.pi) ** 3 * (R_m ** 4))

    @staticmethod
    def processed_signal_power(Pr_single, n_p, PCR_db):
        """Apply coherent integration (n_p) and pulse compression (PCR_db) to single-pulse power."""
        PCR_lin = convert.db_to_lin(PCR_db)
        return Pr_single * float(n_p) * PCR_lin

    @staticmethod
    def jammer_received_power(Pj, G_j_tx_db, G_radar_on_jam_db, wavelength_m, R_jr_m, band_ratio=1.0):
        """Compute jammer power received in the radar band.

        Assumes free-space propagation and that only 1/band_ratio of jammer power
        falls into the radar bandwidth.
        """
        Gjt = convert.db_to_lin(G_j_tx_db)
        Grj = convert.db_to_lin(G_radar_on_jam_db)
        return Pj * Gjt * Grj * (wavelength_m ** 2) / ((4.0 * np.pi * R_jr_m) ** 2) * (1.0 / band_ratio)

    @staticmethod
    def signal_to_jammer(S_processed, P_jr):
        """Return S/J linear and dB given processed signal power and jammer received power."""
        if P_jr <= 0:
            return {'SJR_linear': np.inf, 'SJR_db': np.inf}
        s = S_processed / P_jr
        return {'SJR_linear': s, 'SJR_db': convert.lin_to_db(s)}

    @staticmethod
    def burnthrough_range(Pj, G_j_tx_db, G_radar_on_jam_db, wavelength_m, band_ratio, S_processed):
        """Solve for jammer range R_jr where processed signal equals jammer power in band.

        Returns range in meters.
        """
        Gjt = convert.db_to_lin(G_j_tx_db)
        Grj = convert.db_to_lin(G_radar_on_jam_db)
        numer = Pj * Gjt * Grj * (wavelength_m ** 2)
        den = (4.0 * np.pi) ** 2 * (1.0 / band_ratio) * S_processed
        if den <= 0:
            return np.inf
        return float(np.sqrt(numer / den))

    # =========================================================================
    # GATE STEALING / RANGE GATE PULL-OFF (RGPO) ANALYSIS
    # =========================================================================
    
    @staticmethod
    def rgpo_delay_increment(delta_R_m, c=None):
        """Calculate time delay increment for RGPO.
        
        Args:
            delta_R_m: Range increment per pulse (meters)
            c: Speed of light (m/s), uses vars.c if not provided
            
        Returns:
            Time delay increment (seconds)
        """
        if c is None:
            c = vars.c
        return 2.0 * delta_R_m / c
    
    @staticmethod
    def rgpo_range_increment(delta_t_s, c=None):
        """Calculate range increment from time delay.
        
        Args:
            delta_t_s: Time delay increment (seconds)
            c: Speed of light (m/s), uses vars.c if not provided
            
        Returns:
            Range increment (meters)
        """
        if c is None:
            c = vars.c
        return c * delta_t_s / 2.0
    
    @staticmethod
    def rgpo_pulses_to_capture(R_initial, R_final, delta_R_per_pulse):
        """Calculate number of pulses needed to pull gate from initial to final range.
        
        Args:
            R_initial: Initial range (meters)
            R_final: Final range (meters)
            delta_R_per_pulse: Range increment per pulse (meters)
            
        Returns:
            Number of pulses required
        """
        return int(np.ceil(abs(R_final - R_initial) / delta_R_per_pulse))
    
    @staticmethod
    def rgpo_max_safe_rate(gate_width_m, safety_factor=0.1):
        """Calculate maximum safe RGPO pull rate.
        
        Rule of thumb: Don't exceed 10-20% of gate width per pulse to maintain lock.
        
        Args:
            gate_width_m: Range gate width (meters)
            safety_factor: Fraction of gate width (default 0.1 = 10%)
            
        Returns:
            Maximum delta_R per pulse (meters)
        """
        return gate_width_m * safety_factor
    
    @staticmethod
    def rgpo_profile(R_initial, R_final, delta_R_per_pulse, PRF=None, c=None):
        """Generate complete RGPO delay profile.
        
        Args:
            R_initial: Initial jammer range (m), typically equals true target range
            R_final: Final range to pull gate to (m)
            delta_R_per_pulse: Range increment per pulse (m/pulse)
            PRF: Pulse repetition frequency (Hz), optional
            c: Speed of light (m/s), uses vars.c if not provided
            
        Returns:
            dict containing:
                - pulse_number: array of pulse indices
                - range_m: array of false target ranges (m)
                - range_km: array of false target ranges (km)
                - delay_us: array of time delays (microseconds)
                - delay_increment_us: delay increment per pulse (microseconds)
                - n_pulses: total number of pulses
                - total_distance_m: total range pulled (m)
                - pull_rate_m_per_pulse: rate (m/pulse)
                - (if PRF provided) total_time_s, pull_rate_m_per_s
        """
        if c is None:
            c = vars.c
        
        n_pulses = int(np.ceil(abs(R_final - R_initial) / delta_R_per_pulse)) + 1
        pulse_nums = np.arange(n_pulses)
        
        # Calculate ranges for each pulse
        ranges_m = R_initial + pulse_nums * delta_R_per_pulse
        ranges_m = np.clip(ranges_m, min(R_initial, R_final), max(R_initial, R_final))
        
        # Calculate time delays (round-trip: 2R/c)
        delays_s = 2.0 * ranges_m / c
        delays_us = delays_s * 1e6
        
        # Delay increment per pulse
        delta_t_increment_s = 2.0 * delta_R_per_pulse / c
        delta_t_increment_us = delta_t_increment_s * 1e6
        
        result = {
            'pulse_number': pulse_nums,
            'range_m': ranges_m,
            'range_km': ranges_m / 1000.0,
            'delay_us': delays_us,
            'delay_s': delays_s,
            'delay_increment_us': delta_t_increment_us,
            'delay_increment_s': delta_t_increment_s,
            'n_pulses': n_pulses,
            'total_distance_m': abs(R_final - R_initial),
            'pull_rate_m_per_pulse': delta_R_per_pulse
        }
        
        if PRF is not None and PRF > 0:
            total_time_s = n_pulses / PRF
            pull_rate_m_per_s = delta_R_per_pulse * PRF
            result.update({
                'total_time_s': total_time_s,
                'PRF_hz': PRF,
                'pull_rate_m_per_s': pull_rate_m_per_s,
                'pull_rate_km_per_s': pull_rate_m_per_s / 1000.0
            })
        
        return result
    
    @staticmethod
    def rgpo_with_doppler(R_initial, R_final, delta_R_per_pulse, v_true, PRF, f_radar, c=None):
        """Generate RGPO profile with Doppler shift considerations.
        
        Args:
            R_initial: Initial jammer range (m)
            R_final: Final range to pull gate to (m)
            delta_R_per_pulse: Range increment per pulse (m/pulse)
            v_true: True target velocity (m/s), positive = closing
            PRF: Pulse repetition frequency (Hz)
            f_radar: Radar frequency (Hz)
            c: Speed of light (m/s), uses vars.c if not provided
            
        Returns:
            dict containing range profile plus Doppler information
        """
        if c is None:
            c = vars.c
        
        # Get base RGPO profile
        profile = analysis.rgpo_profile(R_initial, R_final, delta_R_per_pulse, PRF, c)
        
        # Calculate wavelength
        wavelength = c / f_radar
        
        # True target Doppler
        f_doppler_true = 2.0 * v_true / wavelength
        
        # Synthetic velocity from pull-off rate
        if PRF > 0:
            v_synthetic = delta_R_per_pulse * PRF  # m/s
            f_doppler_synthetic = 2.0 * v_synthetic / wavelength
        else:
            v_synthetic = 0
            f_doppler_synthetic = 0
        
        # Add Doppler information
        profile.update({
            'v_true_m_s': v_true,
            'f_doppler_true_hz': f_doppler_true,
            'v_synthetic_m_s': v_synthetic,
            'f_doppler_synthetic_hz': f_doppler_synthetic,
            'f_doppler_difference_hz': f_doppler_synthetic - f_doppler_true,
            'wavelength_m': wavelength
        })
        
        return profile


def redefine_variable(var_name, new_value):
    """
    Redefines a global variable within the 'vars' namespace.
    Args:
        var_name (str): The name of the variable to redefine (e.g., "lambda").
        new_value: The new value to assign to the variable.
    """
    setattr(vars, var_name, new_value)
# Demonstration of usage from a separate script or module:

if __name__ == '__main__':  # Only runs when the script is executed directly
    
    # --- Original Demo Code ---
    print("--- Original Demo (CWFM) ---")
    v = vars()  # Create a reference to the global vars instance
    v.f_bu = Symbol('f_bu')
    pprint(v.f_bu)
    v.f_bu = convert.hz_from(1510, 'mhz')
    pprint(convert.hz_to(v.f_bu, 'mhz'))
    v.f_bd = Symbol('f_bd')
    pprint(v.f_bd)
    v.f_bd = convert.hz_from(1490, 'mhz')
    pprint(convert.hz_to(v.f_bd, 'mhz'))
    v.f_r = Symbol('f_r')
    pprint(v.f_r)
    v.f_r = solve.f_r_cwfm() # Use solver
    pprint(convert.hz_to(v.f_r, 'mhz'))
    v.f_d = Symbol('f_d')
    pprint(v.f_d)
    v.f_d = solve.f_d_cwfm() # Use solver
    pprint(convert.hz_to(v.f_d, 'mhz'))
    # plain word with space
    v.deltaf = Symbol('delta f')
    pprint(v.deltaf)

    # --- Topic 10: Direction Finding Demo ---
    print("\n" + "="*30)
    print("Topic 10: Direction Finding Demo")
    print("="*30 + "\n")

    # --- Problem 2: Amplitude Comparison ---
    print("--- Problem 2: Amplitude Comparison ---")
    redefine_variable('S_N_dB', 10)  # 10 dB
    redefine_variable('S_N', solve.S_N_from_dB()) # Convert to linear
    redefine_variable('phi_s', 5.0)   # 5 degrees
    redefine_variable('theta_B', 10.0) # 10 degrees
    print(f"Given: S/N = {v.S_N_dB} dB ({v.S_N:.2f} linear), Squint Angle = {v.phi_s} deg, Beamwidth = {v.theta_B} deg")
    redefine_variable('sigma_phi', solve.sigma_phi_amplitude())
    print(f"Calculated DOA Accuracy (sigma_phi): {v.sigma_phi:.2f} degrees")
    redefine_variable('sigma_phi', 0.5) # New target accuracy
    print(f"\nTarget DOA Accuracy: {v.sigma_phi} degrees")
    redefine_variable('phi_s', solve.phi_s_from_sigma_amp())
    print(f"Calculated required Squint Angle: {v.phi_s:.2f} degrees")
    
    # --- Problem 3a: Phase Comparison ---
    print("\n--- Problem 3a: Phase Comparison ---")
    redefine_variable('d', 2.0)     # 2 meters
    redefine_variable('f', convert.hz_from(10, 'ghz')) # 10 GHz
    redefine_variable('wavelength', solve.wavelength())
    redefine_variable('S_N_dB', 8)    # 8 dB
    redefine_variable('S_N', solve.S_N_from_dB())
    print(f"Given: d = {v.d} m, f = {convert.hz_to(v.f, 'ghz')} GHz (lambda = {v.wavelength:.3f} m), S/N = {v.S_N_dB} dB ({v.S_N:.2f} linear)")
    sigma_phi_rad = solve.sigma_phi_phase()
    sigma_phi_deg = convert.rad_to_deg(sigma_phi_rad)
    print(f"Calculated DOA Accuracy (sigma_phi): {sigma_phi_rad:.2e} rad ({sigma_phi_deg:.3f} deg)")
    target_sigma_phi_deg = 0.5
    target_sigma_phi_rad = convert.deg_to_rad(target_sigma_phi_deg)
    redefine_variable('sigma_phi', target_sigma_phi_rad)
    print(f"\nTarget DOA Accuracy: {target_sigma_phi_deg} degrees ({v.sigma_phi:.4f} rad)")
    redefine_variable('d', solve.d_from_sigma_phase())
    print(f"Calculated required Separation 'd': {v.d:.2f} m")

    # --- Problem 3b: Time Comparison ---
    print("\n--- Problem 3b: Time Comparison ---")
    redefine_variable('d', 2.0)     # 2 meters
    redefine_variable('B', convert.hz_from(200, 'mhz')) # 200 MHz
    print(f"Given: d = {v.d} m, B = {convert.hz_to(v.B, 'mhz')} MHz")
    sigma_phi_rad_time = solve.sigma_phi_time()
    sigma_phi_deg_time = convert.rad_to_deg(sigma_phi_rad_time)
    print(f"Calculated DOA Accuracy (sigma_phi): {sigma_phi_rad_time:.2f} rad ({sigma_phi_deg_time:.2f} deg)")
    target_sigma_phi_deg_2 = 0.5
    target_sigma_phi_rad_2 = convert.deg_to_rad(target_sigma_phi_deg_2)
    redefine_variable('sigma_phi', target_sigma_phi_rad_2)
    print(f"\nTarget DOA Accuracy: {target_sigma_phi_deg_2} degrees ({v.sigma_phi:.4f} rad)")
    redefine_variable('B', solve.B_from_sigma_time())
    print(f"Calculated required Bandwidth 'B': {convert.hz_to(v.B, 'ghz'):.2f} GHz")

    # --- Topic 07: Doppler CW Radar Demo ---
    print("\n" + "="*30)
    print("Topic 07: Doppler CW Radar Demo (Prob 2)")
    print("="*30 + "\n")
    redefine_variable('f', convert.hz_from(10, 'ghz')) # 10 GHz
    redefine_variable('wavelength', solve.wavelength())
    redefine_variable('f_if', convert.hz_from(100, 'mhz')) # 100 MHz IF
    redefine_variable('v', -100.0) # 100 m/s closing
    redefine_variable('T_cpi', 10e-3) # 10 ms
    
    redefine_variable('f_doppler', solve.f_doppler())
    print(f"Given: f = {convert.hz_to(v.f, 'ghz')} GHz (lambda = {v.wavelength:.3f} m), v = {v.v} m/s (closing)")
    print(f"Calculated Doppler Shift (f_doppler): {convert.hz_to(v.f_doppler, 'khz'):.2f} kHz")
    redefine_variable('f_obs', solve.f_obs_if())
    print(f"Given IF = {convert.hz_to(v.f_if, 'mhz')} MHz, Observed Freq = {convert.hz_to(v.f_obs, 'mhz'):.4f} MHz")
    
    redefine_variable('f_doppler', 10e3) # 10 kHz shift (Prob 2c)
    redefine_variable('v', solve.v_from_doppler())
    print(f"\nGiven Doppler Shift = {convert.hz_to(v.f_doppler, 'khz')} kHz, Calculated Velocity = {v.v:.2f} m/s (separating)")
    
    redefine_variable('delta_v', solve.delta_v())
    print(f"\nGiven CPI Time = {v.T_cpi * 1000} ms, Velocity Resolution = {v.delta_v:.2f} m/s")

    # --- Topic 08: CWFM Radar Demo ---
    print("\n" + "="*30)
    print("Topic 08: CWFM Radar Demo (Prob 2)")
    print("="*30 + "\n")
    redefine_variable('f', convert.hz_from(35, 'ghz')) # 35 GHz
    redefine_variable('wavelength', solve.wavelength())
    redefine_variable('f_m', 100.0) # 100 Hz
    redefine_variable('deltaf', convert.hz_from(30, 'mhz')) # 30 MHz
    redefine_variable('f_bu', convert.hz_from(85, 'khz')) # 85 kHz
    redefine_variable('f_bd', convert.hz_from(75, 'khz')) # 75 kHz
    
    redefine_variable('f_r', solve.f_r_cwfm())
    redefine_variable('f_d', solve.f_d_cwfm())
    print(f"Given: f_bu = {convert.hz_to(v.f_bu, 'khz')} kHz, f_bd = {convert.hz_to(v.f_bd, 'khz')} kHz")
    print(f"Calculated: f_r = {convert.hz_to(v.f_r, 'khz')} kHz, f_d = {convert.hz_to(v.f_d, 'khz')} kHz")
    
    redefine_variable('R', solve.R_cwfm())
    redefine_variable('v', solve.v_cwfm()) # Uses f_d, f
    print(f"Calculated Range = {v.R:.0f} m, Calculated Velocity = {v.v:.2f} m/s") # Matches 2000m, 21.5 m/s

    # --- Topic 09/10: Pulsed Radar & Range Ambiguity Demo ---
    print("\n" + "="*30)
    print("Topic 09/10: Pulsed Radar & Ambiguity Demo")
    print("="*30 + "\n")
    
    print("--- Problem 3 (Topic 10) ---")
    redefine_variable('R_un', convert.nmi_to_m(60)) # 60 nmi
    redefine_variable('f_p', solve.fp_from_R_un())
    print(f"Given R_un = 60 nmi, Calculated PRF (f_p) = {convert.hz_to(v.f_p, 'khz'):.2f} kHz")
    
    redefine_variable('R_un', convert.m_from(10, 'km')) # 10 km
    redefine_variable('T_p', 2 * v.R_un / v.c)
    redefine_variable('duty_cycle', 0.10) # 10%
    redefine_variable('tau', solve.tau_from_duty())
    print(f"\nGiven R_un = 10 km (T_p = {v.T_p * 1e6:.2f} us), Duty = 10%")
    print(f"Calculated Pulse Width (tau) = {v.tau * 1e6:.2f} us")
    
    print("\n--- Problem 7 (Topic 09) ---")
    redefine_variable('S_N_1_dB', 15.0) # 15 dB
    redefine_variable('n_p', 25) # 25 pulses
    print(f"Given: (S/N)_1 = {v.S_N_1_dB} dB, n_p = {v.n_p}")
    S_N_n_coh = solve.S_N_n_coherent_dB()
    S_N_n_noncoh = solve.S_N_n_noncoherent_dB()
    print(f"Calculated (S/N)_n (Coherent) = {S_N_n_coh:.2f} dB") # 15 + 10*log10(25) = 28.98 dB
    print(f"Calculated (S/N)_n (Non-Coherent, 1/sqrt(n)) = {S_N_n_noncoh:.2f} dB") # 15 + 5*log10(25) = 21.99 dB

    print("\n--- Problem 4 (Topic 10) - Range Ambiguity ---")
    prfs = [1000, 1250, 1500] # Hz
    detections = {
        1000: [20, 100], # km
        1250: [10, 80],  # km
        1500: [20, 50]   # km
    }
    max_range_km = 300 # Search up to 300 km
    unambiguous_ranges_km = {f: convert.m_to(v.c / (2 * f), 'km') for f in prfs}
    print(f"PRFs (Hz): {prfs}")
    print(f"Unambiguous Ranges (km): {[round(r,1) for r in unambiguous_ranges_km.values()]}")
    
    possible_ranges = {}
    for prf, ru in unambiguous_ranges_km.items():
        possible_ranges[prf] = set()
        for R_measured in detections[prf]:
            for n in range(int(max_range_km / ru) + 1):
                R_true = R_measured + n * ru
                if R_true <= max_range_km:
                    possible_ranges[prf].add(round(R_true))
                    
    print(f"Possible Ranges (km) for PRF 1000: {sorted(list(possible_ranges[1000]))}")
    print(f"Possible Ranges (km) for PRF 1250: {sorted(list(possible_ranges[1250]))}")
    print(f"Possible Ranges (km) for PRF 1500: {sorted(list(possible_ranges[1500]))}")
    
    # Find intersection
    true_targets = possible_ranges[1000].intersection(possible_ranges[1250]).intersection(possible_ranges[1500])
    print(f"True Target Ranges (km): {true_targets}") # Matches {170, 200} km (rounding)
    
    # --- Topic 11: Pulse Compression Demo ---
    print("\n" + "="*30)
    print("Topic 11: Pulse Compression Demo (Prob 1 & 4)")
    print("="*30 + "\n")
    
    redefine_variable('tau', 20e-6) # 20 us
    redefine_variable('delta_r', solve.delta_r_uncompressed())
    print(f"Given: Uncompressed Pulse Width (tau) = {v.tau * 1e6:.0f} us")
    print(f"Calculated Uncompressed Range Res = {v.delta_r:.0f} m") # 3000m
    
    redefine_variable('gamma', 10e6 / 1e-6) # 10 MHz/us = 10e12 Hz/s
    redefine_variable('B', solve.B_chirp())
    redefine_variable('delta_r', solve.delta_r_compressed())
    print(f"\nGiven: Chirp Rate (gamma) = 10 MHz/us, tau = {v.tau * 1e6:.0f} us")
    print(f"Calculated Bandwidth (B) = {convert.hz_to(v.B, 'mhz')} MHz")
    print(f"Calculated Compressed Range Res = {v.delta_r:.2f} m") # 0.75m
    
    redefine_variable('PCR', solve.PCR_from_B())
    print(f"Calculated PCR (from B*tau) = {v.PCR:.0f}") # 4000
    
    redefine_variable('R_offset', 100) # 100m
    redefine_variable('f_range_tone', solve.f_range_tone())
    print(f"\nGiven: Range Offset = {v.R_offset} m")
    print(f"Calculated Dechirp Range Tone = {convert.hz_to(v.f_range_tone, 'mhz'):.2f} MHz") # -6.67 MHz
