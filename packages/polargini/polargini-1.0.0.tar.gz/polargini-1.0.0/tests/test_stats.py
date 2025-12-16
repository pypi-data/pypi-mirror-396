"""Tests for statistical utilities."""

import numpy as np

from polargini.stats import (
    compute_enrichment_stats,
    compute_pvalues,
    compute_rsmd_matrix,
)


def test_compute_pvalues():
    rmsd = np.array([[1.0, 2.0], [2.0, 0.5]])
    perc = np.array([[0.2, 0.05], [0.3, 0.2]])
    normalized, pval = compute_pvalues(rmsd, perc)
    expected_norm = np.array([[0.5, 1.0], [1.0, 1.0]])
    expected_p = np.array([[0.15865525, 1.0], [0.84134475, 1.0]])
    assert np.allclose(normalized, expected_norm)
    assert np.allclose(pval, expected_p)
    assert ((pval >= 0) & (pval <= 1)).all()


def test_compute_rsmd_matrix():
    coordinates = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    expression = np.array([[1, 0], [0, 1], [1, 1], [0, 0]])
    clusters = np.array([1, 1, 2, 2])
    genes = ["gene1", "gene2"]

    rsmd_matrix = compute_rsmd_matrix(coordinates, expression, clusters, genes)

    assert rsmd_matrix.shape == (2, 2)
    assert not np.all(np.isnan(rsmd_matrix))
    valid_values = rsmd_matrix[~np.isnan(rsmd_matrix)]
    assert np.all(valid_values >= 0)


def test_compute_enrichment_stats():
    try:
        from scipy.stats import fisher_exact  # noqa: F401
    except ImportError:
        import pytest

        pytest.skip("scipy not available")

    expression = np.array([[1, 0], [0, 1], [1, 1], [0, 0]])
    clusters = np.array([1, 1, 2, 2])
    genes = ["gene1", "gene2"]

    mean_exp, perc_exp, p_fisher, odds_ratio = compute_enrichment_stats(
        expression, clusters, genes
    )

    assert mean_exp.shape == (2, 2)
    assert perc_exp.shape == (2, 2)
    assert p_fisher.shape == (2, 2)
    assert odds_ratio.shape == (2, 2)

    assert np.all(mean_exp >= 0)
    assert np.all((perc_exp >= 0) & (perc_exp <= 1))
    assert np.all((p_fisher >= 0) & (p_fisher <= 1))
    assert np.all(odds_ratio > 0)
