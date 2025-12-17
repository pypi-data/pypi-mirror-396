# =====================================================================
# CMFO - Fractal Universal Computation Engine
# =====================================================================
# Academic and personal use permitted under Apache 2.0.
# Commercial, corporate or governmental use requires CMFO license.
# Commercial contact:
#   Jonathan Montero Viquez – San José, Costa Rica
#   jmvlavacar@hotmail.com
# =====================================================================

__version__ = "1.1.0"
__author__ = "Jonathan Montero Viquez"
__credits__ = "CMFO Universe"

# 1. CORE CONSTANTS
from .constants import PHI, PHI_INV, HBAR, C, G, ALPHA, M_PLANCK

# 2. ALGEBRA (Fractal Field Operations)
from .algebra import (
    fractal_product,
    fractal_add,
    fractal_root,
    iterated_fractal_root,
)
# Alias for backward compatibility / explicit naming
fractal_multiply = fractal_product

# 3. LOGIC (Geometric Operations)
from .logic.fractal_logic import (
    TRUE,
    FALSE,
    NEUTRAL,
    f_not,
    f_and,
    f_or,
    f_xor,
)

# 4. GEOMETRY (Fundamental Units)
# The Triangle decides. The Rhombus remembers.
from .geometry.triangle import Triangle
from .geometry.rhombus import Rhombus

# 4.5 MEMORY (Fractal Storage)
from .memory import FractalMemoryCell, FractalMemoryBank

# 4.8 COMPILER (Structural Execution)
from .compiler import FractalGraph, FractalJIT

# 4.9 NPU (Hardware Simulation)
from .npu import FractalNPU, OpCode, asm

# 4.95 TOPOLOGY (Riemannian Manifold)
from .topology import PhiManifold
# Physics is DERIVED from Topology (Spectral Geometry)
# See DERIVATION.md

# 6. BRIDGES (Interdisciplinary Analysis)
from .bridges import analyze_dispersion_relation, analyze_gate_entropy, landauer_cost, analyze_level_spacings

# 7. APPLICATIONS (Fractal AI)
from .apps import FractalNeuron

# 5. PHYSICS (Geometric Mass)
from .physics import geometric_mass, compton_wavelength

# 6. SUPERPOSITION (Deterministic Parallelism)
from .superposition.batch import FractalBatch

# 7. CORE (Legacy & Native)
from .core.t7_tensor import T7Tensor
from .core.matrix import T7Matrix
from .core.fractal import geometric_state_collapse, phi_decision


def tensor(v):
    """Create a T7Tensor from a vector."""
    return T7Tensor(v)


def info():
    """Display CMFO package information."""
    print(f"CMFO Fractal Engine v{__version__}")
    print(f"Author: {__author__}")
    print("-" * 50)
    print("Status: PRODUCTION READY (STANDARD v1.0)")
    print("Architecture: 7D φ-Manifold + Geometric Collapse")
    print("Geometry: Triangle (Decision) | Rhombus (Memory)")
    print("Logic: Geometric Operators (∧_φ, ∨_φ, ¬_φ)")
    print("Physics: Compton Mass | Fractal Time")
    print("-" * 50)
    print("Documentation: https://github.com/1JONMONTERV/CMFO-COMPUTACION-FRACTAL-")
    print("For commercial licensing: jmvlavacar@hotmail.com")


# Validation Entry Point
from .verify import run as verify

__all__ = [
    # Version
    "__version__", "__author__",
    # Constants
    "PHI", "PHI_INV", "HBAR", "C", "G", "ALPHA", "M_PLANCK",
    # Algebra
    "fractal_product", "fractal_add", "fractal_root", "iterated_fractal_root", "fractal_multiply",
    # Logic
    "TRUE", "FALSE", "NEUTRAL", "f_not", "f_and", "f_or", "f_xor",
    # Geometry
    "Triangle", "Rhombus",
    # Memory
    "FractalMemoryCell", "FractalMemoryBank",
    # Compiler
    "FractalGraph", "FractalJIT",
    # NPU
    "FractalNPU", "OpCode", "asm",
    # Topology
    "PhiManifold",
    # Bridges
    "analyze_dispersion_relation", "analyze_gate_entropy", "landauer_cost", "analyze_level_spacings",
    # Applications
    "FractalNeuron",
    # Physics
    "geometric_mass", "compton_wavelength",
    # Superposition
    "FractalBatch",
    # Core/Utilities
    "T7Tensor", "T7Matrix", "tensor", "phi_decision", "geometric_state_collapse",
    "info", "verify",
]
