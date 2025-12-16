#!/usr/bin/env python3
"""Lightweight smoke test for the radar_range_equation package.

This script performs a few small, well-defined checks against the
public API exported by `radar_range_equation` to ensure the package
imports and basic functions behave as expected.
"""

import sys
from math import isclose


def test_package():
    """Run a few assertions against the package API.

    Returns 0 on success, 1 on failure.
    """
    try:
        import radar_range_equation as RRE

        print("✓ Imported radar_range_equation")

        # Basic exported symbols
        for name in ("vars", "equations", "solve", "convert", "redefine_variable"):
            assert hasattr(RRE, name), f"Missing exported symbol: {name}"
        print("✓ Public symbols present")

        # Test a simple conversion helper
        meters = RRE.convert.ft_to_m(1)
        assert isclose(meters, 0.3048, rel_tol=1e-12), f"convert.ft_to_m(1) -> {meters}"
        print(f"✓ convert.ft_to_m(1) = {meters}")

        # Test redefining a variable in the vars namespace
        # Use a non-reserved name that the package exposes: 'f' and 'wavelength'
        RRE.redefine_variable('f', 10.0)
        assert hasattr(RRE.vars, 'f'), "vars.f not present after redefine"
        assert float(RRE.vars.f) == 10.0, f"Expected vars.f == 10.0, got {RRE.vars.f}"
        print(f"✓ vars.f set to {RRE.vars.f}")

        # Compute wavelength from c and f using the provided solver
        # Set c and f to known numeric values, then call solve.wavelength()
        RRE.redefine_variable('c', 3.0e8)
        RRE.redefine_variable('f', 2.0e8)
        wl = RRE.solve.wavelength()
        expected = 3.0e8 / 2.0e8
        assert isclose(wl, expected, rel_tol=1e-12), f"wavelength {wl} != expected {expected}"
        print(f"✓ solve.wavelength() = {wl}")

        print("\n✓ All smoke tests passed")
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
    sys.exit(test_package())
