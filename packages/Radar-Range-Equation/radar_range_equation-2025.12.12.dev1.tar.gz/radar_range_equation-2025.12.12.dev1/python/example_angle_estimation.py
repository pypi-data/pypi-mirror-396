#!/usr/bin/env python3
"""
Example demonstrating angle estimation calculations from the Radar Range Equation package.

This example demonstrates the three main angle measurement techniques:
1. Amplitude Comparison
2. Phase Comparison
3. Time Comparison
"""

import radar_range_equation as RRE
import math

print("=" * 70)
print("Radar Angle Estimation Calculations")
print("=" * 70)

# --- Amplitude Comparison (Page 1 & 2 from problem statement) ---
print("\n--- AMPLITUDE COMPARISON ---\n")

# Calculate Theta from 3-dB beamwidth
RRE.vars.theta_B = 10.0  # degrees
Theta = RRE.solve.calculate_Theta()
print(f"3-dB beamwidth (theta_B): {RRE.vars.theta_B} degrees")
print(f"Calculated Theta parameter: {Theta:.6f}")

# Gaussian beam approximation
RRE.vars.phi = 5.0  # degrees
RRE.vars.phi_s = 5.0  # degrees (center angle)
RRE.vars.Theta = Theta
v = RRE.solve.v_phi()
print(f"\nGaussian beam approximation v_phi(): {v:.6f}")

# Full beam approximation
RRE.vars.phi = 5.0
RRE.vars.phi_s = 5.0
RRE.vars.theta_B = 10.0
v_full = RRE.solve.v_phi_full()
print(f"Full beam approximation v_phi_full(): {v_full:.6f}")

# Linear processor angle estimate
RRE.vars.Delta = 1.0
RRE.vars.Sigma = 1.0
RRE.vars.theta_B = 10.0
RRE.vars.phi_s = 5.0
phi_hat = RRE.solve.estimate_phi_hat()
print(f"\nLinear processor angle estimate:")
print(f"  Delta: {RRE.vars.Delta}, Sigma: {RRE.vars.Sigma}")
print(f"  phi_hat: {phi_hat:.4f} degrees")

# Angle standard deviation (Amplitude)
S_N_dB = 10  # dB
RRE.vars.x = S_N_dB
S_N_linear = RRE.solve.db_to_linear()
print(f"\nSignal-to-Noise Ratio: {S_N_dB} dB (linear: {S_N_linear:.2f})")

RRE.vars.theta_B = 10.0
RRE.vars.S_N = S_N_linear
RRE.vars.phi_s = 5.0
sigma_phi_amp = RRE.solve.sigma_phi_amplitude()
print(f"Angle standard deviation (amplitude comparison): {sigma_phi_amp:.4f} degrees")

# Calculate phi_s needed for a target sigma_phi
target_sigma_phi = 0.5  # degrees
phi_s_needed = (RRE.vars.theta_B**2 * math.sqrt(1 / S_N_linear)) / (8 * math.sqrt(2) * target_sigma_phi * math.log(2))
print(f"\nTo achieve sigma_phi of {target_sigma_phi} degrees:")
print(f"  Required phi_s: {phi_s_needed:.4f} degrees")

# --- Phase Comparison (Page 3 from problem statement) ---
print("\n--- PHASE COMPARISON ---\n")

# Calculate wavelength
c = 3e8  # Speed of light, m/s
f_o = 10e9  # Frequency, 10 GHz
lambda_ = c / f_o
print(f"Frequency: {f_o/1e9:.1f} GHz")
print(f"Wavelength (lambda): {lambda_:.3f} m")

# Convert SNR from dB to linear
S_N_dB_2 = 8  # dB
RRE.vars.x = S_N_dB_2
S_N_linear_2 = RRE.solve.db_to_linear()
print(f"\nSignal-to-Noise Ratio: {S_N_dB_2} dB (linear: {S_N_linear_2:.2f})")

# Angle standard deviation (Phase)
RRE.vars.wavelength = lambda_
RRE.vars.d = 2.0  # Antenna separation, meters
RRE.vars.S_N = S_N_linear_2
sigma_phi_phase_rad = RRE.solve.sigma_phi_phase()
sigma_phi_phase_deg = sigma_phi_phase_rad * (180 / math.pi)
print(f"\nAntenna separation: {RRE.vars.d} m")
print(f"Angle standard deviation (phase comparison):")
print(f"  {sigma_phi_phase_rad:.6f} radians")
print(f"  {sigma_phi_phase_deg:.4f} degrees")

# Calculate d needed for a target sigma_phi
target_sigma_phi_deg = 0.5  # degrees
target_sigma_phi_rad = target_sigma_phi_deg * (math.pi / 180)
d_needed = (lambda_ / (2 * math.pi * target_sigma_phi_rad)) * math.sqrt(1 / S_N_linear_2)
print(f"\nTo achieve sigma_phi of {target_sigma_phi_deg} degrees:")
print(f"  Required antenna separation (d): {d_needed:.4f} m")

# --- Time Comparison (Page 3 from problem statement) ---
print("\n--- TIME COMPARISON ---\n")

# Angle standard deviation (Time)
RRE.vars.c = c
RRE.vars.d = 2.0
RRE.vars.B = 200e6  # Bandwidth, 200 MHz
sigma_phi_time_rad = RRE.solve.sigma_phi_time()
sigma_phi_time_deg = sigma_phi_time_rad * (180 / math.pi)
print(f"Bandwidth: {RRE.vars.B/1e6:.0f} MHz")
print(f"Antenna separation: {RRE.vars.d} m")
print(f"Angle standard deviation (time comparison):")
print(f"  {sigma_phi_time_rad:.4f} radians")
print(f"  {sigma_phi_time_deg:.2f} degrees")

# Calculate B needed for a target sigma_phi
target_sigma_phi_deg_2 = 0.5  # degrees
target_sigma_phi_rad_2 = target_sigma_phi_deg_2 * (math.pi / 180)
B_needed = c / (RRE.vars.d * target_sigma_phi_rad_2)
B_needed_GHz = B_needed / 1e9
print(f"\nTo achieve sigma_phi of {target_sigma_phi_deg_2} degrees:")
print(f"  Required bandwidth (B): {B_needed:.2e} Hz")
print(f"  = {B_needed_GHz:.2f} GHz")

print("\n" + "=" * 70)
print("All calculations completed successfully!")
print("=" * 70)
