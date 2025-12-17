# =====================================================================
# CMFO - Fractal Universal Computation Engine
# =====================================================================
# Academic and personal use permitted under Apache 2.0.
# Commercial, corporate or governmental use requires CMFO license.
# Commercial contact:
#   Jonathan Montero Viquez – San José, Costa Rica
#   jmvlavacar@hotmail.com
# =====================================================================

__version__ = "1.0.0"
__author__ = "Jonathan Montero Viquez"
__credits__ = "CMFO Universe"

# Core constants
from .constants import PHI, PHI_INV, HBAR, C, G, ALPHA, M_PLANCK

# Algebra module
from .algebra import (
    fractal_product,
    fractal_add,
    fractal_root,
    iterated_fractal_root,
)

# Logic module (unified - using new fractal_logic)
from .logic.fractal_logic import (
    TRUE,
    FALSE,
    NEUTRAL,
    f_not,
    f_and,
    f_or,
    f_xor,
)

# Physics module
from .physics import geometric_mass, compton_wavelength

# Legacy core modules (for backward compatibility)
from .core.t7_tensor import T7Tensor
from .core.matrix import T7Matrix
from .core.gamma_phi import gamma_step

# New Fractal Core
from .core.fractal import (
    fractal_root,
    fractal_add,
    fractal_multiply,
    PhiBit,
    phi_and,
    phi_or,
    phi_not,
    phi_decision,
    geometric_state_collapse
)

# Legacy logic (for backward compatibility)
from .logic.phi_logic import (
    phi_sign,
    # phi_and, # Now available from core.fractal
    # phi_or,  # Now available from core.fractal
    # phi_not, # Now available from core.fractal
    phi_xor,
    phi_nand,
)


def tensor(v):
    """Create a T7Tensor from a vector."""
    return T7Tensor(v)


def info():
    """Display CMFO package information."""
    print(f"CMFO Fractal Engine v{__version__}")
    print(f"Author: {__author__}")
    print("-" * 50)
    print("Status: PRODUCTION READY + FRACTAL CORE")
    print("Core: 7D φ-Manifold + Geometric Collapse")
    print("Algebra: Fractal operations (⊕_φ, ⊗_φ, ℛ_φ)")
    print("Logic: Geometric operators (∧_φ, ∨_φ, ¬_φ)")
    print("Physics: Compton mass, Fractal Time")
    print("-" * 50)
    print("Documentation: https://github.com/1JONMONTERV/CMFO-COMPUTACION-FRACTAL-")
    print("For commercial licensing: jmvlavacar@hotmail.com")


__all__ = [
    # Version info
    "__version__",
    "__author__",
    # Constants
    "PHI",
    "PHI_INV",
    "HBAR",
    "C",
    "G",
    "ALPHA",
    "M_PLANCK",
    # Algebra
    "fractal_product",
    "fractal_add",
    "fractal_root",
    "fractal_multiply", # New
    "iterated_fractal_root",
    # Logic (new)
    "TRUE",
    "FALSE",
    "NEUTRAL",
    "f_not",
    "f_and",
    "f_or",
    "f_xor",
    # Fractal Core (New)
    "PhiBit",
    "phi_decision",
    "geometric_state_collapse",
    # Physics
    "geometric_mass",
    "compton_wavelength",
    # Legacy core
    "T7Tensor",
    "T7Matrix",
    "tensor",
    "gamma_step",
    # Legacy logic
    "phi_sign",
    "phi_and",
    "phi_or",
    "phi_not",
    "phi_xor",
    "phi_nand",
    # Utilities
    "info",
    "verify",
]


# Verification
from .verify import run as verify

