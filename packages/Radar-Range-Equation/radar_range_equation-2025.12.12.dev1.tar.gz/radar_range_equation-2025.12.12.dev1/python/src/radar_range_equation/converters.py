"""Radar Range Equation - Unit Conversion Module.

This module defines the convert class which provides unit conversion utilities
for angles, power, frequency, distance, and signal levels.
"""

import numpy as np


class convert:  # add alias con for convenience
    """Unit conversion utilities for radar calculations.
    
    This class provides a comprehensive set of unit conversion functions for
    angles, power, frequency, distance, and signal levels commonly used in
    radar engineering.
    
    Available conversions:
        - Angles: rad_to_deg, deg_to_rad
        - Power/Signal: lin_to_db, db_to_lin
        - Distance: m_to_mi, mi_to_m, m_to_nmi, nmi_to_m, ft_to_m, m_to, m_from
        - Power: w_to, w_from
        - Frequency: hz_to, hz_from
    
    Example:
        >>> from radar_range_equation import convert
        >>> deg = convert.rad_to_deg(3.14159)
        >>> print(f"{deg} degrees")
    """
    pass
    
    def rad_to_deg(value_radians):
        """Convert radians to degrees.
        
        Args:
            value_radians (float): Angle in radians.
        
        Returns:
            float: Angle in degrees.
        
        Example:
            >>> from radar_range_equation import convert
            >>> deg = convert.rad_to_deg(3.14159)
        """
        return value_radians * (180 / np.pi)
    
    def deg_to_rad(value_degrees):
        """Convert degrees to radians.
        
        Args:
            value_degrees (float): Angle in degrees.
        
        Returns:
            float: Angle in radians.
        
        Example:
            >>> from radar_range_equation import convert
            >>> rad = convert.deg_to_rad(180)
        """
        return value_degrees * (np.pi / 180)
    
    def lin_to_db(value_linear):
        """Convert linear value to decibels (dB).
        
        Args:
            value_linear (float): Linear value (must be positive).
        
        Returns:
            float: Value in dB. Returns -inf for non-positive inputs.
        
        Example:
            >>> from radar_range_equation import convert
            >>> db = convert.lin_to_db(10)  # Returns 10 dB
        """
        # Handle non-positive inputs to avoid math errors
        if value_linear <= 0:
            return -np.inf
        return np.log(value_linear)/np.log(10)*10
    
    def db_to_lin(value_db):
        """Convert decibels (dB) to linear value.
        
        Args:
            value_db (float): Value in dB.
        
        Returns:
            float: Linear value.
        
        Example:
            >>> from radar_range_equation import convert
            >>> lin = convert.db_to_lin(10)  # Returns 10.0
        """
        return 10**(value_db / 10.0)
    
    def m_to_mi(value_meters):
        """Convert meters to miles.
        
        Args:
            value_meters (float): Distance in meters.
        
        Returns:
            float: Distance in miles.
        
        Example:
            >>> from radar_range_equation import convert
            >>> miles = convert.m_to_mi(1609.34)  # Returns ~1 mile
        """
        return value_meters / 1609.34
    
    def mi_to_m(value_miles):
        """Convert miles to meters.
        
        Args:
            value_miles (float): Distance in miles.
        
        Returns:
            float: Distance in meters.
        
        Example:
            >>> from radar_range_equation import convert
            >>> meters = convert.mi_to_m(1)  # Returns 1609.34 meters
        """
        return value_miles * 1609.34
        
    def nmi_to_m(value_nmi):
        """Convert nautical miles to meters.
        
        Args:
            value_nmi (float): Distance in nautical miles.
        
        Returns:
            float: Distance in meters.
        
        Example:
            >>> from radar_range_equation import convert
            >>> meters = convert.nmi_to_m(1)  # Returns 1852 meters
        """
        return value_nmi * 1852.0

    def m_to_nmi(value_m):
        """Convert meters to nautical miles.
        
        Args:
            value_m (float): Distance in meters.
        
        Returns:
            float: Distance in nautical miles.
        
        Example:
            >>> from radar_range_equation import convert
            >>> nmi = convert.m_to_nmi(1852)  # Returns ~1 nautical mile
        """
        return value_m / 1852.0

    def w_to(value_w, target_unit):
        """Convert watts to other power units.
        
        Args:
            value_w (float): Power in watts.
            target_unit (str): Target unit ('kw' for kilowatts, 'mw' for milliwatts).
        
        Returns:
            float: Power in the target unit.
        
        Example:
            >>> from radar_range_equation import convert
            >>> kw = convert.w_to(1000, 'kw')  # Returns 1.0 kW
        """
        conversion_factors = {
            'kw': 1 / 1000.0,
            'mw': 1 * 10**6
        }
        return value_w * conversion_factors.get(target_unit.lower(), 1)

    def w_from(value, source_unit):
        """Convert from other power units to watts.
        
        Args:
            value (float): Power in the source unit.
            source_unit (str): Source unit ('kw' for kilowatts, 'mw' for milliwatts).
        
        Returns:
            float: Power in watts.
        
        Example:
            >>> from radar_range_equation import convert
            >>> watts = convert.w_from(1, 'kw')  # Returns 1000.0 W
        """
        conversion_factors = {
            'kw': 1 / 1000.0,
            'mw': 1 * 10**6
        }
        return value / conversion_factors.get(source_unit.lower(), 1)
    
    def ft_to_m(value_feet):
        """Convert feet to meters.
        
        Args:
            value_feet (float): Distance in feet.
        
        Returns:
            float: Distance in meters.
        
        Example:
            >>> from radar_range_equation import convert
            >>> meters = convert.ft_to_m(1)  # Returns 0.3048 meters
        """
        return value_feet * 0.3048

    def hz_to(value_hz, target_unit):
        """Convert hertz to other frequency units.
        
        Args:
            value_hz (float): Frequency in hertz.
            target_unit (str): Target unit ('khz', 'mhz', or 'ghz').
        
        Returns:
            float: Frequency in the target unit.
        
        Example:
            >>> from radar_range_equation import convert
            >>> ghz = convert.hz_to(10e9, 'ghz')  # Returns 10.0 GHz
        """
        conversion_factors = {
            'khz': 1 * 10**3,
            'mhz': 1 * 10**6,
            'ghz': 1 * 10**9
        }
        return value_hz / conversion_factors.get(target_unit.lower(), 1)
    
    def hz_from(value, source_unit):
        """Convert from other frequency units to hertz.
        
        Args:
            value (float): Frequency in the source unit.
            source_unit (str): Source unit ('khz', 'mhz', or 'ghz').
        
        Returns:
            float: Frequency in hertz.
        
        Example:
            >>> from radar_range_equation import convert
            >>> hz = convert.hz_from(10, 'ghz')  # Returns 10e9 Hz
        """
        conversion_factors = {
            'khz': 1 * 10**3,
            'mhz': 1 * 10**6,
            'ghz': 1 * 10**9
        }
        return value * conversion_factors.get(source_unit.lower(), 1)
    
    def m_to(value_meters, target_unit):
        """Convert meters to other distance units.
        
        Args:
            value_meters (float): Distance in meters.
            target_unit (str): Target unit ('km' for kilometers).
        
        Returns:
            float: Distance in the target unit.
        
        Example:
            >>> from radar_range_equation import convert
            >>> km = convert.m_to(1000, 'km')  # Returns 1.0 km
        """
        conversion_factors = {
            'km': 1 / 1000.0
        }
        return value_meters * conversion_factors.get(target_unit.lower(), 1)

    def m_from(value, source_unit):
        """Convert from other distance units to meters.
        
        Args:
            value (float): Distance in the source unit.
            source_unit (str): Source unit ('km', 'nmi', or 'mi').
        
        Returns:
            float: Distance in meters.
        
        Example:
            >>> from radar_range_equation import convert
            >>> meters = convert.m_from(1, 'km')  # Returns 1000.0 meters
        """
        conversion_factors = {
            'km': 1000.0,
            'nmi': 1852.0,
            'mi': 1609.34
        }
        return value * conversion_factors.get(source_unit.lower(), 1)
    
con = convert()  # alias for convenience


