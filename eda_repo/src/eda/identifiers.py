from __future__ import annotations

import re

import pandas as pd

# Columns whose name suggests an identifier, but which the family config does
# not list. They stay in the model features and are listed for a human check.
REVIEW_TOKENS = {"id", "ip", "addr", "address", "time", "timestamp", "date", "start", "end"}
# Tokens that mark a real traffic feature (e.g. MIN_IP_PKT_LEN), not an identifier.
FEATURE_TOKENS = {"len", "length", "pkt", "pkts", "packet", "packets", "bytes", "ttl", "size"}
INDEX_LIKE = re.compile(r"^(unnamed: ?\d+|index|level_\d+)$", re.IGNORECASE)


def _tokens(name):
    return {t for t in re.split(r"[^a-z0-9]+", str(name).lower()) if t}


def build_drop_list(df, family, label_col, time_col=None, extra_drop=()):
    cols = list(df.columns)
    ids = [c for c in family.id_cols if c in cols]
    # The time column is metadata (used for the split), never a feature.
    time_drop = [time_col] if time_col and time_col in cols and time_col not in ids else []
    index_like = [c for c in cols if INDEX_LIKE.match(str(c))]
    label_like = [c for c in family.label_like_cols if c in cols and c != label_col]
    extras = [c for c in extra_drop if c in cols]
    missing_extras = [c for c in extra_drop if c not in cols]
    internal = [c for c in cols if str(c).startswith("_")]
    non_numeric = [
        c for c in cols
        if c != label_col and c not in internal and not pd.api.types.is_numeric_dtype(df[c])
    ]
    drop = sorted(set(ids + time_drop + index_like + label_like + extras + non_numeric) - {label_col})
    ports = [c for c in family.port_cols if c in cols]
    review = []
    for c in cols:
        if c in drop or c == label_col or c in ports or c in internal:
            continue
        tok = _tokens(c)
        if tok & REVIEW_TOKENS and not tok & FEATURE_TOKENS:
            review.append(c)
    return {
        "drop": drop,
        "id_columns": ids + time_drop,
        "index_like": index_like,
        "label_like": label_like,
        "non_numeric": non_numeric,
        "extra": extras,
        "extra_not_found": missing_extras,
        "port_candidates": ports,
        "review_manually": review,
        "redundant": [],
    }
