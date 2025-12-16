# -*- coding: utf-8 -*-
"""
SNF Library Functions for GeneCast.

This module implements the core functions of the Similarity Network Fusion (SNF) algorithm,
which integrates multiple data types into a unified similarity network.

The original SNF algorithm was introduced in:
Wang B, Mezlini AM, Demir F, et al. Similarity network fusion for aggregating data types on a genomic scale.
Nat Methods. 2014;11(3):333-337. doi:10.1038/nmeth.2810

The original implementation is in R, we translated and adapted it to Python here.
And transplanted it on cosine distance metric which is more suitable for genomic data.
Moreover, we added multi-scale fusion and final normalization steps.
None of the code here is directly copied from the original R implementation.
Adapted and extended for GeneCast by the Genecast Team.

"""


import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_distances


# ==========================================
# 1. Core SNF Library Functions
# ==========================================


def calculate_W(data, K=20, mu=0.5, is_distance_matrix=False):
    """
    Constructs the similarity matrix W using the scaled exponential kernel.

    This is a critical step in SNF where raw data or distances are converted into
    a similarity measure between samples.

    Args:
        data (np.ndarray): A (n_samples, n_features) data matrix or
                           a (n_samples, n_samples) precomputed distance matrix.
        K (int): The number of nearest neighbors for local scaling.
                 This defines the local neighborhood for each sample.
        mu (float): A hyperparameter to adjust the kernel width. Usually between 0.3-0.8.
        is_distance_matrix (bool): Set to True if input `data` is already a distance matrix.

    Returns:
        np.ndarray: The (n_samples, n_samples) similarity matrix W.
    """
    # 1. Get distance matrix.
    if is_distance_matrix:
        dist_matrix = data
    else:
        # Cosine distance is commonly used in bioinformatics.
        # Note: scikit-learn's cosine_distances returns values in [0, 2].
        dist_matrix = cosine_distances(data)

    n_samples = dist_matrix.shape[0]

    # 2. Find K nearest neighbors for each sample.
    # `np.argsort` sorts each row in ascending order and returns indices.
    sorted_indices = np.argsort(dist_matrix, axis=1)

    # 3. Calculate local scaling factor epsilon.
    # This factor adapts the kernel width to local data density.
    # We take distances to K nearest neighbors (excluding the sample itself).
    knn_dist = np.take_along_axis(dist_matrix, sorted_indices[:, 1 : K + 1], axis=1)
    mean_dist_K = np.mean(knn_dist, axis=1)

    # Scaling factor epsilon_ij is defined as:
    # (mean_dist_i + mean_dist_j + dist_ij) / 3
    # This can be computed efficiently via NumPy broadcasting.
    combined_mean = mean_dist_K[:, np.newaxis] + mean_dist_K[np.newaxis, :]
    Epsilon = (combined_mean + dist_matrix) / 3

    # Avoid division by zero.
    Epsilon[Epsilon == 0] = 1e-10

    # 4. Calculate similarity matrix W using scaled exponential similarity kernel.
    # W_ij = exp(-dist_ij^2 / (mu * epsilon_ij))
    W = np.exp(-(dist_matrix**2) / (mu * Epsilon))

    # 5. Set diagonal to 1, representing maximal self-similarity.
    np.fill_diagonal(W, 1.0)

    return W


def normalize_P(W):
    """
    Calculates the normalized status matrix P from similarity matrix W.

    This matrix represents the global transition probabilities between samples.

    Args:
        W (np.ndarray): A (n_samples, n_samples) similarity matrix.

    Returns:
        np.ndarray: Normalized status matrix P.
    """
    n = W.shape[0]
    P = W.copy()

    # Set diagonal to 0 to exclude self-similarity when calculating row sums.
    np.fill_diagonal(P, 0)

    # Calculate row sums.
    row_sums = np.sum(P, axis=1)
    # Avoid division by zero for isolated nodes.
    row_sums[row_sums == 0] = 1.0

    # Normalize off-diagonal elements: P(i,j) = W(i,j) / (2 * sum_{k!=i} W(i,k))
    P = P / (2 * row_sums[:, np.newaxis])

    # Diagonal is forced to 0.5 to retain half the information at each node.
    np.fill_diagonal(P, 0.5)

    return P

def calculate_S(W, K=20):
    """
    Calculates the local similarity matrix S.

    This matrix captures the strongest local connections by retaining links
    only to the K nearest neighbors.

    Args:
        W (np.ndarray): A (n_samples, n_samples) similarity matrix.
        K (int): The number of nearest neighbors to retain.

    Returns:
        np.ndarray: Sparse, row-normalized local similarity matrix S.
    """
    n = W.shape[0]
    S = np.zeros_like(W)

    # Sort in descending order to find the most similar neighbors.
    sorted_indices = np.argsort(-W, axis=1)

    # For each sample, keep only the top K strongest similarities.
    for i in range(n):
        neighbor_indices = sorted_indices[i, 0:K]
        S[i, neighbor_indices] = W[i, neighbor_indices]

    # Row-normalize the matrix to represent transition probabilities.
    row_sums = np.sum(S, axis=1)
    row_sums[row_sums == 0] = 1.0
    S = S / row_sums[:, np.newaxis]

    return S


def snf_fusion(list_of_W, K=20, t=20, alpha=0.9):
    """
    Executes the main Similarity Network Fusion iterative process.

    This function fuses multiple similarity matrices into a single, comprehensive network,
    capturing both shared and complementary information.

    Args:
        list_of_W (list): List of similarity matrices [W1, W2, ...], one for each data type.
        K (int): Number of nearest neighbors for local similarity (S matrix).
        t (int): Number of iterations for the fusion process.

    Returns:
        np.ndarray: The final fused similarity matrix.
    """
    num_views = len(list_of_W)

    # Initialize status matrix (P) and local similarity matrix (S) for each view.
    P = [normalize_P(W) for W in list_of_W]
    S = [calculate_S(W, K) for W in list_of_W]

    P_init = P.copy()  # Keep initial P for reference (not used in fusion).

    # Iteratively update status matrices.
    for iteration in range(t):
        P_next = []
        for v in range(num_views):
            # Calculate average status matrix from all *other* views.
            other_Ps = [P[k] for k in range(num_views) if k != v]
            avg_P_others = np.mean(other_Ps, axis=0)

            # Core diffusion step:
            # Use current view's local structure (S[v]) to propagate
            # information from other views (avg_P_others).
            # Formula: P_next = S[v] * avg_P_others * S[v]^T
            next_p = np.dot(np.dot(S[v], avg_P_others), S[v].T)

            # diffusion = np.dot(np.dot(S[v], avg_P_others), S[v].T)
            # next_p = alpha * diffusion + (1 - alpha) * P_init[v]  # Weighted factor controlling influence.

            # Normalize to maintain numerical stability.
            P_next.append(normalize_P(next_p))

        P = P_next  # Update status matrices for next iteration.

    # Final fused network is the average of status matrices after t iterations.
    final_W = np.mean(P, axis=0)

    return final_W


def normalize_network_final(W):
    """
    Performs final normalization on the fused network.

    This includes:
    1. Temporarily removing the diagonal.
    2. Linearly scaling off-diagonal elements to [0, 1] range.
    3. Restoring the diagonal to 1.0.

    This makes the network more suitable for clustering and visualization.

    Args:
        W (np.ndarray): The fused similarity matrix.

    Returns:
        np.ndarray: Normalized final matrix.
    """
    # 1. Create a copy to avoid modifying original data.
    W_norm = W.copy()

    # 2. Temporarily remove diagonal, setting it to 0.
    # The diagonal (self-similarity) is usually 1.0 or very high, and if not removed,
    # it would dominate the min-max scaling.
    np.fill_diagonal(W_norm, 0)

    # 3. Calculate min and max of off-diagonal elements.
    min_val = np.min(W_norm)
    max_val = np.max(W_norm)
    mean_val = np.mean(W_norm)
    print(f"Before normalization: min={min_val}, max={max_val}, mean={mean_val}")

    # 4. Perform min-max scaling to stretch values to [0, 1] range.
    # This enhances contrast and ensures strongest inter-sample connections become 1.0.
    if max_val - min_val > 1e-10:
        W_norm = (W_norm - min_val) / (max_val - min_val)

    print(
        f"After normalization: min={np.min(W_norm)}, max={np.max(W_norm)}, mean={np.mean(W_norm)}"
    )

    # 5. Restore diagonal to 1.0.
    # In a similarity matrix, sample similarity to itself should be maximal.
    np.fill_diagonal(W_norm, 1.0)

    return W_norm


def run_multiscale_snf(dist_views, K_list, t=20):
    """Runs SNF at multiple scales (K values) and averages the results.

    This makes the fusion more robust to the choice of hyperparameter K.

    Args:
        dist_views (list): List of precomputed distance matrices.
        K_list (list): List of K values to use (e.g., [10, 20, 40]).
        t (int): Number of fusion iterations.

    Returns:
        np.ndarray: Final, normalized, multi-scale fused matrix.
    """
    print(f"[Algorithm] Using K={K_list} running multiscale SNF...")
    fused_matrices = []

    for k in K_list:
        # 1. Calculate similarity matrices for all views for current k.
        current_Ws = [calculate_W(d, K=k, is_distance_matrix=True) for d in dist_views]
        # 2. Run fusion process at this scale.
        W_fused_k = snf_fusion(current_Ws, K=k, t=t)
        fused_matrices.append(W_fused_k)

    # 3. Average fused matrices from all scales and perform final normalization.
    W_final_raw = np.mean(fused_matrices, axis=0)
    W_final = normalize_network_final(W_final_raw)

    return W_final



# ==========================================
# Main Execution Block
# ==========================================


def main(dist_matrices, output_file, K_values, t_iter):
    """Main execution logic."""
    # --- 1. Load Data ---
    print("--- Step 1: Loading Data ---")
    try:
        dist_views = [np.loadtxt(path, delimiter=",") for path in dist_matrices]
    except FileNotFoundError as e:
        print(f"Error: Input file not found - {e}")
        return
    except Exception as e:
        print(f"Error loading distance matrices: {e}")
        return

    # --- 2. Run Multi-scale SNF Algorithm ---
    print("\n--- Step 2: Running Algorithm ---")
    W_fused = run_multiscale_snf(dist_views, K_list=K_values, t=t_iter)

    # --- 3. Save Results ---
    np.savetxt(output_file, W_fused, delimiter=",")
    print(f"\n[Complete] Fused matrix saved to '{output_file}'")