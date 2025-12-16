"""Radar Range Equation - Solvers Module.

This module defines the solve class which provides numeric solver functions
for radar calculations using Solvable instances and direct calculations.
"""

import numpy as np
import math
import sympy
from .solvable import Solvable
from .equations import equations
from .variables import vars
from .converters import convert


class solve:
    """Numeric solver functions for radar calculations.
    
    This class provides methods to solve radar equations numerically using values
    from the vars class. Functions either compute values directly using Python/NumPy
    or use the _solver helper to create callable functions from symbolic equations.
    
    The solver functions are organized by topic:
        - Base/Common: Fundamental calculations (wavelength, gain, range)
        - Topic 07: Doppler CW radar solvers
        - Topic 08: CWFM radar solvers
        - Topic 09: Pulsed radar solvers
        - Topic 10: Direction finding solvers
        - Topic 11: Pulse compression solvers
    
    Example:
        >>> import radar_range_equation as RRE
        >>> RRE.vars.c = 3e8
        >>> RRE.vars.f = 10e9
        >>> wavelength = RRE.solve.wavelength()
        >>> print(f"Wavelength: {wavelength} m")
    """
    def __init__():
        pass
    
    # =========================================================================
    # HELPER FUNCTION
    # =========================================================================
    
    def _solver(equation, solve_for_sym):
        """Internal helper to solve a SymPy equation and return a callable function."""
        try:
            # Solve the equation for the desired symbol
            sym_expr = sympy.solve(equation, solve_for_sym)[0]
        except (IndexError, Exception) as e:
            error_msg = f"Error: Could not solve equation for {solve_for_sym}: {e}"
            print(error_msg)
            def error_function():
                raise ValueError(error_msg)
            return error_function
            
        # Helper to convert Python numbers to sympy Floats but leave sympy types alone
        def _s(v):
            return v if isinstance(v, sympy.Basic) else sympy.Float(v)

        # Get all symbols used in the expression
        free_symbols = sym_expr.free_symbols
        
        def calculate():
            """Dynamically created solver function."""
            subs_map = {}
            for s in free_symbols:
                if hasattr(vars, s.name):
                    subs_map[s] = _s(getattr(vars, s.name))
                # Handle special cases like 'lambda'
                elif s.name == 'lambda' and hasattr(vars, 'wavelength'):
                    subs_map[s] = _s(getattr(vars, 'wavelength'))
                # Handle 'Delta f'
                elif str(s) == 'Delta f' and hasattr(vars, 'deltaf'):
                    subs_map[s] = _s(getattr(vars, 'deltaf'))
                else:
                    # This will catch sympy constants like pi, log(2), sqrt(2)
                    # which don't need substitution.
                    pass 
            
            value_sym = sym_expr.subs(subs_map)
            value_simpl = sympy.simplify(value_sym)
            return float(value_simpl.evalf())
        
        return calculate

    # =========================================================================
    # BASE/COMMON SOLVERS
    # =========================================================================
    
    def A_sphere():
        """Calculate the radius of a sphere from its radar cross section.
        
        Uses vars.sigma (radar cross section in m²).
        
        Returns:
            float: Radius of the sphere in meters.
        
        Example:
            >>> import radar_range_equation as RRE
            >>> RRE.vars.sigma = 3.14159
            >>> radius = RRE.solve.A_sphere()
        """
        return (vars.sigma / np.pi) ** (1/2)
    
    def sigma_sphere():
        """Calculate the radar cross section of a sphere from its area.
        
        Uses vars.A (antenna area in m²).
        
        Returns:
            float: Radar cross section in m².
        
        Example:
            >>> import radar_range_equation as RRE
            >>> RRE.vars.A = 1.0
            >>> rcs = RRE.solve.sigma_sphere()
        """
        return np.pi * vars.A ** 2

    def theta_B():
        """Calculate the 3-dB beamwidth using Gaussian approximation.
        
        Uses vars.wavelength (wavelength in m) and vars.D_h (horizontal antenna 
        dimension in m). Uses the approximation: theta_B = 65° * pi/180 * lambda/D_h.
        
        Returns:
            float: Beamwidth in radians.
        
        Example:
            >>> import radar_range_equation as RRE
            >>> RRE.vars.wavelength = 0.03
            >>> RRE.vars.D_h = 1.0
            >>> beamwidth = RRE.solve.theta_B()
        """
        return 65 * vars.pi / 180 * (vars.wavelength / vars.D_h)

    def A_e_rect():
        """Calculate effective aperture for a rectangular antenna.
        
        Uses vars.eta (antenna efficiency), vars.D_h (horizontal dimension in m),
        and vars.D_v (vertical dimension in m).
        
        Returns:
            float: Effective aperture in m².
        
        Example:
            >>> import radar_range_equation as RRE
            >>> RRE.vars.eta = 0.6
            >>> RRE.vars.D_h = 2.0
            >>> RRE.vars.D_v = 1.5
            >>> aperture = RRE.solve.A_e_rect()
        """
        return vars.eta * vars.D_h * vars.D_v

    def A_e_circ():
        """Calculate effective aperture for a circular antenna.
        
        Uses vars.eta (antenna efficiency) and vars.D (antenna diameter in m).
        
        Returns:
            float: Effective aperture in m².
        
        Example:
            >>> import radar_range_equation as RRE
            >>> RRE.vars.eta = 0.6
            >>> RRE.vars.D = 2.0
            >>> aperture = RRE.solve.A_e_circ()
        """
        return vars.eta * vars.pi * (vars.D / 2) ** 2

    # Converted to Solvable instances for interactive, introspective solving
    wavelength = Solvable(equations.wavelength_sym, [equations.wavelength])
    G_t = Solvable(equations.G_t_sym, [equations.G_t])
    
    # Legacy function-based versions (for direct Python calculation without sympy)
    @staticmethod
    def wavelength_func():
        """Calculate wavelength from frequency (legacy direct calculation).
        
        Uses vars.c (speed of light in m/s) and vars.f (frequency in Hz).
        
        Returns:
            float: Wavelength in meters.
        
        Example:
            >>> import radar_range_equation as RRE
            >>> RRE.vars.c = 3e8
            >>> RRE.vars.f = 10e9
            >>> wl = RRE.solve.wavelength_func()
        """
        return vars.c / vars.f

    @staticmethod
    def G_t_func():
        """Calculate transmit antenna gain (legacy direct calculation).
        
        Uses vars.pi (pi constant), vars.A_e (effective aperture in m²),
        and vars.wavelength (wavelength in m).
        
        Returns:
            float: Antenna gain (dimensionless).
        
        Example:
            >>> import radar_range_equation as RRE
            >>> RRE.vars.A_e = 1.0
            >>> RRE.vars.wavelength = 0.03
            >>> gain = RRE.solve.G_t_func()
        """
        return 4 * vars.pi * vars.A_e / (vars.wavelength ** 2)
    
    def R4():
        """Calculate R^4 from the radar range equation.
        
        Uses vars.P_t (transmit power), vars.G_t (transmit gain), vars.G_r (receive gain),
        vars.wavelength (wavelength in m), vars.sigma (radar cross section in m²),
        vars.pi4 (4*pi), and vars.S_min (minimum detectable signal).
        
        Returns:
            float: R^4 value. Take the fourth root to get range in meters.
        
        Example:
            >>> import radar_range_equation as RRE
            >>> RRE.vars.P_t = 1000
            >>> RRE.vars.G_t = 1000
            >>> RRE.vars.G_r = 1000
            >>> r4 = RRE.solve.R4()
            >>> r = r4 ** 0.25  # Get actual range
        """
        value = (vars.P_t * vars.G_t ** 2 * vars.G_r * vars.wavelength ** 2 * vars.sigma) / ( (vars.pi4) ** 3 * vars.S_min )
        return value
    
    # Converted to Solvable instances for interactive, introspective solving
    P_t = Solvable(equations.P_t_sym, [equations.P_t])
    R_max = Solvable(equations.R_max_sym, [equations.R_max])
    
    # Legacy function-based solvers for backward compatibility
    _P_t_func = _solver(equations.P_t, equations.P_t.lhs)
    _R_max_func = _solver(equations.R_max, equations.R_max.lhs)

    # =========================================================================
    # TOPIC 07: DOPPLER CW RADAR SOLVERS
    # =========================================================================
    
    # Converted to Solvable instances
    f_doppler = Solvable(equations.f_doppler_sym, [equations.eq_f_doppler])
    v_from_doppler = Solvable(equations.v_sym, [equations.eq_v_from_doppler])
    f_obs_if = Solvable(equations.f_obs_sym, [equations.eq_f_obs_if])
    delta_v = Solvable(equations.delta_v_sym, [equations.eq_delta_v])
    
    # Legacy function-based versions
    _f_doppler_func = _solver(equations.eq_f_doppler, equations.eq_f_doppler.lhs)
    _v_from_doppler_func = _solver(equations.eq_v_from_doppler, equations.eq_v_from_doppler.lhs)
    _f_obs_if_func = _solver(equations.eq_f_obs_if, equations.eq_f_obs_if.lhs)
    _delta_v_func = _solver(equations.eq_delta_v, equations.eq_delta_v.lhs)

    # =========================================================================
    # TOPIC 08: CWFM RADAR SOLVERS
    # =========================================================================
    
    # Converted to Solvable instances
    R_cwfm = Solvable(equations.R_sym, [equations.R_cwfm])
    v_cwfm = Solvable(equations.v_sym, [equations.v_cwfm])
    f_m_cwfm = Solvable(equations.f_m_sym, [equations.f_m_cwfm])
    f_r_cwfm = Solvable(equations.f_r_sym, [equations.f_r_cwfm])
    f_d_cwfm = Solvable(equations.f_d_sym, [equations.f_d_cwfm])
    f_0_cwfm = Solvable(equations.f_0_sym, [equations.f_0_cwfm])
    
    # Legacy function-based versions
    _R_cwfm_func = _solver(equations.R_cwfm, equations.R_cwfm.lhs)
    _v_cwfm_func = _solver(equations.v_cwfm, equations.v_cwfm.lhs)
    _f_m_cwfm_func = _solver(equations.f_m_cwfm, equations.f_m_cwfm.lhs)
    _f_r_cwfm_func = _solver(equations.f_r_cwfm, equations.f_r_cwfm.lhs)
    _f_d_cwfm_func = _solver(equations.f_d_cwfm, equations.f_d_cwfm.lhs)
    _f_0_cwfm_func = _solver(equations.f_0_cwfm, equations.f_0_cwfm.lhs)

    # =========================================================================
    # TOPIC 09: PULSED RADAR & RANGE AMBIGUITY SOLVERS
    # =========================================================================
    
    R_un_from_fp = _solver(equations.eq_R_un_from_fp, equations.eq_R_un_from_fp.lhs)
    fp_from_R_un = _solver(equations.eq_fp_from_R_un, equations.eq_fp_from_R_un.lhs)
    R_from_time = _solver(equations.eq_R_from_time, equations.eq_R_from_time.lhs)
    tau_from_duty = _solver(equations.eq_tau_from_duty, equations.eq_tau_from_duty.lhs)
    
    def S_N_n_coherent_dB():
        """Calculates integrated SNR (coherent) in dB."""
        S_N_1_lin = convert.db_to_lin(vars.S_N_1_dB)
        S_N_n_lin = vars.n_p * S_N_1_lin
        return convert.lin_to_db(S_N_n_lin)

    def S_N_n_noncoherent_dB():
        """Calculates integrated SNR (non-coherent, E_i=1/sqrt(n)) in dB."""
        S_N_1_lin = convert.db_to_lin(vars.S_N_1_dB)
        S_N_n_lin = np.sqrt(vars.n_p) * S_N_1_lin
        return convert.lin_to_db(S_N_n_lin)

    # =========================================================================
    # TOPIC 10: DIRECTION FINDING SOLVERS
    # =========================================================================
    
    # SymPy-based solvers
    S_N_from_dB = _solver(equations.S_N_from_dB, equations.S_N_from_dB.lhs)
    sigma_phi_amplitude = _solver(equations.sigma_phi_amp, equations.sigma_phi_amp.lhs)
    phi_s_from_sigma_amp = _solver(equations.sigma_phi_amp, equations.phi_s_sym)
    sigma_phi_phase = _solver(equations.sigma_phi_phase, equations.sigma_phi_phase.lhs)
    d_from_sigma_phase = _solver(equations.sigma_phi_phase, equations.d_sym)
    sigma_phi_time = _solver(equations.sigma_phi_time, equations.sigma_phi_time.lhs)
    B_from_sigma_time = _solver(equations.sigma_phi_time, equations.B_sym)

    # Legacy math-based methods (kept for backward compatibility)
    def calculate_Theta():
        """Calculates the Theta parameter from the 3-dB beamwidth.
        
        Uses vars.theta_B
        
        Returns:
            Theta parameter
        """
        return (4 * math.log(2)) / (vars.theta_B**2)
    
    def v_phi():
        """Calculates the Gaussian beam approximation.
        
        Uses vars.phi, vars.phi_s, vars.Theta
        
        Returns:
            Gaussian beam approximation value
        """
        return math.exp(-vars.Theta * (vars.phi - vars.phi_s)**2)
    
    def v_phi_full():
        """Calculates v(phi) using theta_B directly.
        
        Uses vars.phi, vars.phi_s, vars.theta_B
        
        Returns:
            Beam approximation value
        """
        return math.exp((4 * math.log(2) * (vars.phi - vars.phi_s)**2) / (vars.theta_B**2))
    
    def estimate_phi_hat():
        """Calculates the linear processor angle estimate.
        
        Uses vars.Delta, vars.Sigma, vars.theta_B, vars.phi_s
        
        Returns:
            Angle estimate in degrees
        """
        return (vars.Delta / vars.Sigma) * (vars.theta_B**2 / (8 * math.log(2) * vars.phi_s))
    
    def sigma_phi_amplitude():
        """Calculates the angle standard deviation for amplitude comparison.
        
        Uses vars.theta_B, vars.S_N, vars.phi_s
        
        Returns:
            Angle standard deviation in degrees
        """
        return (vars.theta_B**2 * math.sqrt(1 / vars.S_N)) / (8 * math.sqrt(2) * vars.phi_s * math.log(2))
    
    def sigma_phi_phase():
        """Calculates the angle standard deviation for phase comparison.
        
        Uses vars.wavelength, vars.d, vars.S_N
        
        Returns:
            Angle standard deviation in radians
        """
        return (vars.wavelength / (2 * math.pi * vars.d)) * math.sqrt(1 / vars.S_N)
    
    def sigma_phi_time():
        """Calculates the angle standard deviation for time comparison.
        
        Uses vars.c, vars.d, vars.B
        
        Returns:
            Angle standard deviation in radians
        """
        return vars.c / (vars.d * vars.B)
    
    def db_to_linear():
        """Converts SNR from dB to linear.
        
        Uses vars.x (as the dB value)
        
        Returns:
            Linear value
        """
        return 10**(vars.x / 10)

    # =========================================================================
    # TOPIC 11: PULSE COMPRESSION SOLVERS
    # =========================================================================
    
    delta_r_uncompressed = _solver(equations.eq_delta_r_uncompressed, equations.eq_delta_r_uncompressed.lhs)
    B_chirp = _solver(equations.eq_B_chirp, equations.eq_B_chirp.lhs)
    delta_r_compressed = _solver(equations.eq_delta_r_compressed, equations.eq_delta_r_compressed.lhs)
    PCR_from_B = _solver(equations.eq_PCR_1, equations.eq_PCR_1.lhs)
    PCR_from_gamma = _solver(equations.eq_PCR_2, equations.eq_PCR_2.lhs)
    f_range_tone = _solver(equations.eq_f_range_tone, equations.eq_f_range_tone.lhs)
    R_offset_from_tone = _solver(equations.eq_f_range_tone, equations.R_offset_sym)

    # =========================================================================
    # TOPIC 12: CHAFF SOLVERS
    # =========================================================================
    @staticmethod
    def L_fiber():
        """Calculate Chaff Fiber Length (lambda/2).
        Uses vars.wavelength (m).
        Returns: float: Fiber length (m)."""
        return vars.wavelength / 2

    @staticmethod
    def V_ch():
        """Calculate Volume of a single chaff fiber (cylinder).
        Uses vars.L_fiber (m) and vars.D_fiber (m).
        Returns: float: Fiber volume (m^3)."""
        # V_ch = pi * L * D^2 / 4
        return (vars.pi * vars.L_fiber * vars.D_fiber**2) / 4

    @staticmethod
    def N_fiber():
        """Calculate Number of fibers in a cartridge.
        Uses vars.V_box (m^3), vars.Fill_ratio (dim), and vars.V_ch (m^3).
        Returns: float: Number of fibers (dimensionless)."""
        # N_fiber = (V_box * Fill_ratio) / V_ch
        if vars.V_ch == 0:
            raise ValueError("Chaff fiber volume (V_ch) cannot be zero.")
        return (vars.V_box * vars.Fill_ratio) / vars.V_ch

    @staticmethod
    def sigma_ch_t(t_s):
        """Calculate RCS of Chaff Cloud at time t.
        Uses vars.N_fiber (dim), vars.wavelength (m), vars.zeta_ch (s), and t_s (s).
        Returns: float: RCS (m^2)."""
        # sigma_ch(t) = 0.15 * N * lambda^2 * (1 - e^(-t/zeta))
        return 0.15 * vars.N_fiber * vars.wavelength**2 * (1 - math.exp(-t_s / vars.zeta_ch))
        
    # =========================================================================
    # TOPIC 13: NOISE JAMMING SOLVERS
    # =========================================================================
    @staticmethod
    def S_J_ratio():
        """Calculate Signal-to-Jammer (S/J) Ratio for Barrage Noise.
        Uses Pt, Gt, sigma, n_p, Bj, R, Pj, Gj, Lossj, B.
        Returns: float: S/J Ratio (linear)."""
        # S/J = (Pt * Gt * sigma * n_p * Bj) / (4 * pi * R^2 * Pj * Gj * Lossj * B)
        numerator = vars.P_t * vars.G_t * vars.sigma * vars.n_p * vars.Bj
        denominator = 4 * vars.pi * vars.R**2 * vars.Pj * vars.Gj * vars.Lossj * vars.B
        if denominator == 0:
            raise ValueError("Denominator is zero. Check Pj, R, Gj, Lossj, or B.")
        return numerator / denominator

    @staticmethod
    def R_burnthrough():
        """Calculate Burnthrough Range (R_bt).
        Uses Pt, Gt, sigma, n_p, Bj, Pj, Gj, Lossj, B, S_min.
        Returns: float: Burnthrough Range (m)."""
        # R_bt = sqrt( (Pt * Gt * sigma * n_p * Bj) / (4 * pi * Pj * Gj * Lossj * B * S_min) )
        numerator = vars.P_t * vars.G_t * vars.sigma * vars.n_p * vars.Bj
        denominator = 4 * vars.pi * vars.Pj * vars.Gj * vars.Lossj * vars.B * vars.S_min
        if denominator <= 0:
            return np.inf
        return math.sqrt(numerator / denominator)

    # =========================================================================
    # TOPIC 14: GATED NOISE SOLVERS
    # =========================================================================
    @staticmethod
    def t_tgt_2way():
        """Calculate Two-way Time of Flight to Target.
        Uses vars.R_tgt (m) and vars.c (m/s).
        Returns: float: Time (s)."""
        return 2 * vars.R_tgt / vars.c

    @staticmethod
    def t_gn_start_release():
        """Calculate Gated Noise Start Release Time (relative to T=0 radar pulse).
        Uses vars.R_tgt, vars.R_gn_start_offset, vars.c, vars.tau.
        Returns: float: Time (s)."""
        # t_gn_start_release = 2 * (R_tgt - R_gn_start_offset) / c - tau / 2
        R_start = vars.R_tgt - vars.R_gn_start_offset
        return (2 * R_start / vars.c) - (vars.tau / 2)

    # =========================================================================
    # TOPIC 15: FALSE TARGET GENERATION SOLVERS
    # =========================================================================
    @staticmethod
    def f_D_tgt():
        """Calculate Target Doppler Frequency.
        Uses vars.v_tgt (m/s) and vars.wavelength (m).
        Returns: float: Doppler frequency (Hz)."""
        return -2 * vars.v_tgt / vars.wavelength

    @staticmethod
    def f_D_ft():
        """Calculate False Target Doppler Frequency.
        Uses vars.v_ft (m/s) and vars.wavelength (m).
        Returns: float: Doppler frequency (Hz)."""
        return -2 * vars.v_ft / vars.wavelength

    @staticmethod
    def Delta_t_ft():
        """Calculate Time Delay to apply for False Target Generation.
        Uses vars.R_ft (m), vars.R (m), and vars.c (m/s).
        Returns: float: Time delay (s)."""
        # Delta_t_ft = 2 * (R_ft - R) / c
        return 2 * (vars.R_ft - vars.R) / vars.c

    @staticmethod
    def Delta_f_ft():
        """Calculate Frequency Shift to apply for False Target Generation.
        Uses vars.f_D_ft (Hz) and vars.f_D_tgt (Hz).
        Returns: float: Frequency shift (Hz)."""
        # Delta_f_ft = f_D_ft - f_D_tgt
        return vars.f_D_ft - vars.f_D_tgt

    # =========================================================================
    # TOPIC 16: RADAR TRACKING / FALSE TRACKS SOLVERS
    # =========================================================================
    @staticmethod
    def P_density():
        """Calculate Power Density at Target.
        Uses vars.P_t (W), vars.G_t (dim), and vars.R (m).
        Returns: float: Power density (W/m^2)."""
        # P_density = (Pt * Gt) / (4 * pi * R^2)
        if vars.R == 0:
            raise ValueError("Range (R) cannot be zero.")
        return (vars.P_t * vars.G_t) / (4 * vars.pi * vars.R**2)

    @staticmethod
    def Pj_emulated():
        """Calculate Jammer Power required to emulate a target RCS (sigma).
        Uses vars.P_density (W/m^2), vars.sigma (m^2), and vars.Gj (dim).
        Returns: float: Jammer transmit power (W)."""
        # Pj_emulated = (P_density * sigma) / Gj
        if vars.Gj == 0:
            raise ValueError("Jammer gain (Gj) cannot be zero.")
        return (vars.P_density * vars.sigma) / vars.Gj

    # =========================================================================
    # TOPIC 17: GATE STEALING SOLVERS
    # =========================================================================

    @staticmethod
    def rho_v():
        """Calculate Velocity Resolution (Doppler bin size).
        Uses vars.wavelength (m) and vars.T_cpi (s).
        Returns: float: Velocity resolution (m/s)."""
        # rho_v = lambda / (2 * T_cpi)
        if not hasattr(vars, 'T_cpi') or not vars.T_cpi:
            raise ValueError("T_cpi (Coherent Processing Interval) is not set or zero.")
        return (vars.wavelength / (2 * vars.T_cpi))

    @staticmethod
    def Delta_r_max_gate():
        """Calculate the maximum required range offset to exit the gate.
        Uses vars.n_gate_r (cells) and vars.delta_r (m).
        Returns: float: Maximum range offset (m)."""
        # Delta_r_max = n_gate_r * delta_r (Requires delta_r to be set)
        return vars.n_gate_r * vars.delta_r

    @staticmethod
    def T_from_Delta_r():
        """Calculate the time required (T) to achieve range offset (Delta_r_max) at constant acceleration (alpha).
        Uses vars.Delta_r_max (m) and vars.alpha (m/s^2).
        Returns: float: Time duration (s)."""
        # T = sqrt((2 * Delta_r_max) / alpha)
        if vars.alpha <= 0:
            raise ValueError("Acceleration (alpha) must be positive.")
        return math.sqrt((2 * vars.Delta_r_max) / vars.alpha)

    @staticmethod
    def Delta_v_max_gate():
        """Calculate the maximum required velocity offset to exit the gate.
        Uses vars.n_gate_v (cells) and vars.rho_v (m/s).
        Returns: float: Maximum velocity offset (m/s)."""
        # Delta_v_max = n_gate_v * rho_v (Requires rho_v to be set)
        return vars.n_gate_v * vars.rho_v

    @staticmethod
    def T_from_Delta_v():
        """Calculate the time required (T) to achieve velocity offset (Delta_v_max) at constant acceleration (a_accel).
        Uses vars.Delta_v_max (m/s) and vars.a_accel (m/s^2).
        Returns: float: Time duration (s)."""
        # T = Delta_v_max / a_accel
        if vars.a_accel == 0:
            raise ValueError("Acceleration (a_accel) cannot be zero.")
        return vars.Delta_v_max / vars.a_accel

    # =========================================================================
    # TOPIC 18: CROSS-EYE SOLVERS
    # =========================================================================

    @staticmethod
    def phi_hat_cross_eye_amp():
        """Calculate the apparent cross-eye angle error (amplitude monopulse approximation).
        Uses vars.L_cross (m), vars.R (m), and vars.a_gain_ratio (J1/J2, dimensionless).
        Returns: float: Angle error in radians."""
        # phi_hat = (L/(2R)) * (1+a)/(1-a)
        if vars.R == 0:
             raise ValueError("Range (R) cannot be zero.")
        if abs(vars.a_gain_ratio - 1.0) < 1e-9: # Check for a very close to 1
            # The denominator (1-a) approaches zero, causing the angle error to approach infinity (saturating the tracker)
            return np.inf 
        return (vars.L_cross / (2 * vars.R)) * ((1 + vars.a_gain_ratio) / (1 - vars.a_gain_ratio))

    @staticmethod
    def L_cross_from_phi_hat():
        """Calculate the required cross-eye aperture separation (L) to produce a specific angle error (phi_hat_ce).
        Uses vars.phi_hat_ce (rad), vars.R (m), and vars.a_gain_ratio (J1/J2).
        Returns: float: Aperture separation (m)."""
        # Rearrange: L = 2 * R * phi_hat_ce * (1-a)/(1+a)
        if abs(vars.a_gain_ratio + 1.0) < 1e-9: # Check for a very close to -1
            return np.inf # Denominator approaches zero
        return 2 * vars.R * vars.phi_hat_ce * ((1 - vars.a_gain_ratio) / (1 + vars.a_gain_ratio))

    # =========================================================================
    # LEGACY: GATE STEALING / RANGE GATE PULL-OFF (RGPO) SOLVERS
    # =========================================================================
    
    delta_t_pull_from_range = _solver(equations.eq_delta_t_pull, equations.delta_t_pull_sym)
    delta_R_pull_from_time = _solver(equations.eq_delta_R_from_time, equations.delta_R_pull_sym)
    n_pulses_to_capture = _solver(equations.eq_n_pulses_rgpo, equations.n_pulses_capture_sym)
    gate_bias_error = _solver(equations.eq_gate_bias, equations.gate_bias_sym)
    tracking_bandwidth = _solver(equations.eq_BW_track, equations.BW_track_sym)
    
    @staticmethod
    def rgpo_delay_profile(R_initial, R_final, delta_R_per_pulse, n_pulses=None):
        """Generate a Range Gate Pull-Off delay profile.
        
        Args:
            R_initial: Initial range (m) where jammer matches true target
            R_final: Final range (m) to pull the gate to
            delta_R_per_pulse: Range increment per pulse (m/pulse)
            n_pulses: Number of pulses (optional, calculated if not provided)
            
        Returns:
            dict with keys:
                - 'pulse_number': List of pulse indices
                - 'range_m': List of false target ranges (m)
                - 'delay_us': List of time delays (μs)
                - 'n_pulses': Total number of pulses
                - 'total_time_s': Total time if PRF known
        """
        import numpy as np
        
        if n_pulses is None:
            n_pulses = int(np.ceil((R_final - R_initial) / delta_R_per_pulse)) + 1
        
        pulse_nums = np.arange(n_pulses)
        ranges = R_initial + pulse_nums * delta_R_per_pulse
        ranges = np.minimum(ranges, R_final)  # Cap at final range
        
        # Time delay is 2R/c (round-trip)
        delays_s = 2 * ranges / vars.c
        delays_us = delays_s * 1e6
        
        result = {
            'pulse_number': pulse_nums.tolist(),
            'range_m': ranges.tolist(),
            'range_km': (ranges / 1000).tolist(),
            'delay_us': delays_us.tolist(),
            'delay_s': delays_s.tolist(),
            'n_pulses': n_pulses,
            'delta_R_per_pulse': delta_R_per_pulse
        }
        
        # If PRF is set, calculate total time
        if hasattr(vars, 'f_p') and vars.f_p > 0:
            total_time = n_pulses / vars.f_p
            result['total_time_s'] = total_time
            result['PRF_hz'] = vars.f_p
        
        return result
    
    @staticmethod
    def rgpo_max_pull_rate(delta_R_gate, factor=0.1):
        """Calculate maximum safe RGPO pull rate.
        
        The pull rate must be slow enough that the gate doesn't lose lock.
        A common rule of thumb is to move no more than 10-20% of the gate
        width per pulse.
        
        Args:
            delta_R_gate: Range gate width (m)
            factor: Fraction of gate width to move per pulse (default 0.1)
            
        Returns:
            Maximum delta_R per pulse (m/pulse)
        """
        return delta_R_gate * factor
    
    @staticmethod
    def rgpo_capture_analysis(R_true, R_jammer_start, delta_R_pull, gate_width, n_pulses_max=1000):
        """Analyze when/if RGPO captures the tracking gate.
        
        Args:
            R_true: True target range (m)
            R_jammer_start: Initial jammer range (usually equals R_true) (m)
            delta_R_pull: Range pull increment per pulse (m/pulse)
            gate_width: Range gate width (m)
            n_pulses_max: Maximum pulses to simulate
            
        Returns:
            dict with analysis results
        """
        import numpy as np
        
        # Simulate gate tracking
        gate_center = R_true  # Gate initially centered on true target
        jammer_range = R_jammer_start
        
        captured = False
        capture_pulse = None
        
        for pulse in range(n_pulses_max):
            # Jammer pulls off
            jammer_range += delta_R_pull
            
            # Check if jammer is dominant in gate
            # (Simple model: whichever is closer to gate center)
            dist_to_true = abs(gate_center - R_true)
            dist_to_jammer = abs(gate_center - jammer_range)
            
            if dist_to_jammer < dist_to_true:
                # Gate starts tracking jammer
                if not captured:
                    captured = True
                    capture_pulse = pulse
                gate_center = jammer_range  # Simplified: gate follows jammer
            else:
                gate_center = R_true  # Gate follows true target
        
        result = {
            'captured': captured,
            'capture_pulse': capture_pulse,
            'final_gate_position': gate_center,
            'final_jammer_range': jammer_range,
            'gate_error': gate_center - R_true
        }
        
        if captured:
            result['capture_time_pulses'] = capture_pulse
            if hasattr(vars, 'f_p') and vars.f_p > 0:
                result['capture_time_s'] = capture_pulse / vars.f_p
        
        return result

