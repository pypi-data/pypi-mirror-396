#!/usr/bin/env python3
"""Comprehensive procedural test suite for Radar Range Equation package.

This test file thoroughly tests the codebase with procedural, randomized tests
to validate functionality across all modules, ensure robustness, and verify
the interactive solver system works correctly.

Run with: python3 test.py
"""

import sys
import random
import math
from typing import List, Tuple, Dict, Any

# Seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)


def test_imports():
    """Test that all modules can be imported successfully."""
    print("\n" + "="*70)
    print("TEST 1: Module Imports")
    print("="*70)
    
    try:
        import radar_range_equation as RRE
        print("✓ radar_range_equation imported")
        
        # Test all expected modules
        modules = ['vars', 'equations', 'solve', 'convert', 'analysis', 
                   'Solvable', 'constants']
        for mod in modules:
            assert hasattr(RRE, mod), f"Missing module: {mod}"
            print(f"✓ RRE.{mod} accessible")
        
        # Test optional exports
        if hasattr(RRE, 'v'):
            print("✓ RRE.v accessible (optional)")
        
        return RRE, True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return None, False


def test_constants(RRE):
    """Test physical constants module."""
    print("\n" + "="*70)
    print("TEST 2: Physical Constants")
    print("="*70)
    
    try:
        # Test constants exist and have reasonable values
        tests = [
            ('c', 2.9e8, 3.1e8, "Speed of light"),
            ('k', 1e-23, 2e-23, "Boltzmann constant"),
            ('pi', 3.14, 3.15, "Pi constant"),
            ('g', 9.5, 10.0, "Gravitational acceleration"),
        ]
        
        for const, min_val, max_val, desc in tests:
            value = getattr(RRE.constants, const)
            assert min_val <= value <= max_val, f"{const} out of range"
            print(f"✓ {desc} ({const}): {value}")
        
        # Test constants accessible through vars
        assert RRE.vars.c == RRE.constants.c, "vars.c != constants.c"
        assert RRE.vars.pi == RRE.constants.pi, "vars.pi != constants.pi"
        print("✓ Constants accessible through vars module")
        
        return True
    except Exception as e:
        print(f"✗ Constants test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_variables(RRE):
    """Test variable definitions and assignment."""
    print("\n" + "="*70)
    print("TEST 3: Variable Definitions and Assignment")
    print("="*70)
    
    try:
        # Test symbolic variable existence
        symbolic_vars = ['f', 'wavelength', 'R', 'P_t', 'G_t', 'sigma', 
                        'A_e', 'v', 'tau', 'phi']
        
        for var in symbolic_vars:
            assert hasattr(RRE.vars, var), f"Missing variable: {var}"
        print(f"✓ All {len(symbolic_vars)} symbolic variables defined")
        
        # Test variable assignment with random values
        test_assignments = [
            ('f', random.uniform(1e9, 100e9)),
            ('P_t', random.uniform(100, 10000)),
            ('sigma', random.uniform(0.1, 100)),
        ]
        
        for var, value in test_assignments:
            setattr(RRE.vars, var, value)
            retrieved = getattr(RRE.vars, var)
            assert retrieved == value, f"Assignment failed for {var}"
            print(f"✓ Variable assignment: {var} = {value:.2e}")
        
        return True
    except Exception as e:
        print(f"✗ Variables test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_equations(RRE):
    """Test symbolic equations module."""
    print("\n" + "="*70)
    print("TEST 4: Symbolic Equations")
    print("="*70)
    
    try:
        # Test equation existence
        equations_list = ['wavelength', 'G_t', 'R_max', 'P_t', 
                         'eq_f_doppler', 'eq_v_from_doppler']
        
        for eq_name in equations_list:
            assert hasattr(RRE.equations, eq_name), f"Missing equation: {eq_name}"
            eq = getattr(RRE.equations, eq_name)
            print(f"✓ Equation defined: {eq_name}")
        
        # Test equation structure (should have lhs and rhs)
        import sympy
        test_eq = RRE.equations.wavelength
        assert isinstance(test_eq, sympy.Eq), "Equation not a SymPy Eq"
        assert hasattr(test_eq, 'lhs'), "Equation missing lhs"
        assert hasattr(test_eq, 'rhs'), "Equation missing rhs"
        print(f"✓ Equation structure valid: {test_eq}")
        
        return True
    except Exception as e:
        print(f"✗ Equations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_solvable_class(RRE):
    """Test Solvable class functionality."""
    print("\n" + "="*70)
    print("TEST 5: Solvable Class")
    print("="*70)
    
    try:
        # Test Solvable instances exist
        solvable_params = ['wavelength', 'G_t', 'P_t', 'R_max', 
                          'f_doppler', 'v_from_doppler']
        
        for param in solvable_params:
            solver = getattr(RRE.solve, param)
            assert isinstance(solver, RRE.Solvable), f"{param} not a Solvable"
            print(f"✓ {param} is Solvable instance")
        
        # Test Solvable methods
        test_solver = RRE.solve.wavelength
        assert hasattr(test_solver, 'status'), "Missing status() method"
        assert hasattr(test_solver, 'solve'), "Missing solve() method"
        assert callable(test_solver), "Solvable not callable"
        print("✓ Solvable has required methods (status, solve, __call__)")
        
        # Test __repr__ (shouldn't crash)
        repr_result = repr(test_solver)
        assert isinstance(repr_result, str), "__repr__ didn't return string"
        print("✓ __repr__ method works")
        
        return True
    except Exception as e:
        print(f"✗ Solvable class test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_calculations(RRE):
    """Test basic radar calculations with known values."""
    print("\n" + "="*70)
    print("TEST 6: Basic Calculations")
    print("="*70)
    
    try:
        # Test 1: Wavelength calculation
        RRE.vars.c = 3e8
        RRE.vars.f = 10e9
        wavelength = RRE.solve.wavelength()
        expected = 0.03
        assert abs(wavelength - expected) < 1e-9, f"Wavelength calculation wrong: {wavelength}"
        print(f"✓ Wavelength: {wavelength} m (expected ~{expected} m)")
        
        # Test 2: Antenna gain calculation
        RRE.vars.A_e = 1.0
        RRE.vars.wavelength = 0.03
        gain = RRE.solve.G_t()
        assert gain > 10000 and gain < 15000, f"Gain out of range: {gain}"
        print(f"✓ Antenna gain: {gain:.2f}")
        
        # Test 3: Maximum range calculation
        RRE.vars.P_t = 1000.0
        RRE.vars.G_t = 1000.0
        RRE.vars.sigma = 1.0
        RRE.vars.S_min = 1e-13
        RRE.vars.pi = 3.14159265359
        r_max = RRE.solve.R_max()
        assert r_max > 5000 and r_max < 15000, f"R_max out of range: {r_max}"
        print(f"✓ Maximum range: {r_max:.2f} m")
        
        return True
    except Exception as e:
        print(f"✗ Basic calculations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auto_variable_definition(RRE):
    """Test automatic variable definition feature."""
    print("\n" + "="*70)
    print("TEST 7: Auto-Variable Definition")
    print("="*70)
    
    try:
        import sympy
        
        # Reset wavelength to symbolic
        RRE.vars.wavelength = sympy.Symbol('lambda')
        print(f"Before solve: wavelength = {RRE.vars.wavelength} (symbolic)")
        
        # Set required vars and solve
        RRE.vars.c = 3e8
        RRE.vars.f = 15e9
        result = RRE.solve.wavelength()
        
        # Check auto-definition
        assert isinstance(RRE.vars.wavelength, float), "wavelength not auto-defined as float"
        assert abs(RRE.vars.wavelength - result) < 1e-15, "Auto-defined value doesn't match result"
        print(f"After solve: wavelength = {RRE.vars.wavelength} (numeric)")
        print("✓ Auto-variable definition works")
        
        # Test chaining
        RRE.vars.A_e = 1.5
        gain = RRE.solve.G_t()  # Should use auto-defined wavelength
        assert isinstance(RRE.vars.G_t, float), "G_t not auto-defined"
        print(f"✓ Calculation chaining: G_t = {RRE.vars.G_t:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Auto-variable definition test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversions(RRE):
    """Test unit conversion utilities."""
    print("\n" + "="*70)
    print("TEST 8: Unit Conversions")
    print("="*70)
    
    try:
        # Test angle conversions
        rad_val = RRE.constants.pi / 2
        deg_val = RRE.convert.rad_to_deg(rad_val)
        assert abs(deg_val - 90) < 1e-10, f"rad_to_deg failed: {deg_val}"
        print(f"✓ rad_to_deg: {rad_val} rad = {deg_val} deg")
        
        back_to_rad = RRE.convert.deg_to_rad(deg_val)
        assert abs(back_to_rad - rad_val) < 1e-10, "deg_to_rad round-trip failed"
        print(f"✓ deg_to_rad: {deg_val} deg = {back_to_rad} rad")
        
        # Test dB conversions
        linear = 1000
        db = RRE.convert.lin_to_db(linear)
        expected_db = 30
        assert abs(db - expected_db) < 1e-10, f"lin_to_db failed: {db}"
        print(f"✓ lin_to_db: {linear} = {db} dB")
        
        back_to_lin = RRE.convert.db_to_lin(db)
        assert abs(back_to_lin - linear) < 1e-10, "db_to_lin round-trip failed"
        print(f"✓ db_to_lin: {db} dB = {back_to_lin}")
        
        # Test distance conversions
        meters = 1.0
        feet = RRE.convert.ft_to_m(1)
        assert abs(feet - 0.3048) < 1e-10, f"ft_to_m failed: {feet}"
        print(f"✓ ft_to_m: 1 ft = {feet} m")
        
        return True
    except Exception as e:
        print(f"✗ Conversions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_randomized_calculations(RRE, num_tests=10):
    """Test calculations with random valid inputs."""
    print("\n" + "="*70)
    print(f"TEST 9: Randomized Calculations ({num_tests} iterations)")
    print("="*70)
    
    try:
        passed = 0
        for i in range(num_tests):
            # Generate random but valid values
            c = random.uniform(2.99e8, 3.01e8)
            f = random.uniform(1e9, 100e9)
            
            RRE.vars.c = c
            RRE.vars.f = f
            
            wavelength = RRE.solve.wavelength()
            expected = c / f
            
            # Check result is close to expected
            relative_error = abs(wavelength - expected) / expected
            if relative_error < 1e-6:
                passed += 1
            else:
                print(f"  Test {i+1}: FAILED - Error {relative_error:.2e}")
        
        print(f"✓ Passed {passed}/{num_tests} randomized tests")
        assert passed == num_tests, f"Some randomized tests failed: {passed}/{num_tests}"
        
        return True
    except Exception as e:
        print(f"✗ Randomized calculations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_doppler_calculations(RRE):
    """Test Doppler radar calculations."""
    print("\n" + "="*70)
    print("TEST 10: Doppler CW Radar")
    print("="*70)
    
    try:
        # Test Doppler frequency
        RRE.vars.v = -100  # Closing velocity
        RRE.vars.wavelength = 0.03
        f_d = RRE.solve.f_doppler()
        expected = 6666.67
        assert abs(f_d - expected) < 1, f"Doppler frequency wrong: {f_d}"
        print(f"✓ Doppler frequency: {f_d:.2f} Hz")
        
        # Test velocity from Doppler
        RRE.vars.f_doppler = 6666.67
        velocity = RRE.solve.v_from_doppler()
        assert abs(velocity - (-100)) < 1, f"Velocity calculation wrong: {velocity}"
        print(f"✓ Velocity from Doppler: {velocity:.2f} m/s")
        
        # Test velocity resolution
        RRE.vars.T_cpi = 0.01
        delta_v = RRE.solve.delta_v()
        assert delta_v > 0 and delta_v < 10, f"Velocity resolution out of range: {delta_v}"
        print(f"✓ Velocity resolution: {delta_v:.2f} m/s")
        
        return True
    except Exception as e:
        print(f"✗ Doppler calculations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cwfm_calculations(RRE):
    """Test CWFM radar calculations."""
    print("\n" + "="*70)
    print("TEST 11: CWFM Radar")
    print("="*70)
    
    try:
        # Test CWFM range
        RRE.vars.c = 3e8
        RRE.vars.f_r = 80e3
        RRE.vars.f_m = 100
        RRE.vars.deltaf = 30e6
        range_val = RRE.solve.R_cwfm()
        expected = 2000.0
        assert abs(range_val - expected) < 1, f"CWFM range wrong: {range_val}"
        print(f"✓ CWFM range: {range_val:.2f} m")
        
        return True
    except Exception as e:
        print(f"✗ CWFM calculations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling(RRE):
    """Test error handling with missing variables."""
    print("\n" + "="*70)
    print("TEST 12: Error Handling")
    print("="*70)
    
    try:
        import sympy
        
        # Reset variables to symbolic
        RRE.vars.P_t = sympy.Symbol('P_t')
        RRE.vars.sigma = sympy.Symbol('sigma')
        
        # Try to solve without all variables defined
        result = RRE.solve.R_max.solve()
        assert result is None, "Should return None when variables missing"
        print("✓ Returns None when variables are missing")
        
        # Restore values
        RRE.vars.P_t = 1000.0
        RRE.vars.sigma = 1.0
        
        return True
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases(RRE):
    """Test edge cases and boundary conditions."""
    print("\n" + "="*70)
    print("TEST 13: Edge Cases")
    print("="*70)
    
    try:
        # Test very small frequency
        RRE.vars.c = 3e8
        RRE.vars.f = 1e6  # 1 MHz
        wavelength = RRE.solve.wavelength()
        assert wavelength == 300.0, f"Small frequency failed: {wavelength}"
        print(f"✓ Very small frequency: f={1e6} Hz → λ={wavelength} m")
        
        # Test very large frequency
        RRE.vars.f = 100e9  # 100 GHz
        wavelength = RRE.solve.wavelength()
        expected = 0.003
        assert abs(wavelength - expected) < 1e-10, f"Large frequency failed: {wavelength}"
        print(f"✓ Very large frequency: f={100e9} Hz → λ={wavelength} m")
        
        # Test zero-like values (small but non-zero)
        RRE.vars.A_e = 0.001  # Very small aperture
        RRE.vars.wavelength = 0.03
        gain = RRE.solve.G_t()
        assert gain > 0, f"Small aperture gave negative gain: {gain}"
        print(f"✓ Small aperture: A_e={0.001} m² → G={gain:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Edge cases test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_module_integration(RRE):
    """Test integration between different modules."""
    print("\n" + "="*70)
    print("TEST 14: Module Integration")
    print("="*70)
    
    try:
        # Test constants → variables → equations → solvable → solve chain
        # Note: vars.c may have been modified during tests, so check constants exist
        const_c = RRE.constants.c
        assert const_c > 2.9e8 and const_c < 3.1e8, "Speed of light constant invalid"
        print("✓ Constants module accessible and valid")
        
        # Test equations → solvable integration
        wavelength_eq = RRE.equations.wavelength
        wavelength_solver = RRE.solve.wavelength
        assert isinstance(wavelength_solver, RRE.Solvable), "Solver not a Solvable"
        print("✓ Equations integrated with solvable")
        
        # Test full calculation pipeline
        RRE.vars.c = 3e8
        RRE.vars.f = 10e9
        wl = RRE.solve.wavelength()
        
        RRE.vars.A_e = 2.0
        gain = RRE.solve.G_t()  # Uses wl from previous calculation
        
        assert isinstance(gain, float), "Pipeline didn't produce float"
        print(f"✓ Full pipeline: c,f → λ → G_t = {gain:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Module integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility(RRE):
    """Test backward compatibility with function-based interface."""
    print("\n" + "="*70)
    print("TEST 15: Backward Compatibility")
    print("="*70)
    
    try:
        # Test callable syntax (should work as before)
        RRE.vars.c = 3e8
        RRE.vars.f = 10e9
        
        # Old style: calling as function
        result = RRE.solve.wavelength()
        assert isinstance(result, float), "Function call didn't return float"
        print(f"✓ Function call syntax works: wavelength() = {result}")
        
        # Test redefine_variable function
        RRE.redefine_variable('f', 20e9)
        assert RRE.vars.f == 20e9, "redefine_variable failed"
        print(f"✓ redefine_variable: f = {RRE.vars.f}")
        
        return True
    except Exception as e:
        print(f"✗ Backward compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("COMPREHENSIVE PROCEDURAL TEST SUITE")
    print("Radar Range Equation Package")
    print(f"Random Seed: {RANDOM_SEED}")
    print("="*70)
    
    # Import and setup
    RRE, import_success = test_imports()
    if not import_success:
        print("\n✗ CRITICAL: Failed to import package. Aborting tests.")
        return 1
    
    # Run all tests
    tests = [
        ("Constants", lambda: test_constants(RRE)),
        ("Variables", lambda: test_variables(RRE)),
        ("Equations", lambda: test_equations(RRE)),
        ("Solvable Class", lambda: test_solvable_class(RRE)),
        ("Basic Calculations", lambda: test_basic_calculations(RRE)),
        ("Auto-Variable Definition", lambda: test_auto_variable_definition(RRE)),
        ("Conversions", lambda: test_conversions(RRE)),
        ("Randomized Calculations", lambda: test_randomized_calculations(RRE, 10)),
        ("Doppler Calculations", lambda: test_doppler_calculations(RRE)),
        ("CWFM Calculations", lambda: test_cwfm_calculations(RRE)),
        ("Error Handling", lambda: test_error_handling(RRE)),
        ("Edge Cases", lambda: test_edge_cases(RRE)),
        ("Module Integration", lambda: test_module_integration(RRE)),
        ("Backward Compatibility", lambda: test_backward_compatibility(RRE)),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("="*70)
    print(f"Total: {passed}/{total} tests passed ({100*passed//total}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
