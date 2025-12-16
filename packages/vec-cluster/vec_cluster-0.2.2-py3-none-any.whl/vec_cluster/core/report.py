from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

from .data import FeatureTable


def compute_medoid_ids(
    ids: List[str], dist: np.ndarray, labels: np.ndarray
) -> Dict[int, str]:
    """Return medoid ID per cluster (excluding DBSCAN outliers -1)."""
    medoids: Dict[int, str] = {}
    for c in sorted(set(labels.tolist())):
        if c == -1:
            continue
        idx = np.where(labels == c)[0]
        if len(idx) == 1:
            medoids[c] = ids[idx[0]]
            continue
        sub = dist[np.ix_(idx, idx)]
        avg = sub.mean(axis=1)
        medoids[c] = ids[idx[int(np.argmin(avg))]]
    return medoids


def top_feature_deltas(
    X: np.ndarray,
    labels: np.ndarray,
    feature_cols: List[str],
    *,
    top_n: int,
) -> Dict[int, List[Dict[str, float]]]:
    """Top-N features by (cluster_mean - global_mean) absolute magnitude."""
    deltas: Dict[int, List[Dict[str, float]]] = {}
    global_mean = X.mean(axis=0)

    for c in sorted(set(labels.tolist())):
        if c == -1:
            continue
        idx = np.where(labels == c)[0]
        cm = X[idx].mean(axis=0)
        d = cm - global_mean
        order = np.argsort(np.abs(d))[::-1][:top_n]
        deltas[c] = [
            {
                "feature": feature_cols[i],
                "delta": float(d[i]),
                "cluster_mean": float(cm[i]),
                "global_mean": float(global_mean[i]),
            }
            for i in order
        ]

    return deltas


def build_report(
    ft: FeatureTable,
    labels: np.ndarray,
    *,
    dist: Optional[np.ndarray],
    top_n: int,
) -> Dict[str, Any]:
    ids = ft.ids
    clusters = sorted(set(labels.tolist()))

    medoids: Dict[int, str] = {}
    if dist is not None:
        medoids = compute_medoid_ids(ids, dist, labels)

    deltas = top_feature_deltas(ft.X, labels, ft.feature_cols, top_n=top_n)

    items: List[Dict[str, Any]] = []
    for c in clusters:
        idx = np.where(labels == c)[0]
        entry: Dict[str, Any] = {
            "cluster": int(c),
            "size": int(len(idx)),
        }
        if c == -1:
            entry["note"] = "DBSCAN outliers"
        else:
            if c in medoids:
                entry["medoid_id"] = medoids[c]
            entry["top_feature_deltas"] = deltas.get(c, [])
        items.append(entry)

    return {
        "n_items": int(len(ids)),
        "n_clusters": int(len([c for c in clusters if c != -1])),
        "has_outliers": bool(-1 in clusters),
        "clusters": items,
    }
