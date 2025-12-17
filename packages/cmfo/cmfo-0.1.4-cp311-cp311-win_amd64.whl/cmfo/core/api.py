import numpy as np

PHI = (1 + 5 ** 0.5) / 2


def tensor7(a, b):
    a = np.asarray(a)
    b = np.asarray(b)
    # The formula provided in the audit: (a * b + PHI) / (1 + PHI)
    return (a * b + PHI) / (1 + PHI)
