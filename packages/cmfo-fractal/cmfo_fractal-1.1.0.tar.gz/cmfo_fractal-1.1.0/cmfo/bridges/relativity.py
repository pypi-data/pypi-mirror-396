"""
CMFO Bridges - Relativity & DSR
===============================

Exploring the connection between CMFO and Doubly Special Relativity (DSR).

BRIDGE:
Standard SR: E^2 = p^2 c^2 + m^2 c^4
CMFO Theory: E^2 = φ^2 (p^2 c^2) + m^2 c^4 (Hypothesis from user context)

This creates a bridge to 'Rainbow Gravity' or scale-dependent metrics.
"""

import numpy as np
from ..constants import PHI, C

def lorentz_factor_standard(v):
    """Standard Gamma factor."""
    if v >= C: return float('inf')
    return 1 / np.sqrt(1 - (v**2 / C**2))

def lorentz_factor_fractal(v):
    """
    Hypothetical Fractal Gamma factor.
    If the metric is scaled by PHI, the speed limit might be 'c' locally
    but effective path length is longer/shorter.
    """
    # In a space where d_fractal = sqrt(g_ii dx^i), velocities are scaled.
    # We propose that v_effective = v * sqrt(PHI) for traversal.
    v_eff = v * np.sqrt(PHI)
    if v_eff >= C: return float('inf')
    return 1 / np.sqrt(1 - (v_eff**2 / C**2))

def analyze_dispersion_relation():
    """
    Compares Standard vs Fractal dispersion.
    """
    velocities = np.linspace(0, 0.99*C, 10)
    results = []
    
    for v in velocities:
        g_std = lorentz_factor_standard(v)
        g_fr = lorentz_factor_fractal(v)
        
        results.append({
            "v_c": v/C,
            "gamma_std": g_std,
            "gamma_fractal": g_fr,
            "divergence": g_fr - g_std
        })
    return results
