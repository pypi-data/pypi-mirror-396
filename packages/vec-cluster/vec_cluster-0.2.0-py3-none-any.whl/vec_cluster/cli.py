from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from vec_cluster.core import (
    build_report,
    cosine_distance_matrix,
    percentile_dict,
    prepare_feature_table,
    run_dbscan,
    run_hac,
    run_kmeans,
    suggest_hac_thresholds,
    upper_triangle_values,
)

# -----------------------------
# Global help / contract
# -----------------------------

APP_HELP = """Inspect and cluster generic vector features for entities.

Contract (Input)
- Supported formats: .csv, .parquet, .jsonl (one JSON object per line)
- Must include an ID column (default: 'id', configurable via --id-col)
- All other columns are treated as numeric features
  - default: non-numeric -> NaN -> filled with 0.0 (warned in inspect)
  - --strict: fail fast on any non-numeric value
- ID values must be unique (otherwise the tool will error)

Contract (Preprocess)
- Default: StandardScaler on all feature columns (recommended)
  - disable via --no-scale
- Optional cleanup:
  - --drop-allzero: drop all-zero feature columns
  - --drop-constant: drop near-constant columns (std < --constant-threshold)

Contract (Output)
- Primary output table columns:
  - <id-col>
  - cluster (int)
    - DBSCAN: cluster = -1 means outlier
- Output formats: csv (default), parquet, jsonl
- Optional: --report-out to write a JSON cluster report

Commands
- inspect: sniff data health, distance distribution, and suggest parameters
- auto: run a recommended default clustering (HAC + suggested threshold)
- hac: hierarchical clustering (average linkage, cosine distance)
- kmeans: k-means clustering
- dbscan: DBSCAN clustering (cosine distance)
"""

EPILOG = """Examples
  vec-cluster inspect features.csv
  vec-cluster auto features.csv
  vec-cluster hac features.csv --threshold 0.35
  vec-cluster kmeans features.csv --k 12
  vec-cluster dbscan features.csv --eps 0.22 --min-samples 3
"""

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help=APP_HELP,
    epilog=EPILOG,
)

console = Console()


# -----------------------------
# IO helpers (CLI-facing)
# -----------------------------


def load_table(path: Path) -> pd.DataFrame:
    ext = path.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext == ".parquet":
        return pd.read_parquet(path)
    if ext == ".jsonl":
        rows = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return pd.DataFrame(rows)
    raise typer.BadParameter("Unsupported file type. Use .csv, .parquet, or .jsonl")


def write_table(df: pd.DataFrame, path: Path, out_format: str) -> None:
    out_format = out_format.lower()
    if out_format == "csv":
        df.to_csv(path, index=False, encoding="utf-8")
        return
    if out_format == "parquet":
        df.to_parquet(path, index=False)
        return
    if out_format == "jsonl":
        with path.open("w", encoding="utf-8") as f:
            for _, row in df.iterrows():
                f.write(json.dumps(row.to_dict(), ensure_ascii=False) + "\n")
        return
    raise typer.BadParameter("--out-format must be one of: csv, parquet, jsonl")


# -----------------------------
# Presentation helpers
# -----------------------------


def print_inspect_tables(meta: Dict[str, Any], dist_vals: Any) -> None:
    t1 = Table(title="Data Health")
    t1.add_column("Metric")
    t1.add_column("Value", justify="right")

    t1.add_row("rows", str(meta["n_rows"]))
    t1.add_row("features (input)", str(meta["n_features_in"]))
    t1.add_row("features (used)", str(meta["n_features_used"]))
    t1.add_row("scaled", str(meta["scaled"]))
    t1.add_row("NaNs filled", str(meta["na_count_total"]))

    dropped = []
    if meta.get("dropped_allzero"):
        dropped.append(f"allzero={len(meta['dropped_allzero'])}")
    if meta.get("dropped_constant"):
        dropped.append(f"constant={len(meta['dropped_constant'])}")
    t1.add_row("dropped cols", ", ".join(dropped) if dropped else "0")

    console.print(t1)

    nn = meta.get("non_numeric_counts", {})
    nn_total = sum(int(v) for v in nn.values())
    if nn_total > 0:
        tnn = Table(title="Non-numeric Values (coerced to 0.0)")
        tnn.add_column("Column")
        tnn.add_column("Count", justify="right")
        items = sorted(nn.items(), key=lambda kv: kv[1], reverse=True)
        for c, cnt in items[:10]:
            if cnt > 0:
                tnn.add_row(str(c), str(cnt))
        console.print(tnn)

    stats = percentile_dict(dist_vals, [1, 5, 10, 25, 50, 75, 90, 95, 99])
    t2 = Table(title="Cosine Distance Distribution (upper triangle)")
    t2.add_column("Percentile")
    t2.add_column("Value", justify="right")
    for k in ["p1", "p5", "p10", "p25", "p50", "p75", "p90", "p95", "p99"]:
        t2.add_row(k, f"{stats[k]:.4f}")
    console.print(t2)


def print_suggestions(dist_vals: Any) -> Dict[str, float]:
    sugg = suggest_hac_thresholds(dist_vals)

    t = Table(title="Suggested HAC thresholds (cosine distance)")
    t.add_column("Mode")
    t.add_column("threshold", justify="right")
    t.add_column("Meaning")

    t.add_row("tight", f"{sugg['tight']:.4f}", "more clusters, stricter")
    t.add_row("medium", f"{sugg['medium']:.4f}", "balanced")
    t.add_row("loose", f"{sugg['loose']:.4f}", "fewer clusters, looser")

    console.print(t)
    console.print(
        Text(
            "Copy/paste: vec-cluster hac <file> --threshold " + f"{sugg['medium']:.4f}",
            style="bold green",
        )
    )
    return sugg


# -----------------------------
# Common options
# -----------------------------


def common_options_help() -> str:
    return """Common options

--id-col TEXT
  Name of the ID column. Default: id

--strict
  Fail fast on any non-numeric feature value.

--no-scale
  Disable StandardScaler. Not recommended when feature scales differ.

--drop-allzero
  Drop all-zero feature columns.

--drop-constant
  Drop near-constant columns (std < --constant-threshold).

--constant-threshold FLOAT
  Threshold for near-constant detection (default: 1e-12).

--out PATH
  Output path for clusters.

--out-format [csv|parquet|jsonl]
  Output format for clusters. Default: csv.

--report-out PATH
  Write a JSON report with per-cluster summary.

--report-top-n INT
  Number of top feature deltas per cluster in the report.
"""


# -----------------------------
# Commands
# -----------------------------


@app.command(
    help="Sniff data health, distance distribution, and suggest parameters.\n\n"
    + common_options_help()
)
def inspect(
    input: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Input features file (.csv/.parquet/.jsonl)",
    ),
    id_col: str = typer.Option("id", help="ID column name"),
    strict: bool = typer.Option(False, help="Fail on non-numeric feature values"),
    no_scale: bool = typer.Option(False, help="Disable StandardScaler"),
    drop_allzero: bool = typer.Option(True, help="Drop all-zero feature columns"),
    drop_constant: bool = typer.Option(False, help="Drop near-constant columns"),
    constant_threshold: float = typer.Option(
        1e-12, help="Std threshold for near-constant columns"
    ),
    json_out: Optional[Path] = typer.Option(
        None, help="Write inspect report JSON to this path"
    ),
):
    df = load_table(input)
    ft, meta = prepare_feature_table(
        df,
        id_col=id_col,
        strict=strict,
        scale=not no_scale,
        drop_allzero=drop_allzero,
        drop_constant=drop_constant,
        constant_threshold=constant_threshold,
    )

    dist = cosine_distance_matrix(ft.X)
    vals = upper_triangle_values(dist)

    print_inspect_tables(meta, vals)
    sugg = print_suggestions(vals)

    if json_out is not None:
        payload = {
            "meta": meta,
            "distance_percentiles": percentile_dict(
                vals, [1, 5, 10, 25, 50, 75, 90, 95, 99]
            ),
            "hac_threshold_suggestions": sugg,
        }
        json_out.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        console.print(f"Wrote {json_out}")


@app.command(
    help="Auto cluster using a recommended default (HAC + suggested medium threshold).\n\n"
    + common_options_help()
)
def auto(
    input: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Input features file (.csv/.parquet/.jsonl)",
    ),
    id_col: str = typer.Option("id", help="ID column name"),
    strict: bool = typer.Option(False, help="Fail on non-numeric feature values"),
    no_scale: bool = typer.Option(False, help="Disable StandardScaler"),
    drop_allzero: bool = typer.Option(True, help="Drop all-zero feature columns"),
    drop_constant: bool = typer.Option(False, help="Drop near-constant columns"),
    constant_threshold: float = typer.Option(
        1e-12, help="Std threshold for near-constant columns"
    ),
    out: Path = typer.Option(Path("clusters.csv"), help="Output path"),
    out_format: str = typer.Option("csv", help="csv|parquet|jsonl"),
    report_out: Path = typer.Option(
        Path("report.json"), help="Cluster report output path (JSON)"
    ),
    report_top_n: int = typer.Option(8, help="Top-N feature deltas per cluster"),
):
    df = load_table(input)
    ft, _ = prepare_feature_table(
        df,
        id_col=id_col,
        strict=strict,
        scale=not no_scale,
        drop_allzero=drop_allzero,
        drop_constant=drop_constant,
        constant_threshold=constant_threshold,
    )

    dist = cosine_distance_matrix(ft.X)
    vals = upper_triangle_values(dist)
    thresh = suggest_hac_thresholds(vals)["medium"]

    labels = run_hac(ft.X, k=None, threshold=thresh)

    out_df = pd.DataFrame({id_col: ft.ids, "cluster": labels.astype(int)})
    write_table(out_df, out, out_format)

    report = build_report(ft, labels, dist=dist, top_n=report_top_n)
    report_out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    n_clusters = len([c for c in set(labels.tolist()) if c != -1])
    console.print(f"Wrote {out} ({n_clusters} clusters)")
    console.print(f"Wrote {report_out}")
    console.print(Text(f"Auto used HAC threshold={thresh:.4f}", style="bold green"))


@app.command(
    help="Hierarchical clustering (average linkage, cosine distance).\nRequires either --k or --threshold.\n\n"
    + common_options_help()
)
def hac(
    input: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Input features file (.csv/.parquet/.jsonl)",
    ),
    id_col: str = typer.Option("id", help="ID column name"),
    strict: bool = typer.Option(False, help="Fail on non-numeric feature values"),
    no_scale: bool = typer.Option(False, help="Disable StandardScaler"),
    drop_allzero: bool = typer.Option(True, help="Drop all-zero feature columns"),
    drop_constant: bool = typer.Option(False, help="Drop near-constant columns"),
    constant_threshold: float = typer.Option(
        1e-12, help="Std threshold for near-constant columns"
    ),
    k: Optional[int] = typer.Option(None, help="Number of clusters"),
    threshold: Optional[float] = typer.Option(
        None, help="Distance threshold (cosine). Smaller => more clusters."
    ),
    out: Path = typer.Option(Path("clusters.csv"), help="Output path"),
    out_format: str = typer.Option("csv", help="csv|parquet|jsonl"),
    report_out: Optional[Path] = typer.Option(None, help="Write cluster report JSON"),
    report_top_n: int = typer.Option(8, help="Top-N feature deltas per cluster"),
):
    df = load_table(input)
    ft, _ = prepare_feature_table(
        df,
        id_col=id_col,
        strict=strict,
        scale=not no_scale,
        drop_allzero=drop_allzero,
        drop_constant=drop_constant,
        constant_threshold=constant_threshold,
    )

    labels = run_hac(ft.X, k=k, threshold=threshold)

    out_df = pd.DataFrame({id_col: ft.ids, "cluster": labels.astype(int)})
    write_table(out_df, out, out_format)

    n_clusters = len([c for c in set(labels.tolist()) if c != -1])
    console.print(f"Wrote {out} ({n_clusters} clusters)")

    if report_out is not None:
        dist = cosine_distance_matrix(ft.X)
        report = build_report(ft, labels, dist=dist, top_n=report_top_n)
        report_out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        console.print(f"Wrote {report_out}")


@app.command(help="KMeans clustering. Requires --k.\n\n" + common_options_help())
def kmeans(
    input: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Input features file (.csv/.parquet/.jsonl)",
    ),
    id_col: str = typer.Option("id", help="ID column name"),
    strict: bool = typer.Option(False, help="Fail on non-numeric feature values"),
    no_scale: bool = typer.Option(False, help="Disable StandardScaler"),
    drop_allzero: bool = typer.Option(True, help="Drop all-zero feature columns"),
    drop_constant: bool = typer.Option(False, help="Drop near-constant columns"),
    constant_threshold: float = typer.Option(
        1e-12, help="Std threshold for near-constant columns"
    ),
    k: int = typer.Option(..., help="Number of clusters"),
    seed: int = typer.Option(42, help="Random seed"),
    out: Path = typer.Option(Path("clusters.csv"), help="Output path"),
    out_format: str = typer.Option("csv", help="csv|parquet|jsonl"),
    report_out: Optional[Path] = typer.Option(None, help="Write cluster report JSON"),
    report_top_n: int = typer.Option(8, help="Top-N feature deltas per cluster"),
):
    df = load_table(input)
    ft, _ = prepare_feature_table(
        df,
        id_col=id_col,
        strict=strict,
        scale=not no_scale,
        drop_allzero=drop_allzero,
        drop_constant=drop_constant,
        constant_threshold=constant_threshold,
    )

    labels = run_kmeans(ft.X, k=k, seed=seed)

    out_df = pd.DataFrame({id_col: ft.ids, "cluster": labels.astype(int)})
    write_table(out_df, out, out_format)

    n_clusters = len(set(labels.tolist()))
    console.print(f"Wrote {out} ({n_clusters} clusters)")

    if report_out is not None:
        dist = cosine_distance_matrix(ft.X)
        report = build_report(ft, labels, dist=dist, top_n=report_top_n)
        report_out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        console.print(f"Wrote {report_out}")


@app.command(
    help="DBSCAN clustering (cosine distance).\nNote: cluster=-1 means outlier.\n\n"
    + common_options_help()
)
def dbscan(
    input: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Input features file (.csv/.parquet/.jsonl)",
    ),
    id_col: str = typer.Option("id", help="ID column name"),
    strict: bool = typer.Option(False, help="Fail on non-numeric feature values"),
    no_scale: bool = typer.Option(False, help="Disable StandardScaler"),
    drop_allzero: bool = typer.Option(True, help="Drop all-zero feature columns"),
    drop_constant: bool = typer.Option(False, help="Drop near-constant columns"),
    constant_threshold: float = typer.Option(
        1e-12, help="Std threshold for near-constant columns"
    ),
    eps: float = typer.Option(
        0.25, help="Neighborhood radius (cosine distance). Smaller => stricter."
    ),
    min_samples: int = typer.Option(3, help="Min samples to form a core point"),
    out: Path = typer.Option(Path("clusters.csv"), help="Output path"),
    out_format: str = typer.Option("csv", help="csv|parquet|jsonl"),
    report_out: Optional[Path] = typer.Option(None, help="Write cluster report JSON"),
    report_top_n: int = typer.Option(8, help="Top-N feature deltas per cluster"),
):
    df = load_table(input)
    ft, _ = prepare_feature_table(
        df,
        id_col=id_col,
        strict=strict,
        scale=not no_scale,
        drop_allzero=drop_allzero,
        drop_constant=drop_constant,
        constant_threshold=constant_threshold,
    )

    labels = run_dbscan(ft.X, eps=eps, min_samples=min_samples)

    out_df = pd.DataFrame({id_col: ft.ids, "cluster": labels.astype(int)})
    write_table(out_df, out, out_format)

    clusters = set(labels.tolist())
    n_clusters = len([c for c in clusters if c != -1])
    n_outliers = int((labels == -1).sum())
    console.print(f"Wrote {out} ({n_clusters} clusters; outliers={n_outliers})")

    if report_out is not None:
        dist = cosine_distance_matrix(ft.X)
        report = build_report(ft, labels, dist=dist, top_n=report_top_n)
        report_out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        console.print(f"Wrote {report_out}")


if __name__ == "__main__":
    app()
