from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

VERSION = "eda-v1"
SEED = 42

RATIOS = (0.70, 0.15, 0.15)
MIN_PER_SPLIT = 50
GAP_FRACTION = 0.005
FALLBACK_BLOCKS = 20

DROP_EXACT_DUPLICATES = True
DROP_CONFLICTING = False

ANALYSIS_CAP_PER_CLASS = 100_000
CAP_TRAIN = 200_000
CAP_VAL = 50_000

CORR_THRESHOLD = 0.95
CORR_SAMPLE = 200_000
AUROC_THRESHOLD = 0.95
AUROC_MIN_ROWS = 20
TREE_DEPTH = 3
TREE_MIN_LEAF = 20
HIST_SAMPLE = 100_000
HIST_MAX_FEATURES = 40

INJECT_NAME = "inj_spurious"
INJECT_STRENGTH = 0.99


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
        label_like_cols=("Attempted Category",),
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
        label_like_cols=("Label",),
    ),
}
