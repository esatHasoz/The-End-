from __future__ import annotations

import pandas as pd


def _fmt(v):
    if isinstance(v, float):
        return f"{v:,.4f}".rstrip("0").rstrip(".")
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


def md_table(df, max_rows=None):
    if df is None or len(df) == 0:
        return "_(empty)_"
    if max_rows:
        df = df.head(max_rows)
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(map(str, cols)) + " |",
        "|" + "|".join(["---"] * len(cols)) + "|",
    ]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(_fmt(v) for v in row) + " |")
    return "\n".join(lines)


def write_summary(path, ctx):
    q = ctx["quality"]
    lines = [
        f"# EDA summary: {ctx['name']}",
        "",
        f"- EDA version: `{ctx['version']}`, seed {ctx['seed']}",
        f"- Family: {ctx['family']}, label column `{ctx['label_col']}`, benign label `{ctx['benign']}`",
        f"- Rows: {ctx['rows_loaded']:,} loaded, {ctx['rows_raw']:,} with a valid label, {ctx['rows_clean']:,} after cleaning",
        f"- Duplicate rows (features + label): {q['duplicate_rows']:,}"
        + (" (removed)" if ctx["dropped_duplicates"] else " (kept)"),
        f"- Conflicting rows (same features, different label): {q['conflicting_rows']:,}"
        + (" (removed)" if ctx["dropped_conflicting"] else " (kept, reported)"),
        f"- Rows without a valid timestamp: {ctx['rows_no_time']:,}",
        f"- Model features: {len(ctx['features'])}",
        f"- Time parsing: {ctx['time_info']}",
        "",
    ]
    if ctx["warnings"]:
        lines += ["## Warnings", ""] + [f"- {w}" for w in ctx["warnings"]] + [""]
    lines += [
        "## Data quality",
        "",
        f"- Columns with inf: {', '.join(q['columns_with_inf']) or 'none'}",
        f"- Columns with NaN: {', '.join(q['columns_with_nan']) or 'none'}",
        f"- Constant columns: {', '.join(q['constant_columns']) or 'none'}",
        "- Duplicate columns: "
        + (", ".join(f"{k} = {v}" for k, v in q["duplicate_columns"].items()) or "none"),
        "",
        "## Class distribution",
        "",
        md_table(ctx["dist"]),
        "",
        f"Binary (clean): {ctx['binary']}",
        "",
        "## Time split",
        "",
        md_table(ctx["split_report"]),
        "",
        f"Time ranges: {ctx['time_ranges']}",
        "",
    ]
    bad = ctx["split_report"].loc[~ctx["split_report"]["ok"], "class"].tolist()
    if bad:
        lines += [f"**Classes with too few rows in a split:** {', '.join(bad)}", ""]
    lines += [
        "## Identifier and leakage columns",
        "",
        f"- Dropped: {', '.join(ctx['drop']['drop']) or 'none'}",
        f"- Redundant (constant or duplicate): {', '.join(ctx['drop']['redundant']) or 'none'}",
        f"- Port columns kept as shortcut candidates: {', '.join(ctx['drop']['port_candidates']) or 'none'}",
        f"- Review manually: {', '.join(ctx['drop']['review_manually']) or 'none'}",
        "",
        "## Shortcut candidates (train, single-feature AUROC)",
        "",
        md_table(ctx["top_auroc"]),
        "",
        "## Correlated groups (train, Spearman)",
        "",
    ]
    lines += [f"- {', '.join(g)}" for g in ctx["corr_groups"]] or ["none"]
    lines += [
        "",
        "## Sampling",
        "",
        f"- train cap per class: {ctx['plan']['train']['cap_per_class']}, rows {ctx['plan']['train']['rows_before']:,} -> {ctx['plan']['train']['rows_after']:,}",
        f"- val cap per class: {ctx['plan']['val']['cap_per_class']}, rows {ctx['plan']['val']['rows_before']:,} -> {ctx['plan']['val']['rows_after']:,}",
        f"- test: not sampled, {ctx['plan']['test']['rows_after']:,} rows",
        "",
        "## Injected spurious feature",
        "",
        (f"- Agreement with the binary label per split: {ctx['inject']} "
         "(train/val should be about the strength, test label-independent)")
        if ctx["inject"] else "- skipped",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
