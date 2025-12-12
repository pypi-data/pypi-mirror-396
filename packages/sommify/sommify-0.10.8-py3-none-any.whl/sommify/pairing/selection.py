import numpy as np
from numba import njit, prange

from .utils import generate_utility_matrix


@njit(fastmath=True, parallel=True)
def calc_utility_gains_incremental(
    U: np.ndarray,  # (n_recipes, n_wines)
    current_top_vals: np.ndarray,  # (n_recipes, top_k) - The current best scores per recipe
    weights: np.ndarray,  # (top_k,)
    candidates: np.ndarray,  # array of wine indices to evaluate
) -> np.ndarray:
    """
    Calculates utility gain only for valid candidates against the current
    state of top-k values per recipe.
    """
    n_candidates = len(candidates)
    n_recipes, k = current_top_vals.shape
    gains = np.zeros(n_candidates, dtype=np.float32)

    # Pre-calculate current utility for all recipes to compute deltas
    # (This is O(n_recipes * k), negligible compared to the loop)
    current_recipe_utils = np.zeros(n_recipes, dtype=np.float32)
    for r in range(n_recipes):
        for x in range(k):
            current_recipe_utils[r] += current_top_vals[r, x] * weights[x]

    for idx in prange(n_candidates):
        wine_idx = candidates[idx]
        total_gain = 0.0

        for r in range(n_recipes):
            u_val = U[r, wine_idx]

            # Optimization: If u_val is smaller than the worst of the current top_k,
            # it cannot possibly improve the score (assuming positive weights).
            if u_val <= current_top_vals[r, k - 1]:
                continue

            # Simulation: Insert u_val into the sorted current_top_vals
            # We don't allocate new arrays; we just do the math on registers
            new_recipe_util = 0.0
            inserted = False

            # Iterate through rank weights
            # This effectively performs an insertion sort + dot product in one pass
            ranks_filled = 0

            for i in range(k):
                val_at_rank = current_top_vals[r, i]

                if not inserted and u_val > val_at_rank:
                    # Our new wine takes this rank
                    new_recipe_util += u_val * weights[i]
                    inserted = True
                    ranks_filled += 1
                    if ranks_filled == k:
                        break

                    # The displaced value bumps down to the next weight
                    new_recipe_util += val_at_rank * weights[ranks_filled]
                    ranks_filled += 1
                else:
                    new_recipe_util += val_at_rank * weights[ranks_filled]
                    ranks_filled += 1

                if ranks_filled == k:
                    break

            total_gain += new_recipe_util - current_recipe_utils[r]

        gains[idx] = total_gain

    return gains


def greedy_select_topk_weighted(
    dish_embeddings: np.ndarray,  # Replaces U
    wine_embeddings: np.ndarray,  # Renamed from W_E
    C: np.ndarray,
    caps: list[int],
    noise_scale: float = 0.05,  # New Param
    max_card_size: int = 999,
    top_k: int = 3,
    lambda_div: float = 0.3,
    verbose: bool = False,
    weights: np.ndarray | None = None,
    precomputed_utility_matrix: np.ndarray | None = None,
) -> tuple[list[int], float, dict]:
    # --- 1. Pre-Processing & Utility Generation ---
    dish_np = np.ascontiguousarray(dish_embeddings)
    wine_np = np.ascontiguousarray(wine_embeddings)

    # Normalize embeddings once here (Crucial for Cosine Sim)
    dish_norm = dish_np / np.maximum(
        np.linalg.norm(dish_np, axis=1, keepdims=True), 1e-9
    )
    wine_norm = wine_np / np.maximum(
        np.linalg.norm(wine_np, axis=1, keepdims=True), 1e-9
    )

    if verbose:
        print("Generating deterministic utility matrix...")

    # Generate U matrix with fused dot product + deterministic noise
    U = (
        precomputed_utility_matrix
        if precomputed_utility_matrix is not None
        else generate_utility_matrix(dish_norm, wine_norm, noise_scale)
    )

    # --- 2. Standard Setup (Same as before) ---
    n_recipes, n_wines = U.shape
    n_constraints = C.shape[1]

    if weights is None:
        weights = np.array([0.6**i for i in range(top_k)], dtype=np.float32)
        weights[0] = 1.0

    selected = []
    current_counts = np.zeros(n_constraints, dtype=np.int32)
    current_top_vals = np.zeros((n_recipes, top_k), dtype=np.float32)

    # Diversity tracking
    # Note: We use the NORMALIZED wine embeddings for diversity cos-sim
    group_vectors_sum = np.zeros((n_constraints, wine_np.shape[1]), dtype=np.float32)
    group_counts = np.zeros(n_constraints, dtype=np.int32)
    wine_to_groups = [np.where(row == 1)[0] for row in C]

    # --- 3. Main Greedy Loop ---
    while len(selected) < max_card_size and len(selected) < sum(caps):
        # A. Filter Candidates
        is_candidate = np.ones(n_wines, dtype=bool)
        is_candidate[selected] = False

        for g_idx in range(n_constraints):
            if current_counts[g_idx] >= caps[g_idx]:
                wines_in_group = C[:, g_idx] == 1
                is_candidate[wines_in_group] = False

        candidate_indices = np.where(is_candidate)[0]
        if len(candidate_indices) == 0:
            break

        # B. Utility Gains (Incremental)
        util_gains = calc_utility_gains_incremental(
            U, current_top_vals, weights, candidate_indices
        )

        full_util_gains = np.zeros(n_wines)
        full_util_gains[candidate_indices] = util_gains

        # C. Diversity Gains (Vectorized)
        full_div_gains = np.zeros(n_wines)
        for g in range(n_constraints):
            wines_in_this_group = np.where((C[:, g] == 1) & is_candidate)[0]
            if len(wines_in_this_group) == 0:
                continue

            if group_counts[g] == 0:
                full_div_gains[wines_in_this_group] += 1.0
            else:
                centroid = group_vectors_sum[g] / group_counts[g]
                centroid = centroid / np.maximum(np.linalg.norm(centroid), 1e-9)
                sims = wine_norm[wines_in_this_group] @ centroid
                full_div_gains[wines_in_this_group] += 1.0 - sims

        # D. Combine & Select
        u_max = full_util_gains.max()
        d_max = full_div_gains.max()

        scores = (1 - lambda_div) * (
            full_util_gains / u_max if u_max > 0 else 0
        ) + lambda_div * (full_div_gains / d_max if d_max > 0 else 0)

        best_idx_local = np.argmax(scores[candidate_indices])
        best_wine = candidate_indices[best_idx_local]

        selected.append(best_wine)

        # E. Update State
        groups = wine_to_groups[best_wine]
        current_counts[groups] += 1

        vec = wine_norm[best_wine]
        for g in groups:
            group_vectors_sum[g] += vec
            group_counts[g] += 1

        for r in range(n_recipes):
            val = U[r, best_wine]
            if val > current_top_vals[r, -1]:
                # Optimized insertion for small k
                row = current_top_vals[r]
                # Insert val into sorted row
                for k_i in range(top_k):
                    if val > row[k_i]:
                        # Shift remaining
                        row[k_i + 1 :] = row[k_i:-1]
                        row[k_i] = val
                        break

    return selected
