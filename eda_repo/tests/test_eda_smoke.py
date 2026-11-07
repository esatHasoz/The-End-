from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from eda.run import main


def make_cic(path_a, path_b, seed=0):
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2017-07-03 08:00")
    frames = []
    specs = [("BENIGN", 6000, 0, 4 * 24 * 60), ("DoS Hulk", 2000, 60, 120),
             ("PortScan", 1500, 2000, 3000), ("Web Attack � XSS", 30, 3500, 3510)]
    for label, n, lo, hi in specs:
        minutes = rng.uniform(lo, hi, n)
        attack = label != "BENIGN"
        frames.append(pd.DataFrame({
            "Flow ID": [f"f{i}" for i in range(n)],
            " Source IP": rng.choice(["192.168.10.5", "192.168.10.8"], n),
            " Source Port": rng.integers(1024, 65535, n),
            " Destination IP": rng.choice(["192.168.10.50", "8.8.8.8"], n),
            " Destination Port": np.where(attack, 80, rng.choice([443, 53, 22], n)),
            " Protocol": rng.choice([6, 17], n),
            " Timestamp": (start + pd.to_timedelta(minutes, unit="m")).strftime("%d/%m/%Y %I:%M:%S %p"),
            " Flow Duration": rng.exponential(1e5 if attack else 1e6, n),
            "Flow Bytes/s": np.where(rng.random(n) < 0.01, np.inf, rng.exponential(1e4, n)),
            " Fwd Header Length": rng.integers(20, 400, n),
            " Init_Win_bytes_forward": np.where(attack, 29200, rng.integers(0, 65535, n)),
            " Bwd Packets/s": rng.exponential(10, n),
            " Constant Col": np.zeros(n),
            " Label": label,
        }))
    df = pd.concat(frames, ignore_index=True)
    df.insert(df.columns.get_loc(" Fwd Header Length") + 1, " Fwd Header Length.1", df[" Fwd Header Length"])
    df = pd.concat([df, df.iloc[:200]], ignore_index=True)
    conflict = df.iloc[300:310].copy()
    conflict[" Label"] = "DoS Hulk"
    df = pd.concat([df, conflict], ignore_index=True)
    df.columns = [c.replace(".1", "") if c.endswith(".1") else c for c in df.columns]
    half = len(df) // 2
    df.iloc[:half].to_csv(path_a, index=False)
    df.iloc[half:].to_csv(path_b, index=False)


def make_nf3(path, seed=1):
    rng = np.random.default_rng(seed)
    n = 5000
    attack = rng.random(n) < 0.2
    t0 = 1_424_242_190_000
    start = t0 + rng.integers(0, 86_400_000, n)
    pd.DataFrame({
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
        "Label": attack.astype(int),
        "Attack": np.where(attack, rng.choice(["Exploits", "Fuzzers"], n), "Benign"),
    }).to_csv(path, index=False)


def check(out):
    q = json.loads((out / "quality_summary.json").read_text())
    drop = json.loads((out / "drop_cols.json").read_text())
    rep = pd.read_csv(out / "split_report.csv")
    auroc = pd.read_csv(out / "shortcut_candidates.csv")
    clean = pd.read_parquet(out / "clean.parquet")
    return q, drop, rep, auroc, clean


def no_time_overlap(clean, label_col):
    for cls, g in clean.groupby(label_col):
        rep_ok = True
        tr, va, te = (g.loc[g.split == k, "_time"] for k in ("train", "val", "test"))
        if len(tr) and len(va) and len(te):
            rep_ok = tr.max() <= va.min() and va.max() <= te.min()
        yield cls, rep_ok


def run(tmp):
    tmp = pathlib.Path(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    make_cic(tmp / "mon.csv", tmp / "tue.csv")
    main(["--name", "synthetic_cic", "--family", "cicflowmeter",
          "--inputs", str(tmp / "mon.csv"), str(tmp / "tue.csv"),
          "--out", str(tmp / "out_cic"), "--inject"])
    q, drop, rep, auroc, clean = check(tmp / "out_cic")
    assert q["duplicate_rows"] >= 200, q["duplicate_rows"]
    assert q["conflicting_rows"] >= 10, q["conflicting_rows"]
    assert "Flow Bytes/s" in q["columns_with_inf"]
    assert any(k.startswith("Fwd Header Length.") and v == "Fwd Header Length" for k, v in q["duplicate_columns"].items()), q["duplicate_columns"]
    assert "Constant Col" in drop["redundant"]
    for c in ("Flow ID", "Source IP", "Destination IP", "Timestamp"):
        assert c in drop["drop"], c
    assert "Destination Port" in drop["port_candidates"]
    assert "Destination Port" in drop["model_features"]
    assert "Web Attack - XSS" in set(clean["Label"])
    assert not rep.set_index("class").loc["Web Attack - XSS", "ok"]
    timeord = rep[rep.method == "time_order"]["class"].tolist()
    for cls, ok in no_time_overlap(clean, "Label"):
        if cls in timeord:
            assert ok, cls
    top = auroc[auroc.scope == "binary"].iloc[0]
    assert top.feature in ("Init_Win_bytes_forward", "Destination Port"), top.feature
    assert (tmp / "out_cic" / "injected_feature.parquet").exists()
    test_rows = clean[clean.split == "test"]
    plan = json.loads((tmp / "out_cic" / "sampling_config.json").read_text())
    assert plan["test"]["rows_after"] == len(test_rows)

    make_nf3(tmp / "nf3.csv")
    main(["--name", "synthetic_nf3", "--family", "netflow_v3",
          "--inputs", str(tmp / "nf3.csv"), "--out", str(tmp / "out_nf3")])
    q, drop, rep, auroc, clean = check(tmp / "out_nf3")
    for c in ("FLOW_START_MILLISECONDS", "FLOW_END_MILLISECONDS", "IPV4_SRC_ADDR", "Label"):
        assert c in drop["drop"], c
    assert "MIN_IP_PKT_LEN" in drop["review_manually"]
    assert "L4_DST_PORT" in drop["port_candidates"]
    assert rep["ok"].all(), rep
    top = auroc[auroc.scope == "binary"].iloc[0]
    assert top.feature == "MIN_TTL", top.feature
    print("SMOKE TEST OK")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "smoke_out")
