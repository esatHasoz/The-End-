from __future__ import annotations

import hashlib
import pathlib

import numpy as np
import pandas as pd

from .config import SEED


def sha256(path, block=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(block), b""):
            h.update(chunk)
    return h.hexdigest()


def unique_columns(cols):
    seen = {}
    out = []
    for c in cols:
        c = str(c).strip()
        if c in seen:
            seen[c] += 1
            out.append(f"{c}.dup{seen[c]}")
        else:
            seen[c] = 0
            out.append(c)
    return out


def downcast(df):
    for c in df.columns:
        s = df[c]
        if s.dtype == np.float64:
            df[c] = s.astype(np.float32)
        elif s.dtype == np.int64:
            df[c] = pd.to_numeric(s, downcast="integer")
    return df


def read_table(path, frac=None, seed=SEED, chunksize=500_000):
    p = pathlib.Path(path)
    if p.suffix.lower() == ".parquet":
        df = pd.read_parquet(p)
        df.columns = unique_columns(df.columns)
        if frac and frac < 1:
            df = df.sample(frac=frac, random_state=seed)
        return downcast(df.reset_index(drop=True))
    parts = []
    reader = pd.read_csv(
        p, chunksize=chunksize, low_memory=False, encoding_errors="replace"
    )
    for i, chunk in enumerate(reader):
        chunk.columns = unique_columns(chunk.columns)
        if frac and frac < 1:
            chunk = chunk.sample(frac=frac, random_state=seed + i)
        parts.append(downcast(chunk))
        print(f"      {p.name}: {sum(len(x) for x in parts):,} satır okundu", flush=True)
    return pd.concat(parts, ignore_index=True)


def read_many(paths, frac=None, seed=SEED):
    frames = []
    for path in paths:
        df = read_table(path, frac, seed)
        df["_source_file"] = pathlib.Path(path).name
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out["_source_file"] = out["_source_file"].astype("category")
    return out


def coerce_numeric(df, skip, min_ratio=0.99):
    for c in df.columns:
        if c in skip:
            continue
        s = df[c]
        if pd.api.types.is_numeric_dtype(s) or isinstance(s.dtype, pd.CategoricalDtype):
            continue
        conv = pd.to_numeric(s, errors="coerce")
        if conv.notna().sum() >= min_ratio * max(s.notna().sum(), 1):
            df[c] = conv.astype(np.float32)
        else:
            df[c] = s.astype(str)
    return df


def normalize_labels(s):
    return (
        s.astype(str)
        .str.replace("�", "-", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


def parse_time(s, unit=None, dayfirst=False):
    if unit:
        return pd.to_datetime(pd.to_numeric(s, errors="coerce"), unit=unit, errors="coerce")
    try:
        return pd.to_datetime(s, errors="coerce", format="mixed", dayfirst=dayfirst)
    except (TypeError, ValueError):
        return pd.to_datetime(s, errors="coerce", dayfirst=dayfirst)
