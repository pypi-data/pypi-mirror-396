# -*- coding: utf-8 -*-
import os
import json
import base64
import glob
from pathlib import Path
import pandas as pd
from datetime import datetime

def encode_image_to_base64(image_path):
    if not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def generate_html_report(outdir, prefix, parameters=None):
    """
    Generates a standalone HTML report for the Genecast pipeline results.
    """
    report_path = os.path.join(outdir, f"{prefix}_report.html")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Define subdirectories for organization
    plots_subdir = "plots"
    data_files_subdir = "data_files" # Assuming this will be the name

    # 1. Gather Files - Update paths to include subdirectories
    images = {
        "Summary Metrics": os.path.join(plots_subdir, f"{prefix}_summary_metrics.png"),
        "t-SNE Projection": os.path.join(plots_subdir, f"{prefix}_t-sne.png"),
        "UMAP Projection": os.path.join(plots_subdir, f"{prefix}_umap.png"),
        "Circular Dendrogram": os.path.join(plots_subdir, f"{prefix}_circular_dendrogram.png"),
        "View Contribution": os.path.join(plots_subdir, f"{prefix}_view_contribution.png")
    }

    files = {
        "Nucleotide Distance": os.path.join(data_files_subdir, f"{prefix}_nuc_dist.csv"),
        "Protein Distance": os.path.join(data_files_subdir, f"{prefix}_prot_dist.csv"),
        "Fused Similarity": os.path.join(data_files_subdir, f"{prefix}_fused_similarity.csv"),
        "Ward Clusters": os.path.join(data_files_subdir, f"{prefix}_ward_ward_auto.clusters.csv"),
        "Clean Newick Tree": os.path.join(data_files_subdir, f"{prefix}_ward_clean.nwk")
    }
    
    # Check for legacy naming (if prefix was different for intermediate steps)
    # The 'all' command in main.py uses prefix_nuc, prefix_prot for dist steps.
    # We might need to adjust finding these if they don't match exactly.
    # But for now, we assume the user passes the main 'prefix' used in 'viz'.

    # 2. Build HTML Content
    html_parts = []
    
    # --- Header ---
    html_parts.append(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Genecast Pipeline Report - {prefix}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; background-color: #f4f4f9; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            h1 {{ border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .params-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            .params-table th, .params-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            .params-table th {{ background-color: #f2f2f2; }}
            .img-container {{ text-align: center; margin: 20px 0; }}
            .img-container img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }}
            .file-list {{ list-style: none; padding: 0; }}
            .file-list li {{ padding: 5px 0; border-bottom: 1px solid #eee; }}
            .file-list a {{ text-decoration: none; color: #3498db; font-weight: bold; }}
            .file-list a:hover {{ text-decoration: underline; }}
            .missing {{ color: #e74c3c; font-style: italic; }}
            .description {{ color: #666; font-style: italic; margin-bottom: 10px; font-size: 0.95em; }}
            footer {{ text-align: center; margin-top: 40px; font-size: 0.9em; color: #777; }}
        </style>
    </head>
    <body>
        <h1>Genecast Pipeline Analysis Report</h1>
        <p><strong>Date:</strong> {timestamp}</p>
        <p><strong>Prefix:</strong> {prefix}</p>
    """)

    # --- Parameters Section ---
    html_parts.append('<div class="container"><h2>Configuration Parameters</h2>')
    if parameters:
        html_parts.append('<table class="params-table"><thead><tr><th>Parameter</th><th>Value</th></tr></thead><tbody>')
        for k, v in parameters.items():
            html_parts.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
        html_parts.append('</tbody></table>')
    else:
        html_parts.append('<p>No parameters configuration file found (parameters.json).</p>')
    html_parts.append('</div>')

    # Define descriptions for each plot type
    descriptions = {
        "Summary Metrics": "Displays the eigenvalues, eigengaps, and heatmaps for Nucleotide, Protein, and Fused views to help determine the optimal number of clusters.",
        "t-SNE Projection": "A 2D visualization of the fused similarity network using t-SNE (t-Distributed Stochastic Neighbor Embedding), useful for identifying local clusters.",
        "UMAP Projection": "A 2D visualization of the fused similarity network using UMAP (Uniform Manifold Approximation and Projection), preserving both local and global structure.",
        "Circular Dendrogram": "A circular hierarchical clustering tree showing the relationships between samples based on the fused network, with an outer ring indicating cluster assignments.",
        "View Contribution": "Scatter plots showing the correlation between the original Nucleotide/Protein distances and the final Fused Network distances, indicating how much each view contributed."
    }

    # --- Visualizations Section ---
    html_parts.append('<div class="container"><h2>Visualizations</h2>')
    
    for title, relative_filename in images.items():
        filepath = os.path.join(outdir, relative_filename) # Construct full path for reading image
        
        b64_img = encode_image_to_base64(filepath)
        
        html_parts.append(f'<div class="img-container"><h3>{title}</h3>')
        
        # Add description
        desc = descriptions.get(title, "")
        if desc:
            html_parts.append(f'<p class="description">{desc}</p>')
        
        if b64_img:
            html_parts.append(f'<img src="data:image/png;base64,{b64_img}" alt="{title}">')
            html_parts.append(f'<p><small>File: {relative_filename}</small></p>')
        else:
            html_parts.append(f'<p class="missing">Image not found: {relative_filename}</p>')
        html_parts.append('</div>')
    
    html_parts.append('</div>')

    # --- Data Files Section ---
    html_parts.append('<div class="container"><h2>Generated Data Files</h2><ul class="file-list">')
    for label, relative_filename in files.items():
        filepath = os.path.join(outdir, relative_filename) # Construct full path for checking existence
        if os.path.exists(filepath):
            # Link is now relative from report_path (which is in outdir) to data_files_subdir/filename
            html_parts.append(f'<li><strong>{label}:</strong> <a href="{relative_filename}" target="_blank">{relative_filename}</a></li>')
        else:
            html_parts.append(f'<li><strong>{label}:</strong> <span class="missing">Not found ({relative_filename})</span></li>')
    html_parts.append('</ul></div>')

    # --- Footer ---
    html_parts.append(f"""
        <footer>
            Generated by Genecast CLI Tool
        </footer>
    </body>
    </html>
    """)

    full_html = "\n".join(html_parts)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    
    return report_path
