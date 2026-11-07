from __future__ import annotations

import numpy as np
import pandas as pd

from .config import INJECT_NAME, INJECT_STRENGTH, SEED


def inject_spurious(is_attack, split, strength=INJECT_STRENGTH, seed=SEED):
    """Known shortcut for RQ2.

    train / val (and gap rows): the feature equals is_attack with probability `strength`.
    test: the feature is drawn independently of the label with the same base rate,
    so a model that relies on it loses performance on test.
    """
    rng = np.random.default_rng(seed)
    is_attack = np.asarray(is_attack, dtype=bool)
    split = np.asarray(split, dtype=object)
    flip = rng.random(len(is_attack)) > strength
    v = np.where(flip, ~is_attack, is_attack)
    test = split == "test"
    base_rate = float(is_attack[~test].mean()) if (~test).any() else 0.5
    v[test] = rng.random(int(test.sum())) < base_rate
    return v.astype(np.float32)


def injected_frame(row_id, is_attack, split, name=INJECT_NAME, strength=INJECT_STRENGTH, seed=SEED):
    v = inject_spurious(is_attack, split, strength, seed)
    return pd.DataFrame({"row_id": np.asarray(row_id), name: v})


def agreement_by_split(values, is_attack, split):
    """Share of rows where the injected feature equals the binary label, per split."""
    values = np.asarray(values) > 0.5
    is_attack = np.asarray(is_attack, dtype=bool)
    split = np.asarray(split, dtype=object)
    out = {}
    for k in ("train", "val", "test"):
        m = split == k
        out[k] = round(float((values[m] == is_attack[m]).mean()), 4) if m.any() else None
    return out
