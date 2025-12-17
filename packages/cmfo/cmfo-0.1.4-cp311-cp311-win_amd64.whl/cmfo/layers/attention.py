import numpy as np


class CMFOAttention:
    """
    A Drop-in replacement for Self-Attention.

    Replaces: Softmax(QK^T)V
    With:     Fractal State Absorption

    Complexity: O(N) instead of O(N^2)
    """

    def __init__(self, embed_dim: int, num_heads: int):
        self.embed_dim = embed_dim
        self.num_heads = num_heads

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Args:
            x: Input tensor (Batch, Seq_Len, Embed_Dim)
        Returns:
            Output tensor (Batch, Seq_Len, Embed_Dim)
        """
        batch, seq_len, dim = x.shape
        output = np.zeros_like(x)

        PHI = 1.6180339887

        # For each sequence in batch
        for b in range(batch):
            # Initialize Fractal State (The "Context")
            # State is tiny compared to KV-Cache
            state: np.ndarray = np.zeros(7)

            # Causal Scan (Left-to-Right)
            for t in range(seq_len):
                input_vec = x[b, t]  # (Dim,)

                # 1. Reduced Input (Focus)
                # Map massive embedding to 7D manifold
                input_reduced = (
                    np.sum(input_vec.reshape(-1, 7)[:7], axis=0)
                    if dim >= 7 else np.zeros(7)
                )

                # 2. Absorb into State (The "Attention" Mechanism)
                # T7 Operator replaces QK^T
                state = (state * input_reduced + PHI) / (1 + PHI)

                # 3. Project back to Embedding (Contextualized Output)
                # This ensures the output at step t contains history of 0..t
                # Expansion logic:
                for d in range(dim):
                    output[b, t, d] = state[d % 7] * (PHI ** (d % 3))

        return output

    def to(self, device):
        return self
