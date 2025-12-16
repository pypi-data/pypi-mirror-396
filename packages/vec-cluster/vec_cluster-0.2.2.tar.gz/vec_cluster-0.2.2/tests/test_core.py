import numpy as np
import pandas as pd
import pytest
import typer

from vec_cluster.core import (
    FeatureTable,
    build_report,
    compute_medoid_ids,
    cosine_distance_matrix,
    coerce_numeric_features,
    drop_constant_columns,
    ensure_unique_ids,
    percentile_dict,
    prepare_feature_table,
    run_hac,
    run_kmeans,
    top_feature_deltas,
    upper_triangle_values,
)


def make_ft() -> FeatureTable:
    df = pd.DataFrame(
        {
            "id": ["a", "b", "c", "d"],
            "x": [0.0, 0.1, 1.0, 1.1],
            "y": [0.0, 0.2, 1.0, 1.2],
        }
    )
    ft, _ = prepare_feature_table(
        df,
        id_col="id",
        strict=False,
        scale=True,
        drop_allzero=True,
        drop_constant=False,
        constant_threshold=1e-12,
    )
    return ft


def test_ensure_unique_ids_raises_on_duplicates():
    with pytest.raises(typer.BadParameter):
        ensure_unique_ids(["a", "a"])


def test_drop_constant_columns_removes_low_std():
    df = pd.DataFrame({"a": [1, 1, 1], "b": [1, 1.1, 1.2]})
    Xdf, dropped = drop_constant_columns(df, std_threshold=0.05)
    assert dropped == ["a"]
    assert list(Xdf.columns) == ["b"]


def test_prepare_feature_table_strict_fails_on_non_numeric():
    df = pd.DataFrame({"id": [1, 2], "f": [1, "x"]})
    with pytest.raises(typer.BadParameter):
        prepare_feature_table(
            df,
            id_col="id",
            strict=True,
            scale=False,
            drop_allzero=True,
            drop_constant=False,
            constant_threshold=1e-12,
        )


def test_distance_helpers_cover_zero_vector():
    X = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]])
    dist = cosine_distance_matrix(X)
    # zero vector should not produce NaN; distance to itself becomes 1.0
    assert np.allclose(np.diag(dist), [0.0, 0.0, 1.0])
    tri = upper_triangle_values(dist)
    assert len(tri) == 3  # nC2 for n=3
    stats = percentile_dict(tri, [0, 50, 100])
    assert set(stats.keys()) == {"p0", "p50", "p100"}


def test_prepare_feature_table_errors_on_missing_id_and_no_features():
    df_no_id = pd.DataFrame({"x": [1, 2]})
    with pytest.raises(typer.BadParameter):
        prepare_feature_table(
            df_no_id,
            id_col="id",
            strict=False,
            scale=False,
            drop_allzero=True,
            drop_constant=False,
            constant_threshold=1e-12,
        )

    df_only_id = pd.DataFrame({"id": [1, 2]})
    with pytest.raises(typer.BadParameter):
        prepare_feature_table(
            df_only_id,
            id_col="id",
            strict=False,
            scale=False,
            drop_allzero=True,
            drop_constant=False,
            constant_threshold=1e-12,
        )


def test_prepare_feature_table_drop_constant_all_columns_error():
    df = pd.DataFrame({"id": [1, 2, 3], "f": [1.0, 1.0, 1.0]})
    with pytest.raises(typer.BadParameter):
        prepare_feature_table(
            df,
            id_col="id",
            strict=False,
            scale=False,
            drop_allzero=False,
            drop_constant=True,
            constant_threshold=0.01,
        )


def test_coerce_numeric_features_strict_sets_zero_count_when_clean():
    df = pd.DataFrame({"id": [1, 2], "f": [1.2, 3.4]})
    Xdf, counts = coerce_numeric_features(df, ["f"], strict=True)
    assert counts["f"] == 0
    assert Xdf["f"].dtype != object


def test_run_hac_threshold_branch_and_error():
    ft = make_ft()
    labels = run_hac(ft.X, k=None, threshold=0.3)
    assert len(labels) == len(ft.ids)
    with pytest.raises(typer.BadParameter):
        run_hac(ft.X, k=None, threshold=None)


def test_run_kmeans_basic():
    ft = make_ft()
    labels = run_kmeans(ft.X, k=2, seed=0)
    assert len(labels) == len(ft.ids)
    assert set(labels) <= {0, 1}


def test_report_helpers_medoid_and_top_features():
    ft = make_ft()
    labels = np.array([0, 0, 1, -1])  # include outlier
    dist = cosine_distance_matrix(ft.X)
    medoids = compute_medoid_ids(ft.ids, dist, labels)
    assert set(medoids.keys()) == {0, 1}
    deltas = top_feature_deltas(ft.X, labels, ft.feature_cols, top_n=1)
    assert 0 in deltas and 1 in deltas
    report = build_report(ft, labels, dist=dist, top_n=1)
    assert report["n_items"] == 4
    assert report["has_outliers"] is True
    # outlier cluster should carry note
    outlier_entry = [c for c in report["clusters"] if c["cluster"] == -1][0]
    assert outlier_entry["note"] == "DBSCAN outliers"
