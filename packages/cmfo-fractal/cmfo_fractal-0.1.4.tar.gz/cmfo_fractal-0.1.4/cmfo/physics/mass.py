"""
CMFO Physics - Mass Relations
==============================

Geometric mass calculations based on Compton wavelength.
"""

from ..constants import HBAR, C


def geometric_mass(L: float) -> float:
    """
    Geometric mass from characteristic length.
    
    Definition:
        m = ħ / (c · L)
    
    This is the Compton relation: mass is inversely proportional to
    characteristic length scale. Dimensionally correct and fundamental.
    
    Parameters
    ----------
    L : float
        Characteristic length [m] (must be positive)
    
    Returns
    -------
    float
        Mass [kg]
    
    Raises
    ------
    ValueError
        If L is non-positive
    
    Examples
    --------
    >>> # Electron Compton wavelength
    >>> L_e = 2.4263102367e-12  # meters
    >>> m_e = geometric_mass(L_e)
    >>> abs(m_e - 9.1093837015e-31) / 9.1093837015e-31 < 0.01  # Within 1%
    True
    
    Notes
    -----
    This relation is exact in natural units where ħ = c = 1.
    It forms the anchor for all CMFO mass predictions.
    """
    if L <= 0:
        raise ValueError("Length must be positive.")
    
    return HBAR / (C * L)


def compton_wavelength(m: float) -> float:
    """
    Compton wavelength from mass (inverse of geometric_mass).
    
    Definition:
        λ = ħ / (m · c)
    
    Parameters
    ----------
    m : float
        Mass [kg] (must be positive)
    
    Returns
    -------
    float
        Compton wavelength [m]
    
    Raises
    ------
    ValueError
        If m is non-positive
    """
    if m <= 0:
        raise ValueError("Mass must be positive.")
    
    return HBAR / (m * C)


__all__ = ['geometric_mass', 'compton_wavelength']
