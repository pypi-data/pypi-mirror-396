#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Genecast Comprehensive CLI Tool
==============================

This script serves as the main entry point for the Genecast pipeline.
It integrates the following independent modules into a single CLI:

1. dist: Preprocess FASTA into matrices and labels.
2. snf: Perform Similarity Network Fusion (SNF).
3. ward: Run Ward Clustering + Auto-k estimation.
4. viz: Visualize SNF results.

Usage:
    genecast <command> [options]

    Commands:
        dist    Preprocess FASTA files.
        snf     Run Similarity Network Fusion.
        ward    Run Ward clustering.
        viz     Visualize results.
        demo    Run the pipeline with Actine_test demo data.
        report  Generate an HTML report from existing results.
        all     Run the complete pipeline (dist -> snf -> ward -> viz -> report).

Use `genecast <command> --help` for detailed help on each command.
"""

import argparse
import sys
import json
import os

# Import the refactored modules using relative imports for package compatibility
from . import dist
from . import snf
from . import ward
from . import visualization
from . import report_generator


def main():
    parser = argparse.ArgumentParser(
        description="Genecast Comprehensive CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # --- Command: dist ---
    parser_dist = subparsers.add_parser(
        "dist", 
        help="Preprocess FASTA into matrices and labels",
        description="Preprocess FASTA into matrices and labels (dist.py)"
    )
    parser_dist.add_argument("--fasta", nargs="+", required=True, help="Glob pattern(s) for FASTA files (e.g., 'data/**/*.fa*').")
    parser_dist.add_argument("--mode", choices=["nuc", "prot"], required=True, help="nuc: nucleotide k-mers; prot: amino acid properties.")
    parser_dist.add_argument("--kmer", type=int, default=5, help="k for nucleotide k-mers.")
    parser_dist.add_argument("--win", type=int, default=3, help="Window size for amino acid property averaging.")
    parser_dist.add_argument("--outdir", default="output/results", help="Directory to write CSV artifacts.")
    parser_dist.add_argument("--prefix", default="dataset", help="Prefix for output files.")
    parser_dist.add_argument("--max-seqs", type=int, default=0, help="Optional cap on sequences (<=0 means no cap).")

    # --- Command: snf ---
    parser_snf = subparsers.add_parser(
        "snf", 
        help="Similarity Network Fusion (SNF)",
        description="Run Similarity Network Fusion (snf.py)"
    )
    parser_snf.add_argument("--dist-matrices", nargs="+", required=True, help="One or more pre-computed distance matrix CSV files.")
    parser_snf.add_argument("--output-file", required=True, help="Path to save the final fused similarity matrix.")
    parser_snf.add_argument("--K-values", nargs="+", type=int, default=[10, 20, 40], help="List of K values for multi-scale SNF.")
    parser_snf.add_argument("--t-iter", type=int, default=20, help="Number of iterations for the fusion process.")

    # --- Command: ward ---
    parser_ward = subparsers.add_parser(
        "ward", 
        help="Ward Clustering + Auto-k",
        description="Run Ward Clustering + Auto-k estimation (ward.py)"
    )
    parser_ward.add_argument("--input", required=True, help="Input matrix CSV (no header).")
    parser_ward.add_argument("--labels", required=True, help="CSV containing a 'label' column (and optional class column).")
    parser_ward.add_argument("--is-similarity", action="store_true", help="Set this flag if the input is an SNF similarity matrix.")
    parser_ward.add_argument("--outdir", default="results_ward_pipeline", help="Output directory.")
    parser_ward.add_argument("--prefix", default="ward_pipeline", help="Output file prefix.")
    parser_ward.add_argument("--max-k", type=int, default=15, help="Maximum k to search for auto-k estimation.")
    parser_ward.add_argument("--k-fixed", type=int, default=None, help="If provided, output results for this fixed k.")
    parser_ward.add_argument("--no-outlier", action="store_true", help="Disable outlier detection.")
    parser_ward.add_argument("--knn", type=int, default=10, help="KNN parameter for outlier detection.")
    parser_ward.add_argument("--iqr-mult", type=float, default=1.5, help="Tukey IQR multiplier for outlier detection.")

    # --- Command: viz ---
    parser_viz = subparsers.add_parser(
        "viz", 
        help="Comprehensive Visualization (Heatmaps, t-SNE, Trees)",
        description="Visualization of SNF results (visualization.py)"
    )
    parser_viz.add_argument("--nuc-dist", type=str, required=True, help="Path to the nucleotide distance matrix CSV file.")
    parser_viz.add_argument("--prot-dist", type=str, required=True, help="Path to the protein distance matrix CSV file.")
    parser_viz.add_argument("--fused-similarity", type=str, required=True, help="Path to the fused similarity matrix CSV file.")
    parser_viz.add_argument("--labels-path", type=str, required=True, help="Path to the sample labels CSV file.")
    parser_viz.add_argument("--outdir", type=str, required=True, help="Directory to save all plots.")
    parser_viz.add_argument("--prefix", type=str, default="viz", help="Prefix for output plot files.")
    parser_viz.add_argument("--k-clusters", type=int, default=None, help="Optional: Force a specific number of clusters (k).")
    parser_viz.add_argument("--tree", type=str, default=None, help="Path to Newick tree file for circular dendrogram.")
    parser_viz.add_argument("--dendrogram-span", type=int, default=330, help="Angular span (in degrees) for the circular dendrogram (default: 330).")

    # --- Command: report ---
    parser_report = subparsers.add_parser(
        "report",
        help="Generate HTML Report",
        description="Generate a standalone HTML report from existing results."
    )
    parser_report.add_argument("--outdir", required=True, help="Directory containing results.")
    parser_report.add_argument("--prefix", required=True, help="Prefix used for the analysis (e.g., 'analysis').")

    # --- Command: demo ---
    parser_demo = subparsers.add_parser(
        "demo",
        help="Run the pipeline with Actine_test demo data",
        description="Run the complete pipeline with default demo settings using internal demo data."
    )

    # --- Command: all ---
    parser_all = subparsers.add_parser(
        "all",
        help="Run the complete pipeline (dist -> snf -> ward -> viz)",
        description="Run the complete pipeline sequentially."
    )
    parser_all.add_argument("--fasta", nargs="+", required=True, help="Glob pattern(s) for FASTA files.")
    parser_all.add_argument("--outdir", required=True, help="Directory for all outputs.")
    parser_all.add_argument("--prefix", default="analysis", help="Base prefix for output files.")
    parser_all.add_argument("--kmer", type=int, default=5, help="k for nucleotide k-mers.")
    parser_all.add_argument("--win", type=int, default=3, help="Window size for amino acid properties.")
    parser_all.add_argument("--max-seqs", type=int, default=0, help="Optional cap on sequences.")
    parser_all.add_argument("--snf-k", nargs="+", type=int, default=[10, 20, 40], help="K values for SNF.")
    parser_all.add_argument("--snf-t", type=int, default=20, help="Iterations for SNF.")
    parser_all.add_argument("--viz-k", type=int, default=None, help="Optional: Force k for visualization.")
    parser_all.add_argument("--dendrogram-span", type=int, default=330, help="Angular span (in degrees) for the circular dendrogram (default: 330).")

    # Parse arguments
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # Dispatch to sub-modules with unpacked arguments
    if args.command == "dist":
        dist.main(
            fasta_patterns=args.fasta,
            mode=args.mode,
            kmer=args.kmer,
            win=args.win,
            outdir=args.outdir,
            prefix=args.prefix,
            max_seqs=args.max_seqs
        )
    elif args.command == "snf":
        snf.main(
            dist_matrices=args.dist_matrices,
            output_file=args.output_file,
            K_values=args.K_values,
            t_iter=args.t_iter
        )
    elif args.command == "ward":
        ward.main(
            input_file=args.input,
            labels_file=args.labels,
            is_similarity=args.is_similarity,
            outdir=args.outdir,
            prefix=args.prefix,
            max_k=args.max_k,
            k_fixed=args.k_fixed,
            no_outlier=args.no_outlier,
            knn=args.knn,
            iqr_mult=args.iqr_mult
        )
    elif args.command == "viz":
        visualization.main(
            nuc_dist=args.nuc_dist,
            prot_dist=args.prot_dist,
            fused_similarity=args.fused_similarity,
            labels_path=args.labels_path,
            outdir=args.outdir,
            prefix=args.prefix,
            k_clusters=args.k_clusters,
            tree_path=args.tree,
            dendrogram_span=args.dendrogram_span
        )
    elif args.command == "report":
        # Load parameters if available
        params_file = os.path.join(args.outdir, "parameters.json")
        parameters = None
        if os.path.exists(params_file):
            try:
                with open(params_file, "r") as f:
                    parameters = json.load(f)
            except Exception as e:
                print(f"Warning: Could not read parameters.json: {e}")
        
        report_path = report_generator.generate_html_report(
            outdir=args.outdir, 
            prefix=args.prefix,
            parameters=parameters
        )
        print(f"Report generated at: {report_path}")

    elif args.command == "all" or args.command == "demo":
        
        # If command is demo, set default args
        if args.command == "demo":
            print(">>> Running Demo Mode with Actin_test data...")
            
            # Determine path to internal data relative to this script
            package_dir = os.path.dirname(os.path.abspath(__file__))
            demo_fasta_path = os.path.join(package_dir, "demodata", "Actin_test", "actin_nuc.fa")
            
            if not os.path.exists(demo_fasta_path):
                print(f"Error: Demo data not found at '{demo_fasta_path}'. Ensure the package is installed correctly.")
                sys.exit(1)
                
            args.fasta = [demo_fasta_path]
            args.outdir = "output/demo_actin"
            args.prefix = "demo_actin"
            # Set other defaults explicitly
            args.kmer = 5
            args.win = 3
            args.max_seqs = 0
            args.snf_k = [10, 20, 40]
            args.snf_t = 20
            args.viz_k = None
            args.dendrogram_span = 330
            
            print(f"Output will be saved to: {args.outdir}")

        # 1. Define Paths
        outdir = args.outdir
        prefix = args.prefix

        # Define subdirectories for organized output
        plots_subdir = "plots" # For images generated by visualization.py
        data_files_subdir = "data_files" # For CSVs and Newick files from dist, snf, ward

        # Create main output directory and subdirectories
        os.makedirs(outdir, exist_ok=True)
        data_files_output_path = os.path.join(outdir, data_files_subdir)
        os.makedirs(data_files_output_path, exist_ok=True)
        # Note: 'plots' subdirectory is created by visualization.py itself

        # Save parameters (still at top level of outdir)
        params_file = os.path.join(outdir, "parameters.json")
        with open(params_file, "w") as f:
            json.dump(vars(args), f, indent=4)
        print(f"Parameters saved to {params_file}")
        
        # Output prefixes for dist steps
        prefix_nuc = f"{prefix}_nuc"
        prefix_prot = f"{prefix}_prot"
        
        # Expected output files from dist (now in data_files_output_path)
        nuc_dist_file = os.path.join(data_files_output_path, f"{prefix}_nuc_dist.csv")
        prot_dist_file = os.path.join(data_files_output_path, f"{prefix}_prot_dist.csv")
        labels_file = os.path.join(data_files_output_path, f"{prefix}_nuc_labels.csv") # Use nuc labels as canonical
        
        # SNF Output (now in data_files_output_path)
        fused_file = os.path.join(data_files_output_path, f"{prefix}_fused_similarity.csv")
        
        # Ward Output Tree (Clean version, now in data_files_output_path)
        ward_tree_file = os.path.join(data_files_output_path, f"{prefix}_ward_clean.nwk")
        
        print("=== Running Full Pipeline ===")
        print(f"Output Directory: {outdir}")
        
        # 2. Run DIST (Nucleotide)
        print("\n>>> Step 1/5: Preprocessing (Nucleotide)...")
        dist.main(
            fasta_patterns=args.fasta,
            mode="nuc",
            kmer=args.kmer,
            win=args.win,
            outdir=data_files_output_path, # Changed
            prefix=prefix_nuc,
            max_seqs=args.max_seqs
        )
        
        # 3. Run DIST (Protein)
        print("\n>>> Step 2/5: Preprocessing (Protein)...")
        dist.main(
            fasta_patterns=args.fasta,
            mode="prot",
            kmer=args.kmer,
            win=args.win,
            outdir=data_files_output_path, # Changed
            prefix=prefix_prot,
            max_seqs=args.max_seqs
        )
        
        # 4. Run SNF
        print("\n>>> Step 3/5: Similarity Network Fusion...")
        snf.main(
            dist_matrices=[nuc_dist_file, prot_dist_file],
            output_file=fused_file,
            K_values=args.snf_k,
            t_iter=args.snf_t
        )
        
        # 5. Run Ward
        print("\n>>> Step 4/5: Ward Clustering...")
        ward.main(
            input_file=fused_file,
            labels_file=labels_file,
            is_similarity=True,
            outdir=data_files_output_path, # Changed
            prefix=f"{prefix}_ward",
            max_k=15, # Default
            k_fixed=None,
            no_outlier=False,
            knn=10,
            iqr_mult=1.5
        )
        
        # 6. Run Visualization (Merged)
        print("\n>>> Step 5/5: Comprehensive Visualization...")
        visualization.main(
            nuc_dist=nuc_dist_file,
            prot_dist=prot_dist_file,
            fused_similarity=fused_file,
            labels_path=labels_file,
            outdir=outdir,
            prefix=prefix,
            k_clusters=args.viz_k,
            tree_path=ward_tree_file,
            dendrogram_span=args.dendrogram_span
        )
        
        # 7. Generate Report
        print("\n>>> Step 6/6: Generating HTML Report...")
        report_generator.generate_html_report(
            outdir=outdir,
            prefix=prefix,
            parameters=vars(args)
        )
        
        print("\n=== Pipeline Complete ===")


if __name__ == "__main__":
    main()