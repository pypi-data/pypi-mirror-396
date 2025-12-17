# =====================================================================
# CMFO-COMPUTE - AVISO DE LICENCIA
# Uso académico y personal permitido bajo Apache 2.0.
# El uso comercial, corporativo o gubernamental requiere licencia CMFO.
# Contacto comercial:
#   Jonnathan Montero – San José, Costa Rica
#   jmvlavacar@hotmail.com
# =====================================================================
import numpy as np


def gamma_step(v):
    v = np.array(v, dtype=float)
    return np.sin(v)
