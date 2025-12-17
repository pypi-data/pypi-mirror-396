"""
CMFO Logic Module
=================

Fractal logic operations.
"""

from .fractal_logic import TRUE, FALSE, NEUTRAL, f_not, f_and, f_or, f_xor
from .circuits import GeometricGate, AndGate, OrGate, XorGate, NotGate

__all__ = [
    'TRUE', 'FALSE', 'NEUTRAL', 
    'f_not', 'f_and', 'f_or', 'f_xor',
    'GeometricGate', 'AndGate', 'OrGate', 'XorGate', 'NotGate'
]
