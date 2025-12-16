"""Radar Range Equation - Solvable Class Module.

This module defines the Solvable class which provides an interactive,
introspective solver for individual radar parameters.
"""

import sympy
from .variables import vars


class Solvable:
    """A dynamic, introspective solver for a single radar parameter.
    
    This class encapsulates the logic to solve for a single parameter using
    one or more symbolic equations. It can report its status (what's needed
    to solve) and perform the calculation when all required inputs are available.
    
    The Solvable class interacts with the vars module to check which variables
    are defined and uses sympy to perform symbolic and numeric calculations.
    
    Attributes:
        target_symbol (sympy.Symbol): The variable to be solved for
        equation_list (list): List of sympy.Eq equations that can solve for the target
    
    Example:
        >>> import radar_range_equation as RRE
        >>> # In interactive console: RRE.solve.G_t shows status
        >>> # RRE.solve.G_t() executes calculation
    """
    
    def __init__(self, target_symbol, equation_list):
        """Initialize a Solvable instance.
        
        Args:
            target_symbol (sympy.Symbol): The variable to be solved for (e.g., G_t)
            equation_list (list): List of sympy.Eq objects that can calculate the target
        """
        self.target_symbol = target_symbol
        self.equation_list = equation_list if isinstance(equation_list, list) else [equation_list]
    
    def _normalize_var_name(self, sym):
        """Normalize a sympy symbol name to match vars attribute names.
        
        Handles special cases like 'lambda' -> 'wavelength' and 'Delta f' -> 'deltaf'.
        
        Args:
            sym (sympy.Symbol): The symbol to normalize
            
        Returns:
            str: The normalized variable name
        """
        var_name = sym.name
        
        # Handle special case for 'lambda' (wavelength)
        if var_name == 'lambda':
            var_name = 'wavelength'
        # Handle 'Delta f'
        elif str(sym) == 'Delta f':
            var_name = 'deltaf'
        
        return var_name
    
    def status(self):
        """Display a status report showing what's needed to solve for the target.
        
        Iterates through each equation in equation_list and checks which variables
        are defined in the vars module. Prints a human-readable report indicating
        whether each equation is ready to solve or which variables are missing.
        
        Returns:
            None (prints to stdout)
        """
        print(f"\n{'='*70}")
        print(f"Status for solving: {self.target_symbol}")
        print(f"{'='*70}\n")
        
        for i, equation in enumerate(self.equation_list, 1):
            print(f"Equation {i}: {equation}")
            print("-" * 70)
            
            # Get the right-hand side of the equation
            rhs = equation.rhs
            
            # Get all free symbols needed for this equation
            free_symbols = rhs.free_symbols
            
            # Check which variables are defined
            defined_vars = []
            missing_vars = []
            
            for sym in free_symbols:
                # Try to get the value from vars
                var_name = self._normalize_var_name(sym)
                
                if hasattr(vars, var_name):
                    value = getattr(vars, var_name)
                    # Check if it's a numeric value (int or float)
                    if isinstance(value, (int, float)) and not isinstance(value, sympy.Basic):
                        defined_vars.append((sym, value))
                    else:
                        missing_vars.append(sym)
                else:
                    missing_vars.append(sym)
            
            # Determine if equation is solvable
            if not missing_vars:
                print("✓ Status: Ready to solve")
                print(f"  Defined variables ({len(defined_vars)}):")
                for sym, val in defined_vars:
                    print(f"    - {sym} = {val}")
            else:
                print("✗ Status: Missing variables")
                if defined_vars:
                    print(f"  Defined variables ({len(defined_vars)}):")
                    for sym, val in defined_vars:
                        print(f"    - {sym} = {val}")
                print(f"  Missing variables ({len(missing_vars)}):")
                for sym in missing_vars:
                    print(f"    - {sym}")
            
            print()
    
    def solve(self):
        """Attempt to solve for the target variable.
        
        Iterates through equations to find one where all required variables
        are numerically defined in vars. When found, substitutes values and
        calculates the result.
        
        Returns:
            float: The calculated value, or None if no equation can be solved
        """
        # Helper to convert Python numbers to sympy Floats
        def _s(v):
            return v if isinstance(v, sympy.Basic) else sympy.Float(v)
        
        for i, equation in enumerate(self.equation_list, 1):
            # Solve equation symbolically for target
            try:
                sym_expr = sympy.solve(equation, self.target_symbol)[0]
            except (IndexError, Exception):
                # Can't solve this equation, try next
                continue
            
            # Get free symbols in the solved expression
            free_symbols = sym_expr.free_symbols
            
            # Build substitution map
            subs_map = {}
            all_defined = True
            
            for sym in free_symbols:
                var_name = self._normalize_var_name(sym)
                
                if hasattr(vars, var_name):
                    value = getattr(vars, var_name)
                    # Check if it's numeric
                    if isinstance(value, (int, float)) and not isinstance(value, sympy.Basic):
                        subs_map[sym] = _s(value)
                    else:
                        all_defined = False
                        break
                else:
                    all_defined = False
                    break
            
            # If all variables are defined, calculate result
            if all_defined:
                value_sym = sym_expr.subs(subs_map)
                value_simpl = sympy.simplify(value_sym)
                result = float(value_simpl.evalf())
                
                # Automatically define the corresponding variable in vars
                var_name = self._normalize_var_name(self.target_symbol)
                setattr(vars, var_name, result)
                
                return result
        
        # No equation was solvable
        print(f"\n✗ Error: Cannot solve for {self.target_symbol}")
        print("No equation has all required variables defined.\n")
        self.status()
        return None
    
    def __repr__(self):
        """Return string representation by calling status().
        
        This allows interactive consoles to automatically show the status
        when the object name is typed.
        
        Returns:
            str: Empty string (status is printed as side effect)
        """
        self.status()
        return ""
    
    def __call__(self):
        """Make the object callable, invoking solve().
        
        This provides function-like syntax for executing the calculation.
        
        Returns:
            float: The calculated value from solve()
        """
        return self.solve()

