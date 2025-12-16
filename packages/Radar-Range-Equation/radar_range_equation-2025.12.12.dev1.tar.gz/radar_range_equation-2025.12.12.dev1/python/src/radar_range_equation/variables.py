"""Radar Range Equation - Variable Definitions Module.

This module defines the vars class which provides a centralized namespace
for all radar-related variables, including physical constants, antenna
parameters, and topic-specific variables for different radar types.
"""

from sympy import Symbol
from . import constants


class vars:
    """Container for radar system variables and physical constants.
    
    This class provides a centralized namespace for all radar-related variables,
    including physical constants, antenna parameters, radar equation parameters,
    and topic-specific variables for different radar types.
    
    Attributes:
        c (float): Speed of light in m/s (from scipy.constants.c)
        k (float): Boltzmann constant in J/K (from scipy.constants.Boltzmann)
        pi (float): Mathematical constant pi
        pi4 (float): 4*pi constant
        f (Symbol): Frequency (symbolic)
        wavelength (Symbol): Wavelength (symbolic, use getattr/setattr for 'lambda')
        
        Antenna Parameters:
            A_e (Symbol): Effective aperture
            A (Symbol): Antenna area
            D_h (Symbol): Horizontal antenna dimension
            D_v (Symbol): Vertical antenna dimension
            D (Symbol): Antenna diameter
            eta (Symbol): Antenna efficiency
            G_t (Symbol): Transmit antenna gain
            G_r (Symbol): Receive antenna gain
            theta_B (Symbol): Beamwidth
            
        Radar Equation Parameters:
            R (Symbol): Range
            R_max (Symbol): Maximum range
            P_t (Symbol): Transmit power
            S_min (Symbol): Minimum detectable signal
            sigma (Symbol): Radar cross section
            
        Doppler CW Radar (Topic 07):
            f_doppler (Symbol): Doppler frequency shift
            f_if (Symbol): Intermediate frequency
            f_obs (Symbol): Observed frequency at receiver
            T_cpi (Symbol): Coherent processing time
            delta_v (Symbol): Velocity resolution
            
        CWFM Radar (Topic 08):
            R_un (Symbol): Unnormalized range
            f_m (Symbol): Modulation frequency
            f_bu (Symbol): Upper band frequency
            f_bd (Symbol): Lower band frequency
            f_r (Symbol): Radar operating frequency
            f_d (Symbol): Frequency deviation
            
        Pulsed Radar (Topic 09):
            f_p (Symbol): Pulse Repetition Frequency (PRF)
            T_p (Symbol): Pulse Repetition Interval (PRI)
            tau (Symbol): Pulse width
            n_p (Symbol): Number of pulses integrated
            S_N_1 (Symbol): Single pulse SNR
            
        Direction Finding (Topic 10):
            phi (Symbol): Angle
            phi_s (Symbol): Squint angle
            d (Symbol): Element separation
            S_N (Symbol): Signal-to-Noise ratio
            B (Symbol): Bandwidth
            
        Pulse Compression (Topic 11):
            delta_r (Symbol): Range resolution
            gamma (Symbol): Chirp rate
            PCR (Symbol): Pulse Compression Ratio
    """
    # =========================================================================
    # BASE/COMMON PHYSICAL CONSTANTS AND VARIABLES
    # =========================================================================
    
    # Physical constants (imported from constants module)
    c = constants.c                     # speed of light (m/s)
    k = constants.k                     # Boltzmann constant (J/K)
    pi = constants.pi                   # pi (numeric)
    pi4 = constants.pi4                 # 4*pi (numeric)
    g = constants.g                     # Gravitational acceleration (m/s^2)
    T_0 = constants.T_0                 # reference temperature (K)
    
    # Generic and base symbolic variables
    x = Symbol('x')                     # generic variable for conversions (symbolic)
    f = Symbol('f')                     # frequency (symbolic)
    wavelength = Symbol('lambda')       # wavelength (symbolic)
    v = Symbol('v')                     # velocity (symbolic)
    
    # Antenna parameters
    A_e = Symbol('A_e')                 # effective aperture (symbolic)
    A = Symbol('A')                     # antenna area (symbolic)
    D_h = Symbol('D_h')                 # horizontal antenna dimension (symbolic)
    D_v = Symbol('D_v')                 # vertical antenna dimension (symbolic)
    D = Symbol('D')                     # antenna diameter dimension (symbolic)
    eta = Symbol('eta')                 # antenna efficiency (symbolic)
    G_t = Symbol('G_t')                 # transmit antenna gain (symbolic)
    G_t_dB = Symbol('G_t_dB')           # transmit antenna gain in dB (symbolic)
    G_r = Symbol('G_r')                 # receive antenna gain (symbolic)
    G_r_dB = Symbol('G_r_dB')           # receive antenna gain in dB (symbolic)
    theta_B = Symbol('theta_B')         # beamwidth (symbolic)
    
    # Radar equation parameters
    R = Symbol('R')                     # range (symbolic)
    R_max = Symbol('R_max')             # maximum range (symbolic)
    P_t = Symbol('P_t')                 # transmit power (symbolic)
    S_min = Symbol('S_min')             # minimum detectable signal (symbolic)
    sigma = Symbol('sigma')             # radar cross section (symbolic)

    # =========================================================================
    # TOPIC 07: DOPPLER CW RADAR VARS
    # =========================================================================
    
    f_doppler = Symbol('f_doppler')     # Doppler frequency shift (symbolic)
    f_if = Symbol('f_if')               # Intermediate frequency (symbolic)
    f_obs = Symbol('f_obs')             # Observed frequency at receiver (symbolic)
    T_cpi = Symbol('T_cpi')             # Coherent processing time (symbolic)
    delta_v = Symbol('delta_v')         # Velocity resolution (symbolic)

    # =========================================================================
    # TOPIC 08: CWFM RADAR VARS
    # =========================================================================
    
    R_un = Symbol('R_un')               # unnormalized range (symbolic)
    f_m = Symbol('f_m')                 # modulation frequency (symbolic)
    f_bu = Symbol('f_bu')               # upper band frequency (symbolic)
    f_bd = Symbol('f_bd')               # lower band frequency (symbolic)
    f_r = Symbol('f_r')                 # radar operating frequency (symbolic)
    f_d = Symbol('f_d')                 # frequency deviation (symbolic)
    deltaf = Symbol('Delta f')          # frequency difference (symbolic, with space)

    # =========================================================================
    # TOPIC 09: PULSED RADAR VARS
    # =========================================================================
    
    f_p = Symbol('f_p')                 # Pulse Repetition Frequency (PRF) (symbolic)
    T_p = Symbol('T_p')                 # Pulse Repetition Interval (PRI) (symbolic)
    t_delay = Symbol('t_delay')         # Round-trip time delay (symbolic)
    duty_cycle = Symbol('duty_cycle')   # Duty cycle (symbolic)
    tau = Symbol('tau')                 # Pulse width (symbolic)
    n_p = Symbol('n_p')                 # Number of pulses integrated (symbolic)
    t_scan = Symbol('t_scan')           # Antenna scan time (symbolic)
    S_N_1 = Symbol('S_N_1')             # Single pulse SNR (linear) (symbolic)
    S_N_1_dB = Symbol('S_N_1_dB')       # Single pulse SNR (dB) (symbolic)
    S_N_n = Symbol('S_N_n')             # Integrated SNR (linear) (symbolic)
    E_i = Symbol('E_i')                 # Integration efficiency (symbolic)

    # =========================================================================
    # TOPIC 10: DIRECTION FINDING VARS
    # =========================================================================
    
    phi = Symbol('phi')                 # Angle (symbolic)
    phi_s = Symbol('phi_s')             # Squint angle (symbolic)
    Theta = Symbol('Theta')             # Gaussian beam parameter (symbolic)
    v_phi = Symbol('v_phi')             # Gaussian beam voltage (symbolic)
    Delta = Symbol('Delta')             # Difference signal (symbolic)
    Sigma = Symbol('Sigma')             # Sum signal (symbolic)
    phi_hat = Symbol('phi_hat')         # Angle estimate (symbolic)
    sigma_phi = Symbol('sigma_phi')     # Angle standard deviation (symbolic)
    S_N = Symbol('S_N')                 # Signal-to-Noise ratio (linear) (symbolic)
    S_N_dB = Symbol('S_N_dB')           # Signal-to-Noise ratio (dB) (symbolic)
    d = Symbol('d')                     # Element separation (symbolic)
    B = Symbol('B')                     # Bandwidth (symbolic)

    # =========================================================================
    # TOPIC 11: PULSE COMPRESSION VARS
    # =========================================================================
    
    delta_r = Symbol('delta_r')         # Range resolution (symbolic)
    gamma = Symbol('gamma')             # Chirp rate (symbolic)
    PCR = Symbol('PCR')                 # Pulse Compression Ratio (symbolic)
    R_offset = Symbol('R_offset')       # Range offset from reference (symbolic)
    f_range_tone = Symbol('f_range_tone') # IF frequency from dechirp (symbolic)

    # =========================================================================
    # TOPIC 12: CHAFF VARS
    # =========================================================================
    L_fiber = Symbol('L_fiber')         # Chaff Fiber Length (m)
    D_fiber = Symbol('D_fiber')         # Chaff Fiber Diameter (m)
    V_ch = Symbol('V_ch')               # Volume of a single chaff fiber (m^3)
    V_box = Symbol('V_box')             # Volume of chaff cartridge (m^3)
    Fill_ratio = Symbol('Fill_ratio')   # Chaff cartridge fill ratio (dimensionless)
    N_fiber = Symbol('N_fiber')         # Number of chaff fibers (dimensionless)
    sigma_ch = Symbol('sigma_ch')       # Average RCS of chaff (m^2)
    zeta_ch = Symbol('zeta_ch')         # Chaff dispersion constant (s)

    # =========================================================================
    # TOPIC 13: NOISE JAMMING VARS
    # =========================================================================
    Pj = Symbol('Pj')                   # Jammer Transmit Power (W)
    Gj = Symbol('Gj')                   # Jammer Antenna Gain (linear)
    Bj = Symbol('Bj')                   # Jammer Bandwidth (Hz)
    Lossj = Symbol('Lossj')             # Jammer Loss (linear)
    S_J_ratio = Symbol('S/J')           # Signal-to-Jammer Ratio (linear)
    R_bt = Symbol('R_bt')               # Burnthrough Range (m)

    # =========================================================================
    # TOPIC 14: GATED NOISE VARS
    # =========================================================================
    R_tgt = Symbol('R_tgt')             # Target Range (m)
    R_gn_start_offset = Symbol('R_gn_start_offset') # Range before target to start noise (m)
    t_tgt_2way = Symbol('t_tgt_2way')   # Two-way time to target (s)
    t_gn_start_release = Symbol('t_gn_start_release') # Gated Noise start time (s)
    Delta_R_mask = Symbol('Delta_R_mask') # Total masking range (m)

    # =========================================================================
    # TOPIC 15: FALSE TARGET GENERATION VARS
    # =========================================================================
    v_tgt = Symbol('v_tgt')             # Target range rate (m/s)
    R_ft = Symbol('R_ft')               # False Target Range (m)
    v_ft = Symbol('v_ft')               # False Target range rate (m/s)
    f_D_tgt = Symbol('f_D_tgt')         # Doppler Frequency Target (Hz)
    f_D_ft = Symbol('f_D_ft')           # Doppler Frequency False Target (Hz)
    Delta_t_ft = Symbol('Delta_t_ft')   # Time Delay for False Target (s)
    Delta_f_ft = Symbol('Delta_f_ft')   # Frequency Shift for False Target (Hz)

    # =========================================================================
    # TOPIC 16: RADAR TRACKING / FALSE TRACKS VARS
    # =========================================================================
    P_density = Symbol('P_density')     # Power Density (W/m^2)
    Pj_emulated = Symbol('Pj_emulated') # Jammer Power to emulate target RCS (W)

    # =========================================================================
    # TOPIC 17: GATE STEALING VARS
    # =========================================================================
    alpha = Symbol('alpha')             # Target acceleration (effective for range) (symbolic)
    T_time = Symbol('T')                # Time duration (symbolic)
    Delta_r_max = Symbol('Delta_r_max') # Maximum required range offset (symbolic)
    Delta_r_t = Symbol('Delta_r(t)')    # Range offset profile (symbolic)
    rho_v = Symbol('rho_v')             # Velocity resolution (Doppler bin size) (symbolic)
    n_gate_r = Symbol('n_gate_r')       # Range gate size (resolution cells) (symbolic)
    n_gate_v = Symbol('n_gate_v')       # Velocity gate size (resolution cells) (symbolic)
    Delta_v_max = Symbol('Delta_v_max') # Maximum required velocity offset (symbolic)
    a_accel = Symbol('a')               # Target acceleration for velocity (symbolic)
    Delta_v_t = Symbol('Delta_v(t)')    # Velocity offset profile (symbolic)

    # =========================================================================
    # TOPIC 18: CROSS-EYE VARS
    # =========================================================================
    L_cross = Symbol('L')               # Cross-eye aperture separation (symbolic)
    a_gain_ratio = Symbol('a_ratio')    # Jammer gain ratio (J1/J2) (symbolic)
    J_1 = Symbol('J_1')                 # Jammer channel 1 gain (symbolic)
    J_2 = Symbol('J_2')                 # Jammer channel 2 gain (symbolic)
    phi_hat_ce = Symbol('phi_hat_ce')   # Cross-eye angle error (symbolic)
    S_phi_bar = Symbol('S_phi_bar')     # Normalized Monopulse Slope (symbolic)

    # =========================================================================
    # LEGACY: RANGE GATE PULL-OFF (RGPO) VARS (kept for compatibility)
    # =========================================================================
    R_gate = Symbol('R_gate')           # Range gate center position (symbolic)
    delta_R_gate = Symbol('delta_R_gate') # Range gate width (symbolic)
    R_true = Symbol('R_true')           # True target range (symbolic)
    R_false = Symbol('R_false')         # False target range (symbolic)
    delta_t_pull = Symbol('delta_t_pull') # Time delay increment per pulse (symbolic)
    delta_R_pull = Symbol('delta_R_pull') # Range increment per pulse (symbolic)
    pull_rate = Symbol('pull_rate')     # Pull-off rate (m/s or m/pulse) (symbolic)
    n_pulses_capture = Symbol('n_pulses_capture') # Number of pulses to capture gate (symbolic)
    gate_bias = Symbol('gate_bias')     # Range gate bias/error (symbolic)
    alpha_track = Symbol('alpha_track') # Tracking loop gain (symbolic)
    BW_track = Symbol('BW_track')       # Tracking bandwidth (Hz) (symbolic)

    # =========================================================================
    # SPECIAL VARIABLES
    # =========================================================================
    
    latex = False  # Set to True for LaTeX-style variable names
    if latex == True:
        R_hat_max = Symbol(r"\hat{R}_{max}")  # normalized maximum range (symbolic/latex)
    else:
        R_hat_max = Symbol("R\u0302_max")    # normalized maximum range (symbolic)


# Create a global instance of vars for easy access
v = vars()
