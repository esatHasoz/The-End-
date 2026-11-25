# EDA summary: 5g_nidd

- EDA version: `eda-v2`, seed 42
- Family: cicflowmeter, label column `Class`, benign label `Benign`
- Rows: 1,215,890 loaded, 1,215,890 with a valid label, 394,580 after cleaning
- Duplicate rows (features + label): 821,310 (removed)
- Conflicting rows (same features, different label): 632,401 (kept, reported)
- Rows without a valid timestamp: 0
- Model features: 34
- Time parsing: {'method': 'row_order'}

## Warnings

- No timestamp: file row order is used as time. The split is only as valid as the file order.
- Classes with fewer than 50 rows in a split: UDPScan.

## Data quality

- Columns with inf: none
- Columns with NaN: sTos, dTos, sTtl, dTtl, sHops, dHops, SrcGap, DstGap, SrcWin, DstWin, sVid, dVid, SrcTCPBase, DstTCPBase
- Constant columns: sVid, dVid
- Duplicate columns: RunTime = Dur, Mean = Dur, Sum = Dur, Min = Dur, Max = Dur

## Class distribution

| class | is_attack | count_raw | count | removed | pct | imbalance_vs_largest |
|---|---|---|---|---|---|---|
| HTTPFlood | 1 | 140,812 | 140,011 | 801 | 35.4836 | 1 |
| Benign | 0 | 477,737 | 82,234 | 395,503 | 20.8409 | 1.7 |
| SlowrateDoS | 1 | 73,124 | 73,001 | 123 | 18.5009 | 1.92 |
| UDPFlood | 1 | 457,340 | 67,283 | 390,057 | 17.0518 | 2.08 |
| TCPConnectScan | 1 | 20,052 | 20,040 | 12 | 5.0788 | 6.99 |
| SYNFlood | 1 | 9,721 | 9,721 | 0 | 2.4636 | 14.4 |
| SYNScan | 1 | 20,043 | 1,342 | 18,701 | 0.3401 | 104.33 |
| ICMPFlood | 1 | 1,155 | 619 | 536 | 0.1569 | 226.19 |
| UDPScan | 1 | 15,906 | 329 | 15,577 | 0.0834 | 425.57 |

Binary (clean): {'benign': 82234, 'attack': 312346, 'attack_pct': 79.1591}

## Time split

| class | n | train | val | test | gap | method | ok |
|---|---|---|---|---|---|---|---|
| Benign | 82,234 | 57,563 | 12,335 | 11,514 | 822 | time_order | 1 |
| HTTPFlood | 140,011 | 98,007 | 21,001 | 19,603 | 1,400 | time_order | 1 |
| ICMPFlood | 619 | 433 | 92 | 88 | 6 | time_order | 1 |
| SYNFlood | 9,721 | 6,804 | 1,458 | 1,363 | 96 | time_order | 1 |
| SYNScan | 1,342 | 939 | 201 | 190 | 12 | time_order | 1 |
| SlowrateDoS | 73,001 | 51,100 | 10,950 | 10,221 | 730 | time_order | 1 |
| TCPConnectScan | 20,040 | 14,028 | 3,006 | 2,806 | 200 | time_order | 1 |
| UDPFlood | 67,283 | 47,098 | 10,092 | 9,421 | 672 | time_order | 1 |
| UDPScan | 329 | 224 | 45 | 42 | 18 | time_blocks | 0 |

Time ranges: {'train': ['2000-01-01 00:00:00', '2000-01-05 07:06:43'], 'val': ['2000-01-01 03:48:39', '2000-01-05 10:18:27'], 'test': ['2000-01-01 03:42:04', '2000-01-05 13:36:19']}

**Classes with too few rows in a split:** UDPScan

## Identifier and leakage columns

- Dropped: Attack Tool, Attack Type, Cause, Label, Offset, Proto, State, Unnamed: 0, dDSb, sDSb
- Redundant (constant or duplicate): Max, Mean, Min, RunTime, Sum, dVid, sVid
- Port columns kept as shortcut candidates: none
- Review manually: none

## Shortcut candidates (train, single-feature AUROC)

| feature | score | auroc | auroc_tree | direction | is_port | suspicious |
|---|---|---|---|---|---|---|
| Rate | 0.9225 | 0.6233 | 0.9225 | - | 0 | 0 |
| Load | 0.9008 | 0.5967 | 0.9008 | - | 0 | 0 |
| SrcRate | 0.8963 | 0.5956 | 0.8963 | - | 0 | 0 |
| Dur | 0.8714 | 0.5955 | 0.8714 | - | 0 | 0 |
| SrcBytes | 0.8617 | 0.6277 | 0.8617 | - | 0 | 0 |
| SynAck | 0.8515 | 0.8299 | 0.8515 | + | 0 | 0 |
| SrcLoad | 0.8479 | 0.608 | 0.8479 | - | 0 | 0 |
| SrcTCPBase | 0.8459 | 0.5031 | 0.8459 | - | 0 | 0 |
| TcpRtt | 0.8402 | 0.8274 | 0.8402 | + | 0 | 0 |
| sMeanPktSz | 0.8286 | 0.5489 | 0.8286 | - | 0 | 0 |
| DstTCPBase | 0.8282 | 0.5021 | 0.8282 | + | 0 | 0 |
| AckDat | 0.8242 | 0.8209 | 0.8242 | + | 0 | 0 |
| SrcWin | 0.8031 | 0.5752 | 0.8031 | - | 0 | 0 |
| TotBytes | 0.8028 | 0.5456 | 0.8028 | - | 0 | 0 |
| SrcPkts | 0.797 | 0.5921 | 0.797 | - | 0 | 0 |

## Correlated groups (train, Spearman)

- DstBytes, DstPkts, dMeanPktSz
- Load, SrcLoad, SrcRate
- TotBytes, TotPkts
- SrcBytes, SrcPkts
- DstLoad, DstRate
- Loss, pLoss
- AckDat, TcpRtt

## Sampling

- train cap per class: 200000, rows 276,196 -> 276,196
- val cap per class: 50000, rows 59,180 -> 59,180
- test: not sampled, 55,248 rows

## Injected spurious feature

- Agreement with the binary label per split: {'train': 0.9901, 'val': 0.99, 'test': 0.6727} (train/val should be about the strength, test label-independent)
