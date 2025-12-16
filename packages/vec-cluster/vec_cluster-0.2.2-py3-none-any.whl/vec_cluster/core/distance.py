from __future__ import annotations

from typing import Dict, Iterable

import numpy as np


def cosine_distance_matrix(X: np.ndarray) -> np.ndarray:
    """Compute full pairwise cosine distance matrix for small N."""
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    Xn = X / norms
    sim = Xn @ Xn.T
    sim = np.clip(sim, -1.0, 1.0)
    dist = 1.0 - sim
    return dist


def upper_triangle_values(dist: np.ndarray) -> np.ndarray:
    n = dist.shape[0]
    triu = dist[np.triu_indices(n, k=1)]
    return triu


def percentile_dict(vals: np.ndarray, ps: Iterable[int]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for p in ps:
        out[f"p{p}"] = float(np.percentile(vals, p))
    return out


def suggest_hac_thresholds(dist_vals: np.ndarray) -> Dict[str, float]:
    return {
        "tight": float(np.percentile(dist_vals, 20)),
        "medium": float(np.percentile(dist_vals, 35)),
        "loose": float(np.percentile(dist_vals, 50)),
    }
