"""
CMFO Geometry - Rhombus
=======================

The Rhombus is the unit minimal of reversible computation.
It is composed of two Triangles (forward and backward) that ensure 
no information is lost during transformation.

Definition:
    Rhombus = Triangle_forward + Triangle_backward
"""

from .triangle import Triangle

class Rhombus:
    """
    Fundamental unit of reversible computation.
    
    The rhombus guarantees conservation of information by coupling a forward
    process with its geometric inverse.
    
    Attributes
    ----------
    forward : Triangle
        The forward-facing geometric state.
    backward : Triangle
        The backward-facing (inverse) geometric state.
    """
    
    def __init__(self, forward: Triangle, backward: Triangle):
        self.forward = forward
        self.backward = backward
        
    def __repr__(self):
        return f"Rhombus(F={self.forward}, B={self.backward})"
        
    def invert(self):
        """
        Return the geometric inverse of the Rhombus.
        Since it is symmetric, this swaps forward and backward components.
        """
        return Rhombus(forward=self.backward, backward=self.forward)

    def process(self, input_state):
        """
        Process an input through the Rhombus.
        Returns the transformed state.
        """
        # Updates the internal forward triangle state and decides
        self.forward.state = input_state
        return self.forward.decide()

    def recover(self, output_state):
        """
        Recover the original input from the output (Reversibility).
        """
        # Updates the internal backward triangle state and decides
        self.backward.state = output_state
        return self.backward.decide()

    def is_reversible(self, test_input=1.0, tolerance=1e-9) -> bool:
        """
        Check if the computation is strictly reversible.
        In a perfect Rhombus, B(F(x)) == x.
        """
        try:
            y = self.process(test_input)
            x_rec = self.recover(y)
            return abs(x_rec - test_input) < tolerance
        except Exception:
            return False
            
    def remember(self):
        """
        Store the current state in the geometric structure.
        """
        return {
            'forward': self.forward.decide(),
            'backward': self.backward.decide()
        }
