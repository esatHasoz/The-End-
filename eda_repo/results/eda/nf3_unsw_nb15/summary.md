# EDA summary: nf3_unsw_nb15

- EDA version: `eda-v2`, seed 42
- Family: netflow_v3, label column `Attack`, benign label `Benign`
- Rows: 2,365,424 loaded, 2,365,424 with a valid label, 2,139,427 after cleaning
- Duplicate rows (features + label): 225,997 (removed)
- Conflicting rows (same features, different label): 3,647 (kept, reported)
- Rows without a valid timestamp: 0
- Model features: 48
- Time parsing: {'method': 'epoch_ms', 'ampm_fix': 'off', 'ampm_shifted_rows': 0}

## Warnings

- Classes with fewer than 50 rows in a split: Worms.

## Data quality

- Columns with inf: SRC_TO_DST_SECOND_BYTES, DST_TO_SRC_SECOND_BYTES
- Columns with NaN: SRC_TO_DST_SECOND_BYTES
- Constant columns: none
- Duplicate columns: MAX_IP_PKT_LEN = LONGEST_FLOW_PKT

## Class distribution

| class | is_attack | count_raw | count | removed | pct | imbalance_vs_largest |
|---|---|---|---|---|---|---|
| Benign | 0 | 2,237,731 | 2,024,460 | 213,271 | 94.6263 | 1 |
| Exploits | 1 | 42,748 | 42,651 | 97 | 1.9936 | 47.47 |
| Fuzzers | 1 | 33,816 | 33,044 | 772 | 1.5445 | 61.27 |
| Reconnaissance | 1 | 17,074 | 16,878 | 196 | 0.7889 | 119.95 |
| Generic | 1 | 19,651 | 8,066 | 11,585 | 0.377 | 250.99 |
| DoS | 1 | 5,980 | 5,945 | 35 | 0.2779 | 340.53 |
| Backdoor | 1 | 4,659 | 4,621 | 38 | 0.216 | 438.1 |
| Shellcode | 1 | 2,381 | 2,378 | 3 | 0.1112 | 851.33 |
| Analysis | 1 | 1,226 | 1,226 | 0 | 0.0573 | 1,651.27 |
| Worms | 1 | 158 | 158 | 0 | 0.0074 | 12,813.04 |

Binary (clean): {'benign': 2024460, 'attack': 114967, 'attack_pct': 5.3737}

## Time split

| class | n | train | val | test | gap | method | ok |
|---|---|---|---|---|---|---|---|
| Analysis | 1,226 | 858 | 183 | 173 | 12 | time_order | 1 |
| Backdoor | 4,621 | 3,234 | 693 | 648 | 46 | time_order | 1 |
| Benign | 2,024,460 | 1,417,122 | 303,669 | 283,425 | 20,244 | time_order | 1 |
| DoS | 5,945 | 4,161 | 891 | 835 | 58 | time_order | 1 |
| Exploits | 42,651 | 29,855 | 6,397 | 5,973 | 426 | time_order | 1 |
| Fuzzers | 33,044 | 23,130 | 4,956 | 4,628 | 330 | time_order | 1 |
| Generic | 8,066 | 5,646 | 1,209 | 1,131 | 80 | time_order | 1 |
| Reconnaissance | 16,878 | 11,814 | 2,531 | 2,365 | 168 | time_order | 1 |
| Shellcode | 2,378 | 1,664 | 356 | 336 | 22 | time_order | 1 |
| Worms | 158 | 109 | 19 | 18 | 12 | time_blocks | 0 |

Time ranges: {'train': ['2015-01-22 11:49:41', '2015-02-18 12:12:54.109000'], 'val': ['2015-02-18 04:38:03.180000', '2015-02-18 12:24:20.384000'], 'test': ['2015-02-18 01:48:22.716000', '2015-02-18 12:29:24.927000']}

**Classes with too few rows in a split:** Worms

## Identifier and leakage columns

- Dropped: FLOW_END_MILLISECONDS, FLOW_START_MILLISECONDS, IPV4_DST_ADDR, IPV4_SRC_ADDR, Label
- Redundant (constant or duplicate): MAX_IP_PKT_LEN
- Port columns kept as shortcut candidates: L4_SRC_PORT, L4_DST_PORT
- Review manually: DNS_QUERY_ID

## Shortcut candidates (train, single-feature AUROC)

| feature | score | auroc | auroc_tree | direction | is_port | suspicious |
|---|---|---|---|---|---|---|
| MAX_TTL | 1 | 0.9986 | 1 | + | 0 | 1 |
| MIN_TTL | 1 | 0.9986 | 1 | + | 0 | 1 |
| MIN_IP_PKT_LEN | 0.9995 | 0.9959 | 0.9995 | - | 0 | 1 |
| SHORTEST_FLOW_PKT | 0.9816 | 0.8459 | 0.9816 | - | 0 | 1 |
| TCP_WIN_MAX_OUT | 0.9726 | 0.6563 | 0.9726 | + | 0 | 1 |
| SERVER_TCP_FLAGS | 0.9639 | 0.8475 | 0.9639 | - | 0 | 1 |
| TCP_WIN_MAX_IN | 0.9624 | 0.5087 | 0.9624 | - | 0 | 1 |
| DST_TO_SRC_AVG_THROUGHPUT | 0.9569 | 0.9569 | 0.9547 | - | 0 | 1 |
| SRC_TO_DST_SECOND_BYTES | 0.9418 | 0.9129 | 0.9418 | - | 0 | 0 |
| OUT_BYTES | 0.8821 | 0.815 | 0.8821 | - | 0 | 0 |
| OUT_PKTS | 0.8816 | 0.8019 | 0.8816 | - | 0 | 0 |
| DST_TO_SRC_SECOND_BYTES | 0.881 | 0.8467 | 0.881 | - | 0 | 0 |
| L7_PROTO | 0.8738 | 0.742 | 0.8738 | - | 0 | 0 |
| DST_TO_SRC_IAT_MAX | 0.8711 | 0.6435 | 0.8711 | + | 0 | 0 |
| NUM_PKTS_UP_TO_128_BYTES | 0.8668 | 0.7765 | 0.8668 | - | 0 | 0 |

## Correlated groups (train, Spearman)

- OUT_BYTES, OUT_PKTS, RETRANSMITTED_OUT_BYTES, RETRANSMITTED_OUT_PKTS
- SRC_TO_DST_IAT_AVG, SRC_TO_DST_IAT_MAX, SRC_TO_DST_IAT_STDDEV
- DST_TO_SRC_IAT_AVG, DST_TO_SRC_IAT_MAX, DST_TO_SRC_IAT_STDDEV
- CLIENT_TCP_FLAGS, TCP_FLAGS
- DURATION_IN, FLOW_DURATION_MILLISECONDS
- MAX_TTL, MIN_TTL
- DST_TO_SRC_AVG_THROUGHPUT, SRC_TO_DST_SECOND_BYTES
- DST_TO_SRC_SECOND_BYTES, SRC_TO_DST_AVG_THROUGHPUT
- ICMP_IPV4_TYPE, ICMP_TYPE
- DNS_QUERY_ID, DNS_QUERY_TYPE

## Sampling

- train cap per class: 200000, rows 1,497,593 -> 280,471
- val cap per class: 50000, rows 320,904 -> 67,235
- test: not sampled, 299,532 rows

## Injected spurious feature

- Agreement with the binary label per split: {'train': 0.99, 'val': 0.9897, 'test': 0.8989} (train/val should be about the strength, test label-independent)
