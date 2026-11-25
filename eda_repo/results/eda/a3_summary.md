# A3 – Gruplar arası özet

Ayrıntılar: `a3_bshortcut_candidates.md` (Group B), `a3_shortcut_candidates_groupA.md`, `a3_shortcut_candidates_groupC.md`.

## Tekrarlayan shortcut aileleri (Tier 1)

| aile | A: CICIDS2017 orig | A: CICIDS2017 corr | B: NF3-CIC2018 | B: NF3-UNSW | C: 5G-NIDD | C: TII-SSRC-23 |
|---|---|---|---|---|---|---|
| Hedef port | Destination Port | Dst Port | L4_DST_PORT | (1 kapsam, Tier 2) | yok (Argus'ta port yok) | Dst Port |
| Kaynak port | Source Port | Src Port | (Tier 3) | – | yok | Src Port |
| TCP pencere | Init_Win_bytes_fwd/bwd | FWD/Bwd Init Win Bytes | TCP_WIN_MAX_IN/OUT | TCP_WIN_MAX_IN/OUT | SrcWin | FWD Init Win Bytes |
| TTL / ağ konumu | – (CICFlowMeter'da yok) | – | MIN/MAX_TTL | MIN/MAX_TTL | sTtl, SynAck, TcpRtt, AckDat | – |
| Paket boyu şablonu | Tier 2 | Tier 2 | LONGEST_FLOW_PKT | MIN_IP_PKT_LEN, SHORTEST_FLOW_PKT | Tier 2 | Tier 2 |

## Çıkarımlar (RQ1/RQ2 için)

1. **TCP pencere feature'ı 6 dataset'in 6'sında şüpheli.** Farklı laboratuvar, araç ve extractor'a rağmen tekrar etmesi, bunun en güçlü ortak shortcut adayı olduğunu gösteriyor. Ablation'da ilk test edilecek aile.
2. **TTL, TTL'yi raporlayan her feature setinde (NetFlow v3, Argus) şüpheli.** CICFlowMeter TTL üretmediği için Group A ve TII'de test edilemiyor.
3. **Port** CICFlowMeter tabanlı setlerde ve CIC2018'de Tier 1. Portlu/portsuz varyant RQ1 için doğal bir test.
4. **CICIDS2017 original → corrected:** TCP pencere feature'ının şüpheli olduğu sınıf sayısı fwd'de 6 → 2'ye düşüyor, bwd'de 5 → 10'a çıkıyor. Extractor düzeltmesi bir artefaktı azaltırken diğerini görünür kılıyor; Group A'nın "partial ground truth" rolü için iyi bir vaka.

## Injection set-up durumu

- 5 dataset'te test uyumu etiketten bağımsız bir feature için beklenen değere uyuyor.
- **TII-SSRC-23'te işlemiyor** (test 0.9997, benign %0.015). Multi-class etikete bağlı enjeksiyon gerekiyor.

## Ortak açık kararlar

1. Yetersiz sınıflar için tek kural (tüm dataset'ler).
2. Attempted / başarısız bağlantı politikası (CICIDS2017 corrected Attempted, CIC2018 FTP-BruteForce ve SlowHTTPTest).
3. Sınıf bazında zaman split'i benign test'i farklı günden alıyor (CICIDS2017, CIC2018) → gün/ortam shortcut'ı riski.
4. 5G-NIDD ve TII fixed CICFlowMeter ile yeniden çıkarıldıktan sonra Group C A3'ü tekrar çalıştırılmalı.
