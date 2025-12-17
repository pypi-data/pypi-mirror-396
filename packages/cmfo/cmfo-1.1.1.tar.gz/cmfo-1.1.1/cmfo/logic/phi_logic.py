import numpy as np

# =====================================================================
# CMFO-COMPUTE - AVISO DE LICENCIA
# Uso académico y personal permitido bajo Apache 2.0.
# El uso comercial, corporativo o gubernamental requiere licencia CMFO.
# Contacto comercial:
#   Jonnathan Montero – San José, Costa Rica
#   jmvlavacar@hotmail.com
# =====================================================================


def phi_sign(x):
    x = float(np.array(x).mean())
    return 1.0 if x >= 0 else -1.0


def phi_and(a, b):
    return min(phi_sign(a), phi_sign(b))


def phi_or(a, b):
    return phi_sign(a) if phi_sign(a) == 1 else phi_sign(b)


def phi_not(a):
    return -phi_sign(a)


def phi_xor(a, b):
    return 1.0 if phi_sign(a) != phi_sign(b) else -1.0


def phi_nand(a, b):
    return -phi_and(a, b)
