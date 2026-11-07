from __future__ import annotations

import numpy as np
import pandas as pd

from .config import SEED


def cap_positions(labels, cap, seed=SEED):
    """Positions (0..n-1) keeping at most `cap` rows per class, in original order."""
    rng = np.random.default_rng(seed)
    labels = np.asarray(labels, dtype=object)
    keep = []
    for cls in pd.unique(labels):
        pos = np.flatnonzero(labels == cls)
        if cap is not None and len(pos) > cap:
            pos = rng.choice(pos, cap, replace=False)
        keep.append(pos)
    if not keep:
        return np.array([], dtype=np.int64)
    return np.sort(np.concatenate(keep))


def cap_per_class(df, label_col, cap, seed=SEED):
    return df.iloc[cap_positions(df[label_col].astype(str).to_numpy(), cap, seed)]


def sampling_plan(split, labels, row_id, cap_train, cap_val, seed=SEED):
    """Per-class caps on train and val only. Test keeps its natural class ratio.

    Works on arrays, so no copy of the full table is made."""
    split = np.asarray(split, dtype=object)
    labels = np.asarray(labels, dtype=object)
    row_id = np.asarray(row_id)
    plan = {}
    kept = []
    for name, cap in (("train", cap_train), ("val", cap_val), ("test", None)):
        pos = np.flatnonzero(split == name)
        sel = pos[cap_positions(labels[pos], cap, seed)] if len(pos) else pos
        plan[name] = {
            "cap_per_class": cap,
            "rows_before": int(len(pos)),
            "rows_after": int(len(sel)),
            "per_class_after": pd.Series(labels[sel]).value_counts().to_dict(),
        }
        kept.append(row_id[sel])
    plan["note"] = "test is not sampled; report test metrics on its natural class ratio"
    return plan, np.sort(np.concatenate(kept))
