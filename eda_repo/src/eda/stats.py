from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.tree import DecisionTreeClassifier

from .config import (
    AUROC_MIN_ROWS, AUROC_THRESHOLD, CORR_SAMPLE, CORR_THRESHOLD,
    HIST_MAX_FEATURES, HIST_SAMPLE, SEED, TREE_DEPTH, TREE_MIN_LEAF,
)


def class_stats(df, feats, label_col):
    g = df.groupby(df[label_col].astype(str))[feats]
    parts = {"mean": g.mean(), "std": g.std(), "median": g.median(), "skew": g.skew()}
    frames = []
    for name, table in parts.items():
        table = table.copy()
        table.index.name = "class"
        long = table.reset_index().melt(id_vars="class", var_name="feature", value_name=name)
        frames.append(long.set_index(["class", "feature"]))
    return pd.concat(frames, axis=1).reset_index()


def overall_skew(df, feats):
    return df[feats].skew().rename("skew").rename_axis("feature").reset_index()


def hist_grid(df, feats, label_col, benign_label, out_path,
              max_features=HIST_MAX_FEATURES, sample=HIST_SAMPLE, seed=SEED):
    skew = df[feats].skew().abs().sort_values(ascending=False)
    chosen = list(skew.index[:max_features])
    if not chosen:
        return []
    d = df if len(df) <= sample else df.sample(sample, random_state=seed)
    attack = (d[label_col].astype(str) != benign_label).to_numpy()
    ncols = 5
    nrows = math.ceil(len(chosen) / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3.2, nrows * 2.4))
    axes = np.atleast_1d(axes).ravel()
    for ax, c in zip(axes, chosen):
        x = d[c].to_numpy(dtype="float64")
        x = np.sign(x) * np.log1p(np.abs(x))
        ok = np.isfinite(x)
        if ok.any() and np.ptp(x[ok]) > 0:
            bins = np.histogram_bin_edges(x[ok], bins=40)
        else:
            bins = 10
        ax.hist(x[ok & ~attack], bins=bins, alpha=0.5, density=True, label="benign")
        ax.hist(x[ok & attack], bins=bins, alpha=0.5, density=True, label="attack")
        ax.set_title(str(c)[:30], fontsize=7)
        ax.tick_params(labelsize=6)
    for ax in axes[len(chosen):]:
        ax.axis("off")
    axes[0].legend(fontsize=6)
    fig.suptitle("signed log1p histograms (train)", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return chosen


def correlation_groups(df, feats, threshold=CORR_THRESHOLD, sample=CORR_SAMPLE, seed=SEED):
    d = df[feats] if len(df) <= sample else df[feats].sample(sample, random_state=seed)
    keep = [c for c in feats if d[c].nunique(dropna=True) > 1]
    if len(keep) < 2:
        return []
    corr = d[keep].corr(method="spearman").abs().to_numpy()
    parent = list(range(len(keep)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(keep)):
        for j in range(i + 1, len(keep)):
            if corr[i, j] > threshold:
                parent[find(i)] = find(j)
    groups = {}
    for i, c in enumerate(keep):
        groups.setdefault(find(i), []).append(c)
    return sorted((sorted(g) for g in groups.values() if len(g) > 1), key=len, reverse=True)


def _tree_auroc(x, y, seed):
    folds = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    tree = DecisionTreeClassifier(max_depth=TREE_DEPTH, min_samples_leaf=TREE_MIN_LEAF, random_state=seed)
    p = cross_val_predict(tree, x.reshape(-1, 1), y, cv=folds, method="predict_proba")[:, 1]
    return roc_auc_score(y, p)


def single_feature_auroc(df, feats, label_col, benign_label, port_cols=(),
                         threshold=AUROC_THRESHOLD, min_rows=AUROC_MIN_ROWS, seed=SEED):
    labels = df[label_col].astype(str).to_numpy()
    X = df[feats].astype("float64")
    X = X.fillna(X.median())
    attack = labels != benign_label
    scopes = [("binary", np.ones(len(df), dtype=bool), attack)]
    for cls in sorted(set(labels) - {benign_label}):
        mask = (labels == cls) | (labels == benign_label)
        scopes.append((f"{cls} vs benign", mask, labels[mask] == cls))
    rows = []
    for k, (scope, mask, y) in enumerate(scopes, start=1):
        n_pos = int(y.sum())
        n_neg = int(len(y) - n_pos)
        if n_pos < min_rows or n_neg < min_rows:
            print(f"      {k}/{len(scopes)} {scope}: atlandı (az satır)", flush=True)
            continue
        print(f"      {k}/{len(scopes)} {scope}: {n_pos:,} pozitif, {n_neg:,} negatif", flush=True)
        for c in feats:
            x = X[c].to_numpy()[mask]
            if not np.isfinite(x).all() or x.min() == x.max():
                continue
            a = roc_auc_score(y, x)
            t = _tree_auroc(x, y, seed)
            rows.append({
                "feature": c,
                "scope": scope,
                "auroc": round(max(a, 1 - a), 6),
                "auroc_tree": round(t, 6),
                "score": round(max(a, 1 - a, t), 6),
                "direction": "+" if a >= 0.5 else "-",
                "n_pos": n_pos,
                "n_neg": n_neg,
                "is_port": c in port_cols,
            })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["suspicious"] = out["score"] > threshold
    return out.sort_values(["scope", "score"], ascending=[True, False]).reset_index(drop=True)
