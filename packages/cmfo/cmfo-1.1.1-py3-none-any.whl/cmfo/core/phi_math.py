import numpy as np

PHI = (1 + 5 ** 0.5) / 2


def phi_pow(x):
    return PHI ** x


def phi_norm(v):
    v = np.array(v, dtype=float)
    return np.linalg.norm(v)
