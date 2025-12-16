#!/usr/bin/env python3
"""Test script for angle estimation functions.

This script validates the new angle estimation functions added to the
radar_range_equation package, including amplitude, phase, and time comparison methods.
"""

import sys
import math
from math import isclose


def test_angle_estimation():
    """Run tests for the angle estimation functions.

    Returns 0 on success, 1 on failure.
    """
    try:
        import radar_range_equation as RRE

        print("✓ Imported radar_range_equation")

        # Test that new functions are in the solve class
        for name in ("v_phi", "calculate_Theta", "v_phi_full", "estimate_phi_hat",
                     "sigma_phi_amplitude", "sigma_phi_phase", "sigma_phi_time", "db_to_linear"):
            assert hasattr(RRE.solve, name), f"Missing function in solve class: {name}"
        print("✓ All new functions are in solve class")

        # Test v_phi (Gaussian beam approximation)
        RRE.vars.phi = 5.0
        RRE.vars.phi_s = 5.0
        RRE.vars.Theta = 0.0277
        result = RRE.solve.v_phi()
        assert isclose(result, 1.0, rel_tol=1e-9), f"v_phi at center should be ~1.0, got {result}"
        print(f"✓ solve.v_phi() with phi={RRE.vars.phi}, phi_s={RRE.vars.phi_s}, Theta={RRE.vars.Theta} = {result}")

        # Test calculate_Theta
        RRE.vars.theta_B = 10.0
        Theta = RRE.solve.calculate_Theta()
        expected_Theta = (4 * math.log(2)) / (RRE.vars.theta_B**2)
        assert isclose(Theta, expected_Theta, rel_tol=1e-9), f"calculate_Theta() = {Theta}, expected {expected_Theta}"
        print(f"✓ solve.calculate_Theta() with theta_B={RRE.vars.theta_B} = {Theta}")

        # Test v_phi_full
        RRE.vars.phi = 5.0
        RRE.vars.phi_s = 5.0
        RRE.vars.theta_B = 10.0
        result = RRE.solve.v_phi_full()
        assert isclose(result, 1.0, rel_tol=1e-9), f"v_phi_full at center should be ~1.0, got {result}"
        print(f"✓ solve.v_phi_full() with phi={RRE.vars.phi}, phi_s={RRE.vars.phi_s}, theta_B={RRE.vars.theta_B} = {result}")

        # Test estimate_phi_hat
        RRE.vars.Delta = 1.0
        RRE.vars.Sigma = 1.0
        RRE.vars.theta_B = 10.0
        RRE.vars.phi_s = 5.0
        phi_hat = RRE.solve.estimate_phi_hat()
        expected = (1.0 / 1.0) * (10.0**2 / (8 * math.log(2) * 5.0))
        assert isclose(phi_hat, expected, rel_tol=1e-9), f"estimate_phi_hat = {phi_hat}, expected {expected}"
        print(f"✓ solve.estimate_phi_hat() = {phi_hat}")

        # Test db_to_linear
        RRE.vars.x = 10
        S_N_linear = RRE.solve.db_to_linear()
        expected_linear = 10.0
        assert isclose(S_N_linear, expected_linear, rel_tol=1e-9), f"db_to_linear() = {S_N_linear}, expected {expected_linear}"
        print(f"✓ solve.db_to_linear() with x={RRE.vars.x} = {S_N_linear}")

        # Test sigma_phi_amplitude (from problem statement page 2)
        RRE.vars.theta_B = 10.0
        RRE.vars.phi_s = 5.0
        RRE.vars.S_N = 10.0
        sigma_phi_amp = RRE.solve.sigma_phi_amplitude()
        # Expected: approx 0.8 degrees according to problem statement
        expected_amp = (RRE.vars.theta_B**2 * math.sqrt(1 / RRE.vars.S_N)) / (8 * math.sqrt(2) * RRE.vars.phi_s * math.log(2))
        assert isclose(sigma_phi_amp, expected_amp, rel_tol=1e-9), f"sigma_phi_amplitude = {sigma_phi_amp}, expected {expected_amp}"
        print(f"✓ solve.sigma_phi_amplitude() = {sigma_phi_amp:.4f} degrees")

        # Test calculation for target sigma_phi (from problem statement)
        target_sigma_phi = 0.5
        phi_s_calc = (RRE.vars.theta_B**2 * math.sqrt(1 / RRE.vars.S_N)) / (8 * math.sqrt(2) * target_sigma_phi * math.log(2))
        print(f"✓ Calculated phi_s for target sigma_phi of {target_sigma_phi} = {phi_s_calc:.4f} degrees")

        # Test sigma_phi_phase (from problem statement page 3)
        c = 3e8
        f_o = 10e9
        lambda_ = c / f_o  # 0.03 m
        RRE.vars.wavelength = lambda_
        RRE.vars.x = 8
        S_N_linear_2 = RRE.solve.db_to_linear()  # approx 6.3
        RRE.vars.S_N = S_N_linear_2
        RRE.vars.d = 2.0  # 2 meters
        sigma_phi_phase_val = RRE.solve.sigma_phi_phase()
        expected_phase = (lambda_ / (2 * math.pi * RRE.vars.d)) * math.sqrt(1 / S_N_linear_2)
        assert isclose(sigma_phi_phase_val, expected_phase, rel_tol=1e-9), f"sigma_phi_phase = {sigma_phi_phase_val}, expected {expected_phase}"
        print(f"✓ solve.sigma_phi_phase() = {sigma_phi_phase_val:.6f} radians")
        sigma_phi_phase_deg = sigma_phi_phase_val * (180 / math.pi)
        print(f"  = {sigma_phi_phase_deg:.4f} degrees")

        # Test calculation of d for target sigma_phi (from problem statement)
        target_sigma_phi_deg_2 = 0.5
        target_sigma_phi_rad_2 = target_sigma_phi_deg_2 * (math.pi / 180)
        d_calc_2 = (lambda_ / (2 * math.pi * target_sigma_phi_rad_2)) * math.sqrt(1 / S_N_linear_2)
        print(f"✓ Calculated d for target sigma_phi of {target_sigma_phi_deg_2} deg = {d_calc_2:.4f} meters")

        # Test sigma_phi_time (from problem statement page 3)
        RRE.vars.c = c
        RRE.vars.d = 2.0
        RRE.vars.B = 200e6  # 200 MHz
        sigma_phi_time_val = RRE.solve.sigma_phi_time()
        expected_time = c / (RRE.vars.d * RRE.vars.B)
        assert isclose(sigma_phi_time_val, expected_time, rel_tol=1e-9), f"sigma_phi_time = {sigma_phi_time_val}, expected {expected_time}"
        print(f"✓ solve.sigma_phi_time() = {sigma_phi_time_val:.4f} radians")
        sigma_phi_time_deg = sigma_phi_time_val * (180 / math.pi)
        print(f"  = {sigma_phi_time_deg:.2f} degrees")

        # Test calculation of B for target sigma_phi (from problem statement)
        target_sigma_phi_deg_3 = 0.5
        target_sigma_phi_rad_3 = target_sigma_phi_deg_3 * (math.pi / 180)
        B_calc_2 = c / (RRE.vars.d * target_sigma_phi_rad_3)
        print(f"✓ Calculated B for target sigma_phi of {target_sigma_phi_deg_3} deg = {B_calc_2:.2e} Hz")
        B_calc_2_GHz = B_calc_2 / 1e9
        print(f"  = {B_calc_2_GHz:.2f} GHz")

        print("\n✓ All angle estimation tests passed")
        return 0

    except ImportError as e:
        print(f"✗ ImportError: {e}")
        return 1
    except AssertionError as e:
        print(f"✗ Assertion failed: {e}")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(test_angle_estimation())
