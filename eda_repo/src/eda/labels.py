from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import SEED


def distribution(df, label_col, benign_label):
    vc = df[label_col].astype(str).value_counts()
    out = vc.rename_axis("class").reset_index(name="count")
    out["pct"] = (out["count"] / out["count"].sum() * 100).round(4)
    out["imbalance_vs_largest"] = (out["count"].max() / out["count"]).round(2)
    out["is_attack"] = out["class"] != benign_label
    return out


def binary_summary(df, label_col, benign_label):
    attack = int((df[label_col].astype(str) != benign_label).sum())
    benign = int(len(df) - attack)
    return {
        "benign": benign,
        "attack": attack,
        "attack_pct": round(attack / max(len(df), 1) * 100, 4),
    }


def timeline_plot(df, label_col, time_col, out_path, per_class=3000, seed=SEED):
    labels = df[label_col].astype(str)
    classes = sorted(labels.unique())
    fig, ax = plt.subplots(figsize=(12, 0.45 * len(classes) + 2))
    for i, c in enumerate(classes):
        t = df.loc[labels == c, time_col].dropna()
        if len(t) > per_class:
            t = t.sample(per_class, random_state=seed)
        ax.scatter(t, np.full(len(t), i), s=3, alpha=0.4)
    ax.set_yticks(range(len(classes)))
    ax.set_yticklabels(classes, fontsize=8)
    ax.set_xlabel("time")
    ax.set_title("Class x time")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def bar_plot(dist, out_path):
    fig, ax = plt.subplots(figsize=(10, 0.4 * len(dist) + 2))
    ax.barh(dist["class"], dist["count"])
    ax.set_xscale("log")
    ax.invert_yaxis()
    ax.set_xlabel("count (log)")
    ax.tick_params(axis="y", labelsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
