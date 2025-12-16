"""Core utilities for vec-cluster."""

from .data import (
    FeatureTable,
    coerce_numeric_features,
    drop_allzero_columns,
    drop_constant_columns,
    ensure_unique_ids,
    prepare_feature_table,
)
from .distance import (
    cosine_distance_matrix,
    percentile_dict,
    suggest_hac_thresholds,
    upper_triangle_values,
)
from .cluster import run_dbscan, run_hac, run_kmeans
from .report import build_report, compute_medoid_ids, top_feature_deltas

__all__ = [
    "FeatureTable",
    "coerce_numeric_features",
    "drop_allzero_columns",
    "drop_constant_columns",
    "ensure_unique_ids",
    "prepare_feature_table",
    "cosine_distance_matrix",
    "percentile_dict",
    "suggest_hac_thresholds",
    "upper_triangle_values",
    "run_dbscan",
    "run_hac",
    "run_kmeans",
    "build_report",
    "compute_medoid_ids",
    "top_feature_deltas",
]
