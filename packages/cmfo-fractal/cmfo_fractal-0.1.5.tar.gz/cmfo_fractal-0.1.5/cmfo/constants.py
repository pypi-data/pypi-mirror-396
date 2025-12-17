"""
CMFO Constants
==============

Fundamental physical and mathematical constants for CMFO framework.
"""

import math

# Mathematical Constants
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio: φ ≈ 1.618033988749895
PHI_INV = 1 / PHI              # φ⁻¹ ≈ 0.618033988749895

# Physical Constants (CODATA 2018)
HBAR = 1.054571817e-34  # Reduced Planck constant [J·s]
C = 299792458.0         # Speed of light [m/s]
G = 6.67430e-11         # Gravitational constant [m³/(kg·s²)]
ALPHA = 7.29735256e-3   # Fine structure constant (dimensionless)

# Derived Constants
M_PLANCK = math.sqrt((HBAR * C) / G)  # Planck mass [kg]

__all__ = ['PHI', 'PHI_INV', 'HBAR', 'C', 'G', 'ALPHA', 'M_PLANCK']
