from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd


def numeric_columns(df, exclude):
    return [
        c for c in df.columns
        if c not in exclude and not str(c).startswith("_")
        and pd.api.types.is_numeric_dtype(df[c])
    ]


def column_table(df, feats):
    rows = []
    hashes = {}
    for c in feats:
        s = df[c]
        is_float = pd.api.types.is_float_dtype(s)
        rows.append({
            "feature": c,
            "dtype": str(s.dtype),
            "nan": int(s.isna().sum()),
            "inf": int(np.isinf(s.to_numpy()).sum()) if is_float else 0,
            "negative": int((s < 0).sum()),
            "nunique": int(s.nunique(dropna=True)),
        })
        key = hashlib.md5(
            pd.util.hash_pandas_object(s, index=False).to_numpy().tobytes()
        ).hexdigest()
        hashes.setdefault(key, []).append(c)
    table = pd.DataFrame(rows).set_index("feature")
    table["constant"] = table["nunique"] <= 1
    table["duplicate_of"] = ""
    for cols in hashes.values():
        for c in cols[1:]:
            if df[cols[0]].equals(df[c]):
                table.loc[c, "duplicate_of"] = cols[0]
    return table.reset_index()


def replace_inf(df, feats):
    for c in feats:
        if pd.api.types.is_float_dtype(df[c]):
            df[c] = df[c].replace([np.inf, -np.inf], np.nan)
    return df


def row_flags(df, feats, label_col):
    """duplicate: same features and label as an earlier row.
    conflicting: the same feature vector appears with more than one label."""
    h = pd.util.hash_pandas_object(df[feats], index=False).to_numpy()
    y = pd.factorize(df[label_col])[0]
    keys = pd.DataFrame({"h": h, "y": y})
    duplicate = keys.duplicated().to_numpy()
    conflicting = (keys.groupby("h")["y"].transform("nunique") > 1).to_numpy()
    return duplicate, conflicting


def quality_summary(df, table, duplicate, conflicting, label_col):
    labels = df[label_col].astype(str)
    return {
        "rows": int(len(df)),
        "duplicate_rows": int(duplicate.sum()),
        "conflicting_rows": int(conflicting.sum()),
        "conflicting_rows_per_class": labels[conflicting].value_counts().to_dict(),
        "duplicate_rows_per_class": labels[duplicate].value_counts().to_dict(),
        "columns_with_nan": table.loc[table["nan"] > 0, "feature"].tolist(),
        "columns_with_inf": table.loc[table["inf"] > 0, "feature"].tolist(),
        "columns_with_negative": table.loc[table["negative"] > 0, "feature"].tolist(),
        "constant_columns": table.loc[table["constant"], "feature"].tolist(),
        "duplicate_columns": {
            r.feature: r.duplicate_of
            for r in table.itertuples() if r.duplicate_of
        },
    }
