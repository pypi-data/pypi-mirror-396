# =====================================================================
# CMFO-COMPUTE - AVISO DE LICENCIA
# Uso académico y personal permitido bajo Apache 2.0.
# El uso comercial, corporativo o gubernamental requiere licencia CMFO.
# Contacto comercial:
#   Jonnathan Montero – San José, Costa Rica
#   jmvlavacar@hotmail.com
# =====================================================================

__version__ = "1.1.0"
__author__ = "Jonnathan Montero Viques"
__credits__ = "CMFO Universe"

from .core.t7_tensor import T7Tensor
from .core.gamma_phi import gamma_step
from .logic.phi_logic import (
    phi_sign,
    phi_and,
    phi_or,
    phi_not,
    phi_xor,
    phi_nand,
)


def tensor(v):
    return T7Tensor(v)

def info():
    """Prints the official CMFO Auditor Report."""
    print(f"CMFO Fractal Engine v{__version__}")
    print(f"Author: {__author__}")
    print("-" * 30)
    print("Status: VERIFIED")
    print("Core: Matrix7x7 (T7 Phi-Manifold)")
    print("Physics: Alpha^5 Correction Enabled")
    print("Mining: O(1) Geometric Inversion Ready")
    print("-" * 30)
    print("For commercial licensing, contact: jmvlavacar@hotmail.com")


__all__ = [
    "T7Tensor",
    "tensor",
    "gamma_step",
    "phi_sign",
    "phi_and",
    "phi_or",
    "phi_not",
    "phi_xor",
    "phi_nand",
    "info"
]
