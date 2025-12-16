# vec-cluster

Inspect and cluster generic vector features for entities. Lightweight CLI built with Typer + Rich.

- Repo: https://github.com/mikewong23571/vec-cluster
- License: MIT
- Python: 3.10+

## Install

```bash
uv venv
uv sync
```

## Usage

```bash
# Help
uv run vec-cluster -h

# Inspect (recommended first)
uv run vec-cluster inspect features.csv

# One-shot auto cluster
uv run vec-cluster auto features.csv
```

After publishing to PyPI you can run without installing:

```bash
uvx vec-cluster inspect features.csv
```

### Commands quick reference

- `inspect` — data health, distance distribution, HAC threshold suggestions.
- `auto` — HAC with suggested medium threshold, writes clusters + report.
- `hac` — hierarchical clustering (requires `--k` or `--threshold`).
- `kmeans` — k-means (requires `--k`).
- `dbscan` — DBSCAN (`--eps`, `--min-samples`, cluster=-1 => outlier).

## Development

```bash
uv run ruff format
uv run ruff check
uv run mypy src tests
uv run pytest          # full suite with coverage gate
```

Design/contract document: `docs/design.md`.
