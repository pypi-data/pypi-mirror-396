"""Preprocessing utilities for data preparation."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd


def normalize(points: np.ndarray) -> np.ndarray:
    """Normalize points to [0, 1] range per axis."""
    pts = np.asarray(points, dtype=float)
    min_vals = pts.min(axis=0)
    max_vals = pts.max(axis=0)
    return (pts - min_vals) / (max_vals - min_vals)


def split_train_test(
    coordinates: np.ndarray,
    expression: np.ndarray,
    clusters: np.ndarray,
    train_fraction: float = 0.8,
    random_state: Optional[int] = None,
) -> Tuple[
    Tuple[np.ndarray, np.ndarray, np.ndarray],
    Tuple[np.ndarray, np.ndarray, np.ndarray],
]:
    """Split data into training and testing sets.

    Parameters
    ----------
    coordinates : np.ndarray
        Cell coordinates (N_cells, 2).
    expression : np.ndarray
        Gene expression matrix (N_cells, N_genes).
    clusters : np.ndarray
        Cluster assignments (N_cells,).
    train_fraction : float
        Fraction of data to use for training (default 0.8).
    random_state : int, optional
        Random seed for reproducibility.

    Returns
    -------
    train_data : Tuple[np.ndarray, np.ndarray, np.ndarray]
        Training coordinates, expression, and clusters.
    test_data : Tuple[np.ndarray, np.ndarray, np.ndarray]
        Test coordinates, expression, and clusters.
    """
    coords = np.asarray(coordinates, dtype=float)
    expr = np.asarray(expression, dtype=float)
    clus = np.asarray(clusters)

    if coords.shape[0] != expr.shape[0] or coords.shape[0] != clus.shape[0]:
        raise ValueError(
            "Coordinates, expression, and clusters must have same number of cells"
        )
    if train_fraction <= 0 or train_fraction >= 1:
        raise ValueError("train_fraction must be between 0 and 1")

    n_cells = len(clus)
    if random_state is not None:
        np.random.seed(random_state)

    indices = np.random.permutation(n_cells)
    n_train = int(np.round(n_cells * train_fraction))

    train_idx = indices[:n_train]
    test_idx = indices[n_train:]

    train_data = (coords[train_idx], expr[train_idx], clus[train_idx])
    test_data = (coords[test_idx], expr[test_idx], clus[test_idx])

    return train_data, test_data


def prepare_for_spatialde(
    coordinates: np.ndarray,
    expression: np.ndarray,
    clusters: np.ndarray,
    genes: List[str],
    output_dir: str,
) -> None:
    """Prepare data for SpatialDE analysis.

    Writes expression matrices for each cluster with coordinates as index.

    Parameters
    ----------
    coordinates : np.ndarray
        Cell coordinates (N_cells, 2).
    expression : np.ndarray
        Gene expression matrix (N_cells, N_genes).
    clusters : np.ndarray
        Cluster assignments (N_cells,).
    genes : List[str]
        Gene names.
    output_dir : str
        Output directory for cluster files.
    """
    coords = np.asarray(coordinates, dtype=float)
    expr = np.asarray(expression, dtype=float)
    clus = np.asarray(clusters, dtype=int)
    gene_list = list(genes)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    unique_clusters = np.unique(clus)
    for cluster_id in unique_clusters:
        if cluster_id < 0:
            continue

        mask = clus == cluster_id
        cluster_coords = coords[mask]
        cluster_expr = expr[mask]

        coord_index = [f"{c[0]:.6g}x{c[1]:.6g}" for c in cluster_coords]
        df = pd.DataFrame(cluster_expr, index=coord_index, columns=gene_list)

        output_file = output_path / f"cluster_{cluster_id}.csv"
        df.to_csv(output_file)


def prepare_for_trendsceek(
    coordinates: np.ndarray,
    expression: np.ndarray,
    clusters: np.ndarray,
    genes: List[str],
    output_dir: str,
) -> None:
    """Prepare data for Trendsceek analysis.

    Writes separate expression and coordinate files for each cluster.

    Parameters
    ----------
    coordinates : np.ndarray
        Cell coordinates (N_cells, 2).
    expression : np.ndarray
        Gene expression matrix (N_cells, N_genes).
    clusters : np.ndarray
        Cluster assignments (N_cells,).
    genes : List[str]
        Gene names.
    output_dir : str
        Output directory for cluster files.
    """
    coords = np.asarray(coordinates, dtype=float)
    expr = np.asarray(expression, dtype=float)
    clus = np.asarray(clusters, dtype=int)
    gene_list = list(genes)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    unique_clusters = np.unique(clus)
    for cluster_id in unique_clusters:
        if cluster_id < 0:
            continue

        mask = clus == cluster_id
        cluster_coords = coords[mask]
        cluster_expr = expr[mask]

        expr_df = pd.DataFrame(cluster_expr.T, index=gene_list)
        expr_file = output_path / f"cluster_{cluster_id}_expression.csv"
        expr_df.to_csv(expr_file, header=False)

        coord_df = pd.DataFrame(cluster_coords, columns=["x", "y"])
        coord_file = output_path / f"cluster_{cluster_id}_coordinates.csv"
        coord_df.to_csv(coord_file, index=False, header=False)


def select_genes(
    expression: np.ndarray,
    genes: List[str],
    min_expression: float = 0.1,
) -> Tuple[np.ndarray, List[str]]:
    """Filter genes by minimum mean expression.

    Parameters
    ----------
    expression : np.ndarray
        Gene expression matrix (N_cells, N_genes).
    genes : List[str]
        Gene names.
    min_expression : float
        Minimum mean expression threshold for gene inclusion.

    Returns
    -------
    filtered_expression : np.ndarray
        Filtered expression matrix.
    filtered_genes : List[str]
        Filtered gene names.
    """
    expr = np.asarray(expression, dtype=float)
    gene_list = list(genes)

    if expr.shape[1] != len(gene_list):
        raise ValueError("Expression columns must match number of genes")

    mean_expr = expr.mean(axis=0)
    mask = mean_expr > min_expression

    filtered_expr = expr[:, mask]
    filtered_genes = [g for i, g in enumerate(gene_list) if mask[i]]

    return filtered_expr, filtered_genes


def filter_cells(
    coordinates: np.ndarray,
    expression: np.ndarray,
    clusters: np.ndarray,
    cluster_ids: Optional[List[int]] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Filter cells by cluster assignment.

    Parameters
    ----------
    coordinates : np.ndarray
        Cell coordinates (N_cells, 2).
    expression : np.ndarray
        Gene expression matrix (N_cells, N_genes).
    clusters : np.ndarray
        Cluster assignments (N_cells,).
    cluster_ids : List[int], optional
        List of cluster IDs to keep. If None, keeps all non-negative clusters.

    Returns
    -------
    filtered_coordinates : np.ndarray
        Filtered coordinates.
    filtered_expression : np.ndarray
        Filtered expression matrix.
    filtered_clusters : np.ndarray
        Filtered cluster assignments.
    """
    coords = np.asarray(coordinates, dtype=float)
    expr = np.asarray(expression, dtype=float)
    clus = np.asarray(clusters)

    if coords.shape[0] != expr.shape[0] or coords.shape[0] != clus.shape[0]:
        raise ValueError(
            "Coordinates, expression, and clusters must have same number of cells"
        )

    if cluster_ids is None:
        mask = clus >= 0
    else:
        mask = np.isin(clus, cluster_ids)

    return coords[mask], expr[mask], clus[mask]
