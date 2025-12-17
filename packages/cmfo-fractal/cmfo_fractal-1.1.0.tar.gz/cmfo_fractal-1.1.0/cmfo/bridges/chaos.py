"""
CMFO Bridges - Quantum Chaos & Stability
========================================

Analyzes the statistical distribution of energy levels (Laplacian Eigenvalues)
on the 7D Phi-Manifold.

BRIDGE:
- Random Systems (Chaos) -> Wigner-Dyson Distribution (Level Repulsion)
- Stable Systems (Integrable) -> Poisson Distribution (clustering allowed)

Hypothesis: CMFO must be Integrable (Stable) to support 'Fractal Memory'.
We check the Level Spacing Distribution P(s).
"""

import numpy as np
from ..topology.spectral import derive_geometric_spectrum

def analyze_level_spacings(max_n=4):
    """
    Calculates the distribution of nearest-neighbor spacings
    between sorted energy levels.
    s_i = (E_{i+1} - E_i) / <mean_spacing>
    """
    # 1. Get raw spectrum (masses/energies)
    spectrum = derive_geometric_spectrum(max_n)
    energies = sorted([p['eigenvalue'] for p in spectrum])
    
    # Remove duplicates (degeneracies) due to symmetry for statistic analysis
    unique_energies = sorted(list(set(energies)))
    
    if len(unique_energies) < 10:
        return {"status": "Insufficient Data"}

    # 2. Compute Spacings
    spacings = np.diff(unique_energies)
    mean_spacing = np.mean(spacings)
    normalized_spacings = spacings / mean_spacing
    
    # 3. Calculate Variance of spacings
    # Poisson (Stable) variance ~ 1.0 (uncorrelated)
    # Wigner-Dyson (Chaotic) variance ~ 0.27 (rigid, repelling)
    # Berry-Tabor conjecture implies integrability for Torus.
    variance = np.var(normalized_spacings)
    
    return {
        "mean_spacing": mean_spacing,
        "variance": variance,
        "regime": "Poisson-like (Stable/Integrable)" if variance > 0.5 else "Wigner-like (Chaotic/Rigid)",
        "num_levels": len(unique_energies)
    }
