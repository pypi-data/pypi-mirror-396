# -*- coding: utf-8 -*-
import os
import re
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
from sklearn.cluster import SpectralClustering
from sklearn.metrics.pairwise import cosine_distances
from sklearn.manifold import TSNE
from scipy.sparse.linalg import eigsh
from scipy.cluster.hierarchy import linkage, dendrogram, to_tree
from scipy.spatial.distance import squareform

# Try importing UMAP
try:
    import umap
    HAS_UMAP = True
except ImportError:
    HAS_UMAP = False
    print("Notice: 'umap-learn' library not found. UMAP visualization will be skipped.")

# Try importing pycirclize
try:
    from pycirclize import Circos
    HAS_PYCIRCLIZE = True
except ImportError:
    HAS_PYCIRCLIZE = False
    print("Notice: 'pycirclize' library not found. Falling back to simple circular dendrogram.")


# ==========================================
# 1. Helpers & SNF Core (for Re-calc)
# ==========================================

def load_matrix(path):
    return np.loadtxt(path, delimiter=",")

def load_labels(path):
    df = pd.read_csv(path)
    return df['label'].values

def extract_leaves_from_newick(newick_str):
    """
    Rudimentary Newick parser to extract leaf labels in order.
    Assumes standard Newick format: (A:0.1,B:0.2):0.3;
    """
    newick_str = re.sub(r'\[.*?\]', '', newick_str)
    tokens = re.split(r'([(),;])', newick_str)
    leaves = []
    for i, token in enumerate(tokens):
        token = token.strip()
        if not token or token in "(),;":
            continue
        parts = token.split(':')
        label = parts[0].strip()
        prev_token = tokens[i-1].strip() if i > 0 else ""
        if prev_token in "(,":
            leaves.append(label)
    return leaves

def calculate_W(data, K=20, mu=0.5, is_distance_matrix=False):
    """
    Construct Similarity Matrix W using Scaled Exponential Similarity Kernel.
    Used here to reconstruct W for individual views (Nuc/Prot) from their distance matrices.
    """
    if is_distance_matrix:
        dist_matrix = data
    else:
        dist_matrix = cosine_distances(data)

    n_samples = dist_matrix.shape[0]
    sorted_indices = np.argsort(dist_matrix, axis=1)

    knn_dist = np.take_along_axis(dist_matrix, sorted_indices[:, 1 : K + 1], axis=1)
    mean_dist_K = np.mean(knn_dist, axis=1)

    combined_mean = mean_dist_K[:, np.newaxis] + mean_dist_K[np.newaxis, :]
    Epsilon = (combined_mean + dist_matrix) / 3
    Epsilon[Epsilon == 0] = 1e-10

    W = np.exp(-(dist_matrix**2) / (mu * Epsilon))
    np.fill_diagonal(W, 1.0)
    return W

def estimate_n_clusters_robust(W, ax_eigen, ax_gap, max_k=15):
    """
    Estimate optimal cluster number using Eigengap heuristic and plot on provided axes.
    """
    n = W.shape[0]
    max_k = min(max_k, n - 1)

    # Normalized Laplacian: L = I - D^-1/2 * W * D^-1/2
    degrees = np.array(W.sum(axis=1)).flatten()
    d_inv_sqrt = np.zeros_like(degrees)
    valid_mask = degrees > 0
    d_inv_sqrt[valid_mask] = np.power(degrees[valid_mask], -0.5)
    
    W_scaled = W * d_inv_sqrt[:, None] * d_inv_sqrt[None, :]
    L = np.eye(n) - W_scaled

    num_eigen = max_k + 2 
    try:
        eigenvals, _ = eigsh(L, k=num_eigen, which='SA')
    except Exception as e:
        print(f"Eigsh failed ({e}), falling back to numpy.eigh...")
        eigenvals, _ = np.linalg.eigh(L)
        eigenvals = eigenvals[:num_eigen]

    eigenvals = np.sort(eigenvals)
    vals_to_plot = eigenvals[: max_k + 1]
    gaps = np.diff(vals_to_plot)
    
    # Heuristic: Start searching from k=2 (index 1)
    search_start_index = 1
    if len(gaps) > search_start_index:
        best_gap_index_search = np.argmax(gaps[search_start_index:]) + search_start_index
    else:
        best_gap_index_search = np.argmax(gaps)
        
    n_best = best_gap_index_search + 1

    # Plot Eigenvalues
    x_range = range(1, len(vals_to_plot) + 1)
    ax_eigen.plot(x_range, vals_to_plot, "o-", markerfacecolor="white", markersize=6, linewidth=1.5)
    ax_eigen.set_ylabel("Eigenvalue")
    ax_eigen.set_title("Eigenvalues (Low to High)")
    ax_eigen.grid(True, alpha=0.3)
    ax_eigen.axvline(x=n_best, color="green", linestyle="--", alpha=0.5)
    ax_eigen.text(n_best, vals_to_plot[n_best-1], f" k={n_best}", color="green", verticalalignment="bottom")

    # Plot Eigengaps
    bar_colors = ["skyblue"] * len(gaps)
    if best_gap_index_search < len(bar_colors):
        bar_colors[best_gap_index_search] = "orange"
    if len(gaps) > 0:
        bar_colors[0] = "lightgray"

    ax_gap.bar(range(1, len(gaps) + 1), gaps, color=bar_colors)
    ax_gap.set_xlabel("k (Clusters)")
    ax_gap.set_ylabel("Eigengap Size")
    ax_gap.set_title(f"Optimal k={n_best} (Max Gap)")
    ax_gap.grid(True, axis="y", alpha=0.3)
    ax_gap.set_xticks(range(1, len(gaps) + 1))

    return n_best

def run_unsupervised_clustering(W_fused, n_clusters, sample_names):
    """Run Spectral Clustering."""
    print(f"--- Running Unsupervised Spectral Clustering (k={n_clusters}) ---")
    W_fused = (W_fused + W_fused.T) / 2
    spectral = SpectralClustering(n_clusters=n_clusters, affinity="precomputed", random_state=42)
    labels_pred = spectral.fit_predict(W_fused)
    return labels_pred

def plot_unsupervised_heatmap(W, labels_pred, n_clusters, ax):
    """Plot sorted heatmap with cluster bars."""
    cmap = plt.get_cmap("tab20" if n_clusters > 10 else "tab10")
    colors = [cmap(i) for i in range(n_clusters)]
    sample_colors = [colors[label] for label in labels_pred]

    sort_indices = np.argsort(labels_pred)
    sorted_matrix = W[sort_indices, :][:, sort_indices]
    sorted_colors = np.array(sample_colors)[sort_indices]

    # Contrast enhancement
    plot_data = sorted_matrix.copy()
    np.fill_diagonal(plot_data, 0)
    eps = 1e-10
    plot_data = np.log10(np.maximum(plot_data, eps))
    v_min, v_max = np.percentile(plot_data, 5), np.percentile(plot_data, 99)
    plot_data = np.clip(plot_data, v_min, v_max)
    if v_max > v_min:
        plot_data = (plot_data - v_min) / (v_max - v_min)
    np.fill_diagonal(plot_data, 1.0)

    im = ax.imshow(plot_data, cmap="viridis", aspect="auto", interpolation="nearest")
    
    # Add color bar on the left
    ax_divider = ax.inset_axes([-0.05, 0, 0.03, 1])
    ax_divider.imshow(sorted_colors[:, np.newaxis, :], aspect="auto")
    ax_divider.set_xticks([])
    ax_divider.set_yticks([])

    # Legend
    patches = [mpatches.Patch(color=colors[i], label=f"C{i}") for i in range(n_clusters)]
    ax.legend(handles=patches, loc="upper right", title="Clusters", fontsize="small")
    ax.set_title(f"Heatmap (k={n_clusters})")
    ax.set_xlabel("Samples")
    ax.set_ylabel("Samples")


# ==========================================
# 2. Advanced Visualization Functions
# ==========================================

def run_dim_reduction(W_fused, labels, outdir, prefix):
    print("--- Running Dimensionality Reduction (t-SNE/UMAP) ---")
    D_fused = 1.0 - W_fused
    np.fill_diagonal(D_fused, 0.0)
    D_fused[D_fused < 0] = 0.0
    
    # t-SNE
    perplexity = min(30, max(5, W_fused.shape[0] // 4))
    tsne = TSNE(n_components=2, metric='precomputed', init='random', 
                random_state=42, perplexity=perplexity)
    try:
        Y_tsne = tsne.fit_transform(D_fused)
        plot_embedding(Y_tsne, labels, "t-SNE", outdir, prefix)
    except Exception as e:
        print(f"t-SNE failed: {e}")

    # UMAP
    if HAS_UMAP:
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="umap")
                # Also filter generic UserWarning if module filtering isn't enough for specific messages
                warnings.filterwarnings("ignore", message=".*n_jobs value 1 overridden.*")
                warnings.filterwarnings("ignore", message=".*using precomputed metric.*")
                
                reducer = umap.UMAP(metric='precomputed', random_state=42, n_neighbors=min(15, W_fused.shape[0]-1))
                Y_umap = reducer.fit_transform(D_fused)
                plot_embedding(Y_umap, labels, "UMAP", outdir, prefix)
        except Exception as e:
            print(f"UMAP failed: {e}")

def plot_embedding(Y, labels, method, outdir, prefix):
    unique_labels = np.unique(labels)
    colors = cm.tab20(np.linspace(0, 1, len(unique_labels)))
    label_to_color = {lbl: col for lbl, col in zip(unique_labels, colors)}
    
    plt.figure(figsize=(10, 8))
    # Plot points, coloring by label, but without labels for legend
    for lbl in unique_labels:
        mask = (labels == lbl)
        plt.scatter(Y[mask, 0], Y[mask, 1], c=[label_to_color[lbl]], s=60, alpha=0.8, edgecolors='w')
    
    plt.title(f"{method} Projection of Fused Network", fontsize=15)
    plt.xlabel(f"{method} 1")
    plt.ylabel(f"{method} 2")
    # Removed plt.legend() as per request to not show labels/legend
    plt.tight_layout()
    
    filename = f"{prefix}_{method.lower()}.png"
    plt.savefig(os.path.join(outdir, filename), dpi=300)
    plt.close()
    print(f"Saved {method} plot to {filename}")

def run_circular_dendrogram(tree_path, input_labels, fused_cluster_ids, outdir, prefix, span_degrees=330):
    print(f"--- Generating Circular Dendrogram from {tree_path} (Span: {span_degrees} degrees) ---")

    if not HAS_PYCIRCLIZE:
        print("Skipping advanced circular dendrogram (pycirclize not found).")
        return
    
    if not tree_path or not os.path.exists(tree_path):
        print(f"Warning: Tree file not found at {tree_path}. Skipping circular dendrogram.")
        return

    # 1. Read Newick File
    try:
        with open(tree_path, 'r') as f:
            newick_str = f.read().strip()
    except Exception as e:
        print(f"Error reading tree file: {e}")
        return

    # 2. Setup pycirclize
    # Calculate start and end angles to center the gap at 90 degrees (top)
    gap = 360 - span_degrees
    start_angle = 90 + gap / 2
    end_angle = start_angle + span_degrees
    
    # Ensure range is within -360 to 360 as required by pycirclize
    if end_angle > 360:
        start_angle -= 360
        end_angle -= 360
    
    circos = Circos(sectors={"Tree": 360}, start=start_angle, end=end_angle)
    sector = circos.sectors[0]

    # --- Track 1: Dendrogram (Inner) ---
    track_tree = sector.add_track((30, 90)) 
    track_tree.tree(
        newick_str, 
        leaf_label_size=0, # Hide text labels
        line_kws=dict(color="black", lw=0.5, alpha=0.8)
    )

    # --- Track 2: Cluster Color Ring (Outer) ---
    leaf_names = extract_leaves_from_newick(newick_str)
    
    if len(leaf_names) != len(input_labels):
        print(f"Warning: Number of leaves in tree ({len(leaf_names)}) does not match number of labels ({len(input_labels)}).")
    
    label_to_cluster = {}
    for lbl, cid in zip(input_labels, fused_cluster_ids):
        safe_lbl = str(lbl).replace(":", "_").replace(";", "_").replace(",", "_").replace("(", "_").replace(")", "_")
        label_to_cluster[safe_lbl] = cid
    
    ordered_cluster_ids = []
    for leaf in leaf_names:
        if leaf in label_to_cluster:
            ordered_cluster_ids.append(label_to_cluster[leaf])
        else:
            print(f"Warning: Leaf '{leaf}' not found in labels.")
            ordered_cluster_ids.append(-1)
    
    ordered_cluster_ids = np.array(ordered_cluster_ids)
    
    unique_clusters = sorted([c for c in np.unique(ordered_cluster_ids) if c != -1])
    if len(unique_clusters) <= 8:
        cmap_base = plt.get_cmap("Set2")
    else:
        cmap_base = plt.get_cmap("tab20")
    cluster_colors = {cid: cmap_base(i) for i, cid in enumerate(unique_clusters)}
    cluster_colors[-1] = (0.9, 0.9, 0.9, 1.0) # Grey for unknown
    
    cluster_to_int = {cid: i for i, cid in enumerate(unique_clusters)}
    cluster_to_int[-1] = len(unique_clusters) # For grey color
    
    mapped_heatmap_data = np.array([cluster_to_int.get(c, len(unique_clusters)) for c in ordered_cluster_ids]).reshape(1, -1)
    
    c_list = [cluster_colors[cid] for cid in unique_clusters]
    c_list.append(cluster_colors[-1])
    custom_cmap = ListedColormap(c_list)

    track_heatmap = sector.add_track((92, 97)) 
    track_heatmap.heatmap(
        mapped_heatmap_data, 
        cmap=custom_cmap, 
        rect_kws=dict(ec="none") 
    )

    # 3. Plotting
    fig = circos.plotfig(figsize=(10, 10), dpi=300)
    
    # Custom Legend
    handles = []
    for cid in unique_clusters:
        color = cluster_colors[cid]
        patch = mpatches.Patch(color=color, label=f"Cluster {cid}")
        handles.append(patch)
    
    plt.legend(
        handles=handles, 
        title="Clusters", 
        loc="center left", 
        bbox_to_anchor=(1.05, 0.5),
        frameon=False
    )
    plt.title("Circular Dendrogram (Ward) with Clusters", fontsize=14, y=1.02)
    
    filename = f"{prefix}_circular_dendrogram.png"
    plt.savefig(os.path.join(outdir, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Circular Dendrogram to {filename}")

def run_view_contribution(nuc_dist_path, prot_dist_path, W_fused, outdir, prefix):
    print("--- Running View Contribution Analysis ---")
    
    # Load raw distance matrices locally (not passed as arrays to main, but as paths)
    D_nuc = load_matrix(nuc_dist_path)
    D_prot = load_matrix(prot_dist_path)
    
    D_fused = 1.0 - W_fused
    np.fill_diagonal(D_fused, 0.0)
    
    mask = np.triu(np.ones_like(D_fused, dtype=bool), k=1)
    nuc_vals = D_nuc[mask]
    prot_vals = D_prot[mask]
    fused_vals = D_fused[mask]
    
    corr_nuc = np.corrcoef(nuc_vals, fused_vals)[0, 1]
    corr_prot = np.corrcoef(prot_vals, fused_vals)[0, 1]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    axes[0].scatter(nuc_vals, fused_vals, alpha=0.3, color='steelblue', s=10)
    axes[0].set_xlabel("Nucleotide Distance")
    axes[0].set_ylabel("Fused Network Distance (1-W)")
    axes[0].set_title(f"Nucleotide vs Fused\nPearson r = {corr_nuc:.3f}")
    axes[0].grid(True, alpha=0.3)
    
    axes[1].scatter(prot_vals, fused_vals, alpha=0.3, color='darkorange', s=10)
    axes[1].set_xlabel("Protein Distance")
    axes[1].set_ylabel("Fused Network Distance (1-W)")
    axes[1].set_title(f"Protein vs Fused\nPearson r = {corr_prot:.3f}")
    axes[1].grid(True, alpha=0.3)
    
    plt.suptitle("View Contribution Analysis", fontsize=16)
    plt.tight_layout()
    
    filename = f"{prefix}_view_contribution.png"
    plt.savefig(os.path.join(outdir, filename), dpi=300)
    plt.close()
    print(f"Saved Contribution plot to {filename}")


# ==========================================
# Main Execution
# ==========================================

def main(nuc_dist, prot_dist, fused_similarity, labels_path, outdir, prefix, k_clusters=None, tree_path=None, dendrogram_span=330):
    print("\n--- Comprehensive SNF Visualization Script ---")
    
    plots_subdir = "plots"
    plots_output_path = os.path.join(outdir, plots_subdir)
    os.makedirs(plots_output_path, exist_ok=True)
    print(f"Plots will be saved to: {plots_output_path}")

    try:
        # Load matrices
        nuc_dist_mat = load_matrix(nuc_dist)
        prot_dist_mat = load_matrix(prot_dist)
        W_fused = load_matrix(fused_similarity)
        
        # Load labels
        labels = load_labels(labels_path)
    except Exception as e:
        print(f"Failed to load data: {e}")
        return

    # --- Part 1: Basic Summary Plot (3x3 Grid) ---
    print("\n>>> Generating Summary Heatmaps & Eigengaps...")
    
    # Calculate single-view similarity matrices for visualization
    W_nuc = calculate_W(nuc_dist_mat, K=20, is_distance_matrix=True)
    W_prot = calculate_W(prot_dist_mat, K=20, is_distance_matrix=True)

    fig, axes = plt.subplots(3, 3, figsize=(18, 15), constrained_layout=True)
    matrices_info = [
        (W_nuc, "Nucleotide View"),
        (W_prot, "Protein View"),
        (W_fused, "Fused Network"),
    ]

    # Store fused clusters for the circular dendrogram
    fused_cluster_ids = None

    for i, (W, title) in enumerate(matrices_info):
        ax_eigen = axes[i, 0]
        ax_gap = axes[i, 1]
        ax_heat = axes[i, 2]

        estimated_k = estimate_n_clusters_robust(W, ax_eigen, ax_gap)
        BEST_K = k_clusters if k_clusters is not None else estimated_k

        ax_eigen.set_ylabel(f"{title}\n{ax_eigen.get_ylabel()}", fontsize=12, fontweight="bold")
        
        # Run clustering
        labels_pred = run_unsupervised_clustering(W, BEST_K, labels) 
        
        # Capture fused clusters
        if title == "Fused Network":
            fused_cluster_ids = labels_pred

        # Plot heatmap
        plot_unsupervised_heatmap(W, labels_pred, BEST_K, ax_heat)

    plt.suptitle(f"SNF Analysis Summary: {prefix}", fontsize=16)
    summary_path = os.path.join(plots_output_path, f"{prefix}_summary_metrics.png")
    plt.savefig(summary_path, dpi=300)
    plt.close()
    print(f"Saved Summary Plot to {summary_path}")

    # --- Part 2: Advanced Visualizations ---
    print("\n>>> Generating Advanced Plots...")
    
    # 1. t-SNE / UMAP
    # Note: Using labels (ground truth/sample names) for coloring. 
    # If you want to color by predicted clusters, you could swap 'labels' with 'fused_cluster_ids'.
    # Here we stick to 'labels' as per original code, which implies ground truth or sample types.
    run_dim_reduction(W_fused, labels, plots_output_path, prefix)
    
    # 2. Circular Dendrogram
    if fused_cluster_ids is not None:
        run_circular_dendrogram(tree_path, labels, fused_cluster_ids, plots_output_path, prefix, dendrogram_span)
    
    # 3. View Contribution
    run_view_contribution(nuc_dist, prot_dist, W_fused, plots_output_path, prefix)

    print("\n[Visualization] All plots generated successfully.")