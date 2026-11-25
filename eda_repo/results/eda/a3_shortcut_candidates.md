# A3 – Shortcut candidate list (Group B: NF3 datasets)

Kaynak: `eda-v2` çıktıları (`shortcut_candidates.csv`, train split, single-feature AUROC + depth-3 tree skoru, eşik 0.95). Tam tablo: `a3_shortcut_candidates.csv`.

## Tier 1 – güçlü artefakt adayları (ablation'da öncelikli)

| dataset | feature | şüpheli kapsam | binary skor | max skor | gerekçe |
|---|---|---|---|---|---|
| NF3-CSE-CIC-IDS2018 | LONGEST_FLOW_PKT | 11/13 | 0.9614 | 1.0 | Binary'de eşiği geçen tek feature (0.96); 11 kapsamda şüpheli. |
| NF3-CSE-CIC-IDS2018 | L4_DST_PORT | 10/13 | 0.9333 | 0.9999 | Karışık: SSH→22 gerçek işaret; SlowHTTPTest→21 etiket hatası (Liu et al., CNS 2022 kontrol edilecek). |
| NF3-CSE-CIC-IDS2018 | TCP_WIN_MAX_IN | 7/13 | 0.9166 | 0.9997 | Birçok DoS sınıfında 1.000; araç/stack izi olabilir. |
| NF3-CSE-CIC-IDS2018 | MAX_TTL | 6/13 | 0.8968 | 0.9995 | MIN_TTL ile aynı grup. |
| NF3-CSE-CIC-IDS2018 | MIN_TTL | 6/13 | 0.8965 | 0.9995 | HOIC %100 TTL 127, Hulk %100 TTL 63; UNSW'deki TTL artefaktının benzeri. |
| NF3-CSE-CIC-IDS2018 | TCP_WIN_MAX_OUT | 6/13 | 0.9365 | 0.9999 | TCP_WIN_MAX_IN ile aynı tür. |
| NF3-UNSW-NB15 | MAX_TTL | 10/10 | 1.0 | 1.0 | MIN_TTL ile aynı grup (Spearman). Aynı artefakt. |
| NF3-UNSW-NB15 | MIN_IP_PKT_LEN | 10/10 | 0.9995 | 0.9998 | Her sınıfta şüpheli; saldırgan makinelerin paket şablonu/stack izi olabilir. |
| NF3-UNSW-NB15 | MIN_TTL | 10/10 | 1.0 | 1.0 | Testbed topolojisi: Benign %99.7 TTL 31, saldırılar 254/62. UNSW-NB15'in bilinen TTL artefaktı (kaynak teyit edilecek). |
| NF3-UNSW-NB15 | SHORTEST_FLOW_PKT | 10/10 | 0.9816 | 1.0 | MIN_IP_PKT_LEN ile aynı tür; her sınıfta şüpheli. |
| NF3-UNSW-NB15 | TCP_WIN_MAX_OUT | 8/10 | 0.9726 | 1.0 | Saldırılarda tek değerde yığılma; saldırgan TCP stack izi olabilir. |
| NF3-UNSW-NB15 | TCP_WIN_MAX_IN | 6/10 | 0.9624 | 0.9999 | TCP_WIN_MAX_OUT ile aynı tür. |

## Her iki dataset'te şüpheli olan feature'lar (cross-dataset testi için kritik)

CLIENT_TCP_FLAGS, DST_TO_SRC_AVG_THROUGHPUT, DST_TO_SRC_IAT_AVG, DST_TO_SRC_IAT_STDDEV, IN_BYTES, IN_PKTS, L4_DST_PORT, L7_PROTO, LONGEST_FLOW_PKT, MAX_TTL, MIN_IP_PKT_LEN, MIN_TTL, NUM_PKTS_UP_TO_128_BYTES, OUT_BYTES, OUT_PKTS, SERVER_TCP_FLAGS, SHORTEST_FLOW_PKT, SRC_TO_DST_IAT_AVG, SRC_TO_DST_SECOND_BYTES, TCP_FLAGS, TCP_WIN_MAX_IN, TCP_WIN_MAX_OUT

## Sayılar

- NF3-CSE-CIC-IDS2018: 35 şüpheli feature (Tier 1: 6, Tier 2: 28)
- NF3-UNSW-NB15: 28 şüpheli feature (Tier 1: 6, Tier 2: 22)

## Injection set-up

- Her iki dataset'te `inj_spurious` (strength 0.99) var. Etiketle uyum: UNSW train 0.990 / test 0.899 (beklenen 0.898), CIC2018 train 0.990 / test 0.789 (beklenen 0.789). Test'te etiketten bağımsız, doğru kurulmuş.

## Açık kararlar

1. `DNS_QUERY_ID` drop listesine eklensin (AUROC ~0.53, rastgele ID).
2. CIC2018 SlowHTTPTest ve FTP-BruteForce etiketleri (port 21, tek paket, SYN+RST+ACK).
3. CIC2018 class-wise zaman split'i: benign test son günlerden, saldırılar kendi gününden → gün/ortam shortcut'ı riski.
4. CIC2018 şu an %10 örneklem; nihai sonuçlar için daha büyük örneklem.
