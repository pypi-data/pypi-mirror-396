"""Tests for preprocessing utilities."""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from polargini.preprocessing import (
    filter_cells,
    normalize,
    prepare_for_spatialde,
    prepare_for_trendsceek,
    select_genes,
    split_train_test,
)


def test_normalize():
    points = np.array([[0, 0], [1, 1], [2, 2]])
    normalized = normalize(points)
    assert normalized.min() == 0
    assert normalized.max() == 1
    assert normalized.shape == points.shape


def test_split_train_test():
    coords = np.random.rand(100, 2)
    expr = np.random.rand(100, 5)
    clusters = np.repeat(np.arange(1, 6), 20)

    (train_coords, train_expr, train_clus), (test_coords, test_expr, test_clus) = (
        split_train_test(coords, expr, clusters, train_fraction=0.8, random_state=42)
    )

    assert train_coords.shape[0] == 80
    assert test_coords.shape[0] == 20
    assert train_expr.shape[1] == 5
    assert test_expr.shape[1] == 5


def test_select_genes():
    expr = np.array([[1, 0, 0], [1, 0, 0], [1, 0, 0]])
    genes = ["gene1", "gene2", "gene3"]

    filtered_expr, filtered_genes = select_genes(expr, genes, min_expression=0.5)

    assert filtered_expr.shape[1] == 1
    assert filtered_genes == ["gene1"]


def test_filter_cells():
    coords = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
    expr = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
    clusters = np.array([1, 1, 2, -1])

    f_coords, f_expr, f_clus = filter_cells(coords, expr, clusters, cluster_ids=[1, 2])

    assert f_coords.shape[0] == 3
    assert f_expr.shape[0] == 3
    assert np.array_equal(f_clus, np.array([1, 1, 2]))

    f_coords, f_expr, f_clus = filter_cells(coords, expr, clusters)

    assert f_coords.shape[0] == 3
    assert -1 not in f_clus


def test_prepare_for_spatialde():
    with tempfile.TemporaryDirectory() as tmpdir:
        coords = np.array([[0.1, 0.2], [1.1, 1.2]])
        expr = np.array([[1, 0], [0, 1]])
        clusters = np.array([1, 1])
        genes = ["gene1", "gene2"]

        prepare_for_spatialde(coords, expr, clusters, genes, tmpdir)

        output_file = Path(tmpdir) / "cluster_1.csv"
        assert output_file.exists()

        df = pd.read_csv(output_file, index_col=0)
        assert list(df.columns) == genes
        assert len(df) == 2


def test_prepare_for_trendsceek():
    with tempfile.TemporaryDirectory() as tmpdir:
        coords = np.array([[0, 0], [1, 1]])
        expr = np.array([[1, 0], [0, 1]])
        clusters = np.array([1, 1])
        genes = ["gene1", "gene2"]

        prepare_for_trendsceek(coords, expr, clusters, genes, tmpdir)

        expr_file = Path(tmpdir) / "cluster_1_expression.csv"
        coord_file = Path(tmpdir) / "cluster_1_coordinates.csv"

        assert expr_file.exists()
        assert coord_file.exists()
