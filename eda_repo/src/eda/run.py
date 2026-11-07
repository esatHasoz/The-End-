from __future__ import annotations

import argparse
import json
import pathlib
import platform
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from . import config as C
from .config import FAMILIES
from .identifiers import build_drop_list
from .inject import injected_frame
from .labels import bar_plot, binary_summary, distribution, timeline_plot
from .loader import coerce_numeric, normalize_labels, parse_time, read_many, sha256
from .quality import column_table, numeric_columns, quality_summary, replace_inf, row_flags
from .report import write_summary
from .sampling import cap_per_class, sampling_plan
from .split import split_time_ranges, time_split
from .stats import class_stats, correlation_groups, hist_grid, overall_skew, single_feature_auroc

TOTAL = 10


def _step(n, title):
    print(f"[{n}/{TOTAL}] {title} ...", flush=True)
    return time.time()


def _done(t0, extra=""):
    print(f"      tamam ({time.time() - t0:.1f} sn){' - ' + extra if extra else ''}", flush=True)


def _json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def _params():
    return {k: getattr(C, k) for k in dir(C) if k.isupper()}


def parse(argv=None):
    p = argparse.ArgumentParser(prog="eda")
    p.add_argument("--name", required=True)
    p.add_argument("--family", required=True, choices=sorted(FAMILIES))
    p.add_argument("--inputs", nargs="+", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--source-url", default="")
    p.add_argument("--version", default="")
    p.add_argument("--license", default="")
    p.add_argument("--label-col")
    p.add_argument("--time-col")
    p.add_argument("--benign-label")
    p.add_argument("--frac", type=float)
    p.add_argument("--extra-drop", nargs="*", default=[])
    p.add_argument("--inject", action="store_true")
    return p.parse_args(argv)


def main(argv=None):
    a = parse(argv)
    fam = FAMILIES[a.family]
    label_col = a.label_col or fam.label_col
    time_col = a.time_col or fam.time_col
    benign = a.benign_label or fam.benign_label
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    started = time.time()

    t0 = _step(0, "data card")
    files = [
        {"file": pathlib.Path(p).name, "size_bytes": pathlib.Path(p).stat().st_size, "sha256": sha256(p)}
        for p in a.inputs
    ]
    card = [
        f"# Data card: {a.name}",
        "",
        f"- Source URL: {a.source_url or 'TODO'}",
        f"- Version: {a.version or 'TODO'}",
        f"- License: {a.license or 'TODO'}",
        f"- Feature family: {fam.name}",
        f"- Sampling at load: {a.frac or 'none'}",
        f"- Created: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- EDA version: {C.VERSION}",
        "",
        "| file | size_bytes | sha256 |",
        "|---|---|---|",
    ] + [f"| {f['file']} | {f['size_bytes']:,} | {f['sha256']} |" for f in files]
    (out / "data_card.md").write_text("\n".join(card) + "\n", encoding="utf-8")
    _done(t0)

    t0 = _step(1, "load and convert to parquet")
    df = read_many(a.inputs, a.frac)
    for col in (label_col, time_col):
        if col not in df.columns:
            raise SystemExit(
                f"Column '{col}' not found. Use --label-col / --time-col. "
                f"Available: {list(df.columns)[:15]} ..."
            )
    skip = {label_col, time_col, "_source_file", *fam.id_cols}
    df = coerce_numeric(df, skip)
    df[label_col] = normalize_labels(df[label_col])
    df.to_parquet(out / "raw.parquet", index=False)
    mem = df.memory_usage(deep=True).sum() / 1e6
    dtypes = df.dtypes.astype(str).value_counts().to_dict()
    _json(out / "load_info.json", {
        "rows": len(df), "columns": df.shape[1], "memory_mb": round(mem, 1),
        "dtypes": dtypes, "column_names": list(df.columns),
    })
    _done(t0, f"{len(df):,} satır, {df.shape[1]} sütun, {mem:,.0f} MB")

    drop = build_drop_list(df, fam, label_col, a.extra_drop)
    feats = numeric_columns(df, set(drop["drop"]) | {label_col})

    t0 = _step(2, "data quality")
    table = column_table(df, feats)
    table.to_csv(out / "quality_columns.csv", index=False)
    replace_inf(df, feats)
    duplicate, conflicting = row_flags(df, feats, label_col)
    q = quality_summary(df, table, duplicate, conflicting, label_col)
    _json(out / "quality_summary.json", q)
    raw_dist = distribution(df, label_col, benign)
    remove = np.zeros(len(df), dtype=bool)
    if C.DROP_EXACT_DUPLICATES:
        remove |= duplicate
    if C.DROP_CONFLICTING:
        remove |= conflicting
    clean = df.loc[~remove].reset_index(drop=True)
    clean["_conflicting"] = conflicting[~remove]
    del df
    drop["redundant"] = sorted(set(q["constant_columns"]) | set(q["duplicate_columns"]))
    feats = [c for c in feats if c not in drop["redundant"]]
    _done(t0, f"{q['duplicate_rows']:,} tekrar, {q['conflicting_rows']:,} çelişkili satır")

    t0 = _step(3, "label distribution")
    clean_dist = distribution(clean, label_col, benign)
    dist = clean_dist.merge(
        raw_dist[["class", "count"]].rename(columns={"count": "count_raw"}), on="class", how="outer"
    ).fillna({"count": 0, "count_raw": 0})
    dist["removed"] = dist["count_raw"] - dist["count"]
    dist = dist[["class", "is_attack", "count_raw", "count", "removed", "pct", "imbalance_vs_largest"]]
    dist = dist.sort_values("count", ascending=False).reset_index(drop=True)
    dist.to_csv(out / "label_distribution.csv", index=False)
    binary = binary_summary(clean, label_col, benign)
    clean["_time"] = parse_time(clean[time_col], fam.time_unit if not a.time_col else None, fam.dayfirst)
    valid = clean["_time"].notna()
    if valid.mean() < 0.5:
        raise SystemExit(f"Only {valid.mean():.1%} of '{time_col}' parsed as time. Check --time-col.")
    bar_plot(clean_dist, out / "label_bar.png")
    timeline_plot(clean[valid], label_col, "_time", out / "label_timeline.png")
    _done(t0, f"{len(clean_dist)} sınıf, saldırı oranı %{binary['attack_pct']}")

    t0 = _step(4, "identifier and leakage list")
    drop["model_features"] = feats
    _json(out / "drop_cols.json", drop)
    _done(t0, f"{len(drop['drop'])} sütun çıkarıldı, {len(feats)} özellik kaldı")

    t0 = _step(5, "time-based split per class")
    split, split_report = time_split(clean[valid], label_col, "_time")
    clean["split"] = "no_time"
    clean.loc[split.index, "split"] = split
    clean.insert(0, "row_id", np.arange(len(clean)))
    split_report.to_csv(out / "split_report.csv", index=False)
    clean[["row_id", "split"]].to_parquet(out / "splits.parquet", index=False)
    clean.to_parquet(out / "clean.parquet", index=False)
    ranges = split_time_ranges(clean, clean["split"], "_time")
    bad = split_report.loc[~split_report["ok"], "class"].tolist()
    _done(t0, f"yetersiz sınıf: {', '.join(bad) if bad else 'yok'}")

    train = clean[clean["split"] == "train"]
    analysis = cap_per_class(train, label_col, C.ANALYSIS_CAP_PER_CLASS)

    t0 = _step(6, "feature distributions (train)")
    class_stats(analysis, feats, label_col).to_csv(out / "class_stats.csv", index=False)
    overall_skew(analysis, feats).to_csv(out / "skewness.csv", index=False)
    hist_grid(analysis, feats, label_col, benign, out / "feature_hists.png")
    _done(t0, f"analiz örneği {len(analysis):,} satır")

    t0 = _step(7, "correlation groups (train)")
    groups = correlation_groups(analysis, feats)
    _json(out / "correlated_groups.json", {"threshold": C.CORR_THRESHOLD, "groups": groups})
    _done(t0, f"{len(groups)} grup")

    t0 = _step(8, "single-feature AUROC (train)")
    auroc = single_feature_auroc(analysis, feats, label_col, benign, drop["port_candidates"])
    auroc.to_csv(out / "shortcut_candidates.csv", index=False)
    n_susp = int(auroc["suspicious"].sum()) if len(auroc) else 0
    _done(t0, f"{n_susp} şüpheli (özellik, kapsam) çifti")

    t0 = _step(9, "injected spurious feature")
    if a.inject:
        injected_frame(clean[label_col], benign).to_parquet(out / "injected_feature.parquet", index=False)
        _done(t0, f"{C.INJECT_NAME} ve {C.INJECT_NAME}_flipped yazıldı")
    else:
        _done(t0, "atlandı (--inject verilmedi)")

    t0 = _step(10, "sampling plan")
    plan, kept = sampling_plan(clean, "split", label_col, C.CAP_TRAIN, C.CAP_VAL)
    _json(out / "sampling_config.json", plan)
    pd.DataFrame({"row_id": kept}).to_parquet(out / "sample_index.parquet", index=False)
    _done(t0, f"{len(kept):,} satır seçildi")

    top = pd.DataFrame()
    if len(auroc):
        top = auroc[auroc["scope"] == "binary"].head(15)[["feature", "score", "auroc", "auroc_tree", "direction", "is_port", "suspicious"]]
    write_summary(out / "summary.md", {
        "name": a.name, "version": C.VERSION, "seed": C.SEED, "family": fam.name,
        "label_col": label_col, "benign": benign, "rows_raw": q["rows"],
        "rows_clean": len(clean), "rows_no_time": int((~valid).sum()),
        "dropped_duplicates": C.DROP_EXACT_DUPLICATES, "dropped_conflicting": C.DROP_CONFLICTING,
        "quality": q, "features": feats, "dist": dist, "binary": binary,
        "split_report": split_report, "time_ranges": ranges, "drop": drop,
        "top_auroc": top, "corr_groups": groups, "plan": plan,
    })
    _json(out / "manifest.json", {
        "eda_version": C.VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "args": vars(a),
        "params": _params(),
        "python": platform.python_version(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "runtime_sec": round(time.time() - started, 1),
    })
    print(f"Bitti: {out} ({time.time() - started:.1f} sn)", flush=True)


if __name__ == "__main__":
    main()
