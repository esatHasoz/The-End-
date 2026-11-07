from __future__ import annotations

import numpy as np

from .config import SEED


def cap_per_class(df, label_col, cap, seed=SEED):
    rng = np.random.default_rng(seed)
    labels = df[label_col].astype(str).to_numpy()
    keep = []
    for cls in np.unique(labels):
        pos = np.flatnonzero(labels == cls)
        if len(pos) > cap:
            pos = np.sort(rng.choice(pos, cap, replace=False))
        keep.append(pos)
    if not keep:
        return df.iloc[0:0]
    return df.iloc[np.sort(np.concatenate(keep))]


def sampling_plan(df, split_col, label_col, cap_train, cap_val, seed=SEED):
    plan = {}
    kept = []
    for name, cap in (("train", cap_train), ("val", cap_val), ("test", None)):
        sub = df[df[split_col] == name]
        out = sub if cap is None else cap_per_class(sub, label_col, cap, seed)
        plan[name] = {
            "cap_per_class": cap,
            "rows_before": int(len(sub)),
            "rows_after": int(len(out)),
            "per_class_after": out[label_col].astype(str).value_counts().to_dict(),
        }
        kept.append(out.index.to_numpy())
    plan["note"] = "test is not sampled; report test metrics on its natural class ratio"
    return plan, np.sort(np.concatenate(kept))
