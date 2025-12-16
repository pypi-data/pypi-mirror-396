from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import typer
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class FeatureTable:
    df: pd.DataFrame
    id_col: str
    feature_cols: List[str]
    ids: List[str]
    X_raw: np.ndarray  # numeric features before scaling
    X: np.ndarray  # processed features (maybe scaled)


def ensure_unique_ids(ids: List[str], *, max_examples: int = 10) -> None:
    s = pd.Series(ids)
    dup = s[s.duplicated(keep=False)]
    if not dup.empty:
        examples = dup.head(max_examples).tolist()
        msg = "Duplicate IDs detected (showing examples): " + ", ".join(
            map(str, examples)
        )
        raise typer.BadParameter(msg)


def coerce_numeric_features(
    df: pd.DataFrame,
    feature_cols: List[str],
    *,
    strict: bool,
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Return numeric feature df + a dict of non-numeric counts per column."""
    Xdf = df[feature_cols].copy()
    non_numeric_counts: Dict[str, int] = {}

    for c in feature_cols:
        if strict:
            try:
                Xdf[c] = pd.to_numeric(Xdf[c], errors="raise")
                non_numeric_counts[c] = 0
            except Exception as e:
                raise typer.BadParameter(
                    f"Non-numeric values in column '{c}': {e}"
                ) from e
        else:
            before_na = Xdf[c].isna().sum()
            Xdf[c] = pd.to_numeric(Xdf[c], errors="coerce")
            after_na = Xdf[c].isna().sum()
            non_numeric_counts[c] = int(after_na - before_na)

    return Xdf, non_numeric_counts


def drop_allzero_columns(Xdf: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    dropped = [c for c in Xdf.columns if (Xdf[c] == 0).all()]
    if dropped:
        Xdf = Xdf.drop(columns=dropped)
    return Xdf, dropped


def drop_constant_columns(
    Xdf: pd.DataFrame, *, std_threshold: float
) -> Tuple[pd.DataFrame, List[str]]:
    stds = Xdf.std(axis=0, ddof=0)
    dropped = stds[stds < std_threshold].index.tolist()
    if dropped:
        Xdf = Xdf.drop(columns=dropped)
    return Xdf, dropped


def prepare_feature_table(
    df: pd.DataFrame,
    *,
    id_col: str,
    strict: bool,
    scale: bool,
    drop_allzero: bool,
    drop_constant: bool,
    constant_threshold: float,
) -> Tuple[FeatureTable, Dict[str, Any]]:
    """Parse, validate, and preprocess features."""
    if id_col not in df.columns:
        raise typer.BadParameter(f"Missing ID column: {id_col}")

    ids = df[id_col].astype(str).tolist()
    ensure_unique_ids(ids)

    feature_cols = [c for c in df.columns if c != id_col]
    if not feature_cols:
        raise typer.BadParameter("No feature columns found (only ID column present).")

    Xdf, non_numeric_counts = coerce_numeric_features(df, feature_cols, strict=strict)

    # Fill NaNs with 0
    na_count_total = int(Xdf.isna().sum().sum())
    Xdf = Xdf.fillna(0.0)

    dropped_allzero: List[str] = []
    dropped_constant: List[str] = []

    if drop_allzero:
        Xdf, dropped_allzero = drop_allzero_columns(Xdf)

    if drop_constant:
        Xdf, dropped_constant = drop_constant_columns(
            Xdf, std_threshold=constant_threshold
        )

    if Xdf.shape[1] == 0:
        raise typer.BadParameter("All feature columns were dropped; check your input.")

    X_raw = Xdf.values.astype(float)
    X = X_raw

    if scale:
        scaler = StandardScaler()
        X = scaler.fit_transform(X_raw)

    ft = FeatureTable(
        df=df,
        id_col=id_col,
        feature_cols=Xdf.columns.tolist(),
        ids=ids,
        X_raw=X_raw,
        X=X,
    )

    meta: Dict[str, Any] = {
        "n_rows": int(df.shape[0]),
        "n_features_in": int(len(feature_cols)),
        "n_features_used": int(Xdf.shape[1]),
        "na_count_total": na_count_total,
        "non_numeric_counts": non_numeric_counts,
        "dropped_allzero": dropped_allzero,
        "dropped_constant": dropped_constant,
        "scaled": bool(scale),
    }
    return ft, meta
