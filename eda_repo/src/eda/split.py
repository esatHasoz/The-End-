from __future__ import annotations

import numpy as np
import pandas as pd

from .config import FALLBACK_BLOCKS, GAP_FRACTION, MIN_PER_SPLIT, RATIOS, SEED


def _time_order(order, ratios, gap):
    n = len(order)
    n_tr = int(n * ratios[0])
    n_va = int(n * ratios[1])
    lab = np.full(n, "gap", dtype=object)
    lab[:n_tr] = "train"
    lab[n_tr + gap:n_tr + gap + n_va] = "val"
    lab[n_tr + gap + n_va + gap:] = "test"
    return lab


def _blocks(order, ratios, gap_fraction, blocks, rng):
    n = len(order)
    b = max(3, min(blocks, n // 10))
    ids = np.arange(n) * b // n
    n_va = max(1, round(b * ratios[1]))
    n_te = max(1, round(b * ratios[2]))
    perm = rng.permutation(b)
    assign = np.full(b, "train", dtype=object)
    assign[perm[:n_va]] = "val"
    assign[perm[n_va:n_va + n_te]] = "test"
    lab = assign[ids]
    g = max(1, int(gap_fraction * n / b))
    gap = np.zeros(n, dtype=bool)
    starts = np.searchsorted(ids, np.arange(1, b))
    for k, s in enumerate(starts, start=1):
        if assign[k] != assign[k - 1]:
            gap[max(0, s - g):s + g] = True
    lab = lab.copy()
    lab[gap] = "gap"
    return lab


def _counts(lab):
    return {k: int((lab == k).sum()) for k in ("train", "val", "test", "gap")}


def time_split(
    df, label_col, time_col, ratios=RATIOS, gap_fraction=GAP_FRACTION,
    min_per_split=MIN_PER_SPLIT, blocks=FALLBACK_BLOCKS, seed=SEED,
):
    rng = np.random.default_rng(seed)
    split = pd.Series("gap", index=df.index, dtype=object)
    labels = df[label_col].astype(str)
    times = df[time_col]
    rows = []
    for cls in sorted(labels.unique()):
        idx = labels.index[labels.to_numpy() == cls]
        order = times.loc[idx].sort_values(kind="stable").index.to_numpy()
        n = len(order)
        if n < 3:
            lab = np.full(n, "train", dtype=object)
            method = "too_small"
        else:
            lab = _time_order(order, ratios, int(n * gap_fraction))
            method = "time_order"
            c = _counts(lab)
            if min(c["train"], c["val"], c["test"]) < min_per_split:
                lab = _blocks(order, ratios, gap_fraction, blocks, rng)
                method = "time_blocks"
        split.loc[order] = lab
        c = _counts(lab)
        rows.append({
            "class": cls,
            "n": n,
            **c,
            "method": method,
            "ok": min(c["train"], c["val"], c["test"]) >= min_per_split,
        })
    return split, pd.DataFrame(rows)


def split_time_ranges(df, split, time_col):
    t = df[time_col]
    out = {}
    for k in ("train", "val", "test"):
        s = t[split == k]
        out[k] = [str(s.min()), str(s.max())] if len(s) else [None, None]
    return out
