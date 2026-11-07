from __future__ import annotations

import hashlib
import pathlib

import numpy as np
import pandas as pd

from .config import AMPM_SHIFT_HOURS, FLOAT32, SEED

MISSING_LABELS = {"", "nan", "NaN", "None", "none", "null", "NULL"}


def sha256(path, block=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(block), b""):
            h.update(chunk)
    return h.hexdigest()


def unique_columns(cols):
    """Strip whitespace from names and rename repeated names to name.dup1, name.dup2."""
    seen = {}
    out = []
    for c in cols:
        c = str(c).strip()
        # pandas renames a repeated CSV header to 'name.1'; undo that so the
        # repeat is detected the same way for CSV and parquet input.
        base = c
        if "." in c:
            head, tail = c.rsplit(".", 1)
            if tail.isdigit() and head in seen:
                base = head
        if base in seen:
            seen[base] += 1
            out.append(f"{base}.dup{seen[base]}")
        else:
            seen[base] = 0
            out.append(base)
    return out


def downcast(df, keep=()):
    """float64 -> float32 and int64 -> smallest int. Columns in `keep` (the
    time column) are left alone: float32 cannot hold epoch milliseconds."""
    for c in df.columns:
        if c in keep:
            continue
        s = df[c]
        if FLOAT32 and s.dtype == np.float64:
            df[c] = s.astype(np.float32)
        elif s.dtype == np.int64:
            df[c] = pd.to_numeric(s, downcast="integer")
    return df


def _to_category(df, cat_cols):
    for c in cat_cols:
        if c in df.columns and not isinstance(df[c].dtype, pd.CategoricalDtype):
            df[c] = df[c].astype("category")
    return df


def _concat(frames):
    """Concatenate while keeping categorical columns categorical (saves memory)."""
    cat_cols = set()
    for f in frames:
        cat_cols |= {c for c in f.columns if isinstance(f[c].dtype, pd.CategoricalDtype)}
    for c in cat_cols:
        cats = None
        for f in frames:
            if c not in f.columns:
                continue
            if not isinstance(f[c].dtype, pd.CategoricalDtype):
                f[c] = f[c].astype("category")
            cur = f[c].cat.categories
            cats = cur if cats is None else cats.union(cur)
        for f in frames:
            if c in f.columns:
                f[c] = f[c].cat.set_categories(cats)
    out = pd.concat(frames, ignore_index=True)
    for c in cat_cols:
        if c in out.columns and not isinstance(out[c].dtype, pd.CategoricalDtype):
            out[c] = out[c].astype("category")
    return out


def read_table(path, frac=None, seed=SEED, cat_cols=(), keep=(), chunksize=500_000):
    p = pathlib.Path(path)
    if p.suffix.lower() == ".parquet":
        df = pd.read_parquet(p)
        df.columns = unique_columns(df.columns)
        if frac and frac < 1:
            df = df.sample(frac=frac, random_state=seed).sort_index()
        df = _to_category(df, cat_cols)
        return downcast(df.reset_index(drop=True), keep)
    parts = []
    reader = pd.read_csv(p, chunksize=chunksize, low_memory=False, encoding_errors="replace")
    n_read = 0
    for i, chunk in enumerate(reader):
        chunk.columns = unique_columns(chunk.columns)
        if frac and frac < 1:
            # sort_index keeps file order, which breaks ties between equal timestamps
            chunk = chunk.sample(frac=frac, random_state=seed + i).sort_index()
        parts.append(downcast(_to_category(chunk, cat_cols), keep))
        n_read += len(parts[-1])
        print(f"      {p.name}: {n_read:,} satır okundu", flush=True)
    if not parts:
        raise SystemExit(f"{p} is empty.")
    return _concat(parts)


def read_many(paths, frac=None, seed=SEED, cat_cols=(), keep=()):
    frames = []
    for path in paths:
        df = read_table(path, frac, seed, cat_cols, keep)
        df["_source_file"] = pd.Categorical([pathlib.Path(path).name] * len(df))
        frames.append(df)
    return _concat(frames)


def coerce_numeric(df, skip, min_ratio=0.99):
    """Turn text columns that are (almost) all numbers into float32; leave the rest as text."""
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
            df[c] = s.astype("category")
    return df


def _normalize_text(values):
    return (
        pd.Series(values, dtype=object).astype(str)
        .str.replace("�", "-", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


def normalize_labels(s):
    """Clean label text (encoding damage, spaces) and return a categorical series.

    Works on the categories, not on every row, so it is cheap for 20M rows.
    Missing or empty labels become NaN.
    """
    if not isinstance(s.dtype, pd.CategoricalDtype):
        s = s.astype("category")
    cats = _normalize_text(s.cat.categories)
    cats = cats.where(~cats.isin(MISSING_LABELS))
    uniq = pd.unique(cats.dropna())
    pos = {v: i for i, v in enumerate(uniq)}
    remap = np.array([pos.get(v, -1) if isinstance(v, str) else -1 for v in cats], dtype=np.int64)
    codes = s.cat.codes.to_numpy()
    new = np.where(codes >= 0, remap[np.maximum(codes, 0)], -1)
    return pd.Series(pd.Categorical.from_codes(new, categories=uniq), index=s.index, name=s.name)


def resolve_benign(labels, benign):
    """Return the benign label as spelled in the data (case-insensitive match)."""
    classes = [str(c) for c in pd.Series(labels).dropna().unique()]
    if benign in classes:
        return benign
    match = [c for c in classes if c.lower() == benign.lower()]
    if len(match) == 1:
        return match[0]
    raise SystemExit(
        f"Benign label '{benign}' not found. Classes: {sorted(classes)[:20]}. "
        f"Use --benign-label."
    )


def apply_attempted(labels, policy, benign):
    """Corrected CICIDS2017: '<attack> - Attempted' classes.

    keep   -> separate classes (attack in binary analyses)
    benign -> relabelled as benign
    drop   -> rows removed (returned mask marks them)
    """
    s = labels.astype(object)
    attempted = s.astype(str).str.contains(r"attempted", case=False, regex=True) & s.notna()
    n = int(attempted.sum())
    drop = np.zeros(len(s), dtype=bool)
    if n and policy == "benign":
        s = s.where(~attempted, benign)
    elif n and policy == "drop":
        drop = attempted.to_numpy()
    return s.astype("category"), drop, n


def _infer_epoch_unit(num):
    med = float(np.nanmedian(np.abs(num.to_numpy(dtype="float64"))))
    if med < 1e11:
        return "s"
    if med < 1e14:
        return "ms"
    if med < 1e17:
        return "us"
    return "ns"


def parse_time(s, unit=None, dayfirst=False, ampm_fix="off"):
    """Parse a timestamp column. Returns (datetime series, info dict).

    - numeric columns (or text that is all numbers) are read as epoch time;
      the unit is taken from the family or inferred from the magnitude
    - text is parsed once per unique value (fast for millions of rows)
    - ampm_fix handles CICIDS2017's 12-hour clock without AM/PM
    """
    info = {"method": "", "ampm_fix": ampm_fix, "ampm_shifted_rows": 0}
    if isinstance(s.dtype, pd.CategoricalDtype):
        s = s.astype(object)
    num = pd.to_numeric(s, errors="coerce") if not pd.api.types.is_numeric_dtype(s) else s
    if pd.api.types.is_numeric_dtype(s) or num.notna().mean() >= 0.99:
        u = unit or _infer_epoch_unit(num)
        info["method"] = f"epoch_{u}"
        return pd.to_datetime(num, unit=u, errors="coerce"), info

    codes, uniques = pd.factorize(s.astype(str))
    text = pd.Series(uniques, dtype=object).str.strip()
    parsed = pd.to_datetime(text, errors="coerce", dayfirst=dayfirst)
    info["method"] = "text_inferred_format"
    if parsed.notna().mean() < 0.99:
        parsed = pd.to_datetime(text, errors="coerce", dayfirst=dayfirst, format="mixed")
        info["method"] = "text_mixed_format"

    if ampm_fix in ("auto", "on"):
        has_marker = text.str.contains(r"\b(?:AM|PM)\b", case=False, regex=True).any()
        hours = parsed.dt.hour
        lo, hi = AMPM_SHIFT_HOURS
        shift = parsed.notna() & hours.between(lo, hi)
        apply = ampm_fix == "on" or (not has_marker and not (hours >= 13).any() and shift.any())
        if apply:
            parsed = parsed.where(~shift, parsed + pd.Timedelta(hours=12))
            counts = np.bincount(codes[codes >= 0], minlength=len(uniques))
            info["ampm_shifted_rows"] = int(counts[shift.to_numpy()].sum())
        info["ampm_applied"] = bool(apply)

    values = parsed.to_numpy()
    out = np.full(len(codes), values.dtype.type("NaT"), dtype=values.dtype)
    ok = codes >= 0
    out[ok] = values[codes[ok]]
    return pd.Series(out, index=s.index), info


def row_order_time(n):
    """Synthetic, strictly increasing time for datasets without a timestamp."""
    return pd.Series(pd.Timestamp("2000-01-01") + pd.to_timedelta(np.arange(n), unit="s"))
