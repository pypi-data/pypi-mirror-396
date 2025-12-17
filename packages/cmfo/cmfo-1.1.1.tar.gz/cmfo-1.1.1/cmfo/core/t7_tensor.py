# =====================================================================
# CMFO-COMPUTE - AVISO DE LICENCIA
# Uso académico y personal permitido bajo Apache 2.0.
# El uso comercial, corporativo o gubernamental requiere licencia CMFO.
# Contacto comercial:
#   Jonnathan Montero – San José, Costa Rica
#   jmvlavacar@hotmail.com
# =====================================================================
import numpy as np
from .gamma_phi import gamma_step


class T7Tensor:
    def __init__(self, v):
        self.v = np.array(v, dtype=float)

    def evolve(self, steps=1):
        v = self.v
        for _ in range(steps):
            v = gamma_step(v)
        return T7Tensor(v)

    def norm(self):
        return float(np.linalg.norm(self.v))

    def __repr__(self):
        return f"T7Tensor({self.v})"
