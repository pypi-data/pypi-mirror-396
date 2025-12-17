"""
CMFO Algebra Module
===================

Fractal algebraic operations.
"""

from .fractal_ops import fractal_product, fractal_add
from .roots import fractal_root, iterated_fractal_root

__all__ = [
    'fractal_product',
    'fractal_add',
    'fractal_root',
    'iterated_fractal_root',
]
