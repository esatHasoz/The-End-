# EDA summary: cicids2017_corrected

- EDA version: `eda-v2`, seed 42
- Family: cicflowmeter, label column `Label`, benign label `BENIGN`
- Rows: 2,100,814 loaded, 2,100,814 with a valid label, 2,084,929 after cleaning
- Duplicate rows (features + label): 15,885 (removed)
- Conflicting rows (same features, different label): 4 (kept, reported)
- Rows without a valid timestamp: 0
- Model features: 76
- Time parsing: {'method': 'text_inferred_format', 'ampm_fix': 'auto', 'ampm_shifted_rows': 0, 'ampm_applied': False}

## Warnings

- 9,144 '- Attempted' rows, policy: keep.
- Classes with fewer than 50 rows in a split: DoS GoldenEye - Attempted, FTP-Patator - Attempted, Heartbleed, Infiltration, Infiltration - Attempted, SSH-Patator - Attempted, Web Attack - Brute Force, Web Attack - Sql Injection, Web Attack - XSS.

## Data quality

- Columns with inf: Flow Bytes/s, Flow Packets/s
- Columns with NaN: Flow Bytes/s, Flow IAT Mean, Flow IAT Std, Flow IAT Max, Flow IAT Min
- Constant columns: none
- Duplicate columns: Average Packet Size = Packet Length Mean, Fwd Segment Size Avg = Fwd Packet Length Mean, Bwd Segment Size Avg = Bwd Packet Length Mean

## Class distribution

| class | is_attack | count_raw | count | removed | pct | imbalance_vs_largest |
|---|---|---|---|---|---|---|
| BENIGN | 0 | 1,657,693 | 1,641,843 | 15,850 | 78.7481 | 1 |
| PortScan | 1 | 159,151 | 159,144 | 7 | 7.6331 | 10.32 |
| DoS Hulk | 1 | 158,469 | 158,469 | 0 | 7.6007 | 10.36 |
| DDoS | 1 | 95,123 | 95,123 | 0 | 4.5624 | 17.26 |
| DoS GoldenEye | 1 | 7,567 | 7,567 | 0 | 0.3629 | 216.97 |
| DoS slowloris | 1 | 4,001 | 3,974 | 27 | 0.1906 | 413.15 |
| FTP-Patator | 1 | 3,973 | 3,973 | 0 | 0.1906 | 413.25 |
| DoS Slowhttptest - Attempted | 1 | 3,369 | 3,369 | 0 | 0.1616 | 487.34 |
| SSH-Patator | 1 | 2,980 | 2,980 | 0 | 0.1429 | 550.95 |
| DoS Slowhttptest | 1 | 1,742 | 1,742 | 0 | 0.0836 | 942.5 |
| DoS slowloris - Attempted | 1 | 1,731 | 1,731 | 0 | 0.083 | 948.49 |
| Bot - Attempted | 1 | 1,470 | 1,469 | 1 | 0.0705 | 1,117.66 |
| Web Attack - Brute Force - Attempted | 1 | 1,214 | 1,214 | 0 | 0.0582 | 1,352.42 |
| Bot | 1 | 738 | 738 | 0 | 0.0354 | 2,224.72 |
| Web Attack - XSS - Attempted | 1 | 652 | 652 | 0 | 0.0313 | 2,518.16 |
| DoS Hulk - Attempted | 1 | 593 | 593 | 0 | 0.0284 | 2,768.71 |
| Web Attack - Brute Force | 1 | 151 | 151 | 0 | 0.0072 | 10,873.13 |
| DoS GoldenEye - Attempted | 1 | 80 | 80 | 0 | 0.0038 | 20,523.04 |
| Infiltration | 1 | 32 | 32 | 0 | 0.0015 | 51,307.59 |
| Web Attack - XSS | 1 | 27 | 27 | 0 | 0.0013 | 60,809 |
| Infiltration - Attempted | 1 | 16 | 16 | 0 | 0.0008 | 102,615.19 |
| Web Attack - Sql Injection | 1 | 12 | 12 | 0 | 0.0006 | 136,820.25 |
| Heartbleed | 1 | 11 | 11 | 0 | 0.0005 | 149,258.45 |
| FTP-Patator - Attempted | 1 | 11 | 11 | 0 | 0.0005 | 149,258.45 |
| SSH-Patator - Attempted | 1 | 8 | 8 | 0 | 0.0004 | 205,230.38 |

Binary (clean): {'benign': 1641843, 'attack': 443086, 'attack_pct': 21.2519}

## Time split

| class | n | train | val | test | gap | method | ok |
|---|---|---|---|---|---|---|---|
| BENIGN | 1,641,843 | 1,149,290 | 246,276 | 229,859 | 16,418 | time_order | 1 |
| Bot | 738 | 516 | 110 | 106 | 6 | time_order | 1 |
| Bot - Attempted | 1,469 | 1,028 | 220 | 207 | 14 | time_order | 1 |
| DDoS | 95,123 | 66,586 | 14,268 | 13,319 | 950 | time_order | 1 |
| DoS GoldenEye | 7,567 | 5,296 | 1,135 | 1,062 | 74 | time_order | 1 |
| DoS GoldenEye - Attempted | 80 | 58 | 8 | 8 | 6 | time_blocks | 0 |
| DoS Hulk | 158,469 | 110,928 | 23,770 | 22,187 | 1,584 | time_order | 1 |
| DoS Hulk - Attempted | 593 | 415 | 88 | 86 | 4 | time_order | 1 |
| DoS Slowhttptest | 1,742 | 1,219 | 261 | 246 | 16 | time_order | 1 |
| DoS Slowhttptest - Attempted | 3,369 | 2,358 | 505 | 474 | 32 | time_order | 1 |
| DoS slowloris | 3,974 | 2,781 | 596 | 559 | 38 | time_order | 1 |
| DoS slowloris - Attempted | 1,731 | 1,211 | 259 | 245 | 16 | time_order | 1 |
| FTP-Patator | 3,973 | 2,781 | 595 | 559 | 38 | time_order | 1 |
| FTP-Patator - Attempted | 11 | 2 | 3 | 2 | 4 | time_blocks | 0 |
| Heartbleed | 11 | 2 | 2 | 3 | 4 | time_blocks | 0 |
| Infiltration | 32 | 9 | 10 | 9 | 4 | time_blocks | 0 |
| Infiltration - Attempted | 16 | 5 | 4 | 3 | 4 | time_blocks | 0 |
| PortScan | 159,144 | 111,400 | 23,871 | 22,283 | 1,590 | time_order | 1 |
| SSH-Patator | 2,980 | 2,086 | 447 | 419 | 28 | time_order | 1 |
| SSH-Patator - Attempted | 8 | 1 | 1 | 2 | 4 | time_blocks | 0 |
| Web Attack - Brute Force | 151 | 103 | 18 | 16 | 14 | time_blocks | 0 |
| Web Attack - Brute Force - Attempted | 1,214 | 849 | 182 | 171 | 12 | time_order | 1 |
| Web Attack - Sql Injection | 12 | 3 | 2 | 3 | 4 | time_blocks | 0 |
| Web Attack - XSS | 27 | 8 | 7 | 8 | 4 | time_blocks | 0 |
| Web Attack - XSS - Attempted | 652 | 456 | 97 | 93 | 6 | time_order | 1 |

Time ranges: {'train': ['2017-07-03 13:55:58', '2017-07-07 21:10:22'], 'val': ['2017-07-04 14:22:57', '2017-07-07 21:13:23'], 'test': ['2017-07-04 14:24:34', '2017-07-07 22:02:40']}

**Classes with too few rows in a split:** DoS GoldenEye - Attempted, FTP-Patator - Attempted, Heartbleed, Infiltration, Infiltration - Attempted, SSH-Patator - Attempted, Web Attack - Brute Force, Web Attack - Sql Injection, Web Attack - XSS

## Identifier and leakage columns

- Dropped: Dst IP, Flow ID, Src IP, Timestamp
- Redundant (constant or duplicate): Average Packet Size, Bwd Segment Size Avg, Fwd Segment Size Avg
- Port columns kept as shortcut candidates: Src Port, Dst Port
- Review manually: none

## Shortcut candidates (train, single-feature AUROC)

| feature | score | auroc | auroc_tree | direction | is_port | suspicious |
|---|---|---|---|---|---|---|
| Total Length of Bwd Packet | 0.98 | 0.5849 | 0.98 | + | 0 | 1 |
| Bwd Packet Length Mean | 0.9789 | 0.6103 | 0.9789 | + | 0 | 1 |
| Packet Length Max | 0.9769 | 0.6175 | 0.9769 | + | 0 | 1 |
| Bwd Packet Length Max | 0.9752 | 0.6147 | 0.9752 | + | 0 | 1 |
| Packet Length Std | 0.9683 | 0.6258 | 0.9683 | + | 0 | 1 |
| Packet Length Variance | 0.9683 | 0.6258 | 0.9683 | + | 0 | 1 |
| Subflow Bwd Bytes | 0.9651 | 0.6043 | 0.9651 | + | 0 | 1 |
| Packet Length Mean | 0.9636 | 0.6071 | 0.9636 | + | 0 | 1 |
| Fwd Packet Length Max | 0.9582 | 0.6836 | 0.9582 | - | 0 | 1 |
| Dst Port | 0.954 | 0.756 | 0.954 | + | 1 | 1 |
| Total Length of Fwd Packet | 0.9519 | 0.695 | 0.9519 | - | 0 | 1 |
| ACK Flag Count | 0.9449 | 0.6829 | 0.9449 | + | 0 | 0 |
| RST Flag Count | 0.942 | 0.9177 | 0.942 | + | 0 | 0 |
| Bwd Header Length | 0.927 | 0.6889 | 0.927 | + | 0 | 0 |
| SYN Flag Count | 0.8881 | 0.7743 | 0.8881 | + | 0 | 0 |

## Correlated groups (train, Spearman)

- Bwd Packets/s, Flow Duration, Flow IAT Max, Flow IAT Mean, Flow IAT Std, Flow Packets/s, Fwd IAT Max, Fwd IAT Mean, Fwd IAT Total, Fwd Packets/s
- Bwd Packet Length Max, Bwd Packet Length Mean, Bwd Packet Length Std, Packet Length Max, Packet Length Mean, Packet Length Std, Packet Length Variance, Subflow Bwd Bytes
- Active Max, Active Mean, Active Min, Idle Max, Idle Mean, Idle Min
- Bwd Packet Length Min, Fwd Packet Length Min, Packet Length Min, Protocol
- Bwd IAT Max, Bwd IAT Mean, Bwd IAT Total
- Bwd PSH Flags, Fwd PSH Flags, PSH Flag Count
- Fwd Bulk Rate Avg, Fwd Bytes/Bulk Avg, Fwd Packet/Bulk Avg
- Bwd Bulk Rate Avg, Bwd Bytes/Bulk Avg, Bwd Packet/Bulk Avg
- Fwd Packet Length Max, Total Length of Fwd Packet
- Fwd Packet Length Mean, Subflow Fwd Bytes

## Sampling

- train cap per class: 200000, rows 1,459,391 -> 510,101
- val cap per class: 50000, rows 312,735 -> 116,459
- test: not sampled, 291,929 rows

## Injected spurious feature

- Agreement with the binary label per split: {'train': 0.99, 'val': 0.99, 'test': 0.6652} (train/val should be about the strength, test label-independent)
