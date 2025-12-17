import numpy as np

PHI = (1 + 5 ** 0.5) / 2


def text_to_tensor(text: str) -> np.ndarray:
    """
    Converts a string into a fractal tensor state (7D vector).

    This is a deterministic mapping where each character influences
    the geometric state via recursive phase shifting.

    Args:
        text (str): Input string.

    Returns:
        np.ndarray: A 7-element vector representing the text's
                    semantic geometry.
    """
    # Initialize the state vector (Concept of "Silence")
    state: np.ndarray = np.zeros(7, dtype=float)

    # Iterate through characters and absorb them into the state
    for i, char in enumerate(text):
        # 1. Map char to a scalar frequency
        # Normalizing ASCII/Unicode to a reasonable range [0, 1]
        val = (ord(char) % 255) / 255.0

        # 2. Geometric Injection
        # We affect the dimension corresponding to (index % 7)
        # But we also diffuse energy across all dimensions using PHI
        dim_idx = i % 7

        # Resonance Update Rule:
        # New state is a function of old state + new signal, rotated by PHI
        state[dim_idx] += val

        # Global Diffusion (Fractal Mixing)
        # This ensures that "A B" is different from "B A" due to order
        # dependency
        # Damping factor to prevent explosion
        state = (state + PHI) / (1 + PHI * 0.1)

        # Normalize to keep within unit hypersphere approximate
        norm = np.linalg.norm(state)
        if norm > 0:
            state = state / norm

    return state


def encode_sequence(text: str) -> list:
    """
    Encodes text into a sequence of tensors (one per character/token).
    Useful for visualization.
    """
    sequence = []
    state: np.ndarray = np.zeros(7, dtype=float)

    for i, char in enumerate(text):
        val = (ord(char) % 255) / 255.0
        dim_idx = i % 7
        state[dim_idx] += val
        state = (state + PHI) / (1 + PHI * 0.1)

        norm = np.linalg.norm(state)
        if norm > 0:
            state = state / norm

        sequence.append(state.copy())

    return sequence
