"""
CMFO Bridges - Thermodynamics & Information
===========================================

Exploring the connection between CMFO and Entropy.

BRIDGE:
Landauer's Principle: H_erasure >= k * T * ln(2)
CMFO Rhombus: Reversible operation => H_change = 0.

This connects CMFO to 'Zero-Entropy Computing'.
"""

import math

BOLTZMANN_K = 1.380649e-23

def shannon_entropy(probabilities):
    """Calculates Shannon Entropy in nats."""
    h = 0
    for p in probabilities:
        if p > 0:
            h -= p * math.log(p)
    return h

def landauer_cost(temp_kelvin=300):
    """Min energy to erase 1 bit at Temp T."""
    # ln(2) approx 0.693
    return BOLTZMANN_K * temp_kelvin * math.log(2)

def analyze_gate_entropy(gate_type):
    """
    Analyzes the entropy change of a logic operation.
    """
    if gate_type == "AND_Standard":
        # 4 inputs (00,01,10,11) -> 2 outputs (0, 1) distributed 3:1
        # Input H = ln(4) = 2 bits
        # Output H = -0.75*ln(0.75) - 0.25*ln(0.25) approx 0.81 bits
        # Loss = 1.19 bits -> Energy dissipated
        return {"entropy_loss_bits": 1.188, "reversible": False}
        
    elif gate_type == "Rhombus_Process":
        # Input mapped 1:1 to Output (Bijective)
        # H_in = H_out
        # Loss = 0
        return {"entropy_loss_bits": 0.0, "reversible": True}
        
    return None
