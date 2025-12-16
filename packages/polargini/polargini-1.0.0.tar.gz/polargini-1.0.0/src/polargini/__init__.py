"""Top-level package for PGC."""

from .io import (
    convert_rsmd_results,
    legacy_to_csv,
    load_csv,
    load_legacy_dataset,
    load_legacy_for_pgc,
)
from .metrics import gini, rmsd
from .pgc import polar_gini_curve
from .plotting import plot_embedding_and_pgc, plot_pgc
from .preprocessing import (
    filter_cells,
    normalize,
    prepare_for_spatialde,
    prepare_for_trendsceek,
    select_genes,
    split_train_test,
)
from .stats import compute_enrichment_stats, compute_pvalues, compute_rsmd_matrix

__all__ = [
    "polar_gini_curve",
    "gini",
    "rmsd",
    "compute_pvalues",
    "compute_rsmd_matrix",
    "compute_enrichment_stats",
    "plot_pgc",
    "plot_embedding_and_pgc",
    "normalize",
    "split_train_test",
    "prepare_for_spatialde",
    "prepare_for_trendsceek",
    "select_genes",
    "filter_cells",
    "load_csv",
    "load_legacy_dataset",
    "legacy_to_csv",
    "load_legacy_for_pgc",
    "convert_rsmd_results",
]

__version__ = "1.0.0"
