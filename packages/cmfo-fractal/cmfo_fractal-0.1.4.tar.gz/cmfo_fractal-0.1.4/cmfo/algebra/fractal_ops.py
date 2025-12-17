"""
CMFO Algebra - Fractal Operations
==================================

Core algebraic operations in the fractal field.
"""

import math
from ..constants import PHI


def fractal_product(x: float, y: float) -> float:
    """
    Fractal product operation.
    
    Definition:
        x ⊗_φ y = x^(log_φ(y))
    
    This operation encodes scale rather than quantity, making it suitable
    for hierarchical and self-similar structures.
    
    Parameters
    ----------
    x : float
        First operand (must be positive)
    y : float
        Second operand (must be positive)
    
    Returns
    -------
    float
        Result of fractal product
    
    Raises
    ------
    ValueError
        If either x or y is non-positive
    
    Examples
    --------
    >>> fractal_product(2.0, PHI)
    2.0
    >>> fractal_product(PHI, PHI)
    2.618033988749895  # φ²
    """
    if x <= 0 or y <= 0:
        raise ValueError("Fractal product requires positive inputs.")
    
    # x^(log_φ(y)) = exp(log(x) * log(y) / log(φ))
    return math.exp(math.log(x) * (math.log(y) / math.log(PHI)))


def fractal_add(x: float, y: float) -> float:
    """
    Fractal addition (standard addition).
    
    Definition:
        x ⊕_φ y = x + y
    
    Standard addition is preserved in the fractal field.
    Fractality emerges from other operations.
    
    Parameters
    ----------
    x, y : float
        Operands
    
    Returns
    -------
    float
        Sum of x and y
    """
    return x + y


__all__ = ['fractal_product', 'fractal_add']
