# EDA summary: cicids2017_orig

- EDA version: `eda-v2`, seed 42
- Family: cicflowmeter, label column `Label`, benign label `BENIGN`
- Rows: 3,119,345 loaded, 2,830,743 with a valid label, 2,812,414 after cleaning
- Duplicate rows (features + label): 18,329 (removed)
- Conflicting rows (same features, different label): 0 (kept, reported)
- Rows without a valid timestamp: 0
- Model features: 65
- Time parsing: {'method': 'text_mixed_format', 'ampm_fix': 'auto', 'ampm_shifted_rows': 1466965, 'ampm_applied': True}

## Warnings

- 288,602 rows without a label were removed at load.
- 12-hour clock without AM/PM: 1,466,965 rows shifted by 12 h (hours 1-7).
- Classes with fewer than 50 rows in a split: Heartbleed, Infiltration, Web Attack - Sql Injection.

## Data quality

- Columns with inf: Flow Bytes/s, Flow Packets/s
- Columns with NaN: Flow Bytes/s
- Constant columns: Bwd PSH Flags, Bwd URG Flags, Fwd Avg Bytes/Bulk, Fwd Avg Packets/Bulk, Fwd Avg Bulk Rate, Bwd Avg Bytes/Bulk, Bwd Avg Packets/Bulk, Bwd Avg Bulk Rate
- Duplicate columns: Bwd URG Flags = Bwd PSH Flags, SYN Flag Count = Fwd PSH Flags, CWE Flag Count = Fwd URG Flags, Avg Fwd Segment Size = Fwd Packet Length Mean, Avg Bwd Segment Size = Bwd Packet Length Mean, Fwd Header Length.dup1 = Fwd Header Length, Fwd Avg Bytes/Bulk = Bwd PSH Flags, Fwd Avg Packets/Bulk = Bwd PSH Flags, Fwd Avg Bulk Rate = Bwd PSH Flags, Bwd Avg Bytes/Bulk = Bwd PSH Flags, Bwd Avg Packets/Bulk = Bwd PSH Flags, Bwd Avg Bulk Rate = Bwd PSH Flags, Subflow Fwd Packets = Total Fwd Packets, Subflow Bwd Packets = Total Backward Packets

## Class distribution

| class | is_attack | count_raw | count | removed | pct | imbalance_vs_largest |
|---|---|---|---|---|---|---|
| BENIGN | 0 | 2,273,097 | 2,262,380 | 10,717 | 80.4426 | 1 |
| DoS Hulk | 1 | 231,073 | 223,488 | 7,585 | 7.9465 | 10.12 |
| PortScan | 1 | 158,930 | 158,930 | 0 | 5.651 | 14.24 |
| DDoS | 1 | 128,027 | 128,027 | 0 | 4.5522 | 17.67 |
| DoS GoldenEye | 1 | 10,293 | 10,293 | 0 | 0.366 | 219.8 |
| FTP-Patator | 1 | 7,938 | 7,938 | 0 | 0.2822 | 285.01 |
| SSH-Patator | 1 | 5,897 | 5,897 | 0 | 0.2097 | 383.65 |
| DoS slowloris | 1 | 5,796 | 5,769 | 27 | 0.2051 | 392.16 |
| DoS Slowhttptest | 1 | 5,499 | 5,499 | 0 | 0.1955 | 411.42 |
| Bot | 1 | 1,966 | 1,966 | 0 | 0.0699 | 1,150.75 |
| Web Attack - Brute Force | 1 | 1,507 | 1,507 | 0 | 0.0536 | 1,501.25 |
| Web Attack - XSS | 1 | 652 | 652 | 0 | 0.0232 | 3,469.91 |
| Infiltration | 1 | 36 | 36 | 0 | 0.0013 | 62,843.89 |
| Web Attack - Sql Injection | 1 | 21 | 21 | 0 | 0.0007 | 107,732.38 |
| Heartbleed | 1 | 11 | 11 | 0 | 0.0004 | 205,670.91 |

Binary (clean): {'benign': 2262380, 'attack': 550034, 'attack_pct': 19.5574}

## Time split

| class | n | train | val | test | gap | method | ok |
|---|---|---|---|---|---|---|---|
| BENIGN | 2,262,380 | 1,583,666 | 339,357 | 316,735 | 22,622 | time_order | 1 |
| Bot | 1,966 | 1,376 | 294 | 278 | 18 | time_order | 1 |
| DDoS | 128,027 | 89,618 | 19,204 | 17,925 | 1,280 | time_order | 1 |
| DoS GoldenEye | 10,293 | 7,205 | 1,543 | 1,443 | 102 | time_order | 1 |
| DoS Hulk | 223,488 | 156,441 | 33,523 | 31,290 | 2,234 | time_order | 1 |
| DoS Slowhttptest | 5,499 | 3,849 | 824 | 772 | 54 | time_order | 1 |
| DoS slowloris | 5,769 | 4,038 | 865 | 810 | 56 | time_order | 1 |
| FTP-Patator | 7,938 | 5,556 | 1,190 | 1,114 | 78 | time_order | 1 |
| Heartbleed | 11 | 3 | 2 | 2 | 4 | time_blocks | 0 |
| Infiltration | 36 | 10 | 11 | 11 | 4 | time_blocks | 0 |
| PortScan | 158,930 | 111,251 | 23,839 | 22,252 | 1,588 | time_order | 1 |
| SSH-Patator | 5,897 | 4,127 | 884 | 828 | 58 | time_order | 1 |
| Web Attack - Brute Force | 1,507 | 1,054 | 226 | 213 | 14 | time_order | 1 |
| Web Attack - Sql Injection | 21 | 6 | 5 | 6 | 4 | time_blocks | 0 |
| Web Attack - XSS | 652 | 456 | 97 | 93 | 6 | time_order | 1 |

Time ranges: {'train': ['2017-07-03 08:55:58', '2017-07-07 16:10:00'], 'val': ['2017-07-04 10:02:00', '2017-07-07 16:13:00'], 'test': ['2017-07-04 10:11:00', '2017-07-07 17:02:00']}

**Classes with too few rows in a split:** Heartbleed, Infiltration, Web Attack - Sql Injection

## Identifier and leakage columns

- Dropped: Destination IP, Flow ID, Source IP, Timestamp
- Redundant (constant or duplicate): Avg Bwd Segment Size, Avg Fwd Segment Size, Bwd Avg Bulk Rate, Bwd Avg Bytes/Bulk, Bwd Avg Packets/Bulk, Bwd PSH Flags, Bwd URG Flags, CWE Flag Count, Fwd Avg Bulk Rate, Fwd Avg Bytes/Bulk, Fwd Avg Packets/Bulk, Fwd Header Length.dup1, SYN Flag Count, Subflow Bwd Packets, Subflow Fwd Packets
- Port columns kept as shortcut candidates: Source Port, Destination Port
- Review manually: none

## Shortcut candidates (train, single-feature AUROC)

| feature | score | auroc | auroc_tree | direction | is_port | suspicious |
|---|---|---|---|---|---|---|
| Average Packet Size | 0.9465 | 0.5238 | 0.9465 | + | 0 | 0 |
| Packet Length Std | 0.9423 | 0.5671 | 0.9423 | + | 0 | 0 |
| Packet Length Variance | 0.9423 | 0.5671 | 0.9423 | + | 0 | 0 |
| Total Length of Bwd Packets | 0.9387 | 0.5513 | 0.9387 | + | 0 | 0 |
| Subflow Bwd Bytes | 0.9387 | 0.5513 | 0.9387 | + | 0 | 0 |
| Bwd Packet Length Mean | 0.9349 | 0.565 | 0.9349 | + | 0 | 0 |
| Max Packet Length | 0.9324 | 0.5461 | 0.9324 | + | 0 | 0 |
| Bwd Packet Length Max | 0.9281 | 0.5675 | 0.9281 | + | 0 | 0 |
| Packet Length Mean | 0.9201 | 0.5271 | 0.9201 | + | 0 | 0 |
| Fwd Packet Length Max | 0.9039 | 0.6568 | 0.9039 | - | 0 | 0 |
| Total Length of Fwd Packets | 0.883 | 0.6481 | 0.883 | - | 0 | 0 |
| Subflow Fwd Bytes | 0.883 | 0.6481 | 0.883 | - | 0 | 0 |
| Destination Port | 0.8792 | 0.575 | 0.8792 | + | 1 | 0 |
| Init_Win_bytes_backward | 0.8654 | 0.6124 | 0.8654 | + | 0 | 0 |
| Flow Duration | 0.8285 | 0.5442 | 0.8285 | + | 0 | 0 |

## Correlated groups (train, Spearman)

- Average Packet Size, Bwd Packet Length Max, Bwd Packet Length Mean, Max Packet Length, Packet Length Mean, Packet Length Std, Packet Length Variance, Subflow Bwd Bytes, Total Length of Bwd Packets
- Flow Duration, Flow IAT Max, Flow IAT Mean, Flow Packets/s, Fwd Packets/s
- Fwd Packet Length Max, Fwd Packet Length Mean, Subflow Fwd Bytes, Total Length of Fwd Packets
- Fwd IAT Max, Fwd IAT Mean, Fwd IAT Total
- Bwd IAT Max, Bwd IAT Mean, Bwd IAT Total
- Active Max, Active Mean, Active Min
- Idle Max, Idle Mean, Idle Min
- Fwd Header Length, Total Fwd Packets
- Bwd Header Length, Total Backward Packets
- Fwd Packet Length Min, Min Packet Length
- ECE Flag Count, RST Flag Count

## Sampling

- train cap per class: 200000, rows 1,968,656 -> 584,990
- val cap per class: 50000, rows 421,864 -> 132,507
- test: not sampled, 393,772 rows

## Injected spurious feature

- Agreement with the binary label per split: {'train': 0.99, 'val': 0.99, 'test': 0.6857} (train/val should be about the strength, test label-independent)
