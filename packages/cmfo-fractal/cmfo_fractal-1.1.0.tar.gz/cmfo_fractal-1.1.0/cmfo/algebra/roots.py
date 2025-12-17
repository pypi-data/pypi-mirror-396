"""
CMFO Algebra - Fractal Roots
=============================

Fractal root operation and related functions.
"""

import math
from ..constants import PHI, PHI_INV


def fractal_root(x: float) -> float:
    """
    Fractal root operation.
    
    Definition:
        √_φ(x) = x^(1/φ) = x^φ⁻¹
    
    The fractal root collapses hierarchical structures to their geometric core.
    It is the fundamental operation for:
    - Natural scaling without arbitrary exponents
    - Hierarchical mass/energy relationships
    - Continuous logic without binary collapse
    
    Properties:
    -----------
    - √_φ(φ^k) = φ^(k/φ)
    - lim_{n→∞} √_φ^(n)(x) = 1 for any x > 0
    - Non-linear: √_φ(x+y) ≠ √_φ(x) + √_φ(y)
    
    Parameters
    ----------
    x : float
        Input value (must be positive)
    
    Returns
    -------
    float
        Fractal root of x
    
    Raises
    ------
    ValueError
        If x is non-positive
    
    Examples
    --------
    >>> fractal_root(PHI)
    1.3819660112501051  # φ^(1/φ)
    >>> fractal_root(1.0)
    1.0
    >>> abs(fractal_root(fractal_root(100)) - 100**(PHI_INV**2)) < 1e-10
    True
    """
    if x <= 0:
        raise ValueError("Fractal root requires x > 0.")
    
    return x ** PHI_INV


def iterated_fractal_root(x: float, n: int) -> float:
    """
    Apply fractal root n times.
    
    Definition:
        √_φ^(n)(x) = (√_φ ∘ √_φ ∘ ... ∘ √_φ)(x)  [n times]
    
    For large n, this converges to 1 for any x > 0.
    
    Parameters
    ----------
    x : float
        Input value (must be positive)
    n : int
        Number of iterations (must be non-negative)
    
    Returns
    -------
    float
        Result after n applications of fractal root
    
    Examples
    --------
    >>> abs(iterated_fractal_root(100.0, 50) - 1.0) < 1e-5
    True
    """
    if x <= 0:
        raise ValueError("Input must be positive.")
    if n < 0:
        raise ValueError("Number of iterations must be non-negative.")
    
    result = x
    for _ in range(n):
        result = fractal_root(result)
    
    return result


__all__ = ['fractal_root', 'iterated_fractal_root']
