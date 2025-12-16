import json
from pathlib import Path

import numpy as np
import pandas as pd
from typer.testing import CliRunner

from vec_cluster import __version__
from vec_cluster.cli import app
from vec_cluster.core import (
    coerce_numeric_features,
    prepare_feature_table,
    run_dbscan,
    run_hac,
)


runner = CliRunner()


def make_sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": ["a", "b", "c"],
            "f1": [1, 1, 10],
            "f2": [1, "x", 10],  # non-numeric value in row b
            "f3": [0, 0, 0],  # all-zero column should be droppable
        }
    )


def test_coerce_numeric_features_non_strict():
    df = make_sample_df()
    Xdf, nn = coerce_numeric_features(df, ["f1", "f2", "f3"], strict=False)
    assert nn["f2"] == 1  # one non-numeric coerced
    assert Xdf["f2"].isna().sum() == 1


def test_prepare_feature_table_drops_all_zero_and_scales():
    df = make_sample_df()
    ft, meta = prepare_feature_table(
        df,
        id_col="id",
        strict=False,
        scale=True,
        drop_allzero=True,
        drop_constant=False,
        constant_threshold=1e-12,
    )
    # f3 should be dropped as all-zero
    assert "f3" not in ft.feature_cols
    # two features remain
    assert meta["n_features_used"] == 2
    # scaled output should have mean ~0
    assert np.allclose(ft.X.mean(axis=0), 0, atol=1e-7)


def test_run_hac_with_k_two_clusters():
    df = pd.DataFrame(
        {
            "id": ["a", "b", "c", "d"],
            "x": [0.0, 0.1, 10.0, 10.1],
            "y": [0.0, 0.2, 10.0, 10.2],
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
    labels = run_hac(ft.X, k=2, threshold=None)
    assert sorted(set(labels.tolist())) == [0, 1]
    # first two points should be in same cluster
    assert labels[0] == labels[1]
    # far points together
    assert labels[2] == labels[3]


def test_run_dbscan_marks_outlier():
    df = pd.DataFrame(
        {
            "id": ["a", "b", "c"],
            "x": [0.0, 0.05, 2.0],
            "y": [0.0, 0.05, 2.0],
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
    labels = run_dbscan(ft.X, eps=0.2, min_samples=2)
    # cluster for first two, outlier for third
    assert -1 in labels
    assert labels[0] == labels[1]
    assert labels[2] == -1


def test_cli_auto_writes_outputs(tmp_path: Path):
    df = pd.DataFrame(
        {
            "id": ["a", "b", "c", "d"],
            "f1": [0, 0, 1, 1],
            "f2": [0, 0, 1, 1],
        }
    )
    data_path = tmp_path / "features.csv"
    df.to_csv(data_path, index=False)

    out_path = tmp_path / "clusters.csv"
    report_path = tmp_path / "report.json"

    result = runner.invoke(
        app,
        [
            "auto",
            str(data_path),
            "--out",
            str(out_path),
            "--report-out",
            str(report_path),
        ],
    )
    assert result.exit_code == 0
    assert out_path.exists()
    assert report_path.exists()

    clusters_df = pd.read_csv(out_path)
    assert set(clusters_df.columns) == {"id", "cluster"}
    # two clusters expected for simple separable data
    assert len(set(clusters_df["cluster"].tolist())) >= 1

    report = json.loads(report_path.read_text())
    assert "clusters" in report
    assert report["n_items"] == 4


def test_version_exposed():
    assert __version__ == "0.2.2"
