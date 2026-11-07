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
from .config import DATASETS, FAMILIES, ROW_ORDER
from .identifiers import build_drop_list
from .inject import agreement_by_split, injected_frame
from .labels import bar_plot, binary_summary, distribution, timeline_plot
from .loader import (
    apply_attempted, coerce_numeric, normalize_labels, parse_time, read_many,
    resolve_benign, row_order_time, sha256,
)
from .quality import column_table, numeric_columns, quality_summary, replace_inf, row_flags
from .report import write_summary
from .sampling import cap_positions, sampling_plan
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
    return {k: getattr(C, k) for k in dir(C) if k.isupper() and k not in ("DATASETS", "FAMILIES")}


def parse(argv=None):
    p = argparse.ArgumentParser(prog="eda")
    p.add_argument("--dataset", choices=sorted(DATASETS),
                   help="preset for one of the six project datasets (fills the options below)")
    p.add_argument("--name")
    p.add_argument("--family", choices=sorted(FAMILIES))
    p.add_argument("--inputs", nargs="+", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--source-url")
    p.add_argument("--version")
    p.add_argument("--license")
    p.add_argument("--label-col")
    p.add_argument("--time-col", help=f"timestamp column, or {ROW_ORDER} when there is none")
    p.add_argument("--benign-label")
    p.add_argument("--ampm-fix", choices=("auto", "on", "off"))
    p.add_argument("--attempted", choices=("keep", "benign", "drop"), default="keep",
                   help="corrected CICIDS2017 '- Attempted' classes")
    p.add_argument("--frac", type=float, help="random fraction of rows to load (large sets)")
    p.add_argument("--extra-drop", nargs="*", default=None)
    p.add_argument("--no-inject", action="store_true", help="skip step 9")
    p.add_argument("--inject", action="store_true", help=argparse.SUPPRESS)  # v1 compatibility
    a = p.parse_args(argv)

    ds = DATASETS.get(a.dataset)
    a.name = a.name or (ds.name if ds else None)
    a.family = a.family or (ds.family if ds else None)
    if not a.name or not a.family:
        p.error("give --dataset, or both --name and --family")
    fam = FAMILIES[a.family]
    a.source_url = a.source_url or (ds.source_url if ds else "")
    a.version = a.version or (ds.version if ds else "")
    a.license = a.license or (ds.license if ds else "")
    a.label_col = a.label_col or (ds.label_col if ds else None) or fam.label_col
    a.time_col = a.time_col or (ds.time_col if ds else None) or fam.time_col
    a.benign_label = a.benign_label or (ds.benign_label if ds else None) or fam.benign_label
    a.ampm_fix = a.ampm_fix or (ds.ampm_fix if ds else "off")
    a.extra_drop = list(a.extra_drop if a.extra_drop is not None else (ds.extra_drop if ds else ()))
    a.notes = ds.notes if ds else ""
    a.group = ds.group if ds else ""
    a.owner = ds.owner if ds else ""
    if a.frac is not None and not 0 < a.frac <= 1:
        p.error("--frac must be in (0, 1]")
    for path in a.inputs:
        if not pathlib.Path(path).is_file():
            p.error(f"input not found: {path}")
    return a


def main(argv=None):
    a = parse(argv)
    fam = FAMILIES[a.family]
    label_col, time_col = a.label_col, a.time_col
    row_order = time_col == ROW_ORDER
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    started = time.time()
    warnings = []

    # ------------------------------------------------------------------ 0
    t0 = _step(0, "data card")
    files = [
        {"file": pathlib.Path(p).name, "size_bytes": pathlib.Path(p).stat().st_size, "sha256": sha256(p)}
        for p in a.inputs
    ]
    card = [
        f"# Data card: {a.name}",
        "",
        f"- Group / owner: {a.group or '-'} / {a.owner or '-'}",
        f"- Source URL: {a.source_url or 'TODO'}",
        f"- Version: {a.version or 'TODO'}",
        f"- License: {a.license or 'TODO'}",
        f"- Feature family: {fam.name}",
        f"- Label column: `{label_col}`, benign label: `{a.benign_label}`, time column: `{time_col}`",
        f"- Sampling at load: {a.frac or 'none'}",
        f"- Created: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- EDA version: {C.VERSION}",
    ]
    if a.notes:
        card += [f"- Notes: {a.notes}"]
    card += ["", "| file | size_bytes | sha256 |", "|---|---|---|"]
    card += [f"| {f['file']} | {f['size_bytes']:,} | {f['sha256']} |" for f in files]
    (out / "data_card.md").write_text("\n".join(card) + "\n", encoding="utf-8")
    _done(t0)

    # ------------------------------------------------------------------ 1
    t0 = _step(1, "load and convert to parquet")
    cat_cols = [c for c in fam.id_cols if c != time_col] + [label_col]
    df = read_many(a.inputs, a.frac, cat_cols=cat_cols, keep=(time_col,))
    needed = [label_col] + ([] if row_order else [time_col])
    for col in needed:
        if col not in df.columns:
            raise SystemExit(
                f"Column '{col}' not found. Use --label-col / --time-col "
                f"(or --time-col {ROW_ORDER} if there is no timestamp). "
                f"Available: {list(df.columns)[:25]} ..."
            )
    rows_loaded = len(df)

    df[label_col] = normalize_labels(df[label_col])
    missing = df[label_col].isna().to_numpy()
    if missing.any():
        warnings.append(f"{int(missing.sum()):,} rows without a label were removed at load.")
        df = df.loc[~missing].reset_index(drop=True)
    classes = set(map(str, df[label_col].cat.categories))
    if classes & {"NeedManualLabel", "No Label"}:
        raise SystemExit(
            "Label column still contains CICFlowMeter's 'NeedManualLabel'. Label the flows first."
        )
    benign = resolve_benign(df[label_col], a.benign_label)
    if benign != a.benign_label:
        warnings.append(f"Benign label matched case-insensitively: '{benign}'.")
    df[label_col], attempted_drop, n_attempted = apply_attempted(df[label_col], a.attempted, benign)
    if n_attempted:
        warnings.append(f"{n_attempted:,} '- Attempted' rows, policy: {a.attempted}.")
        if attempted_drop.any():
            df = df.loc[~attempted_drop].reset_index(drop=True)
    df[label_col] = df[label_col].cat.remove_unused_categories()
    if df[label_col].nunique() < 2:
        raise SystemExit(f"Only one class in '{label_col}': {list(df[label_col].cat.categories)}.")

    skip = {label_col, time_col, "_source_file", *fam.id_cols}
    df = coerce_numeric(df, skip)
    df.to_parquet(out / "raw.parquet", index=False)
    mem = df.memory_usage(deep=True).sum() / 1e6
    _json(out / "load_info.json", {
        "rows_loaded": rows_loaded, "rows": len(df), "columns": df.shape[1],
        "memory_mb": round(mem, 1),
        "dtypes": df.dtypes.astype(str).value_counts().to_dict(),
        "column_names": list(df.columns),
    })
    _done(t0, f"{len(df):,} satır, {df.shape[1]} sütun, {mem:,.0f} MB")

    drop = build_drop_list(df, fam, label_col, None if row_order else time_col, a.extra_drop)
    if drop["extra_not_found"]:
        warnings.append(f"--extra-drop columns not found: {drop['extra_not_found']}.")
    feats = numeric_columns(df, set(drop["drop"]) | {label_col})
    if not feats:
        raise SystemExit("No numeric feature columns left. Check the family / column names.")

    # ------------------------------------------------------------------ 2
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
    del df
    clean["_conflicting"] = conflicting[~remove]
    clean[label_col] = clean[label_col].cat.remove_unused_categories()
    drop["redundant"] = sorted(set(q["constant_columns"]) | set(q["duplicate_columns"]))
    feats = [c for c in feats if c not in drop["redundant"]]
    _done(t0, f"{q['duplicate_rows']:,} tekrar, {q['conflicting_rows']:,} çelişkili satır")

    # ------------------------------------------------------------------ 3
    t0 = _step(3, "label distribution")
    clean_dist = distribution(clean, label_col, benign)
    dist = clean_dist.merge(
        raw_dist[["class", "count"]].rename(columns={"count": "count_raw"}), on="class", how="outer"
    ).fillna({"count": 0, "count_raw": 0})
    dist["is_attack"] = dist["class"] != benign
    dist["removed"] = dist["count_raw"] - dist["count"]
    dist = dist[["class", "is_attack", "count_raw", "count", "removed", "pct", "imbalance_vs_largest"]]
    dist = dist.sort_values("count", ascending=False).reset_index(drop=True)
    dist.to_csv(out / "label_distribution.csv", index=False)
    binary = binary_summary(clean, label_col, benign)
    if row_order:
        clean["_time"] = row_order_time(len(clean)).to_numpy()
        time_info = {"method": "row_order"}
        warnings.append("No timestamp: file row order is used as time. The split is only as "
                        "valid as the file order.")
    else:
        parsed, time_info = parse_time(
            clean[time_col], fam.time_unit if time_col == fam.time_col else None,
            fam.dayfirst, a.ampm_fix,
        )
        clean["_time"] = parsed.to_numpy()
        if time_info.get("ampm_shifted_rows"):
            warnings.append(f"12-hour clock without AM/PM: {time_info['ampm_shifted_rows']:,} rows "
                            f"shifted by 12 h (hours {C.AMPM_SHIFT_HOURS[0]}-{C.AMPM_SHIFT_HOURS[1]}).")
    valid = clean["_time"].notna().to_numpy()
    if valid.mean() < 0.5:
        raise SystemExit(f"Only {valid.mean():.1%} of '{time_col}' parsed as time. Check --time-col.")
    if not valid.all():
        warnings.append(f"{int((~valid).sum()):,} rows have no valid timestamp (split = no_time).")
    bar_plot(clean_dist, out / "label_bar.png")
    timeline_plot(clean.loc[valid, [label_col, "_time"]], label_col, "_time", out / "label_timeline.png")
    _done(t0, f"{len(clean_dist)} sınıf, saldırı oranı %{binary['attack_pct']}")

    # ------------------------------------------------------------------ 4
    t0 = _step(4, "identifier and leakage list")
    drop["model_features"] = feats
    drop["metadata"] = {"time_col": None if row_order else time_col, "label_col": label_col}
    _json(out / "drop_cols.json", drop)
    _done(t0, f"{len(drop['drop'])} sütun çıkarıldı, {len(feats)} özellik kaldı")

    # ------------------------------------------------------------------ 5
    t0 = _step(5, "time-based split per class")
    split, split_report = time_split(clean.loc[valid, [label_col, "_time"]], label_col, "_time")
    clean["split"] = "no_time"
    clean.loc[split.index, "split"] = split
    clean.insert(0, "row_id", np.arange(len(clean), dtype=np.int64))
    split_report.to_csv(out / "split_report.csv", index=False)
    clean[["row_id", "split"]].to_parquet(out / "splits.parquet", index=False)
    clean.to_parquet(out / "clean.parquet", index=False)
    ranges = split_time_ranges(clean, clean["split"], "_time")
    bad = split_report.loc[~split_report["ok"], "class"].tolist()
    if bad:
        warnings.append(f"Classes with fewer than {C.MIN_PER_SPLIT} rows in a split: {', '.join(bad)}.")
    _done(t0, f"yetersiz sınıf: {', '.join(bad) if bad else 'yok'}")

    labels = clean[label_col].astype(str).to_numpy()
    split_arr = clean["split"].to_numpy()
    is_attack = labels != benign

    train_pos = np.flatnonzero(split_arr == "train")
    analysis = clean.iloc[train_pos[cap_positions(labels[train_pos], C.ANALYSIS_CAP_PER_CLASS)]]

    # ------------------------------------------------------------------ 6
    t0 = _step(6, "feature distributions (train)")
    class_stats(analysis, feats, label_col).to_csv(out / "class_stats.csv", index=False)
    overall_skew(analysis, feats).to_csv(out / "skewness.csv", index=False)
    hist_grid(analysis, feats, label_col, benign, out / "feature_hists.png")
    _done(t0, f"analiz örneği {len(analysis):,} satır")

    # ------------------------------------------------------------------ 7
    t0 = _step(7, "correlation groups (train)")
    groups = correlation_groups(analysis, feats)
    _json(out / "correlated_groups.json", {"threshold": C.CORR_THRESHOLD, "groups": groups})
    _done(t0, f"{len(groups)} grup")

    # ------------------------------------------------------------------ 8
    t0 = _step(8, "single-feature AUROC (train)")
    auroc = single_feature_auroc(analysis, feats, label_col, benign, drop["port_candidates"])
    auroc.to_csv(out / "shortcut_candidates.csv", index=False)
    n_susp = int(auroc["suspicious"].sum()) if len(auroc) else 0
    _done(t0, f"{n_susp} şüpheli (özellik, kapsam) çifti")
    del analysis

    # ------------------------------------------------------------------ 9
    t0 = _step(9, "injected spurious feature")
    inject_check = None
    if not a.no_inject:
        inj = injected_frame(clean["row_id"].to_numpy(), is_attack, split_arr)
        inj.to_parquet(out / "injected_feature.parquet", index=False)
        inject_check = agreement_by_split(inj[C.INJECT_NAME].to_numpy(), is_attack, split_arr)
        _json(out / "injected_feature_check.json", {
            "name": C.INJECT_NAME, "strength": C.INJECT_STRENGTH,
            "agreement_with_label": inject_check,
            "expected": {"train": C.INJECT_STRENGTH, "val": C.INJECT_STRENGTH,
                         "test": "about 1 - 2p(1-p), p = attack share; label-independent"},
        })
        _done(t0, f"etiketle uyum {inject_check}")
    else:
        _done(t0, "atlandı (--no-inject)")

    # ------------------------------------------------------------------ 10
    t0 = _step(10, "sampling plan")
    plan, kept = sampling_plan(split_arr, labels, clean["row_id"].to_numpy(), C.CAP_TRAIN, C.CAP_VAL)
    _json(out / "sampling_config.json", plan)
    pd.DataFrame({"row_id": kept}).to_parquet(out / "sample_index.parquet", index=False)
    _done(t0, f"{len(kept):,} satır seçildi")

    top = pd.DataFrame()
    if len(auroc):
        top = auroc[auroc["scope"] == "binary"].head(15)[
            ["feature", "score", "auroc", "auroc_tree", "direction", "is_port", "suspicious"]
        ]
    write_summary(out / "summary.md", {
        "name": a.name, "version": C.VERSION, "seed": C.SEED, "family": fam.name,
        "label_col": label_col, "benign": benign, "rows_loaded": rows_loaded, "rows_raw": q["rows"],
        "rows_clean": len(clean), "rows_no_time": int((~valid).sum()),
        "dropped_duplicates": C.DROP_EXACT_DUPLICATES, "dropped_conflicting": C.DROP_CONFLICTING,
        "quality": q, "features": feats, "dist": dist, "binary": binary,
        "split_report": split_report, "time_ranges": ranges, "time_info": time_info, "drop": drop,
        "top_auroc": top, "corr_groups": groups, "plan": plan, "inject": inject_check,
        "warnings": warnings,
    })
    _json(out / "manifest.json", {
        "eda_version": C.VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "args": vars(a),
        "params": _params(),
        "time_parsing": time_info,
        "warnings": warnings,
        "python": platform.python_version(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "runtime_sec": round(time.time() - started, 1),
    })
    for w in warnings:
        print(f"  UYARI: {w}", flush=True)
    print(f"Bitti: {out} ({time.time() - started:.1f} sn)", flush=True)


if __name__ == "__main__":
    main()
