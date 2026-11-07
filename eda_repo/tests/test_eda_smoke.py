"""Smoke test: one synthetic file per project dataset, in that dataset's real format.

Run from the repo root:  python tests/test_eda_smoke.py smoke_out
The last line must be SMOKE TEST OK.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from eda.run import main  # noqa: E402

CIC_SPECS = [  # label, rows, start minute, end minute (from Monday 08:00)
    ("BENIGN", 6000, 0, 4 * 24 * 60),
    ("DoS Hulk", 2000, 60, 120),                 # 09:00-10:00 Monday
    ("PortScan", 1500, 6 * 60, 7 * 60),          # 14:00-15:00 Monday (afternoon!)
    ("Web Attack � XSS", 30, 3500, 3510),   # too small for a split
]


def _cic_frame(rng, specs, start, fmt, names):
    frames = []
    for label, n, lo, hi in specs:
        minutes = np.sort(rng.uniform(lo, hi, n))
        attack = not str(label).upper().startswith("BENIGN")
        ts = start + pd.to_timedelta(minutes, unit="m")
        frames.append(pd.DataFrame({
            names["fid"]: [f"f{i}" for i in range(n)],
            names["sip"]: rng.choice(["192.168.10.5", "192.168.10.8"], n),
            names["sport"]: rng.integers(1024, 65535, n),
            names["dip"]: rng.choice(["192.168.10.50", "8.8.8.8"], n),
            names["dport"]: np.where(attack, 80, rng.choice([443, 53, 22], n)),
            " Protocol": rng.choice([6, 17], n),
            names["ts"]: fmt(ts),
            " Flow Duration": rng.exponential(1e5 if attack else 1e6, n),
            "Flow Bytes/s": np.where(rng.random(n) < 0.01, np.inf, rng.exponential(1e4, n)),
            " Fwd Header Length": rng.integers(20, 400, n),
            " Init_Win_bytes_forward": np.where(attack, 29200, rng.integers(0, 65535, n)),
            " Bwd Packets/s": rng.exponential(10, n),
            " Constant Col": np.zeros(n),
            " Label": label,
        }))
    return pd.concat(frames, ignore_index=True)


def _twelve_hour_no_ampm(ts):
    # CICIDS2017 TrafficLabelling style: '3/7/2017 2:05' means 14:05
    return [f"{t.day}/{t.month}/{t.year} {t.hour % 12 or 12}:{t.minute:02d}" for t in ts]


def make_cic_orig(path_a, path_b, seed=0):
    rng = np.random.default_rng(seed)
    names = dict(fid="Flow ID", sip=" Source IP", sport=" Source Port", dip=" Destination IP",
                 dport=" Destination Port", ts=" Timestamp")
    df = _cic_frame(rng, CIC_SPECS, pd.Timestamp("2017-07-03 08:00"), _twelve_hour_no_ampm, names)
    # repeated column, as in the original release
    df.insert(df.columns.get_loc(" Fwd Header Length") + 1, " Fwd Header Length.1", df[" Fwd Header Length"])
    df = pd.concat([df, df.iloc[:200]], ignore_index=True)          # exact duplicates
    conflict = df.iloc[300:310].copy()
    conflict[" Label"] = "DoS Hulk"
    df = pd.concat([df, conflict], ignore_index=True)               # conflicting labels
    empty = pd.DataFrame(np.nan, index=range(50), columns=df.columns)
    df = pd.concat([df, empty], ignore_index=True)                  # empty rows (Thursday file)
    header = [c[:-2] if c.endswith(".1") else c for c in df.columns]
    half = len(df) // 2
    df.iloc[:half].to_csv(path_a, index=False, header=header)
    df.iloc[half:].to_csv(path_b, index=False, header=header)


def make_cic_corrected(path, seed=1):
    rng = np.random.default_rng(seed)
    names = dict(fid="Flow ID", sip="Src IP", sport="Src Port", dip="Dst IP", dport="Dst Port", ts="Timestamp")
    specs = CIC_SPECS[:3] + [("DoS Hulk - Attempted", 300, 60, 120)]
    df = _cic_frame(rng, specs, pd.Timestamp("2017-07-03 08:00"),
                    lambda ts: ts.strftime("%Y-%m-%d %H:%M:%S.%f"), names)
    df.insert(0, "id", np.arange(len(df)))
    df["Attempted Category"] = np.where(df[" Label"].str.contains("Attempted"), 1, -1)
    df.columns = [c.strip() for c in df.columns]
    df.to_csv(path, index=False)


def make_cicflowmeter_reextracted(path, seed=2, need_label=False):
    """Fixed CICFlowMeter output (Group C): dd/MM/yyyy hh:mm:ss AM/PM, label in 'Label'."""
    rng = np.random.default_rng(seed)
    names = dict(fid="Flow ID", sip="Src IP", sport="Src Port", dip="Dst IP", dport="Dst Port", ts="Timestamp")
    specs = [("Benign", 5000, 0, 600), ("SYNFlood", 800, 100, 160), ("SYNScan", 700, 400, 460)]
    df = _cic_frame(rng, specs, pd.Timestamp("2022-05-10 10:00"),
                    lambda ts: ts.strftime("%d/%m/%Y %I:%M:%S %p"), names)
    df.columns = [c.strip() for c in df.columns]
    if need_label:
        df["Label"] = "NeedManualLabel"
    df.to_csv(path, index=False)


def make_published_no_time(path, seed=3):
    """Plan B style file (e.g. TII-SSRC-23 published CSV): no timestamp, several label columns."""
    rng = np.random.default_rng(seed)
    n = 4000
    typ = rng.choice(["Benign", "DoS", "Mirai"], n, p=[0.7, 0.2, 0.1])
    pd.DataFrame({
        "Unnamed: 0": np.arange(n),
        "Flow Duration": rng.exponential(1e5, n),
        "Tot Fwd Pkts": np.where(typ == "Mirai", 3, rng.integers(1, 50, n)),
        "Pkt Len Mean": rng.exponential(300, n),
        "Label": np.where(typ == "Benign", "Benign", "Malicious"),
        "Traffic Type": typ,
        "Traffic Subtype": typ,
    }).to_csv(path, index=False)


def make_nf3(path, seed=4, n=6000, attacks=("Exploits", "Fuzzers"), with_nan_time=False):
    rng = np.random.default_rng(seed)
    attack = rng.random(n) < 0.2
    t0 = 1_424_242_190_123
    start = (t0 + np.sort(rng.integers(0, 86_400_000, n))).astype("float64")
    if with_nan_time:
        start[5] = np.nan                     # forces a float column, as in real files
    df = pd.DataFrame({
        "FLOW_START_MILLISECONDS": start,
        "FLOW_END_MILLISECONDS": start + rng.integers(0, 5000, n),
        "IPV4_SRC_ADDR": rng.choice(["59.166.0.1", "175.45.176.1"], n),
        "L4_SRC_PORT": rng.integers(1024, 65535, n),
        "IPV4_DST_ADDR": rng.choice(["149.171.126.1", "149.171.126.9"], n),
        "L4_DST_PORT": rng.choice([80, 53, 111], n),
        "PROTOCOL": rng.choice([6, 17], n),
        "IN_BYTES": rng.exponential(1000, n),
        "OUT_BYTES": rng.exponential(2000, n),
        "MIN_TTL": np.where(attack, 254, 31),
        "MIN_IP_PKT_LEN": rng.integers(20, 100, n),
        "SRC_TO_DST_IAT_AVG": rng.exponential(50, n),
        "Label": attack.astype(int),
        "Attack": np.where(attack, rng.choice(list(attacks), n), "Benign"),
    })
    df.to_csv(path, index=False)
    return start


def load(out):
    out = pathlib.Path(out)
    return {
        "q": json.loads((out / "quality_summary.json").read_text()),
        "drop": json.loads((out / "drop_cols.json").read_text()),
        "rep": pd.read_csv(out / "split_report.csv"),
        "auroc": pd.read_csv(out / "shortcut_candidates.csv"),
        "clean": pd.read_parquet(out / "clean.parquet"),
        "manifest": json.loads((out / "manifest.json").read_text()),
        "inject": (json.loads((out / "injected_feature_check.json").read_text())
                   if (out / "injected_feature_check.json").exists() else None),
        "plan": json.loads((out / "sampling_config.json").read_text()),
    }


def check_common(r, label_col, benign):
    clean, rep = r["clean"], r["rep"]
    # no time overlap between train/val/test inside a class split by time order
    for cls in rep.loc[rep.method == "time_order", "class"]:
        g = clean[clean[label_col].astype(str) == cls]
        tr, va, te = (g.loc[g.split == k, "_time"] for k in ("train", "val", "test"))
        assert tr.max() <= va.min() and va.max() <= te.min(), cls
    # test is never sampled
    assert r["plan"]["test"]["rows_after"] == int((clean.split == "test").sum())
    # identifiers never reach the model
    feats = set(r["drop"]["model_features"])
    assert not feats & set(r["drop"]["id_columns"]), feats & set(r["drop"]["id_columns"])
    # injected feature: correlated in train/val, label-independent in test
    if r["inject"]:
        agr = r["inject"]["agreement_with_label"]
        assert agr["train"] > 0.97 and agr["val"] > 0.97, agr
        p = float((clean.loc[clean.split == "test", label_col].astype(str) != benign).mean())
        expected = 1 - 2 * p * (1 - p)
        assert abs(agr["test"] - expected) < 0.06, (agr, expected)


def run(tmp):
    tmp = pathlib.Path(tmp)
    tmp.mkdir(parents=True, exist_ok=True)

    # 1) CICIDS2017 original: 12-hour clock without AM/PM, empty rows, repeated column
    make_cic_orig(tmp / "mon.csv", tmp / "tue.csv")
    main(["--dataset", "cicids2017_orig", "--inputs", str(tmp / "mon.csv"), str(tmp / "tue.csv"),
          "--out", str(tmp / "cicids2017_orig")])
    r = load(tmp / "cicids2017_orig")
    q, drop, clean = r["q"], r["drop"], r["clean"]
    assert q["duplicate_rows"] >= 200 and q["conflicting_rows"] >= 10, q
    assert "Flow Bytes/s" in q["columns_with_inf"]
    assert q["duplicate_columns"].get("Fwd Header Length.dup1") == "Fwd Header Length", q["duplicate_columns"]
    assert "Constant Col" in drop["redundant"]
    for c in ("Flow ID", "Source IP", "Destination IP", "Timestamp"):
        assert c in drop["drop"], c
    assert "Destination Port" in drop["port_candidates"] and "Destination Port" in drop["model_features"]
    assert "Web Attack - XSS" in set(clean["Label"].astype(str))
    assert "nan" not in set(clean["Label"].astype(str))
    assert r["manifest"]["time_parsing"]["ampm_applied"] is True
    ps = clean.loc[clean.Label.astype(str) == "PortScan", "_time"]
    assert ps.dt.hour.between(14, 15).all(), ps.dt.hour.value_counts()
    assert not r["rep"].set_index("class").loc["Web Attack - XSS", "ok"]
    top = r["auroc"][r["auroc"].scope == "binary"].iloc[0]
    assert top.feature in ("Init_Win_bytes_forward", "Destination Port"), top.feature
    check_common(r, "Label", "BENIGN")

    # 2) CICIDS2017 corrected: ISO 24 h timestamps, 'id', Attempted classes
    make_cic_corrected(tmp / "corrected.csv")
    for policy in ("keep", "benign", "drop"):
        out = tmp / f"cicids2017_corrected_{policy}"
        main(["--dataset", "cicids2017_corrected", "--inputs", str(tmp / "corrected.csv"),
              "--out", str(out), "--attempted", policy])
        r = load(out)
        classes = set(r["clean"]["Label"].astype(str))
        assert ("DoS Hulk - Attempted" in classes) == (policy == "keep"), (policy, classes)
        assert "id" in r["drop"]["drop"] and "Attempted Category" in r["drop"]["drop"]
        assert r["manifest"]["time_parsing"].get("ampm_applied") is False
        check_common(r, "Label", "BENIGN")

    # 3) NF3-UNSW-NB15
    make_nf3(tmp / "NF-UNSW-NB15-v3.csv")
    main(["--dataset", "nf3_unsw_nb15", "--inputs", str(tmp / "NF-UNSW-NB15-v3.csv"),
          "--out", str(tmp / "nf3_unsw_nb15")])
    r = load(tmp / "nf3_unsw_nb15")
    for c in ("FLOW_START_MILLISECONDS", "FLOW_END_MILLISECONDS", "IPV4_SRC_ADDR", "IPV4_DST_ADDR", "Label"):
        assert c in r["drop"]["drop"], c
    assert "SRC_TO_DST_IAT_AVG" in r["drop"]["model_features"]
    assert "MIN_IP_PKT_LEN" not in r["drop"]["review_manually"]
    assert "L4_DST_PORT" in r["drop"]["port_candidates"]
    assert r["rep"]["ok"].all(), r["rep"]
    assert r["auroc"][r["auroc"].scope == "binary"].iloc[0].feature == "MIN_TTL"
    check_common(r, "Attack", "Benign")

    # 4) NF3-CSE-CIC-IDS2018 with --frac and a float time column (precision check)
    start = make_nf3(tmp / "NF-CSE-CIC-IDS2018-v3.csv", seed=5, n=12000,
                     attacks=("DDoS", "DoS", "BruteForce"), with_nan_time=True)
    main(["--dataset", "nf3_cse_cic_ids2018", "--inputs", str(tmp / "NF-CSE-CIC-IDS2018-v3.csv"),
          "--out", str(tmp / "nf3_cse_cic_ids2018"), "--frac", "0.5"])
    r = load(tmp / "nf3_cse_cic_ids2018")
    raw = pd.read_parquet(tmp / "nf3_cse_cic_ids2018" / "raw.parquet", columns=["FLOW_START_MILLISECONDS"])
    assert raw["FLOW_START_MILLISECONDS"].dtype == np.float64, raw.dtypes
    t = r["clean"]["_time"].dropna()
    ms = (t - pd.Timestamp("1970-01-01")) // pd.Timedelta(milliseconds=1)
    assert set(ms.astype("int64")) <= set(start[~np.isnan(start)].astype("int64")), "time precision lost"
    assert 0.4 < r["manifest"]["args"]["frac"] <= 0.5
    check_common(r, "Attack", "Benign")

    # 5) 5G-NIDD re-extracted with CICFlowMeter (AM/PM present, 'Benign' spelled differently)
    make_cicflowmeter_reextracted(tmp / "5g_nidd.csv")
    main(["--dataset", "5g_nidd", "--inputs", str(tmp / "5g_nidd.csv"), "--out", str(tmp / "5g_nidd")])
    r = load(tmp / "5g_nidd")
    assert any("case-insensitively" in w for w in r["manifest"]["warnings"]), r["manifest"]["warnings"]
    assert "Src IP" in r["drop"]["drop"] and "Dst Port" in r["drop"]["port_candidates"]
    check_common(r, "Label", "Benign")

    # unlabelled CICFlowMeter output must stop with a clear message
    make_cicflowmeter_reextracted(tmp / "unlabelled.csv", need_label=True)
    try:
        main(["--dataset", "5g_nidd", "--inputs", str(tmp / "unlabelled.csv"), "--out", str(tmp / "x")])
        raise AssertionError("NeedManualLabel was not rejected")
    except SystemExit as e:
        assert "NeedManualLabel" in str(e), e

    # 6) TII-SSRC-23: re-extracted (same format as 5G-NIDD) and Plan B (published CSV, no time)
    make_cicflowmeter_reextracted(tmp / "tii.csv", seed=6)
    main(["--dataset", "tii_ssrc_23", "--inputs", str(tmp / "tii.csv"), "--out", str(tmp / "tii_ssrc_23")])
    check_common(load(tmp / "tii_ssrc_23"), "Label", "Benign")

    pq = tmp / "tii_published.parquet"
    make_published_no_time(tmp / "tii_published.csv")
    pd.read_csv(tmp / "tii_published.csv").to_parquet(pq, index=False)
    main(["--dataset", "tii_ssrc_23", "--inputs", str(pq), "--out", str(tmp / "tii_planb"),
          "--label-col", "Traffic Type", "--benign-label", "Benign", "--time-col", "__row_order__"])
    r = load(tmp / "tii_planb")
    for c in ("Label", "Traffic Subtype", "Unnamed: 0"):
        assert c in r["drop"]["drop"], c
    assert any("row order" in w for w in r["manifest"]["warnings"])
    check_common(r, "Traffic Type", "Benign")

    print("SMOKE TEST OK")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "smoke_out")
