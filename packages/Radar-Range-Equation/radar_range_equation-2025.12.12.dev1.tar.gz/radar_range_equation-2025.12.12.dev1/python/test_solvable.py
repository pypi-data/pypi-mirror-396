#!/usr/bin/env python3
"""Test suite for the Solvable class and interactive solver system.

This test validates that the refactored solver system provides:
1. Status reporting via status() method and __repr__()
2. Callable solving via solve() and __call__()
3. Introspective variable checking
4. Error handling with automatic status display
"""

import sys
from math import isclose


def test_solvable():
    """Run comprehensive tests on the Solvable class functionality.
    
    Returns 0 on success, 1 on failure.
    """
    try:
        import radar_range_equation as RRE
        
        print("="*70)
        print("Testing Solvable Class Functionality")
        print("="*70)
        
        # Test 1: Verify Solvable class is exported
        assert hasattr(RRE, 'Solvable'), "Solvable class not exported"
        print("✓ Solvable class is exported")
        
        # Test 2: Verify key solvers are Solvable instances
        assert isinstance(RRE.solve.wavelength, RRE.Solvable), "wavelength is not a Solvable"
        assert isinstance(RRE.solve.G_t, RRE.Solvable), "G_t is not a Solvable"
        assert isinstance(RRE.solve.P_t, RRE.Solvable), "P_t is not a Solvable"
        assert isinstance(RRE.solve.R_max, RRE.Solvable), "R_max is not a Solvable"
        print("✓ Key solvers are Solvable instances")
        
        # Test 3: Verify Solvable has required methods
        solvable = RRE.solve.wavelength
        assert hasattr(solvable, 'status'), "Solvable missing status() method"
        assert hasattr(solvable, 'solve'), "Solvable missing solve() method"
        assert callable(solvable), "Solvable is not callable (__call__ missing)"
        print("✓ Solvable has all required methods")
        
        # Test 4: Test wavelength calculation
        RRE.vars.c = 3e8
        RRE.vars.f = 10e9
        wavelength = RRE.solve.wavelength()
        expected = 0.03
        assert isclose(wavelength, expected, rel_tol=1e-9), \
            f"wavelength {wavelength} != expected {expected}"
        print(f"✓ wavelength calculation: {wavelength} m")
        
        # Test 5: Test G_t calculation
        RRE.vars.A_e = 1.0
        RRE.vars.wavelength = 0.03
        gain = RRE.solve.G_t()
        # Expected: 4 * pi * 1.0 / (0.03^2) ≈ 13962.63
        assert gain > 13000 and gain < 14000, \
            f"gain {gain} out of expected range"
        print(f"✓ G_t calculation: {gain:.2f}")
        
        # Test 6: Test R_max calculation
        RRE.vars.P_t = 1000.0
        RRE.vars.G_t = 1000.0
        RRE.vars.sigma = 1.0
        RRE.vars.S_min = 1e-13
        RRE.vars.pi = 3.14159265359
        r_max = RRE.solve.R_max()
        # Should be in the km range
        assert r_max > 5000 and r_max < 15000, \
            f"R_max {r_max} out of expected range"
        print(f"✓ R_max calculation: {r_max:.2f} m")
        
        # Test 7: Test error handling (missing variables)
        # Reset a variable to trigger error
        import sympy
        old_sigma = RRE.vars.sigma
        RRE.vars.sigma = sympy.Symbol('sigma')  # Reset to symbolic
        result = RRE.solve.R_max.solve()
        assert result is None, "Should return None when variables missing"
        RRE.vars.sigma = old_sigma  # Restore
        print("✓ Error handling works (returns None for missing vars)")
        
        # Test 8: Test Doppler solvers
        RRE.vars.wavelength = 0.03
        # For v=-100 m/s, λ=0.03m: f_doppler = -2*v/λ = -2*(-100)/0.03 = 6666.67 Hz
        RRE.vars.f_doppler = 6666.67
        velocity = RRE.solve.v_from_doppler()
        expected_v = -100.0
        assert isclose(velocity, expected_v, rel_tol=1e-2), \
            f"velocity {velocity} != expected {expected_v}"
        print(f"✓ Doppler velocity calculation: {velocity:.2f} m/s")
        
        # Test 9: Test CWFM solvers
        RRE.vars.c = 3e8
        RRE.vars.f_r = 80e3
        RRE.vars.f_m = 100
        RRE.vars.deltaf = 30e6
        # CWFM equation: R = c*f_r/(4*f_m*Δf) = 3e8*80e3/(4*100*30e6) = 2000 m
        range_val = RRE.solve.R_cwfm()
        expected_r = 2000.0
        assert isclose(range_val, expected_r, rel_tol=1e-9), \
            f"range {range_val} != expected {expected_r}"
        print(f"✓ CWFM range calculation: {range_val:.2f} m")
        
        # Test 10: Test that status() method works (doesn't crash)
        # We can't easily test the output, but we can ensure it runs
        try:
            RRE.solve.wavelength.status()
            print("✓ status() method executes without error")
        except Exception as e:
            print(f"✗ status() method failed: {e}")
            return 1
        
        # Test 11: Test that __repr__ works
        try:
            repr_str = repr(RRE.solve.wavelength)
            assert isinstance(repr_str, str), "__repr__ should return string"
            print("✓ __repr__() method works")
        except Exception as e:
            print(f"✗ __repr__() method failed: {e}")
            return 1
        
        # Test 12: Test backward compatibility with legacy functions
        # The old function-based solvers should still work
        RRE.vars.c = 3e8
        RRE.vars.f = 10e9
        # Call as function (uses __call__)
        wl_call = RRE.solve.wavelength()
        assert isclose(wl_call, 0.03, rel_tol=1e-9), \
            "Function call syntax broken"
        print("✓ Backward compatibility maintained (callable syntax)")
        
        print("\n" + "="*70)
        print("✓ All Solvable tests passed!")
        print("="*70)
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
    sys.exit(test_solvable())
