"""
CMFO Logic - Fractal Circuits
=============================

Geometric implementation of logic gates using Triangle formulations.
Each gate is a specific configuration of a Decision Triangle.
"""

from ..geometry.triangle import Triangle
from .fractal_logic import f_and, f_or, f_not, f_xor

class GeometricGate:
    """
    Base class for geometric logic gates.
    Wraps a Triangle configured with specific fractal logic operators.
    """
    def __init__(self, operation):
        self.operation = operation
    
    def apply(self, *inputs):
        """
        Apply the gate to inputs.
        Creates a transient Triangle to collapse the state.
        """
        # The 'state' is the inputs, the 'relation' is the logic operator
        # The Triangle decides the outcome.
        t = Triangle(state=inputs, relation=lambda x: self.operation(*x))
        return t.decide()

class AndGate(GeometricGate):
    def __init__(self):
        super().__init__(f_and)

class OrGate(GeometricGate):
    def __init__(self):
        super().__init__(f_or)

class XorGate(GeometricGate):
    def __init__(self):
        super().__init__(f_xor)

class NotGate(GeometricGate):
    def __init__(self):
        # NOT only takes 1 argument, handling packing/unpacking
        super().__init__(lambda x: f_not(x[0] if isinstance(x, (tuple, list)) else x))

def circuit_layer(inputs, gate_type):
    """
    Apply a layer of geometric gates to a set of inputs.
    """
    gate = gate_type()
    # Pairwise application for simplicity in this demo implementation
    results = []
    for i in range(0, len(inputs)-1, 2):
        results.append(gate.apply(inputs[i], inputs[i+1]))
    return results
