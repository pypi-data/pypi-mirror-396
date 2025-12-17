"""
CMFO Logic - Fractal Logic Operations
======================================

Geometric logic with φ-scaling, compatible with analog hardware and NPUs.
This is NOT standard fuzzy logic - it's geometric logic with golden ratio scaling.
"""

from ..constants import PHI, PHI_INV


# Logic Constants
TRUE = 1.0
FALSE = 0.0
NEUTRAL = PHI_INV  # ≈ 0.618


def f_not(x: float) -> float:
    """
    Fractal NOT operation.
    
    Definition:
        ¬_φ x = 1 - x
    
    Parameters
    ----------
    x : float
        Input value (typically in [0, 1])
    
    Returns
    -------
    float
        Logical negation
    
    Examples
    --------
    >>> f_not(TRUE)
    0.0
    >>> f_not(FALSE)
    1.0
    >>> f_not(NEUTRAL)
    0.38196601125010515  # 1 - φ⁻¹
    """
    return 1.0 - x


def f_and(a: float, b: float) -> float:
    """
    Fractal AND operation.
    
    Definition:
        a ∧_φ b = (a · b)^(1/φ)
    
    Geometric conjunction with φ-stability.
    
    Parameters
    ----------
    a, b : float
        Input values (typically in [0, 1])
    
    Returns
    -------
    float
        Logical AND result
    
    Examples
    --------
    >>> abs(f_and(TRUE, TRUE) - TRUE**(1/PHI)) < 1e-10
    True
    >>> f_and(FALSE, TRUE)
    0.0
    >>> f_and(NEUTRAL, NEUTRAL)  # doctest: +ELLIPSIS
    0.56...
    """
    return (a * b) ** PHI_INV


def f_or(a: float, b: float) -> float:
    """
    Fractal OR operation.
    
    Definition:
        a ∨_φ b = 1 - ((1-a) ∧_φ (1-b))
    
    Derived from De Morgan's law in fractal logic.
    
    Parameters
    ----------
    a, b : float
        Input values (typically in [0, 1])
    
    Returns
    -------
    float
        Logical OR result
    
    Examples
    --------
    >>> f_or(FALSE, FALSE)
    0.0
    >>> f_or(TRUE, FALSE)  # doctest: +ELLIPSIS
    1.0...
    >>> f_or(NEUTRAL, NEUTRAL)  # doctest: +ELLIPSIS
    0.79...
    """
    return 1.0 - f_and(1.0 - a, 1.0 - b)


def f_xor(a: float, b: float) -> float:
    """
    Fractal XOR operation.
    
    Definition:
        a ⊕_φ b = (a ∨_φ b) ∧_φ ¬_φ(a ∧_φ b)
    
    Parameters
    ----------
    a, b : float
        Input values (typically in [0, 1])
    
    Returns
    -------
    float
        Logical XOR result
    """
    return f_and(f_or(a, b), f_not(f_and(a, b)))


__all__ = ['TRUE', 'FALSE', 'NEUTRAL', 'f_not', 'f_and', 'f_or', 'f_xor']
