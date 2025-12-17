import numpy as np
import sys
from typing import Optional


def plot_tensor_ascii(tensor: np.ndarray, label: Optional[str] = None):
    """
    Prints an ASCII bar chart of a 7D tensor to stdout.
    """
    if label:
        print(f"\n--- {label} ---")
    else:
        print("\n--- Tensor Visualizer ---")

    dims = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]

    for i, val in enumerate(tensor):
        # Normalize for display: assume val is typically [-1, 1] or [0, 1]
        # We clamp to 0-1 for bar length
        bar_val = max(0.0, min(1.0, abs(val)))

        # Create bar
        # Length 20 chars
        bar_len = int(bar_val * 40)
        bar_str = "#" * bar_len

        # Color coding (conceptual via spaces)
        # T1..T7
        print(f"{dims[i]} | {val:+.4f} | {bar_str}")


def plot_attractor_trajectory(sequence: list):
    """
    Simulates a 2D trace of the 7D attractor.
    Projects first 2 dimensions.
    """
    print("\n--- Attractor Trajectory (2D Projection) ---")
    print("Start >", end="")
    for vec in sequence:
        # Simple ascii sparkline-ish trace based on dominant dim
        dom_dim = np.argmax(vec)
        if dom_dim == 0:
            sys.stdout.write("-")
        elif dom_dim == 1:
            sys.stdout.write("/")
        elif dom_dim == 2:
            sys.stdout.write("|")
        elif dom_dim == 3:
            sys.stdout.write("\\")
        elif dom_dim == 4:
            sys.stdout.write("_")
        elif dom_dim == 5:
            sys.stdout.write("^")
        elif dom_dim == 6:
            sys.stdout.write("*")
    print("< End")
