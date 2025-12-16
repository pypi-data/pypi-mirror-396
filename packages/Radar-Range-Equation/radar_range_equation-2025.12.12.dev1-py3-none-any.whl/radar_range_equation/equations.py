"""Radar Range Equation - Symbolic Equations Module.

This module defines the equations class which contains symbolic SymPy
representations of radar equations for various radar types and calculations.
"""

import sympy
from sympy import Symbol, exp, sqrt, log


class equations:
    """Symbolic SymPy equations for radar calculations.
    
    This class contains symbolic representations of radar equations using SymPy.
    Each equation is stored as a SymPy Eq object that can be manipulated symbolically
    or solved numerically using the solve class.
    
    The equations are organized by topic:
        - Base/Common: Fundamental radar equations (wavelength, gain, range)
        - Topic 07: Doppler CW radar equations
        - Topic 08: CWFM radar equations
        - Topic 09: Pulsed radar equations
        - Topic 10: Direction finding equations
        - Topic 11: Pulse compression equations
    
    Attributes:
        A_e (Eq): Effective aperture equation
        wavelength (Eq): Wavelength equation (lambda = c/f)
        G_t (Eq): Transmit antenna gain equation
        R_max (Eq): Maximum radar range equation
        Linear_to_dB (Eq): Linear to dB conversion equation
        
        Doppler CW Radar:
            eq_f_doppler (Eq): Doppler frequency shift equation
            eq_v_from_doppler (Eq): Velocity from Doppler shift
            eq_delta_v (Eq): Velocity resolution equation
            
        CWFM Radar:
            R_cwfm (Eq): Range equation for CWFM radar
            v_cwfm (Eq): Velocity equation for CWFM radar
            
        Pulsed Radar:
            eq_R_un_from_fp (Eq): Unambiguous range from PRF
            eq_T_p (Eq): Pulse repetition interval equation
            eq_S_N_n_coherent (Eq): Coherent integration SNR
            
        Direction Finding:
            phi_hat_amp (Eq): Angle estimate for amplitude comparison
            sigma_phi_amp (Eq): Angle accuracy for amplitude comparison
            sigma_phi_phase (Eq): Angle accuracy for phase comparison
            sigma_phi_time (Eq): Angle accuracy for time comparison
            
        Pulse Compression:
            eq_delta_r_uncompressed (Eq): Uncompressed range resolution
            eq_delta_r_compressed (Eq): Compressed range resolution
            eq_PCR_1 (Eq): Pulse compression ratio equation
    
    Example:
        >>> from radar_range_equation import equations
        >>> print(equations.wavelength)
        Eq(lambda, c/f)
    """
    # --- Base/Common Symbols ---
    c_sym = Symbol('c')
    f_sym = Symbol('f')
    eta_sym = Symbol('eta')
    D_h_sym = Symbol('D_h')
    D_v_sym = Symbol('D_v')
    x_sym = Symbol('x')
    R_sym = Symbol('R')
    A_e_sym = Symbol('A_e')
    wavelength_sym = Symbol('lambda')
    G_t_sym = Symbol('G_t')
    P_t_sym = Symbol('P_t')
    sigma_sym = Symbol('sigma')
    S_min_sym = Symbol('S_min')
    R_max_sym = Symbol('R_max')
    pi_sym = Symbol('pi')
    theta_B_sym = Symbol('theta_B')
    v_sym = Symbol('v')

    # --- Topic 07: Doppler CW Radar Symbols ---
    f_doppler_sym = Symbol('f_doppler')
    f_if_sym = Symbol('f_if')
    f_obs_sym = Symbol('f_obs')
    T_cpi_sym = Symbol('T_cpi')
    delta_v_sym = Symbol('delta_v')

    # --- Topic 08: CWFM Radar Symbols ---
    R_un_sym = Symbol('R_un')
    f_m_sym = Symbol('f_m')
    f_bu_sym = Symbol('f_bu')
    f_bd_sym = Symbol('f_bd')
    f_r_sym = Symbol('f_r')
    f_d_sym = Symbol('f_d')
    f_0_sym = Symbol('f_0')
    deltaf_sym = Symbol('Delta f')
    
    # --- Topic 09: Pulsed Radar Symbols ---
    f_p_sym = Symbol('f_p')
    T_p_sym = Symbol('T_p')
    t_delay_sym = Symbol('t_delay')
    duty_cycle_sym = Symbol('duty_cycle')
    tau_sym = Symbol('tau')
    n_p_sym = Symbol('n_p')
    t_scan_sym = Symbol('t_scan')
    S_N_1_sym = Symbol('S_N_1')
    S_N_n_sym = Symbol('S_N_n')
    E_i_sym = Symbol('E_i')

    # --- Topic 10: Direction Finding Symbols ---
    phi_sym = Symbol('phi')
    phi_s_sym = Symbol('phi_s')
    Theta_sym = Symbol('Theta')
    v_phi_sym = Symbol('v_phi')
    Delta_sym = Symbol('Delta')
    Sigma_sym = Symbol('Sigma')
    phi_hat_sym = Symbol('phi_hat')
    sigma_phi_sym = Symbol('sigma_phi')
    S_N_sym = Symbol('S_N')
    S_N_dB_sym = Symbol('S_N_dB')
    d_sym = Symbol('d')
    B_sym = Symbol('B')

    # --- Topic 11: Pulse Compression Symbols ---
    delta_r_sym = Symbol('delta_r')
    gamma_sym = Symbol('gamma')
    PCR_sym = Symbol('PCR')
    R_offset_sym = Symbol('R_offset')
    f_range_tone_sym = Symbol('f_range_tone')

    # --- Topic 12: Chaff Symbols ---
    L_fiber_sym = Symbol('L_fiber')
    D_fiber_sym = Symbol('D_fiber')
    V_ch_sym = Symbol('V_ch')
    V_box_sym = Symbol('V_box')
    Fill_ratio_sym = Symbol('Fill_ratio')
    N_fiber_sym = Symbol('N_fiber')
    sigma_ch_sym = Symbol('sigma_ch')
    zeta_ch_sym = Symbol('zeta_ch')
    
    # --- Topic 13: Noise Jamming Symbols ---
    Pj_sym = Symbol('Pj')
    Gj_sym = Symbol('Gj')
    Bj_sym = Symbol('Bj')
    Lossj_sym = Symbol('Lossj')
    S_J_ratio_sym = Symbol('S/J')
    R_bt_sym = Symbol('R_bt')
    
    # --- Topic 14: Gated Noise Symbols ---
    R_tgt_sym = Symbol('R_tgt')
    R_gn_start_offset_sym = Symbol('R_gn_start_offset')
    t_tgt_2way_sym = Symbol('t_tgt_2way')
    t_gn_start_release_sym = Symbol('t_gn_start_release')
    Delta_R_mask_sym = Symbol('Delta_R_mask')
    
    # --- Topic 15: False Target Generation Symbols ---
    v_tgt_sym = Symbol('v_tgt')
    R_ft_sym = Symbol('R_ft')
    v_ft_sym = Symbol('v_ft')
    f_D_tgt_sym = Symbol('f_D_tgt')
    f_D_ft_sym = Symbol('f_D_ft')
    Delta_t_ft_sym = Symbol('Delta_t_ft')
    Delta_f_ft_sym = Symbol('Delta_f_ft')
    
    # --- Topic 16: Radar Tracking / False Tracks Symbols ---
    P_density_sym = Symbol('P_density')
    Pj_emulated_sym = Symbol('Pj_emulated')

    # --- Topic 17: Gate Stealing Symbols ---
    alpha_sym = Symbol('alpha')
    g_sym = Symbol('g')
    T_time_sym = Symbol('T')
    Delta_r_max_sym = Symbol('Delta_r_max')
    Delta_r_t_sym = Symbol('Delta_r(t)')
    rho_v_sym = Symbol('rho_v')
    n_gate_r_sym = Symbol('n_gate_r')
    n_gate_v_sym = Symbol('n_gate_v')
    Delta_v_max_sym = Symbol('Delta_v_max')
    a_accel_sym = Symbol('a')
    Delta_v_t_sym = Symbol('Delta_v(t)')

    # --- Topic 18: Cross-Eye Symbols ---
    L_cross_sym = Symbol('L')
    a_gain_ratio_sym = Symbol('a_ratio')
    J_1_sym = Symbol('J_1')
    J_2_sym = Symbol('J_2')
    phi_hat_ce_sym = Symbol('phi_hat_ce')
    S_phi_bar_sym = Symbol('S_phi_bar')

    # --- Legacy: Range Gate Pull-Off (RGPO) Symbols ---
    R_gate_sym = Symbol('R_gate')
    delta_R_gate_sym = Symbol('delta_R_gate')
    R_true_sym = Symbol('R_true')
    R_false_sym = Symbol('R_false')
    delta_t_pull_sym = Symbol('delta_t_pull')
    delta_R_pull_sym = Symbol('delta_R_pull')
    pull_rate_sym = Symbol('pull_rate')
    n_pulses_capture_sym = Symbol('n_pulses_capture')
    gate_bias_sym = Symbol('gate_bias')
    alpha_track_sym = Symbol('alpha_track')
    BW_track_sym = Symbol('BW_track')

    # =========================================================================
    # EQUATIONS
    # =========================================================================

    # --- Base/Common Equations ---
    A_e = sympy.Eq(A_e_sym, eta_sym * D_h_sym * D_v_sym)
    wavelength = sympy.Eq(wavelength_sym, c_sym / f_sym)
    G_t = sympy.Eq(G_t_sym, 4 * sympy.pi * A_e_sym / (wavelength_sym ** 2))
    Linear_to_dB = sympy.Eq(x_sym, 10 * sympy.log(x_sym) / sympy.log(10))
    R4 = sympy.Eq(R_sym**4, (P_t_sym * G_t_sym**2 * wavelength_sym**2 * sigma_sym) / ((4 * sympy.pi)**3 * S_min_sym))
    P_t = sympy.Eq(P_t_sym, ((4 * pi_sym)**3 * S_min_sym * R_sym**4) / (G_t_sym**2 * wavelength_sym**2 * sigma_sym))
    R_max = sympy.Eq(R_max_sym, sympy.Pow((P_t_sym * (G_t_sym**2) * (wavelength_sym**2) * sigma_sym) / ((4 * pi_sym)**3 * S_min_sym), sympy.Rational(1, 4), evaluate=False), evaluate=False)
    theta_B = sympy.Eq(theta_B_sym, 65 * sympy.pi / 180 * (wavelength_sym / D_h_sym)) # Gaussian approx

    # --- Topic 07: Doppler CW Radar Equations ---
    eq_f_doppler = sympy.Eq(f_doppler_sym, -2 * v_sym / wavelength_sym)
    eq_v_from_doppler = sympy.Eq(v_sym, -wavelength_sym * f_doppler_sym / 2)
    eq_f_obs_if = sympy.Eq(f_obs_sym, f_if_sym + f_doppler_sym)
    eq_delta_v = sympy.Eq(delta_v_sym, wavelength_sym / (2 * T_cpi_sym))
    
    # --- Topic 08: CWFM Radar Equations ---
    R_cwfm = sympy.Eq(R_sym, (c_sym*f_r_sym)/(4*f_m_sym*deltaf_sym))
    v_cwfm = sympy.Eq(v_sym, -(c_sym/f_sym)*(f_d_sym/2))
    f_m_cwfm = sympy.Eq(f_m_sym, c_sym/(2*R_un_sym))
    f_0_cwfm = sympy.Eq(f_0_sym, 2*f_m_sym*deltaf_sym)
    f_r_cwfm = sympy.Eq(f_r_sym, .5*(f_bu_sym+f_bd_sym))
    f_d_cwfm = sympy.Eq(f_d_sym, .5*(f_bu_sym-f_bd_sym))

    # --- Topic 09: Pulsed Radar & Range Ambiguity Equations ---
    eq_R_un_from_fp = sympy.Eq(R_un_sym, c_sym / (2 * f_p_sym))
    eq_fp_from_R_un = sympy.Eq(f_p_sym, c_sym / (2 * R_un_sym))
    eq_T_p = sympy.Eq(T_p_sym, 1 / f_p_sym)
    eq_R_from_time = sympy.Eq(R_sym, c_sym * t_delay_sym / 2)
    eq_tau_from_duty = sympy.Eq(tau_sym, T_p_sym * duty_cycle_sym)
    eq_n_p = sympy.Eq(n_p_sym, f_p_sym * t_scan_sym * (theta_B_sym / (2 * pi_sym)))
    eq_S_N_n_coherent = sympy.Eq(S_N_n_sym, n_p_sym * S_N_1_sym)
    eq_S_N_n_noncoherent_Ei = sympy.Eq(S_N_n_sym, E_i_sym * n_p_sym * S_N_1_sym)
    eq_E_i_sqrt_n = sympy.Eq(E_i_sym, 1 / sqrt(n_p_sym))
    eq_S_N_n_noncoherent = eq_S_N_n_noncoherent_Ei.subs(E_i_sym, eq_E_i_sqrt_n.rhs)
    eq_theta_B_skolnik = sympy.Eq(theta_B_sym, 1.2 * wavelength_sym / D_h_sym)

    # --- Topic 10: Direction Finding Equations ---
    S_N_from_dB = sympy.Eq(S_N_sym, 10**(S_N_dB_sym / 10))
    v_phi = sympy.Eq(v_phi_sym, exp(-Theta_sym * (phi_sym - phi_s_sym)**2))
    Theta = sympy.Eq(Theta_sym, (4 * log(2)) / theta_B_sym**2)
    phi_hat_amp = sympy.Eq(phi_hat_sym, (Delta_sym / Sigma_sym) * (theta_B_sym**2 / (8 * log(2) * phi_s_sym)))
    sigma_phi_amp = sympy.Eq(sigma_phi_sym, (theta_B_sym**2 * sqrt(1 / S_N_sym)) / (8 * sqrt(2) * phi_s_sym * log(2)))
    sigma_phi_phase = sympy.Eq(sigma_phi_sym, (wavelength_sym / (2 * pi_sym * d_sym)) * sqrt(1 / S_N_sym))
    sigma_phi_time = sympy.Eq(sigma_phi_sym, c_sym / (d_sym * B_sym))

    # --- Topic 11: Pulse Compression Equations ---
    eq_delta_r_uncompressed = sympy.Eq(delta_r_sym, c_sym * tau_sym / 2)
    eq_B_chirp = sympy.Eq(B_sym, gamma_sym * tau_sym)
    eq_delta_r_compressed = sympy.Eq(delta_r_sym, c_sym / (2 * B_sym))
    eq_PCR_1 = sympy.Eq(PCR_sym, tau_sym * B_sym)
    eq_PCR_2 = sympy.Eq(PCR_sym, (tau_sym**2) * gamma_sym)
    eq_f_range_tone = sympy.Eq(f_range_tone_sym, -gamma_sym * (2 * R_offset_sym / c_sym))

    # --- Topic 12: Chaff Equations ---
    # Chaff Fiber Length
    eq_L_fiber = sympy.Eq(L_fiber_sym, wavelength_sym / 2)
    # Volume of a Single Chaff Fiber (approximated as cylinder)
    eq_V_ch = sympy.Eq(V_ch_sym, (sympy.pi * L_fiber_sym * D_fiber_sym**2) / 4)
    # Number of Fibers in Box
    eq_N_fiber = sympy.Eq(N_fiber_sym, (V_box_sym * Fill_ratio_sym) / V_ch_sym)
    # RCS of Chaff Cloud (Time-dependent)
    eq_sigma_ch_t = sympy.Eq(sigma_ch_sym, 0.15 * N_fiber_sym * wavelength_sym**2 * (1 - exp(-t_delay_sym / zeta_ch_sym)))
    # Max RCS of Chaff Cloud (t -> inf)
    eq_sigma_ch_max = sympy.Eq(sigma_ch_sym, 0.15 * N_fiber_sym * wavelength_sym**2)
    
    # --- Topic 13: Noise Jamming Equations ---
    # Signal-to-Jammer (S/J) Ratio for Barrage Noise
    eq_S_J_ratio = sympy.Eq(S_J_ratio_sym, (P_t_sym * G_t_sym * sigma_sym * n_p_sym * Bj_sym) / (4 * sympy.pi * R_sym**2 * Pj_sym * Gj_sym * Lossj_sym * B_sym))
    # Burnthrough Range
    eq_R_bt = sympy.Eq(R_bt_sym**2, (P_t_sym * G_t_sym * sigma_sym * n_p_sym * Bj_sym) / (4 * sympy.pi * Pj_sym * Gj_sym * Lossj_sym * B_sym * S_min_sym))
    
    # --- Topic 14: Gated Noise Equations ---
    # Two-way time to target
    eq_t_tgt_2way = sympy.Eq(t_tgt_2way_sym, 2 * R_tgt_sym / c_sym)
    # Gated Noise Start Release Time
    eq_t_gn_start_release = sympy.Eq(t_gn_start_release_sym, (2 * (R_tgt_sym - R_gn_start_offset_sym) / c_sym) - (tau_sym / 2))
    
    # --- Topic 15: False Target Generation Equations ---
    # Target Doppler Frequency
    eq_f_D_tgt = sympy.Eq(f_D_tgt_sym, -2 * v_tgt_sym / wavelength_sym)
    # False Target Doppler Frequency
    eq_f_D_ft = sympy.Eq(f_D_ft_sym, -2 * v_ft_sym / wavelength_sym)
    # Time Delay to apply
    eq_Delta_t_ft = sympy.Eq(Delta_t_ft_sym, (2 * R_ft_sym / c_sym) - (2 * R_sym / c_sym))
    # Frequency Shift to apply
    eq_Delta_f_ft = sympy.Eq(Delta_f_ft_sym, f_D_ft_sym - f_D_tgt_sym)

    # --- Topic 16: Radar Tracking / False Tracks Equations ---
    # Power Density at Jammer/Target
    eq_P_density = sympy.Eq(P_density_sym, (P_t_sym * G_t_sym) / (4 * sympy.pi * R_sym**2))
    # Required Jammer Power to Emulate RCS
    eq_Pj_emulated = sympy.Eq(Pj_emulated_sym, (P_density_sym * sigma_sym) / Gj_sym)

    # --- Topic 17: Gate Stealing Equations ---
    # Velocity Resolution (Doppler bin size)
    eq_rho_v = sympy.Eq(rho_v_sym, wavelength_sym / (2 * T_cpi_sym))
    # Required Max Range Offset (Gate Size * Resolution)
    eq_Delta_r_max_gate = sympy.Eq(Delta_r_max_sym, n_gate_r_sym * delta_r_sym)
    # Time (T) from Max Range Offset (Delta_r_max = 0.5 * alpha * T^2)
    eq_T_from_Delta_r = sympy.Eq(Delta_r_max_sym, sympy.Rational(1, 2) * alpha_sym * T_time_sym**2)
    # Range Offset Profile (Delta_r(t) = 0.5 * alpha * t^2)
    eq_Delta_r_t = sympy.Eq(Delta_r_t_sym, sympy.Rational(1, 2) * alpha_sym * t_delay_sym**2)
    # Required Max Velocity Offset (Gate Size * Resolution)
    eq_Delta_v_max_gate = sympy.Eq(Delta_v_max_sym, n_gate_v_sym * rho_v_sym)
    # Time (T) from Max Velocity Offset (Delta_v_max = a * T)
    eq_T_from_Delta_v = sympy.Eq(Delta_v_max_sym, a_accel_sym * T_time_sym)
    # Velocity Offset Profile (Delta_v(t) = a * t)
    eq_Delta_v_t = sympy.Eq(Delta_v_t_sym, a_accel_sym * t_delay_sym)

    # --- Topic 18: Cross-Eye Equations ---
    # Jammer Gain Ratio (a)
    eq_J_ratio = sympy.Eq(a_gain_ratio_sym, J_1_sym / J_2_sym)
    # Apparent Cross-Eye Angle Error (Amplitude Monopulse Approximation)
    eq_phi_hat_ce_amp = sympy.Eq(phi_hat_ce_sym, sympy.Rational(1, 2) * (L_cross_sym / R_sym) * (1 + a_gain_ratio_sym) / (1 - a_gain_ratio_sym))

    # --- Legacy: Gate Stealing / Range Gate Pull-Off (RGPO) Equations ---
    # Time delay per pull increment
    eq_delta_t_pull = sympy.Eq(delta_t_pull_sym, 2 * delta_R_pull_sym / c_sym)
    
    # Range increment from time delay increment
    eq_delta_R_from_time = sympy.Eq(delta_R_pull_sym, c_sym * delta_t_pull_sym / 2)
    
    # Pull-off rate (range per pulse)
    eq_pull_rate = sympy.Eq(pull_rate_sym, delta_R_pull_sym)
    
    # Number of pulses to pull gate a certain distance
    eq_n_pulses_rgpo = sympy.Eq(n_pulses_capture_sym, (R_false_sym - R_true_sym) / delta_R_pull_sym)
    
    # Gate bias/tracking error
    eq_gate_bias = sympy.Eq(gate_bias_sym, R_gate_sym - R_true_sym)
    
    # Tracking loop bandwidth (first-order alpha-beta filter approximation)
    eq_BW_track = sympy.Eq(BW_track_sym, alpha_track_sym * f_p_sym / (2 * pi_sym))
    eq_B_chirp = sympy.Eq(B_sym, gamma_sym * tau_sym)
    eq_delta_r_compressed = sympy.Eq(delta_r_sym, c_sym / (2 * B_sym))
    eq_PCR_1 = sympy.Eq(PCR_sym, tau_sym * B_sym)
    eq_PCR_2 = sympy.Eq(PCR_sym, (tau_sym**2) * gamma_sym)
    eq_f_range_tone = sympy.Eq(f_range_tone_sym, -gamma_sym * (2 * R_offset_sym / c_sym))

