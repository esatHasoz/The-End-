from __future__ import annotations

import numpy as np
import pandas as pd

from .config import INJECT_NAME, INJECT_STRENGTH, SEED


def inject_spurious(labels, benign_label, strength=INJECT_STRENGTH, seed=SEED):
    rng = np.random.default_rng(seed)
    attack = labels.astype(str).to_numpy() != benign_label
    noise = rng.random(len(attack)) > strength
    return np.where(noise, ~attack, attack).astype(np.float32)


def injected_frame(labels, benign_label, name=INJECT_NAME, strength=INJECT_STRENGTH, seed=SEED):
    v = inject_spurious(labels, benign_label, strength, seed)
    return pd.DataFrame({
        "row_id": np.arange(len(v)),
        name: v,
        f"{name}_flipped": (1 - v).astype(np.float32),
    })
