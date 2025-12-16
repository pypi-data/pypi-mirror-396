from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
import typer
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans


def run_hac(
    X: np.ndarray, *, k: Optional[int], threshold: Optional[float]
) -> np.ndarray:
    if k is None and threshold is None:
        raise typer.BadParameter("HAC requires either --k or --threshold")

    kwargs: Dict[str, Any] = {"linkage": "average", "metric": "cosine"}

    if k is not None:
        model = AgglomerativeClustering(n_clusters=k, **kwargs)
    else:
        model = AgglomerativeClustering(
            n_clusters=None, distance_threshold=threshold, **kwargs
        )

    return model.fit_predict(X)


def run_kmeans(X: np.ndarray, *, k: int, seed: int) -> np.ndarray:
    model = KMeans(n_clusters=k, n_init="auto", random_state=seed)
    return model.fit_predict(X)


def run_dbscan(X: np.ndarray, *, eps: float, min_samples: int) -> np.ndarray:
    model = DBSCAN(metric="cosine", eps=eps, min_samples=min_samples)
    return model.fit_predict(X)
