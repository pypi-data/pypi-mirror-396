#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone Preprocessing Script: Converts FASTA files into CSV artifacts (labels, features, distance matrices).
No external module dependencies - all functions are self-contained.

Usage:
    python3 dist.py --fasta "path/*.fa" --mode nuc --kmer 5 --prefix output
    python3 dist.py --fasta "path/*.fa" --mode prot --win 3 --prefix output
"""

from __future__ import annotations

import gzip
import math
import os
import glob
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==================== FASTA File Input/Output ====================

def read_fasta(path: Path) -> Iterable[Tuple[str, str]]:
    """
    Reads a FASTA file (supports gzip compression).

    Args:
        path (Path): Path to the FASTA file.

    Yields:
        Iterable[Tuple[str, str]]: An iterator where each element is a (header, sequence) tuple.
    """
    # Select appropriate opener based on file suffix
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as handle:
        header = None
        seq_chunks: List[str] = []
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                # If header exists, a sequence has been read, yield result
                if header is not None:
                    yield header, "".join(seq_chunks)
                # Start new sequence
                header = line[1:]
                seq_chunks = []
            else:
                # Accumulate sequence chunks
                seq_chunks.append(line)
        # Handle the last sequence at end of file
        if header is not None:
            yield header, "".join(seq_chunks)


def infer_gene_from_filename(path: Path) -> str:
    """
    Infers gene name hint from filename.

    Args:
        path (Path): File path.

    Returns:
        str: Inferred gene name.
    """
    name = path.name
    # Remove common file extensions
    if name.endswith(".fasta.gz"):
        base = name[: -len(".fasta.gz")]
    elif name.endswith(".fa.gz"):
        base = name[: -len(".fa.gz")]
    elif name.endswith(".fasta"):
        base = name[: -len(".fasta")]
    elif name.endswith(".fa"):
        base = name[: -len(".fa")]
    else:
        base = path.stem
    parts = base.split(".")
    # Usually the gene name is in the last part of the filename segment
    return parts[-1] if len(parts) > 1 else base


# ==================== Label Generation ====================


def original_label(
    header: str, gene_hint: str, counter: Dict[str, int]
) -> Tuple[str, str]:
    """
    Cleans label:
    1. Removes leading/trailing whitespace.
    2. Replaces all internal whitespace (spaces, tabs) with underscores.
    3. Removes commas (to prevent breaking CSV format).
    4. Handles duplicates.

    Args:
        header (str): FASTA sequence header (without >).
        gene_hint (str): Filename hint.
        counter (Dict[str, int]): Used to ensure label uniqueness.

    Returns:
        Tuple[str, str]: (Cleaned label, gene_hint).
    """
    # 1. Remove leading/trailing whitespace
    label = header.strip()

    # 2. Replace internal whitespace (spaces, Tabs etc.) with single underscore
    # E.g.: "Gene A   Isoform 1" -> "Gene_A_Isoform_1"
    label = re.sub(r"\s+", "_", label)

    # 3. Remove commas (because output is CSV, comma is separator, must be removed)
    label = label.replace(",", "")

    # 4. Simple uniqueness handling: if header is identical, add suffix _1, _2
    counter[label] = counter.get(label, 0) + 1
    if counter[label] > 1:
        label = f"{label}_{counter[label]}"

    return label, gene_hint


# ==================== Sequence Utility Functions ====================

def clean_dna(seq: str) -> str:
    """
    Removes non-alphabetic characters from sequence and converts to uppercase.

    Args:
        seq (str): Original DNA sequence.

    Returns:
        str: Cleaned DNA sequence.
    """
    return "".join(ch for ch in seq.upper() if ch.isalpha())


def looks_like_dna(seq: str, threshold: float = 0.85) -> bool:
    """
    Checks if sequence looks like DNA (based on proportion of ACGTN characters).

    Args:
        seq (str): Input sequence.
        threshold (float): Threshold for DNA character proportion.

    Returns:
        bool: Returns True if sequence looks like DNA.
    """
    seq = "".join(ch for ch in seq.upper() if ch.isalpha())
    if not seq:
        return False
    dna_letters = set("ACGTN")
    dna_count = sum(1 for ch in seq if ch in dna_letters)
    return dna_count / len(seq) >= threshold


# ==================== Translation ====================

# Standard Codon Table
CODON_TABLE = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*", # * is stop codon
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}


def translate(seq: str) -> str:
    """
    Translates DNA sequence to protein sequence.

    Args:
        seq (str): DNA sequence.

    Returns:
        str: Protein sequence.
    """
    seq = clean_dna(seq)
    # Ensure sequence length is multiple of 3
    seq = seq[: len(seq) - (len(seq) % 3)]
    aas: List[str] = []
    for i in range(0, len(seq), 3):
        codon = seq[i : i + 3]
        # Use 'X' when encountering unknown codon
        aas.append(CODON_TABLE.get(codon, "X") )
    # Replace stop codon '*' with 'X'
    return "".join(aas).replace("*", "X")


# ==================== Protein Features ====================

# Amino Acid Physicochemical Properties: (Hydrophobicity, Molecular Weight, Charge)
AA_PROP = {
    "A": (1.8, 88.6, 0), "R": (-4.5, 173.4, 1), "N": (-3.5, 114.1, 0),
    "D": (-3.5, 111.1, -1), "C": (2.5, 108.5, 0), "Q": (-3.5, 143.8, 0),
    "E": (-3.5, 138.4, -1), "G": (-0.4, 60.1, 0), "H": (-3.2, 153.2, 0.1),
    "I": (4.5, 166.7, 0), "L": (3.8, 166.7, 0), "K": (-3.9, 168.6, 1),
    "M": (1.9, 162.9, 0), "F": (2.8, 189.9, 0), "P": (-1.6, 112.7, 0),
    "S": (-0.8, 89.0, 0), "T": (-0.7, 116.1, 0), "W": (-0.9, 227.8, 0),
    "Y": (-1.3, 193.6, 0), "V": (4.2, 140.0, 0), "X": (0.0, 140.0, 0), # Unknown amino acid
}


def aa_prop_vector(seq: str, win: int) -> Dict[Tuple[float, float, float], float]:
    """
    Generates amino acid property vector using sliding window.

    Args:
        seq (str): Protein sequence.
        win (int): Sliding window size.

    Returns:
        Dict[Tuple[float, float, float], float]: Feature vector, keys are property tuples, values are frequencies.
    """
    seq = "".join(ch for ch in seq.upper() if ch.isalpha())
    if not seq:
        return {}
    if win <= 0:
        win = 1
    if len(seq) < win:
        windows = [seq]
    else:
        windows = [seq[i : i + win] for i in range(len(seq) - win + 1)]
    
    buckets: Counter[Tuple[float, float, float]] = Counter()
    for window in windows:
        props = [AA_PROP.get(aa, AA_PROP["X"]) for aa in window]
        # Calculate average properties within window
        mean = tuple(sum(p[j] for p in props) / len(props) for j in range(3))
        # Round average to one decimal place as feature bucket
        bucket = tuple(round(x, 1) for x in mean)
        buckets[bucket] += 1
    
    total = sum(buckets.values()) or 1.0
    # Normalize to frequency
    return {k: c / total for k, c in buckets.items()}


# ==================== Distance Calculation ====================

def cosine_distance_sparse(vectors: List[Dict]) -> np.ndarray:
    """
    Calculates pairwise cosine distances from sparse vectors.

    Args:
        vectors (List[Dict]): List of sparse feature vectors.

    Returns:
        np.ndarray: Pairwise distance matrix.
    """
    n = len(vectors)
    dist = np.zeros((n, n), dtype=float)
    # Precompute norm for each vector
    norms = [math.sqrt(sum(val * val for val in vec.values())) for vec in vectors]
    for i in range(n):
        for j in range(i + 1, n):
            if norms[i] == 0 or norms[j] == 0:
                d = 1.0 # If any vector is zero vector, distance is 1
            else:
                # Calculate dot product
                keys = vectors[i].keys() & vectors[j].keys()
                dot = sum(vectors[i][k] * vectors[j][k] for k in keys)
                # Calculate cosine similarity and convert to distance
                d = 1.0 - dot / (norms[i] * norms[j])
            dist[i, j] = dist[j, i] = d
    return dist


def build_feature_matrix(vectors: List[Dict]) -> Tuple[np.ndarray, List]:
    """
    Converts list of sparse vectors to dense matrix.

    Args:
        vectors (List[Dict]): List of sparse feature vectors.

    Returns:
        Tuple[np.ndarray, List]: (Dense feature matrix, list of feature names).
    """
    key_set = set()
    for vec in vectors:
        key_set.update(vec.keys())
    keys = sorted(key_set)
    if not keys:
        return np.zeros((len(vectors), 0)), []
    
    mat = np.zeros((len(vectors), len(keys)), dtype=float)
    key_index = {k: idx for idx, k in enumerate(keys)}
    for i, vec in enumerate(vectors):
        for k, v in vec.items():
            mat[i, key_index[k]] = v
    return mat, keys


# ==================== Pipeline Functions ====================

def run_nucleotide(records: List[Tuple[str, str, str]], k: int):
    """
    Nucleotide k-mer pipeline.

    Args:
        records (List[Tuple[str, str, str]]): List of records (header, sequence, gene_hint).
        k (int): k value for k-mer.

    Returns:
        Tuple: (Label list, feature matrix, distance matrix).
    """
    print(f"[Pipeline] Running nucleotide k-mer pipeline with k={k}...")
    counter: Dict[str, int] = {}
    labels: List[str] = []
    seqs: List[str] = []
    # Generate labels and clean sequences
    for h, seq, gene in records:
        lbl, _ = original_label(h, gene, counter)
        labels.append(lbl)
        seqs.append(clean_dna(seq))

    if k <= 0:
        k = 1
    try:
        # Use CountVectorizer to calculate k-mer frequencies
        vec = CountVectorizer(analyzer="char", ngram_range=(k, k))
        kmer_matrix = vec.fit_transform(seqs)
    except ValueError as e:
        raise SystemExit(f"Failed to build k-mer matrix (k={k}): {e}")

    feature_matrix = kmer_matrix.toarray()
    # Calculate cosine similarity and convert to distance
    similarity = cosine_similarity(kmer_matrix)
    similarity = np.power(similarity, 2) # Square to amplify differences
    dist = 1.0 - similarity
    np.fill_diagonal(dist, 0.0)
    dist[dist < 0] = 0.0
    return labels, feature_matrix, dist


def run_protein(records: List[Tuple[str, str, str]], win: int):
    """
    Protein property pipeline.

    Args:
        records (List[Tuple[str, str, str]]): List of records (header, sequence, gene_hint).
        win (int): Sliding window size.

    Returns:
        Tuple: (Label list, feature matrix, distance matrix).
    """
    print(f"[Pipeline] Running protein property pipeline with window={win}...")
    counter: Dict[str, int] = {}
    labels: List[str] = []
    for h, _, gene in records:
        lbl, _ = original_label(h, gene, counter)
        labels.append(lbl)
    
    aa_seqs = []
    for _, seq, _ in records:
        # If looks like DNA, translate first
        if looks_like_dna(seq):
            aa_seqs.append(translate(seq))
        else:
            aa_seqs.append("".join(ch for ch in seq.upper() if ch.isalpha()))
    
    vectors = [aa_prop_vector(seq, win) for seq in aa_seqs]
    dist = cosine_distance_sparse(vectors)
    features, _ = build_feature_matrix(vectors)
    return labels, features, dist


# ==================== File Loading ====================

def get_base_key(path: Path) -> str:
    """
    Gets unique base key from path by stripping FASTA/Gzip extensions.
    Used to treat 'gene.fa' and 'gene.fasta.gz' as the same file.
    """
    name = path.name
    if name.endswith(".gz"):
        name = name[:-3]
    
    if name.endswith(".fasta"):
        return name[:-6]
    if name.endswith(".fa"):
        return name[:-3]
    
    # Fallback for other extensions (like .fna)
    return Path(name).stem


def load_records(patterns: List[str], max_seqs: int) -> List[Tuple[str, str, str]]:
    """
    Loads FASTA records from file patterns, handling mixed extensions and duplicates.

    Args:
        patterns (List[str]): List of glob patterns for file paths.
        max_seqs (int): Maximum sequence limit.

    Returns:
        List[Tuple[str, str, str]]: List of records (header, sequence, gene_hint).
    """
    files: List[Path] = []
    for pattern in patterns:
        matched = glob.glob(pattern, recursive=True)
        files.extend(sorted(Path(p) for p in matched))
    
    # If both compressed and uncompressed versions exist, prefer uncompressed
    files = sorted(files, key=lambda p: (p.name.endswith(".gz"), p.name))
    
    # Deduplicate using base key
    seen = set()
    uniq: List[Path] = []
    for fp in files:
        key = get_base_key(fp)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(fp)
    
    records: List[Tuple[str, str, str]] = []
    for fp in uniq:
        gene_hint = infer_gene_from_filename(fp)
        lower_hint = (gene_hint or "").lower()
        
        # If filename is generic, fall back to using parent directory name as gene hint
        if lower_hint in {"cds", "fna", "fa", "fasta", "protein", "prot", "faa"}:
            parent = fp.parent.name
            grand = fp.parent.parent.name if fp.parent.parent else ""
            if parent.lower() not in {"cds", "protein", "prot"} and parent:
                gene_hint = parent
            elif grand:
                gene_hint = grand
        
        for header, seq in read_fasta(fp):
            records.append((header, seq, gene_hint))
    
    # If exceeding max sequences, truncate
    if max_seqs and max_seqs > 0 and len(records) > max_seqs:
        records = records[:max_seqs]
    return records


# ==================== File Saving ====================

def save_matrix_csv(mat: np.ndarray, path: Path):
    """
    Saves matrix as CSV file.

    Args:
        mat (np.ndarray): Numpy matrix to save.
        path (Path): Output file path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(path, mat, delimiter=",")


def save_labels(labels: List[str], path: Path):
    """
    Saves label list as CSV file.

    Args:
        labels (List[str]): Label list.
        path (Path): Output file path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write("label\n")
        for lbl in labels:
            f.write(f"{lbl}\n")


# ==================== Main Function ====================

def main(fasta_patterns: List[str], mode: str, kmer: int, win: int, outdir: str, prefix: str, max_seqs: int):
    """Main execution logic."""
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    records = load_records(fasta_patterns, max_seqs)
    if not records:
        print("No sequences found for given patterns.")
        return

    base = out_path / prefix
    if mode == "nuc":
        labels, features, dist = run_nucleotide(records, kmer)
    else:
        labels, features, dist = run_protein(records, win)

    # Save artifacts
    save_labels(labels, Path(f"{base}_labels.csv"))
    save_matrix_csv(features, Path(f"{base}_features.csv"))
    save_matrix_csv(dist, Path(f"{base}_dist.csv"))
    print(f"[done] Wrote {base}_labels.csv, {base}_features.csv, {base}_dist.csv")