# EDA summary: nf3_cse_cic_ids2018

- EDA version: `eda-v2`, seed 42
- Family: netflow_v3, label column `Attack`, benign label `Benign`
- Rows: 2,011,291 loaded, 2,011,291 with a valid label, 1,889,737 after cleaning
- Duplicate rows (features + label): 121,554 (removed)
- Conflicting rows (same features, different label): 36,085 (kept, reported)
- Rows without a valid timestamp: 0
- Model features: 47
- Time parsing: {'method': 'epoch_ms', 'ampm_fix': 'off', 'ampm_shifted_rows': 0}

## Warnings

- Classes with fewer than 50 rows in a split: Brute_Force_-Web, Brute_Force_-XSS, DDOS_attack-LOIC-UDP, SQL_Injection.

## Data quality

- Columns with inf: none
- Columns with NaN: none
- Constant columns: FTP_COMMAND_RET_CODE
- Duplicate columns: MAX_IP_PKT_LEN = LONGEST_FLOW_PKT

## Class distribution

| class | is_attack | count_raw | count | removed | pct | imbalance_vs_largest |
|---|---|---|---|---|---|---|
| Benign | 0 | 1,751,703 | 1,663,434 | 88,269 | 88.0246 | 1 |
| DDOS_attack-HOIC | 1 | 103,466 | 103,389 | 77 | 5.4711 | 16.09 |
| DDoS_attacks-LOIC-HTTP | 1 | 28,616 | 28,559 | 57 | 1.5113 | 58.25 |
| Bot | 1 | 20,487 | 18,888 | 1,599 | 0.9995 | 88.07 |
| SSH-Bruteforce | 1 | 18,883 | 17,918 | 965 | 0.9482 | 92.84 |
| Infilteration | 1 | 18,740 | 17,699 | 1,041 | 0.9366 | 93.98 |
| FTP-BruteForce | 1 | 38,682 | 13,332 | 25,350 | 0.7055 | 124.77 |
| DoS_attacks-Hulk | 1 | 10,006 | 10,006 | 0 | 0.5295 | 166.24 |
| DoS_attacks-SlowHTTPTest | 1 | 10,461 | 7,654 | 2,807 | 0.405 | 217.33 |
| DoS_attacks-GoldenEye | 1 | 6,094 | 5,809 | 285 | 0.3074 | 286.35 |
| DoS_attacks-Slowloris | 1 | 3,572 | 2,548 | 1,024 | 0.1348 | 652.84 |
| DDOS_attack-LOIC-UDP | 1 | 344 | 328 | 16 | 0.0174 | 5,071.45 |
| Brute_Force_-Web | 1 | 152 | 138 | 14 | 0.0073 | 12,053.87 |
| SQL_Injection | 1 | 39 | 19 | 20 | 0.001 | 87,549.16 |
| Brute_Force_-XSS | 1 | 46 | 16 | 30 | 0.0008 | 103,964.62 |

Binary (clean): {'benign': 1663434, 'attack': 226303, 'attack_pct': 11.9754}

## Time split

| class | n | train | val | test | gap | method | ok |
|---|---|---|---|---|---|---|---|
| Benign | 1,663,434 | 1,164,403 | 249,515 | 232,882 | 16,634 | time_order | 1 |
| Bot | 18,888 | 13,221 | 2,833 | 2,646 | 188 | time_order | 1 |
| Brute_Force_-Web | 138 | 91 | 19 | 16 | 12 | time_blocks | 0 |
| Brute_Force_-XSS | 16 | 5 | 4 | 3 | 4 | time_blocks | 0 |
| DDOS_attack-HOIC | 103,389 | 72,372 | 15,508 | 14,477 | 1,032 | time_order | 1 |
| DDOS_attack-LOIC-UDP | 328 | 221 | 46 | 47 | 14 | time_blocks | 0 |
| DDoS_attacks-LOIC-HTTP | 28,559 | 19,991 | 4,283 | 4,001 | 284 | time_order | 1 |
| DoS_attacks-GoldenEye | 5,809 | 4,066 | 871 | 814 | 58 | time_order | 1 |
| DoS_attacks-Hulk | 10,006 | 7,004 | 1,500 | 1,402 | 100 | time_order | 1 |
| DoS_attacks-SlowHTTPTest | 7,654 | 5,357 | 1,148 | 1,073 | 76 | time_order | 1 |
| DoS_attacks-Slowloris | 2,548 | 1,783 | 382 | 359 | 24 | time_order | 1 |
| FTP-BruteForce | 13,332 | 9,332 | 1,999 | 1,869 | 132 | time_order | 1 |
| Infilteration | 17,699 | 12,389 | 2,654 | 2,480 | 176 | time_order | 1 |
| SQL_Injection | 19 | 5 | 6 | 4 | 4 | time_blocks | 0 |
| SSH-Bruteforce | 17,918 | 12,542 | 2,687 | 2,511 | 178 | time_order | 1 |

Time ranges: {'train': ['2018-02-14 12:28:08.390000', '2018-03-02 18:28:03.472000'], 'val': ['2018-02-14 15:10:15.668000', '2018-03-02 19:34:59.870000'], 'test': ['2018-02-14 15:29:39.745000', '2018-03-02 20:04:25.247000']}

**Classes with too few rows in a split:** Brute_Force_-Web, Brute_Force_-XSS, DDOS_attack-LOIC-UDP, SQL_Injection

## Identifier and leakage columns

- Dropped: FLOW_END_MILLISECONDS, FLOW_START_MILLISECONDS, IPV4_DST_ADDR, IPV4_SRC_ADDR, Label
- Redundant (constant or duplicate): FTP_COMMAND_RET_CODE, MAX_IP_PKT_LEN
- Port columns kept as shortcut candidates: L4_SRC_PORT, L4_DST_PORT
- Review manually: DNS_QUERY_ID

## Shortcut candidates (train, single-feature AUROC)

| feature | score | auroc | auroc_tree | direction | is_port | suspicious |
|---|---|---|---|---|---|---|
| LONGEST_FLOW_PKT | 0.9614 | 0.64 | 0.9614 | + | 0 | 1 |
| TCP_WIN_MAX_OUT | 0.9365 | 0.6307 | 0.9365 | + | 0 | 0 |
| OUT_BYTES | 0.9361 | 0.6356 | 0.9361 | + | 0 | 0 |
| L7_PROTO | 0.934 | 0.5108 | 0.934 | - | 0 | 0 |
| L4_DST_PORT | 0.9333 | 0.5434 | 0.9333 | - | 1 | 0 |
| IN_BYTES | 0.9261 | 0.6106 | 0.9261 | + | 0 | 0 |
| NUM_PKTS_UP_TO_128_BYTES | 0.9184 | 0.6384 | 0.9184 | + | 0 | 0 |
| TCP_WIN_MAX_IN | 0.9166 | 0.8778 | 0.9166 | + | 0 | 0 |
| SERVER_TCP_FLAGS | 0.8997 | 0.7518 | 0.8997 | + | 0 | 0 |
| MAX_TTL | 0.8968 | 0.5636 | 0.8968 | + | 0 | 0 |
| MIN_TTL | 0.8965 | 0.5639 | 0.8965 | + | 0 | 0 |
| IN_PKTS | 0.888 | 0.6152 | 0.888 | + | 0 | 0 |
| OUT_PKTS | 0.8867 | 0.6308 | 0.8867 | + | 0 | 0 |
| TCP_FLAGS | 0.859 | 0.7717 | 0.859 | + | 0 | 0 |
| DURATION_OUT | 0.8554 | 0.58 | 0.8554 | + | 0 | 0 |

## Correlated groups (train, Spearman)

- DNS_QUERY_ID, DNS_QUERY_TYPE, DNS_TTL_ANSWER, PROTOCOL
- DURATION_IN, FLOW_DURATION_MILLISECONDS, SRC_TO_DST_IAT_AVG, SRC_TO_DST_IAT_MAX
- ICMP_IPV4_TYPE, ICMP_TYPE, RETRANSMITTED_IN_BYTES, RETRANSMITTED_IN_PKTS
- IN_PKTS, NUM_PKTS_UP_TO_128_BYTES, OUT_PKTS
- DST_TO_SRC_IAT_AVG, DST_TO_SRC_IAT_MAX, DURATION_OUT
- CLIENT_TCP_FLAGS, TCP_FLAGS
- MAX_TTL, MIN_TTL
- DST_TO_SRC_SECOND_BYTES, SRC_TO_DST_SECOND_BYTES
- RETRANSMITTED_OUT_BYTES, RETRANSMITTED_OUT_PKTS

## Sampling

- train cap per class: 200000, rows 1,322,782 -> 358,379
- val cap per class: 50000, rows 283,455 -> 83,940
- test: not sampled, 264,584 rows

## Injected spurious feature

- Agreement with the binary label per split: {'train': 0.99, 'val': 0.9899, 'test': 0.7889} (train/val should be about the strength, test label-independent)
