"""
CMFO Topology - Spectral Geometry
=================================

Deriving 'Physics' strictly from the Geometry of the 7D Torus (T^7).

Principle:
Particles are not added to the universe; they are standing waves (eigenmodes)
of the 7D Manifold. Mass is the eigenvalue of the Laplacian.

Math:
    Δψ = -λψ
    
    On a T^7 torus with metric g_ii = φ^i, the eigenvalues are:
    λ_k = 4π² ∑ (n_i² / g_ii)
    
    where n_i are integers (winding numbers) around the 7 dimensions.
"""

import numpy as np
import math
from ..constants import PHI

def get_metric_diagonal(dim=7):
    """
    Returns the metric components g_ii = PHI^i.
    This defines the 'shape' of the torus.
    """
    # Dimensions are compacted by powers of Phi
    return np.array([PHI**i for i in range(dim)])

def calculate_eigenvalue(n_vector, metric):
    """
    Calculates the Laplacian Eigenvalue (Energy^2) for a given mode n.
    λ = 4π² * sum( n_i^2 / g_ii )
    """
    # High dimensions (large g_ii) contribute LESS to energy (lighter modes).
    # Low dimensions (small g_ii) contribute MORE to energy (heavy modes).
    terms = (np.array(n_vector)**2) / metric
    return 4 * (math.pi**2) * np.sum(terms)

def derive_geometric_spectrum(max_quantum_number=2):
    """
    Generates the low-energy particle spectrum purely from geometry.
    Iterates through quantum numbers n_0, ..., n_6.
    """
    metric = get_metric_diagonal()
    spectrum = []
    
    # We scan reduced quantum numbers for demonstration speed
    # In a full solver, we'd use a better iterator
    from itertools import product
    range_n = range(max_quantum_number + 1)
    
    for n_vec in product(range_n, repeat=7):
        if sum(n_vec) == 0: continue # Vacuum state
        
        lambda_val = calculate_eigenvalue(n_vec, metric)
        # Mass is proportional to sqrt(lambda)
        mass_proxy = math.sqrt(lambda_val)
        
        spectrum.append({
            "mode": n_vec,
            "eigenvalue": lambda_val,
            "geometric_mass": mass_proxy
        })
        
    # Sort by mass
    spectrum.sort(key=lambda x: x['geometric_mass'])
    return spectrum
