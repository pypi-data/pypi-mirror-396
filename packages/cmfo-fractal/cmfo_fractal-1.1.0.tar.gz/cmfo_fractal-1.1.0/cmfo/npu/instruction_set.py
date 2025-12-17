"""
CMFO NPU - Instruction Set Architecture (ISA)
=============================================

Defines the low-level operations supported by the Fractal NPU.
This is the "Assembly" of the fractal machine.
"""

from enum import Enum, auto

class OpCode(Enum):
    # Data Movement
    LOAD = auto()   # Load from memory to register
    STORE = auto()  # Store from register to memory
    MOVE = auto()   # Move between registers
    
    # Fractal Arithmetic
    F_ADD = auto()      # Fractal Addition (x + y)
    F_MUL = auto()      # Fractal Product (x ⊗φ y)
    F_ROOT = auto()     # Fractal Root (ℛφ x)
    
    # Logic / Collapse
    DECIDE = auto()     # Geometric Decision (Collapse)
    INVERT = auto()     # Geometric Inversion
    
    # Control Flow
    HALT = auto()       # Stop execution

class Instruction:
    """
    A single machine instruction.
    """
    def __init__(self, opcode: OpCode, operands: list):
        self.opcode = opcode
        self.operands = operands
        
    def __repr__(self):
        return f"{self.opcode.name} {self.operands}"

def asm(opcode, *operands):
    """Helper to create an instruction."""
    return Instruction(opcode, list(operands))
