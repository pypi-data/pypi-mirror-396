#!/usr/bin/env python3
"""
Ward + Auto-k Pipeline [SNF Compatible & Benchmark Optional]
Fixed Version: Added mandatory correction for tiny negative values in Ward clustering results (Z-Matrix Correction).

Features:
1. Benchmark Decoupling: Input files no longer strictly require a ground truth column.
2. Compatibility: Supports SNF similarity matrix input (--is-similarity).
3. Robustness: Force correction of negative height issues caused by floating-point precision.

Dependencies:
- Python: numpy, pandas, scipy, sklearn
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple, Sequence, Optional
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage, to_tree
from scipy.sparse.linalg import eigsh
from sklearn import metrics


# ==========================================
# PART 1: Basic Data Processing
# ==========================================


def condensed_from_square(dist: np.ndarray) -> np.ndarray:
    n = dist.shape[0]
    iu = np.triu_indices(n, k=1)
    return dist[iu]


def load_labels(path: Path) -> tuple[list[str], Optional[list[str]]]:
    """
    Loads labels.
    If no ground truth column is found, returns None, and script runs in 'Discovery Mode' instead of 'Benchmark Mode'.
    """
    df = pd.read_csv(path)
    if "label" not in df.columns:
        raise ValueError(f"'label' column not found in {path}")

    class_col = None
    for c in [
        "gene",
        "family",
        "gene4",
        "label_class",
        "class",
        "true",
        "ground_truth",
    ]:
        if c in df.columns:
            class_col = c
            break

    if class_col is None:
        print(
            "Notice: No ground truth column found. Running in Discovery Mode (no metrics)."
        )
        return df["label"].tolist(), None
    else:
        print(
            f"Notice: Ground truth column '{class_col}' found. Running in Benchmark Mode."
        )
        return df["label"].tolist(), df[class_col].tolist()


def load_matrix(path: Path) -> np.ndarray:
    try:
        mat = pd.read_csv(path, header=None).values.astype(float)
    except ValueError as e:
        raise ValueError(f"Failed to read matrix, please check if file contains non-numeric characters: {e}")

    if mat.shape[0] != mat.shape[1]:
        raise ValueError(f"Input matrix must be square; got {mat.shape}")

    # Check and handle NaN (Very important!)
    if np.isnan(mat).any():
        print(f"Warning: NaNs detected in {path.name}. Replacing with 0.0.")
        np.nan_to_num(mat, copy=False, nan=0.0)

    # Ensure symmetry
    mat = (mat + mat.T) / 2.0
    # Prevent tiny negative numbers in input itself
    mat[mat < 0] = 0.0

    return mat


def linkage_to_newick(node, labels: Sequence[str]) -> str:
    if node.is_leaf():
        lbl = str(labels[node.id])
        # Sanitize label for Newick format
        lbl = lbl.replace(":", "_").replace(";", "_").replace(",", "_").replace("(", "_").replace(")", "_")
        return lbl
    left = linkage_to_newick(node.get_left(), labels)
    right = linkage_to_newick(node.get_right(), labels)
    return (
        f"({left}:{node.dist - node.get_left().dist:.6f},"
        f"{right}:{node.dist - node.get_right().dist:.6f})"
    )


# ==========================================
# PART 2: Outlier Detection
# ==========================================


def outlier_scores_knn(dist: np.ndarray, k: int = 10) -> np.ndarray:
    scores = []
    for i in range(dist.shape[0]):
        row = np.sort(dist[i])
        knn = row[1 : min(k + 1, len(row))]
        scores.append(knn.mean() if len(knn) else 0.0)
    return np.array(scores)


def split_core_outliers(
    scores: np.ndarray, iqr_mult: float = 1.5
) -> Tuple[np.ndarray, np.ndarray]:
    q1, q3 = np.quantile(scores, [0.25, 0.75])
    iqr = q3 - q1
    T = q3 + iqr_mult * iqr
    out_idx = np.where(scores > T)[0]
    core_idx = np.array(
        [i for i in range(len(scores)) if i not in set(out_idx)], dtype=int
    )
    return core_idx, out_idx


def medoid_for_cluster(indices: List[int], dist: np.ndarray) -> int:
    best, best_score = None, float("inf")
    for i in indices:
        d_avg = dist[i, indices].mean()
        if d_avg < best_score:
            best_score = d_avg
            best = i
    return best if best is not None else indices[0]


def assign_outliers(
    outlier_indices: List[int],
    cluster_to_members: Dict[int, List[int]],
    dist: np.ndarray,
) -> Dict[int, int]:
    medoids = {
        cid: medoid_for_cluster(members, dist)
        for cid, members in cluster_to_members.items()
    }
    assignments = {}
    for oi in outlier_indices:
        best_c, best_d = None, float("inf")
        for cid, m in medoids.items():
            d = dist[oi, m]
            if d < best_d:
                best_d = d
                best_c = cid
        assignments[oi] = best_c if best_c is not None else -1
    return assignments


# ==========================================
# PART 3: Core Algorithm (Eigengap)
# ==========================================


def estimate_n_clusters_robust(W, max_k=15):
    n = W.shape[0]
    max_k = min(max_k, n - 1)

    degrees = np.array(W.sum(axis=1)).flatten()
    d_inv_sqrt = np.zeros_like(degrees)
    valid_mask = degrees > 0
    d_inv_sqrt[valid_mask] = np.power(degrees[valid_mask], -0.5)

    W_scaled = W * d_inv_sqrt[:, None] * d_inv_sqrt[None, :]
    L = np.eye(n) - W_scaled

    num_eigen = max_k + 2
    try:
        eigenvals, _ = eigsh(L, k=num_eigen, which="SA")
    except Exception as e:
        eigenvals, _ = np.linalg.eigh(L)
        eigenvals = eigenvals[:num_eigen]

    eigenvals = np.sort(eigenvals)
    vals_to_plot = eigenvals[: max_k + 1]

    gaps = np.diff(vals_to_plot)

    search_start_index = 1
    if len(gaps) > search_start_index:
        best_gap_index_search = (
            np.argmax(gaps[search_start_index:]) + search_start_index
        )
    else:
        best_gap_index_search = np.argmax(gaps)

    n_best = best_gap_index_search + 1
    return n_best


# ==========================================
# PART 4: Process Controller
# ==========================================


def prepare_core(
    dist_sq: np.ndarray,
    sim_matrix: np.ndarray | None,
    max_k: int,
    use_outlier: bool,
    knn: int,
    iqr_mult: float,
) -> tuple[int, np.ndarray, np.ndarray]:

    n = dist_sq.shape[0]

    if use_outlier:
        scores = outlier_scores_knn(dist_sq, k=knn)
        core_idx, out_idx = split_core_outliers(scores, iqr_mult=iqr_mult)
    else:
        core_idx = np.arange(n, dtype=int)
        out_idx = np.array([], dtype=int)

    if sim_matrix is not None:
        W_core = sim_matrix[np.ix_(core_idx, core_idx)].copy()
    else:
        core_dist = dist_sq[np.ix_(core_idx, core_idx)]
        W_core = 1.0 / (core_dist + 1e-6)

    np.fill_diagonal(W_core, 0.0)

    k_auto = estimate_n_clusters_robust(W_core, max_k=max_k)

    return k_auto, core_idx, out_idx


# ==========================================
# PART 5: Result Output (Benchmarking Optional)
# ==========================================


def build_cluster_records(
    labels: list[str],
    core_idx: np.ndarray,
    core_clusters: np.ndarray,
    out_idx: np.ndarray,
    dist_sq: np.ndarray,
):
    core_labels = [labels[i] for i in core_idx]
    cluster_to_members: Dict[int, List[int]] = {}
    core_records = []
    idx_map = {lbl: i for i, lbl in enumerate(labels)}

    for lbl, cid in zip(core_labels, core_clusters):
        idx = idx_map[lbl]
        cluster_to_members.setdefault(int(cid), []).append(idx)
        core_records.append((lbl, int(cid), 0))

    out_assign = assign_outliers(
        [idx_map[labels[i]] for i in out_idx], cluster_to_members, dist_sq
    )
    final = core_records.copy()

    for i in out_idx:
        lbl = labels[i]
        cid = out_assign[i]
        final.append((lbl, int(cid), 1))
    return final


def save_clusters_and_metrics(
    prefix: str,
    records: list[tuple[str, int, int]],
    labels: list[str],
    true_classes: Optional[list[str]],
    out_idx: np.ndarray,
    k_auto: int,
    outdir: Path,
    use_outlier: bool,
):
    # 1. Save cluster details (Clusters CSV)
    clusters_path = outdir / f"{prefix}.clusters.csv"
    with clusters_path.open("w", encoding="utf-8") as f:
        f.write("label,cluster_id,is_outlier\n")
        for lbl, cid, flag in records:
            f.write(f"{lbl},{cid},{flag}\n")

    # Calculate predicted number of clusters
    pred = [cid for _, cid, _ in records]
    n_clusters_pred = len(set(pred))

    # 2. Save metrics statistics (Metrics CSV)
    if true_classes is not None:
        # === New Logic: Calculate true number of classes ===
        n_true_classes = len(set(true_classes))
        # =================================

        ari = metrics.adjusted_rand_score(true_classes, pred)
        ami = metrics.adjusted_mutual_info_score(
            true_classes, pred, average_method="arithmetic"
        )
        nmi = metrics.normalized_mutual_info_score(
            true_classes, pred, average_method="arithmetic"
        )

        metrics_row = {
            "n": len(labels),
            "k_predicted": n_clusters_pred,  # Number of clusters predicted by algorithm
            "k_true": n_true_classes,  # True number of classes
            "outliers": len(out_idx),
            "ARI": ari,
            "AMI": ami,
            "NMI": nmi,
            "use_outlier": use_outlier,
            "k_auto_est": k_auto,  # Raw k estimated by algorithm (without manual fix)
        }

        # Save
        pd.DataFrame([metrics_row]).to_csv(
            outdir / f"{prefix}.metrics.csv", sep=",", index=False
        )

        print(
            f"[{prefix}] Pred={n_clusters_pred} | True={n_true_classes} | "
            f"Outliers={len(out_idx)} | ARI={ari:.4f}"
        )
    else:
        # If no ground truth, output basic info only
        print(
            f"[{prefix}] k={n_clusters_pred} | Outliers={len(out_idx)} | "
            f"(No ground truth, metrics skipped)"
        )


def main(input_file, labels_file, is_similarity, outdir, prefix, max_k, k_fixed, no_outlier, knn, iqr_mult):
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    labels, true_classes = load_labels(Path(labels_file))
    raw_matrix = load_matrix(Path(input_file))

    if is_similarity:
        print("Mode: Input is Similarity Matrix (SNF detected).")
        sim_matrix = raw_matrix.copy()
        dist_sq = 1.0 - raw_matrix
        dist_sq[dist_sq < 0] = 0.0
        np.fill_diagonal(dist_sq, 0.0)
    else:
        print("Mode: Input is Distance Matrix.")
        dist_sq = raw_matrix
        np.fill_diagonal(dist_sq, 0.0)
        sim_matrix = None

    use_outlier = not no_outlier

    # 1. Core calculation
    k_auto, core_idx, out_idx = prepare_core(
        dist_sq=dist_sq,
        sim_matrix=sim_matrix,
        max_k=max_k,
        use_outlier=use_outlier,
        knn=knn,
        iqr_mult=iqr_mult,
    )

    print(
        f"Pipeline Info: Total={len(labels)}, Core={len(core_idx)}, Outliers={len(out_idx)}"
    )
    print(f"Auto-k Estimation: {k_auto} clusters")

    # 2. Tree construction
    # [Core Fix]: Full Tree
    Z_full = linkage(condensed_from_square(dist_sq), method="ward")
    # Force fix negative values to prevent to_tree error
    Z_full[Z_full[:, 2] < 0, 2] = 0.0
    full_nwk = linkage_to_newick(to_tree(Z_full, rd=False), labels) + ";"
    (out_path / f"{prefix}.nwk").write_text(full_nwk)

    # [Core Fix]: Clean Tree
    clean_labels = [labels[i] for i in core_idx]
    clean_dist = dist_sq[np.ix_(core_idx, core_idx)]
    Z_clean = linkage(condensed_from_square(clean_dist), method="ward")
    # Force fix negative values to prevent to_tree error
    Z_clean[Z_clean[:, 2] < 0, 2] = 0.0
    clean_nwk = linkage_to_newick(to_tree(Z_clean, rd=False), clean_labels) + ";"
    (out_path / f"{prefix}_clean.nwk").write_text(clean_nwk)

    # 3. Clustering output (Auto-k)
    core_clusters_auto = fcluster(Z_clean, t=k_auto, criterion="maxclust")
    records_auto = build_cluster_records(
        labels, core_idx, core_clusters_auto, out_idx, dist_sq
    )
    save_clusters_and_metrics(
        f"{prefix}_ward_auto",
        records_auto,
        labels,
        true_classes,
        out_idx,
        k_auto,
        out_path,
        use_outlier,
    )

    # 4. Clustering output (Fixed-k)
    if k_fixed is not None:
        core_clusters_fix = fcluster(Z_clean, t=k_fixed, criterion="maxclust")
        records_fix = build_cluster_records(
            labels, core_idx, core_clusters_fix, out_idx, dist_sq
        )
        save_clusters_and_metrics(
            f"{prefix}_ward_k{k_fixed}",
            records_fix,
            labels,
            true_classes,
            out_idx,
            k_auto,
            out_path,
            use_outlier,
        )