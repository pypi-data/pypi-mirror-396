2025.10.27

Main updates include support for theta_B and calculations for spheres, RCS and radius from RCS.

**New:** Plotting capabilities for visualizing radar signals including pulsed radar, CW Doppler, CWFM, pulse compression, range profiles, and Doppler spectra.

## Radar Range Equation

A compact toolbox for deriving and evaluating radar range equations. It exposes a small programmatic API for setting physical variables, performing common radar-related calculations, converting units, and visualizing radar signals.

## Install

pip install radar-range-equation
```

## Quick start

```python
import radar_range_equation as RRE

# Set common variables
RRE.vars.c = 3.0e8        # speed of light (m/s)
RRE.vars.f = 430e6        # frequency (Hz)
RRE.vars.eta = 0.6        # antenna efficiency (unitless)

# Because `lambda` is a reserved word in Python, access it with getattr/setattr
setattr(RRE.vars, 'lambda', RRE.vars.c / RRE.vars.f)
print('wavelength (m):', getattr(RRE.vars, 'lambda'))

# Compute effective aperture (circular antenna example)
RRE.vars.D = RRE.convert_ft_to_m(60)  # antenna diameter in meters
RRE.vars.A_e = RRE.solve.A_e_circ()
print('A_e (m^2):', RRE.vars.A_e)

# Visualize a pulsed radar signal
RRE.plot.pulsed_radar_signal(
    amplitude=20,
    frequency=0.5e6,  # 0.5 MHz
    pulse_width=15e-6,  # 15 microseconds
    pri=50e-6,  # 50 microseconds
    num_pulses=3
)
```

## Public API (short)

- `vars` — namespace-like container of variables (speed of light `c`, frequency `f`, wavelength `lambda`, gains, power, sigma, etc.). Use `getattr`/`setattr` for `lambda`.
- `solve` — helper functions for computing aperture, gain, R_max, P_t and other routine expressions (e.g., `solve.wavelength()`, `solve.G_t()`).
- `equations` — symbolic SymPy expressions representing the radar equations used by `solve`.
- `plot` — plotting utilities for visualizing radar signals (pulsed radar, CW Doppler, CWFM, pulse compression, range profiles, Doppler spectra).
- `redefine_variable(name, value)` — convenience to set attributes on the `vars` namespace.
- `convert` — unit conversion helpers (e.g., `convert.ft_to_m()`, `convert.lin_to_db()`, `convert.hz_to()`, etc.).

## Plotting Capabilities

The package now includes comprehensive plotting functions for visualizing radar signals:

### Pulsed Radar Signal
```python
import radar_range_equation as RRE

# Visualize a pulsed radar transmit signal
t, signal, fig = RRE.plot.pulsed_radar_signal(
    amplitude=20,           # Peak amplitude
    frequency=0.5e6,        # 0.5 MHz carrier
    pulse_width=15e-6,      # 15 µs pulse width
    pri=50e-6,              # 50 µs pulse repetition interval
    num_pulses=3,           # 3 pulses
    time_span=150e-6        # 150 µs total time
)
```

### Other Plotting Functions
- `plot.cw_doppler_signal()` — CW radar with Doppler shift
- `plot.cwfm_signal()` — Continuous Wave Frequency Modulated radar
- `plot.pulse_compression_signal()` — Chirp pulse and compressed output
- `plot.range_profile()` — Target detections at various ranges
- `plot.doppler_spectrum()` — Velocity distribution of targets

See `python/example_plotting.py` for complete examples of all plotting capabilities.

## Testing

After installing the package you can run the included smoke test:

```powershell
python python/test_package.py
```

The test script checks basic import and example calculations.

To test the plotting functionality:

```powershell
python python/test_plotting.py
```

To see examples of all plotting capabilities:

```powershell
python python/example_plotting.py
```

## Notes and gotchas

- `lambda` is a reserved Python keyword; use `getattr(vars, 'lambda')` and `setattr(vars, 'lambda', value)` when reading/writing the wavelength variable.
- The package mixes symbolic (SymPy) and numeric (NumPy/Scipy) approaches. The `equations` module provides symbolic forms while `solve` returns numeric results based on values in `vars`.

## Contributing

Small, focused improvements (tests, docs, type hints) are welcome. The repository uses Hatch in CI for packaging; see `.github/workflows/python-package.yml` for the build/test flow.

## License

See the repository `LICENSE` file for licensing details.

# Radar Range Equation
A basic toolbox for solving radar range equations

## Testing

After building and installing the package, you can run the test script to verify functionality:

```bash
python python/test_package.py
```

This test script verifies that:
- The package can be imported successfully
- Variables can be set dynamically (e.g., `c`, `f`, `lambda`)
- The `redefine_variable` function works correctly
- Calculations work as expected (e.g., `lambda = c/f`)

### Example Usage

```python
import radar_range_equation as RRE

# Set the speed of light (m/s)
RRE.vars.c = 3.00 * 10**8

# Set the frequency (Hz)
RRE.vars.f = 10

# Calculate and set wavelength (m)
# Note: 'lambda' is a reserved keyword in Python, so use setattr/getattr
setattr(RRE.vars, 'lambda', RRE.vars.c / RRE.vars.f)

# Print the wavelength
print(getattr(RRE.vars, 'lambda'))  # Output: 30000000.0
```
