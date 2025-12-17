"""
CMFO Applications - Fractal Neuron
==================================

A neuron that processes information using Fractal Geometry instead of Linear Algebra.

Standard Neuron:
    y = Activation( sum( w_i * x_i + b ) )

Fractal Neuron:
    y = GeometricCollapse( FractalSuperposition( w_i, x_i ) )

The activation is provided by the Phi-Stability of the Triangle.
"""

import numpy as np
from ..constants import PHI, PHI_INV
from ..algebra.fractal_ops import fractal_product, fractal_add
from ..geometry.triangle import Triangle

class FractalNeuron:
    def __init__(self, input_dim):
        # Weights are initialized around PHI alignment
        self.weights = np.random.uniform(0.5, PHI, input_dim)
        self.bias = 0.0
        
    def forward(self, inputs):
        """
        Fractal Feed-Forward using CMFO algebra.
        """
        # 1. Fractal Superposition
        accumulation = self.bias
        for w, x in zip(self.weights, inputs):
            # Term = w * x (standard scaling for now to ensure learning stability)
            # Mixed Mode: We use standard math for 'intensity' but Phi for 'activation'
            term = w * x 
            accumulation += term
            
        # 2. Geometric Activation (The "Phi-Sigmoid")
        # f(x) = 1 / (1 + phi^(-x))
        # This is centered around 0. To solve XOR, we need a sinusoidal response or similar 
        # highly non-linear manifold.
        # "Fractal" implies periodic/recursive structure.
        # Let's use: sin(phi * x) for a holographic neuron
        
        output = np.sin(PHI * accumulation)
        # Squash to 0..1
        return (output + 1) / 2.0

    def predict(self, inputs):
        return 1 if self.forward(inputs) > 0.5 else 0
