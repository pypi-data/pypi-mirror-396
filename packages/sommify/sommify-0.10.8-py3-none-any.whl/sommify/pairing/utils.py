import numpy as np

# We keep the imports, but ensure 'wang_hash_noise' in your .hash module
# is NOT decorated with @njit if you want to pass numpy arrays to it,
# or ensure it can handle vector/matrix inputs.
from .hash import compute_vector_signatures, wang_hash_noise


def generate_utility_matrix(
    dish_emb: np.ndarray,
    wine_emb: np.ndarray,
    noise_scale: float,
    dish_countries: list[str | None] | None = None,
    wine_countries: list[str | None] | None = None,
    geo_boost_factor: float = 0.05,
) -> np.ndarray:
    """
    Pure NumPy implementation of the utility matrix generation with geographical boost.

    Args:
        dish_emb: Dish embeddings (N, d)
        wine_emb: Wine embeddings (M, d)
        noise_scale: Scale factor for deterministic noise
        dish_countries: Array of country codes for dishes (N,) - optional
        wine_countries: Array of country codes for wines (M,) - optional
        geo_boost_factor: Multiplicative boost when countries match (default: 0.05)
    """

    # convert country codes to numpy arrays
    if dish_countries is not None:
        dish_countries = np.array(dish_countries)
    if wine_countries is not None:
        wine_countries = np.array(wine_countries)

    # 1. Normalize Embeddings
    d_norm = np.linalg.norm(dish_emb, axis=1, keepdims=True)
    dish_emb = dish_emb / np.maximum(d_norm, 1e-9)

    w_norm = np.linalg.norm(wine_emb, axis=1, keepdims=True)
    wine_emb = wine_emb / np.maximum(w_norm, 1e-9)

    # 2. Compute Cosine Similarity (Vectorized)
    base_utility = dish_emb @ wine_emb.T

    # 3. Deterministic Noise Addition
    dish_sigs = compute_vector_signatures(dish_emb)
    wine_sigs = compute_vector_signatures(wine_emb)
    combined_seeds = np.bitwise_xor(dish_sigs[:, None], wine_sigs[None, :])
    noise_matrix = wang_hash_noise(combined_seeds) * noise_scale

    # 4. Combine base utility and noise
    utility_with_noise = base_utility + noise_matrix

    # 5. Apply geographical boost (multiplicative)
    if dish_countries is not None and wine_countries is not None:
        # Create geographical match matrix: 1 where countries match, 0 otherwise
        geo_matrix = (
            dish_countries[:, np.newaxis] == wine_countries[np.newaxis, :]
        ).astype(float)

        # Apply multiplicative boost: utility * (1 + boost_factor * match)
        utility_with_noise = utility_with_noise * (1 + geo_boost_factor * geo_matrix)

    return utility_with_noise


def generate_recommendation_matrix(
    utility_matrix: np.ndarray,
    constraint_matrix: np.ndarray,
    top_k_pct: float = 0.25,
    min_k: int = 2,
    threshold: float = 0.0,
) -> np.ndarray:
    """
    Generates a recommendation matrix (Nd x Nw) with 0s and 1s based on
    similarity scores and group-wise constraints.
    (This function was already pure NumPy, so it remains largely unchanged).
    """
    Nd, Nw = utility_matrix.shape

    # 1. Determine the number of groups and the group index for each wine
    wine_groups = np.argmax(constraint_matrix, axis=1)
    Nc = constraint_matrix.shape[1]

    # 2. Initialize the result matrix
    recommendation_matrix = np.zeros((Nd, Nw), dtype=int)

    # 3. Iterate through each constraint group
    for c in range(Nc):
        # Find the indices of wines belonging to the current group 'c'
        group_wine_indices = np.where(wine_groups == c)[0]
        group_size = len(group_wine_indices)

        if group_size == 0:
            continue

        # 4. Calculate the required 'top k' count for this group
        k_pct = int(np.ceil(group_size * top_k_pct))
        k = max(min_k, k_pct)
        k = min(k, group_size)

        # 5. Determine the top 'k' wines in the group for *each* dish

        # Extract utility scores for this group
        group_utility = utility_matrix[:, group_wine_indices]  # Nd x group_size

        # Find indices that sort utility descending
        # np.argsort sorts ascending, so we sort -group_utility
        sorted_indices = np.argsort(-group_utility, axis=1)

        # Get top k indices (local to the group subset)
        top_k_local_indices = sorted_indices[:, :k]

        # Create a boolean mask for top k items
        group_top_k_mask = np.zeros_like(group_utility, dtype=bool)

        # Advanced indexing to set True for top k items
        rows = np.arange(Nd)[:, None]  # Shape (Nd, 1) for broadcasting
        group_top_k_mask[rows, top_k_local_indices] = True

        # 6. Apply the recommendation logic
        is_above_threshold = group_utility > threshold
        group_recommendations = np.logical_and(group_top_k_mask, is_above_threshold)

        # 7. Map back to full matrix
        recommendation_matrix[:, group_wine_indices] = group_recommendations.astype(int)

    return recommendation_matrix
