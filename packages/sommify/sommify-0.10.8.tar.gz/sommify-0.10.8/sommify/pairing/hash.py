import numpy as np


def wang_hash_noise(seed) -> np.ndarray:
    """
    Vectorized Wang Hash.
    Returns deterministic floats between -1.0 and 1.0 based on inputs.

    Accepts: int or np.ndarray (of any shape)
    Returns: np.ndarray (of float64) with same shape
    """
    # 1. Force the seed into uint32.
    # This is crucial: Python integers have arbitrary precision, but this hash
    # relies on 32-bit integer overflow/wrapping behavior to work correctly.
    # np.array(...) handles both scalar inputs and array inputs.
    seed = np.array(seed, dtype=np.uint32)

    # 2. Perform the hash steps using NumPy bitwise operators
    # We use explicit casts to uint32 in the shifts to ensure consistency
    seed = seed ^ np.uint32(61)
    seed = seed ^ (seed >> np.uint32(16))
    seed = seed * np.uint32(9)
    seed = seed ^ (seed >> np.uint32(4))
    seed = seed * np.uint32(0x27D4EB2D)
    seed = seed ^ (seed >> np.uint32(15))

    # 3. Map uint32 range [0, 2^32-1] to float range [-1.0, 1.0]
    return (seed / 4294967296.0) * 2.0 - 1.0


def compute_vector_signatures(embeddings: np.ndarray) -> np.ndarray:
    """
    Creates a unique integer signature for each row in the embedding matrix.
    Vectorized for performance by iterating over dimensions instead of rows.
    """
    n_items, n_dim = embeddings.shape

    # Initialize signatures for all items to 0
    signatures = np.zeros(n_items, dtype=np.int64)

    # Pre-scale and cast the entire matrix at once.
    # This replaces: int(val * 1234567.0)
    scaled_matrix = (embeddings * 1234567.0).astype(np.int64)

    # Loop over dimensions (columns).
    # Since n_dim (e.g., 512) is much smaller than n_items (e.g., 10,000),
    # a Python loop here is perfectly fine.
    # We update the signature for ALL items simultaneously for each dimension.
    for d in range(n_dim):
        col_vals = scaled_matrix[:, d]

        # Apply the mixing step: h = (h * 31) ^ int_val
        signatures = (signatures * 31) ^ col_vals

    return signatures
