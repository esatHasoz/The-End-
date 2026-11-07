from __future__ import annotations

import re

import pandas as pd

REVIEW = re.compile(
    r"(^|[^a-z0-9])(id|ip|addr|address|time|timestamp|date|start|end)([^a-z0-9]|$)",
    re.IGNORECASE,
)


def build_drop_list(df, family, label_col, extra_drop=()):
    cols = list(df.columns)
    ids = [c for c in family.id_cols if c in cols]
    label_like = [c for c in family.label_like_cols if c in cols and c != label_col]
    extras = [c for c in extra_drop if c in cols]
    non_numeric = [
        c for c in cols
        if c != label_col and not pd.api.types.is_numeric_dtype(df[c])
    ]
    drop = sorted(set(ids + label_like + extras + non_numeric) - {label_col})
    ports = [c for c in family.port_cols if c in cols]
    review = [
        c for c in cols
        if c not in drop and c != label_col and c not in ports and REVIEW.search(c)
    ]
    return {
        "drop": drop,
        "id_columns": ids,
        "label_like": label_like,
        "non_numeric": non_numeric,
        "extra": extras,
        "port_candidates": ports,
        "review_manually": review,
        "redundant": [],
    }
