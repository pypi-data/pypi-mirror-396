"""
CMFO NPU - Hardware Simulator
=============================

Software model of the Fractal Processing Unit.
Simulates registers, memory, and the execution cycle.

Architecture:
- Registers: R0-R7 (General Purpose)
- Memory: Linear address space (mapped to FractalMemoryBank)
- ALU: Fractal Arithmetic Logic Unit
"""

from .instruction_set import OpCode
from ..algebra import fractal_add, fractal_product, fractal_root
from ..core.fractal import phi_decision

class FractalNPU:
    def __init__(self, memory_size=1024):
        # Hardware State
        self.registers = [0.0] * 8  # R0-R7
        self.memory = [0.0] * memory_size # Simplified RAM for v1.0
        self.pc = 0 # Program Counter
        self.running = False
        
    def load_program(self, program):
        """Load a list of Instructions into memory (starting at 0 for simplicity)."""
        self.program = program # Harvard architecture for simulation simplicity
        self.pc = 0
        
    def step(self):
        """Execute one cycle."""
        if self.pc >= len(self.program):
            self.running = False
            return
            
        instr = self.program[self.pc]
        self.pc += 1
        self.execute(instr)
        
    def execute(self, instr):
        op = instr.opcode
        args = instr.operands
        
        if op == OpCode.LOAD: # LOAD RDEST, ADDR
            dest, addr = args[0], args[1]
            self.registers[dest] = self.memory[addr]
            
        elif op == OpCode.STORE: # STORE RSRC, ADDR
            src, addr = args[0], args[1]
            self.memory[addr] = self.registers[src]
            
        elif op == OpCode.MOVE: # MOVE RDEST, RSRC
            dest, src = args[0], args[1]
            self.registers[dest] = self.registers[src]
            
        elif op == OpCode.F_ADD: # F_ADD RDEST, RSRC1, RSRC2
            dest, s1, s2 = args[0], args[1], args[2]
            self.registers[dest] = fractal_add(self.registers[s1], self.registers[s2])
            
        elif op == OpCode.F_MUL: # F_MUL RDEST, RSRC1, RSRC2
            dest, s1, s2 = args[0], args[1], args[2]
            self.registers[dest] = fractal_product(self.registers[s1], self.registers[s2])
            
        elif op == OpCode.F_ROOT: # F_ROOT RDEST, RSRC
            dest, s1 = args[0], args[1]
            self.registers[dest] = fractal_root(self.registers[s1])
            
        elif op == OpCode.HALT:
            self.running = False

    def run(self):
        """Run until HALT."""
        self.running = True
        while self.running:
            self.step()
            
    def dump_registers(self):
        return {f"R{i}": val for i, val in enumerate(self.registers)}
