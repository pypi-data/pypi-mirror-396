import json
from pathlib import Path

import pandas as pd
from typer.testing import CliRunner

from vec_cluster.cli import app


runner = CliRunner()


def test_cli_rejects_unsupported_extension(tmp_path: Path):
    bad = tmp_path / "features.txt"
    bad.write_text("id,f1\n1,2\n", encoding="utf-8")
    result = runner.invoke(app, ["inspect", str(bad)])
    assert result.exit_code != 0
    assert "Unsupported file type" in result.output


def test_cli_inspect_jsonl_and_drop_constant(tmp_path: Path):
    data = [
        {"id": "a", "f1": 1, "f2": 1},
        {"id": "b", "f1": 1, "f2": 1},
        {"id": "c", "f1": 2, "f2": 1},
    ]
    jsonl_path = tmp_path / "features.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row) + "\n")
    result = runner.invoke(
        app,
        [
            "inspect",
            str(jsonl_path),
            "--drop-constant",
            "--constant-threshold",
            "0.001",
        ],
    )
    assert result.exit_code == 0
    assert "Data Health" in result.stdout


def test_cli_hac_threshold_json_output(tmp_path: Path):
    df = pd.DataFrame(
        {
            "id": ["a", "b", "c", "d"],
            "x": [0.1, 0.2, 1.0, 1.1],
            "y": [0.1, 0.2, 1.0, 1.1],
        }
    )
    data_path = tmp_path / "features.csv"
    df.to_csv(data_path, index=False)

    out_path = tmp_path / "clusters.jsonl"
    result = runner.invoke(
        app,
        [
            "hac",
            str(data_path),
            "--threshold",
            "0.2",
            "--out",
            str(out_path),
            "--out-format",
            "jsonl",
            "--no-scale",
            "--report-out",
            str(tmp_path / "report_hac.json"),
        ],
    )
    assert result.exit_code == 0
    assert out_path.exists()
    rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines()]
    assert set(rows[0].keys()) == {"id", "cluster"}


def test_cli_inspect_parquet_json_out_non_numeric(tmp_path: Path):
    df = pd.DataFrame(
        {
            "id": ["a", "b", "c"],
            "f1": [1, 2, 3],
            "f2": ["x", "y", "z"],  # non-numeric
            "zero": [0, 0, 0],  # all-zero column
        }
    )
    parquet_path = tmp_path / "features.parquet"
    df.to_parquet(parquet_path, index=False)
    json_out = tmp_path / "inspect.json"
    result = runner.invoke(
        app,
        [
            "inspect",
            str(parquet_path),
            "--json-out",
            str(json_out),
        ],
    )
    assert result.exit_code == 0
    assert json_out.exists()
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert payload["meta"]["dropped_allzero"]  # zero column dropped
    # non-numeric counts captured
    assert payload["meta"]["non_numeric_counts"]["f2"] == 3


def test_cli_kmeans_parquet_with_report(tmp_path: Path):
    df = pd.DataFrame(
        {
            "id": ["a", "b", "c", "d"],
            "x": [0.0, 0.1, 1.0, 1.1],
            "y": [0.0, 0.2, 1.0, 1.2],
        }
    )
    data_path = tmp_path / "features.csv"
    df.to_csv(data_path, index=False)
    out_path = tmp_path / "clusters.parquet"
    report_path = tmp_path / "kmeans_report.json"

    result = runner.invoke(
        app,
        [
            "kmeans",
            str(data_path),
            "--k",
            "2",
            "--out",
            str(out_path),
            "--out-format",
            "parquet",
            "--report-out",
            str(report_path),
        ],
    )
    assert result.exit_code == 0
    assert out_path.exists()
    assert report_path.exists()


def test_cli_dbscan_with_report(tmp_path: Path):
    df = pd.DataFrame(
        {
            "id": ["a", "b", "c"],
            "x": [0.0, 0.05, 2.0],
            "y": [0.0, 0.05, 2.0],
        }
    )
    data_path = tmp_path / "features.csv"
    df.to_csv(data_path, index=False)
    out_path = tmp_path / "clusters.csv"
    report_path = tmp_path / "dbscan_report.json"
    result = runner.invoke(
        app,
        [
            "dbscan",
            str(data_path),
            "--eps",
            "0.2",
            "--min-samples",
            "2",
            "--out",
            str(out_path),
            "--report-out",
            str(report_path),
        ],
    )
    assert result.exit_code == 0
    assert out_path.exists()
    assert report_path.exists()


def test_cli_out_format_invalid(tmp_path: Path):
    df = pd.DataFrame({"id": [1, 2], "x": [0.0, 1.0]})
    data_path = tmp_path / "features.csv"
    df.to_csv(data_path, index=False)
    out_path = tmp_path / "clusters.bad"
    result = runner.invoke(
        app,
        [
            "auto",
            str(data_path),
            "--out",
            str(out_path),
            "--out-format",
            "bad",
        ],
    )
    assert result.exit_code != 0
    assert "out-format" in result.output
