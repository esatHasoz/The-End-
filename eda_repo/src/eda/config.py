"""Shared EDA settings. Every number used by the pipeline lives here.

Changing anything in this file means a new EDA version: bump VERSION, open a PR,
and re-run all six datasets.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

VERSION = "eda-v2"
SEED = 42

# --- split -------------------------------------------------------------------
RATIOS = (0.70, 0.15, 0.15)
MIN_PER_SPLIT = 50          # a class needs at least this many rows in train, val and test
GAP_FRACTION = 0.005        # rows left out between consecutive splits (per class)
FALLBACK_BLOCKS = 20        # time blocks used when the plain time order fails

# --- cleaning ----------------------------------------------------------------
DROP_EXACT_DUPLICATES = True    # same features + same label
DROP_CONFLICTING = False        # same features, different label: kept, flagged, reported
FLOAT32 = True                  # float64 -> float32 at load (halves memory)

# --- analysis (train only) ---------------------------------------------------
ANALYSIS_CAP_PER_CLASS = 100_000
CORR_THRESHOLD = 0.95
CORR_SAMPLE = 200_000
AUROC_THRESHOLD = 0.95
AUROC_MIN_ROWS = 20
TREE_DEPTH = 3
TREE_MIN_LEAF = 20
HIST_SAMPLE = 100_000
HIST_MAX_FEATURES = 40

# --- sampling for modelling --------------------------------------------------
CAP_TRAIN = 200_000         # per class
CAP_VAL = 50_000            # per class; test is never sampled

# --- injected spurious feature (RQ2 ground truth) ----------------------------
INJECT_NAME = "inj_spurious"
INJECT_STRENGTH = 0.99      # P(feature == is_attack) in train and val
# In test the feature is drawn independently of the label with the same base
# rate, so a model that relies on it loses performance on test.

# --- time --------------------------------------------------------------------
ROW_ORDER = "__row_order__"  # pass as --time-col when a dataset has no timestamp
AMPM_SHIFT_HOURS = (1, 7)    # 12-hour clock without AM/PM: hours 1..7 are read as 13..19


@dataclass(frozen=True)
class Family:
    name: str
    label_col: str
    benign_label: str
    time_col: str
    time_unit: Optional[str]
    id_cols: tuple
    port_cols: tuple
    label_like_cols: tuple = ()
    dayfirst: bool = False


FAMILIES = {
    "cicflowmeter": Family(
        name="cicflowmeter",
        label_col="Label",
        benign_label="BENIGN",
        time_col="Timestamp",
        time_unit=None,
        id_cols=(
            "Flow ID", "Source IP", "Destination IP", "Src IP", "Dst IP",
            "Timestamp", "id",
        ),
        port_cols=("Source Port", "Destination Port", "Src Port", "Dst Port"),
        # Other label columns that some releases ship next to the main label.
        # Whichever one is not --label-col is removed from the features.
        label_like_cols=(
            "Label", "Attempted Category", "Traffic Type", "Traffic Subtype",
            "Attack Type", "Attack Tool", "Attack",
        ),
        dayfirst=True,
    ),
    "netflow_v3": Family(
        name="netflow_v3",
        label_col="Attack",
        benign_label="Benign",
        time_col="FLOW_START_MILLISECONDS",
        time_unit="ms",
        id_cols=(
            "IPV4_SRC_ADDR", "IPV4_DST_ADDR",
            "FLOW_START_MILLISECONDS", "FLOW_END_MILLISECONDS",
        ),
        port_cols=("L4_SRC_PORT", "L4_DST_PORT"),
        label_like_cols=("Label", "Attack"),
    ),
}


@dataclass(frozen=True)
class Dataset:
    name: str
    family: str
    group: str
    owner: str
    source_url: str = ""
    version: str = ""
    license: str = ""
    label_col: Optional[str] = None
    benign_label: Optional[str] = None
    time_col: Optional[str] = None
    ampm_fix: str = "off"           # auto | on | off
    extra_drop: tuple = field(default_factory=tuple)
    notes: str = ""


UQ_LICENSE = "Permitted Re-Use with Commercial Use Restriction (UQ RDM)"

DATASETS = {
    "cicids2017_orig": Dataset(
        name="cicids2017_orig", family="cicflowmeter", group="A", owner="Ahmet",
        source_url="https://www.unb.ca/cic/datasets/ids-2017.html",
        version="GeneratedLabelledFlows / TrafficLabelling CSVs",
        license="CIC/UNB dataset terms; cite Sharafaldin et al. 2018",
        ampm_fix="auto",
        notes=(
            "Use the TrafficLabelling CSVs. MachineLearningCVE CSVs have no Timestamp "
            "or IP columns and will stop at step 1. Timestamps use a 12-hour clock "
            "without AM/PM; ampm_fix=auto detects this and shifts hours 1-7 by 12."
        ),
    ),
    "cicids2017_corrected": Dataset(
        name="cicids2017_corrected", family="cicflowmeter", group="A", owner="Ahmet",
        version="Engelen et al. 2021 (WTMC) corrected CICIDS2017",
        license="see dataset page; cite Engelen et al. 2021",
        ampm_fix="auto",
        notes=(
            "Contains '- Attempted' classes. Default --attempted keep treats them as "
            "separate classes (attack in binary). Record the CICFlowMeter build used "
            "and pass it to Selim."
        ),
    ),
    "nf3_cse_cic_ids2018": Dataset(
        name="nf3_cse_cic_ids2018", family="netflow_v3", group="B", owner="Esad",
        source_url="https://rdm.uq.edu.au/files/4ac221b1-6bd6-42b1-bdf7-03f4fc7efb22",
        version="NetFlow v3 (Luay et al. 2025)", license=UQ_LICENSE,
        notes="About 20M flows. Start with --frac 0.25 on a 16 GB machine.",
    ),
    "nf3_unsw_nb15": Dataset(
        name="nf3_unsw_nb15", family="netflow_v3", group="B", owner="Esad",
        source_url="https://rdm.uq.edu.au/files/abd2f5d8-e268-4ff0-84fb-f2f7b3ca3e8f",
        version="NetFlow v3 (Luay et al. 2025)", license=UQ_LICENSE,
        notes="About 2.4M flows. Smallest set; template is tested on it first.",
    ),
    "5g_nidd": Dataset(
        name="5g_nidd", family="cicflowmeter", group="C", owner="Selim",
        version="flows re-extracted from GTP-removed pcaps with the fixed CICFlowMeter",
        license="see dataset page; cite Samarakoon et al. 2022",
        label_col="Label", benign_label="BENIGN",
        notes=(
            "Flows must be labelled before EDA (CICFlowMeter writes 'NeedManualLabel'). "
            "Use BENIGN for benign flows. Plan B (published Argus features): "
            "--time-col __row_order__ and drop the extra label columns with --extra-drop."
        ),
    ),
    "tii_ssrc_23": Dataset(
        name="tii_ssrc_23", family="cicflowmeter", group="C", owner="Selim",
        version="flows re-extracted from pcaps with the fixed CICFlowMeter",
        license="see dataset page; cite Herzalla et al. 2023",
        label_col="Label", benign_label="BENIGN",
        notes=(
            "About 8.6M flows. Flows must be labelled before EDA. Use BENIGN for benign "
            "flows. Plan B (published CSV): pass --label-col 'Traffic Type' or similar; "
            "the other label columns are removed automatically."
        ),
    ),
}
