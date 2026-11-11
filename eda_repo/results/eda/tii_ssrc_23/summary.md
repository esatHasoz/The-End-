# EDA summary: tii_ssrc_23

- EDA version: `eda-v2`, seed 42
- Family: cicflowmeter, label column `Class`, benign label `Benign`
- Rows: 8,656,767 loaded, 8,656,767 with a valid label, 8,653,998 after cleaning
- Duplicate rows (features + label): 2,769 (removed)
- Conflicting rows (same features, different label): 35 (kept, reported)
- Rows without a valid timestamp: 0
- Model features: 72
- Time parsing: {'method': 'text_inferred_format', 'ampm_fix': 'off', 'ampm_shifted_rows': 0}

## Data quality

- Columns with inf: none
- Columns with NaN: none
- Constant columns: Bwd PSH Flags, Bwd URG Flags, Fwd Bytes/Bulk Avg, Fwd Packet/Bulk Avg, Fwd Bulk Rate Avg
- Duplicate columns: Bwd URG Flags = Bwd PSH Flags, Fwd Segment Size Avg = Fwd Packet Length Mean, Bwd Segment Size Avg = Bwd Packet Length Mean, Fwd Bytes/Bulk Avg = Bwd PSH Flags, Fwd Packet/Bulk Avg = Bwd PSH Flags, Fwd Bulk Rate Avg = Bwd PSH Flags

## Class distribution

| class | is_attack | count_raw | count | removed | pct | imbalance_vs_largest |
|---|---|---|---|---|---|---|
| DoS | 1 | 7,490,929 | 7,490,852 | 77 | 86.5594 | 1 |
| Information Gathering | 1 | 1,038,363 | 1,038,362 | 1 | 11.9986 | 7.21 |
| Mirai | 1 | 91,002 | 88,311 | 2,691 | 1.0205 | 84.82 |
| Bruteforce | 1 | 35,172 | 35,172 | 0 | 0.4064 | 212.98 |
| Benign | 0 | 1,301 | 1,301 | 0 | 0.015 | 5,757.76 |

Binary (clean): {'benign': 1301, 'attack': 8652697, 'attack_pct': 99.985}

## Time split

| class | n | train | val | test | gap | method | ok |
|---|---|---|---|---|---|---|---|
| Benign | 1,301 | 910 | 195 | 184 | 12 | time_order | 1 |
| Bruteforce | 35,172 | 24,620 | 5,275 | 4,927 | 350 | time_order | 1 |
| DoS | 7,490,852 | 5,243,596 | 1,123,627 | 1,048,721 | 74,908 | time_order | 1 |
| Information Gathering | 1,038,362 | 726,853 | 155,754 | 145,373 | 10,382 | time_order | 1 |
| Mirai | 88,311 | 61,817 | 13,246 | 12,366 | 882 | time_order | 1 |

Time ranges: {'train': ['1970-01-01 04:08:55', '2023-02-08 03:43:51'], 'val': ['1970-01-01 09:17:28', '2023-02-08 03:43:57'], 'test': ['1970-01-01 09:18:27', '2023-02-08 04:17:06']}

## Identifier and leakage columns

- Dropped: Label, Timestamp, Traffic Subtype, Traffic Type
- Redundant (constant or duplicate): Bwd PSH Flags, Bwd Segment Size Avg, Bwd URG Flags, Fwd Bulk Rate Avg, Fwd Bytes/Bulk Avg, Fwd Packet/Bulk Avg, Fwd Segment Size Avg
- Port columns kept as shortcut candidates: Src Port, Dst Port
- Review manually: none

## Shortcut candidates (train, single-feature AUROC)

| feature | score | auroc | auroc_tree | direction | is_port | suspicious |
|---|---|---|---|---|---|---|
| Packet Length Max | 0.9015 | 0.6749 | 0.9015 | - | 0 | 0 |
| Fwd Packet Length Max | 0.8847 | 0.6506 | 0.8847 | - | 0 | 0 |
| Flow IAT Min | 0.8805 | 0.8492 | 0.8805 | + | 0 | 0 |
| Total Fwd Packet | 0.8737 | 0.8737 | 0.8412 | - | 0 | 0 |
| FWD Init Win Bytes | 0.8554 | 0.561 | 0.8554 | + | 0 | 0 |
| Flow IAT Std | 0.8427 | 0.7135 | 0.8427 | - | 0 | 0 |
| Src Port | 0.8354 | 0.7054 | 0.8354 | - | 1 | 0 |
| Fwd IAT Std | 0.8342 | 0.774 | 0.8342 | - | 0 | 0 |
| Fwd IAT Total | 0.8173 | 0.8173 | 0.8163 | - | 0 | 0 |
| Fwd Header Length | 0.8049 | 0.733 | 0.8049 | - | 0 | 0 |
| Flow Duration | 0.8011 | 0.7746 | 0.8011 | - | 0 | 0 |
| Total Length of Fwd Packet | 0.8007 | 0.6684 | 0.8007 | - | 0 | 0 |
| Fwd IAT Mean | 0.7979 | 0.5715 | 0.7979 | - | 0 | 0 |
| Dst Port | 0.7965 | 0.6463 | 0.7965 | - | 1 | 0 |
| Average Packet Size | 0.7812 | 0.6205 | 0.7812 | - | 0 | 0 |

## Correlated groups (train, Spearman)

- Flow Duration, Flow IAT Max, Flow IAT Mean, Flow Packets/s, Fwd Packets/s
- Fwd Packet Length Max, Fwd Packet Length Mean, Fwd Packet Length Min, Packet Length Max
- Fwd IAT Max, Fwd IAT Mean, Fwd IAT Min, Fwd IAT Total
- Bwd IAT Max, Bwd IAT Mean, Bwd IAT Min, Bwd IAT Total
- Average Packet Size, Packet Length Mean, Total Length of Fwd Packet
- Bwd Packet Length Max, Bwd Packet Length Mean, Total Length of Bwd Packet
- Bwd Bulk Rate Avg, Bwd Bytes/Bulk Avg, Bwd Packet/Bulk Avg
- Active Max, Active Mean, Active Min
- Idle Max, Idle Mean, Idle Min
- Fwd URG Flags, URG Flag Count
- Packet Length Std, Packet Length Variance

## Sampling

- train cap per class: 200000, rows 6,057,796 -> 487,347
- val cap per class: 50000, rows 1,298,097 -> 118,716
- test: not sampled, 1,211,571 rows

## Injected spurious feature

- Agreement with the binary label per split: {'train': 0.9899, 'val': 0.99, 'test': 0.9997} (train/val should be about the strength, test label-independent)
