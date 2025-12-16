"""Statistical utilities for PGC."""

from __future__ import annotations

from math import erf, sqrt
from typing import List, Tuple

import numpy as np

from .metrics import rmsd
from .pgc import polar_gini_curve

try:
    from scipy.stats import fisher_exact

    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def compute_rsmd_matrix(
    coordinates: np.ndarray,
    expression: np.ndarray,
    clusters: np.ndarray,
    genes: List[str],
) -> np.ndarray:
    """Compute RSMD matrix for genes across clusters.

    For each gene and cluster, computes the RMSD between the PGC of expressing
    cells in the cluster versus all cells in the cluster.

    Parameters
    ----------
    coordinates : np.ndarray
        2D coordinates of cells (N_cells, 2).
    expression : np.ndarray
        Gene expression matrix (N_cells, N_genes).
    clusters : np.ndarray
        Cluster assignments for each cell (N_cells,). Should be 1-based integers.
    genes : List[str]
        List of gene names corresponding to expression columns.

    Returns
    -------
    rsmd_matrix : np.ndarray
        Matrix of RSMD scores (N_genes, N_clusters). NaN where no expressing cells.
    """
    coords = np.asarray(coordinates, dtype=float)
    expr = np.asarray(expression, dtype=float)
    clus = np.asarray(clusters, dtype=int)
    gene_list = list(genes)

    if coords.shape[0] != expr.shape[0] or coords.shape[0] != clus.shape[0]:
        raise ValueError(
            "Coordinates, expression, and clusters must have same number of cells"
        )
    if expr.shape[1] != len(gene_list):
        raise ValueError("Expression columns must match number of genes")
    if coords.shape[1] != 2:
        raise ValueError("Coordinates must be 2D")

    num_genes = len(gene_list)
    num_clusters = int(np.max(clus))
    rsmd_matrix = np.full((num_genes, num_clusters), np.nan)

    for i in range(num_genes):
        for j in range(1, num_clusters + 1):
            cluster_mask = clus == j
            cluster_coords = coords[cluster_mask]
            if len(cluster_coords) == 0:
                continue
            cluster_labels = np.ones(len(cluster_coords), dtype=int)

            gene_mask = cluster_mask & (expr[:, i] > 0)
            expressing_coords = coords[gene_mask]
            if len(expressing_coords) == 0:
                continue
            expressing_labels = np.full(len(expressing_coords), 2, dtype=int)

            all_coords = np.vstack([expressing_coords, cluster_coords])
            all_labels = np.concatenate([expressing_labels, cluster_labels])

            angles, curves = polar_gini_curve(all_coords, all_labels)

            if len(curves) >= 2:
                rsmd_val = rmsd(curves[0], curves[1])
                rsmd_matrix[i, j - 1] = rsmd_val

    return rsmd_matrix


def compute_enrichment_stats(
    expression: np.ndarray,
    clusters: np.ndarray,
    genes: List[str],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute gene enrichment statistics for clusters.

    For each gene and cluster, computes mean expression, percentage of expressing
    cells, and performs Fisher's exact test for enrichment in the cluster.

    Parameters
    ----------
    expression : np.ndarray
        Gene expression matrix (N_cells, N_genes).
    clusters : np.ndarray
        Cluster assignments for each cell (N_cells,). Should be 1-based integers.
    genes : List[str]
        List of gene names corresponding to expression columns.

    Returns
    -------
    mean_exp : np.ndarray
        Mean expression per gene per cluster (N_genes, N_clusters).
    perc_exp : np.ndarray
        Percentage of cells expressing each gene per cluster (N_genes, N_clusters).
    p_fisher : np.ndarray
        P-values from Fisher's exact test (N_genes, N_clusters).
    odds_ratio : np.ndarray
        Odds ratios from Fisher's exact test (N_genes, N_clusters).
    """
    if not HAS_SCIPY:
        raise ImportError("scipy is required for compute_enrichment_stats")

    expr = np.asarray(expression, dtype=float)
    clus = np.asarray(clusters, dtype=int)
    gene_list = list(genes)

    if expr.shape[0] != clus.shape[0]:
        raise ValueError("Expression and clusters must have same number of cells")
    if expr.shape[1] != len(gene_list):
        raise ValueError("Expression columns must match number of genes")

    num_genes = len(gene_list)
    num_clusters = int(np.max(clus))

    mean_exp = np.zeros((num_genes, num_clusters))
    perc_exp = np.zeros((num_genes, num_clusters))
    p_fisher = np.ones((num_genes, num_clusters))
    odds_ratio = np.ones((num_genes, num_clusters))

    for i in range(num_genes):
        for j in range(1, num_clusters + 1):
            cluster_mask = clus == j
            cluster_expr = expr[cluster_mask, i]
            mean_exp[i, j - 1] = np.mean(cluster_expr)
            perc_exp[i, j - 1] = np.mean(cluster_expr > 0)

            expr_in: int = np.sum(cluster_expr > 0)
            not_expr_in: int = len(cluster_expr) - expr_in
            expr_out: int = np.sum((~cluster_mask) & (expr[:, i] > 0))
            not_expr_out: int = np.sum((~cluster_mask) & (expr[:, i] == 0))

            table = np.array([[not_expr_out, not_expr_in], [expr_out, expr_in]])

            table = table + 1

            odds_ratio[i, j - 1], p_fisher[i, j - 1] = fisher_exact(
                table, alternative="greater"
            )

    return mean_exp, perc_exp, p_fisher, odds_ratio


def compute_pvalues(
    rmsd_matrix: np.ndarray, expression_percent: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Normalize RMSD scores and compute p-values.

    Parameters
    ----------
    rmsd_matrix:
        Matrix of raw RMSD scores where rows correspond to genes and columns to
        clusters.
    expression_percent:
        Percentage of cells expressing each gene in each cluster. Only entries
        greater than ``0.1`` are considered when computing statistics.

    Returns
    -------
    normalized:
        RMSD scores normalized by the maximum score of each cluster.
    p_values:
        Normal-distribution based p-values matching the shape of ``rmsd_matrix``.
    """
    rmsd = np.asarray(rmsd_matrix, dtype=float)
    perc = np.asarray(expression_percent, dtype=float)
    if rmsd.shape != perc.shape:
        raise ValueError("Input matrices must have the same shape")

    normalized = np.ones_like(rmsd)
    p_values = np.ones_like(rmsd)

    for j in range(rmsd.shape[1]):
        all_cluster = rmsd[:, j]
        index = np.where(perc[:, j] > 0.1)[0]
        if index.size == 0:
            continue
        values = all_cluster[index]
        max_score = values.max()
        normalized[index, j] = all_cluster[index] / max_score
        values = values / max_score
        mu = values.mean()
        sigma = values.std()
        if sigma == 0:
            p = np.where(values >= mu, 1.0, 0.0)
        else:
            z = (values - mu) / (sigma * sqrt(2.0))
            p = 0.5 * (1.0 + np.vectorize(erf)(z))
        p_values[index, j] = p

    return normalized, p_values
