"""Grup C hazırlık script'i: yayınlanmış 5G-NIDD ve TII-SSRC-23 CSV'lerini ortak EDA koduna uygun hale getirir.

Ham dosyalara dokunmaz; yeni bir parquet dosyası yazar.

    python scripts/prep_group_c.py tii   data/raw/tii_ssrc_23/*.csv  --out data/interim/tii_ssrc_23/tii_published.parquet
    python scripts/prep_group_c.py 5gnidd data/raw/5g_nidd/Combined.csv --out data/interim/5g_nidd/5g_nidd_published.parquet

Ne yapar:
  TII-SSRC-23 : Flow ID ve IP sütunlarını çıkarır (kimlik; bellek için), `Class` etiket sütunu üretir: Label == Benign ise "Benign", değilse Traffic Type
                (Bruteforce, DoS, Information Gathering, Mirai). Benign trafiğin Traffic Type'ı
                Audio/Background/Text/Video olduğu için bu birleştirme gerekli.
  5G-NIDD     : Argus sütunlarını EDA kodunun tanıdığı adlara çevirir (SrcAddr -> Src IP,
                Sport -> Src Port, ...), hex portları sayıya çevirir, `Class` etiketini üretir
                (Attack Type, yoksa Label), zaman sütununu `Timestamp` yapar ve `Seq`'i
                (Argus kayıt sıra numarası = kimlik) çıkarır. --keep-seq ile tutulabilir.
Çıktının sonunda EDA için çalıştırılacak komut yazdırılır.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

CHUNK = 500_000
BENIGN = "Benign"

# Argus adı (küçük harf) -> EDA kodunun cicflowmeter ailesinde tanıdığı ad
ARGUS_RENAME = {
    "srcaddr": "Src IP", "saddr": "Src IP",
    "dstaddr": "Dst IP", "daddr": "Dst IP",
    "sport": "Src Port", "dport": "Dst Port",
    "starttime": "Timestamp", "stime": "Timestamp",
}
ARGUS_DROP = {"seq"}                       # kimlik; EDA'ya girmez (--keep-seq ile tutulur)
ARGUS_TIME_EXTRA = {"lasttime", "ltime"}   # bitiş zamanı: zaman bilgisi, özellik değil


def find(cols, *names):
    low = {c.strip().lower(): c for c in cols}
    for n in names:
        if n.lower() in low:
            return low[n.lower()]
    return None


def to_port(s):
    """Argus portları bazen hex ('0x0303') veya boş yazar."""
    num = pd.to_numeric(s, errors="coerce")
    bad = num.isna() & s.notna()
    if bad.any():
        def conv(v):
            try:
                return float(int(str(v).strip(), 0))
            except ValueError:
                return np.nan
        num[bad] = s[bad].map(conv)
    return num.astype("float64")


def stable(chunk):
    """Her chunk'ta aynı şema: sayısal -> float32 (EDA zaten float32'ye çeviriyor; bellek yarıya iner),
    diğerleri -> string."""
    for c in chunk.columns:
        if pd.api.types.is_numeric_dtype(chunk[c]) and not pd.api.types.is_bool_dtype(chunk[c]):
            chunk[c] = chunk[c].astype("float32")
        else:
            chunk[c] = chunk[c].astype("string")
    return chunk


TII_ID_COLS = ("Flow ID", "Src IP", "Dst IP")  # kimlik; EDA de çıkarıyor, burada çıkarmak belleği azaltır


def prep_tii(chunk, info):
    ids = [c for c in TII_ID_COLS if c in chunk.columns]
    if ids:
        chunk = chunk.drop(columns=ids)
        info["dropped"].update(ids)
    lab = find(chunk.columns, "Label")
    typ = find(chunk.columns, "Traffic Type")
    if lab is None or typ is None:
        sys.exit(f"TII: 'Label' veya 'Traffic Type' sütunu yok. Sütunlar: {list(chunk.columns)[:30]}")
    is_benign = chunk[lab].astype(str).str.strip().str.lower() == BENIGN.lower()
    chunk["Class"] = np.where(is_benign, BENIGN, chunk[typ].astype(str).str.strip())
    info["benign_types"].update(chunk.loc[is_benign, typ].astype(str).str.strip().unique())
    return chunk


def prep_5g(chunk, info, keep_seq):
    ren = {}
    for c in chunk.columns:
        k = c.strip().lower()
        if k in ARGUS_RENAME and ARGUS_RENAME[k] not in ren.values():
            ren[c] = ARGUS_RENAME[k]
    chunk = chunk.rename(columns=ren)
    info["renamed"].update(f"{a} -> {b}" for a, b in ren.items())
    drop = [c for c in chunk.columns
            if c.strip().lower() in ARGUS_TIME_EXTRA or (c.strip().lower() in ARGUS_DROP and not keep_seq)]
    if drop:
        chunk = chunk.drop(columns=drop)
        info["dropped"].update(drop)
    for p in ("Src Port", "Dst Port"):
        if p in chunk.columns:
            chunk[p] = to_port(chunk[p])
    typ = find(chunk.columns, "Attack Type", "Attack_Type", "AttackType")
    lab = find(chunk.columns, "Label")
    src = typ or lab
    if src is None:
        sys.exit(f"5G-NIDD: etiket sütunu ('Attack Type' / 'Label') yok. Sütunlar: {list(chunk.columns)[:40]}")
    cls = chunk[src].astype(str).str.strip()
    if lab is not None:
        cls = cls.where(chunk[lab].astype(str).str.strip().str.lower() != BENIGN.lower(), BENIGN)
    chunk["Class"] = cls.where(cls.str.lower() != BENIGN.lower(), BENIGN)
    return chunk


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("dataset", choices=["tii", "5gnidd"])
    p.add_argument("inputs", nargs="+")
    p.add_argument("--out", required=True)
    p.add_argument("--keep-seq", action="store_true", help="5G-NIDD: Seq sütununu çıkarma")
    a = p.parse_args(argv)

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    info = {"rows": 0, "classes": {}, "benign_types": set(), "renamed": set(), "dropped": set(),
            "has_time": None}
    writer, schema = None, None
    for path in a.inputs:
        for chunk in pd.read_csv(path, chunksize=CHUNK, low_memory=False, encoding_errors="replace"):
            chunk.columns = [str(c).strip() for c in chunk.columns]
            chunk = prep_tii(chunk, info) if a.dataset == "tii" else prep_5g(chunk, info, a.keep_seq)
            chunk = stable(chunk)
            if info["has_time"] is None:
                info["has_time"] = "Timestamp" in chunk.columns
            for k, v in chunk["Class"].value_counts().items():
                info["classes"][k] = info["classes"].get(k, 0) + int(v)
            table = pa.Table.from_pandas(chunk, preserve_index=False)
            if writer is None:
                schema = table.schema
                writer = pq.ParquetWriter(out, schema)
            else:
                missing = set(schema.names) ^ set(table.schema.names)
                if missing:
                    sys.exit(f"{path}: sütunlar önceki dosyalardan farklı: {sorted(missing)}")
                table = table.select(schema.names).cast(schema)
            writer.write_table(table)
            info["rows"] += len(chunk)
            print(f"  {pathlib.Path(path).name}: {info['rows']:,} satır", flush=True)
    if writer is None:
        sys.exit("Hiç satır okunmadı.")
    writer.close()

    print(f"\nYazıldı: {out}  ({info['rows']:,} satır)")
    print("Sınıflar (Class):")
    for k, v in sorted(info["classes"].items(), key=lambda x: -x[1]):
        print(f"  {k:30s} {v:>12,}")
    if a.dataset == "tii":
        print(f"Benign olan Traffic Type değerleri: {sorted(info['benign_types'])}")
        print(f"Çıkarılan (kimlik): {sorted(info['dropped']) or 'yok'}")
    else:
        print(f"Yeniden adlandırılan: {sorted(info['renamed']) or 'yok'}")
        print(f"Çıkarılan: {sorted(info['dropped']) or 'yok'}")
    time_arg = "" if info["has_time"] else " --time-col __row_order__"
    if not info["has_time"]:
        print("UYARI: zaman sütunu bulunamadı; satır sırası zaman olarak kullanılacak.")
    preset = "tii_ssrc_23" if a.dataset == "tii" else "5g_nidd"
    print("\nŞimdi EDA'yı çalıştır (eda_repo klasöründen):")
    print(f"PYTHONPATH=src python -m eda --dataset {preset} --inputs {out} --out results/eda/{preset} "
          f"--label-col Class --benign-label {BENIGN}{time_arg}")


if __name__ == "__main__":
    main()