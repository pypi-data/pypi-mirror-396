"""
CMFO Geometry - Triangle
=========================

The Triangle is the unit minimal of determination in CMFO.
It replaces the concept of a 'bit' with a geometric structure that carries 
state, relation, and scale.

Definition:
    Triangle = (state, relation, scale)
             = (x, f(x), φ^k)
"""

from ..constants import PHI

class Triangle:
    """
    Fundamental unit of determination.
    
    A Triangle creates a deterministic decision by fixing orientation and scale.
    unlike a probabilistic bit, a Triangle cannot differ from itself.
    
    Attributes
    ----------
    state : any
        The base state (x).
    relation : any
        The relational state (f(x)).
    scale : float
         The fractal scale factor (φ^k).
    """
    
    def __init__(self, state, relation, scale=1.0):
        self.state = state
        self.relation = relation
        self.scale = scale
        
    def __repr__(self):
        return f"Triangle(x={self.state}, f(x)={self.relation}, scale={self.scale})"
    
    
    def decide(self):
        """
        Produce a deterministic decision.
        
        The triangle stabilizes the state by applying the relation and 
        collapsing any ambiguity using the fractal geometry.
        
        If the state is a vector/tensor, this applies `phi_decision`.
        If the state is a scalar, it returns the stabilized value.
        """
        import numpy as np
        from ..core.fractal import phi_decision, fractal_root
        
        # 1. Apply Relation (Project the state)
        if callable(self.relation):
            projected = self.relation(self.state)
        else:
            projected = self.relation
            
        # 2. Geometric Collapse (The "Decision")
        if isinstance(projected, (list, np.ndarray)):
            # "The triangle decides" -> collapses vector to index/class
            return phi_decision(np.array(projected))
        else:
            # Scalar stabilization
            return fractal_root(projected * self.scale)
