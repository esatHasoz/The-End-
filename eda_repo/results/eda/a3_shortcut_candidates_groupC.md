# A3 – Shortcut candidate list (Group C: 5G-NIDD, TII-SSRC-23)

Kaynak: `eda-v2` çıktıları (`shortcut_candidates.csv`, train split, single-feature AUROC + depth-3 tree skoru, eşik 0.95) ve ekip notları (`notes.md`). Tam tablo: `a3_shortcut_candidates_groupC.csv`. Tier ataması yorumdur; toplantıda gözden geçirilecek.

## Tier 1 – güçlü artefakt adayları (ablation'da öncelikli)

| dataset | feature | şüpheli kapsam | binary skor | max skor | gerekçe |
|---|---|---|---|---|---|
| 5G-NIDD | SrcWin | 4/9 | 0.8031 | 0.9999 | SYNFlood/SYNScan ~1.00, TCPConnectScan 0.99. hping3/nmap sabit pencere değeri → araç imzası. |
| 5G-NIDD | AckDat | 2/9 | 0.8242 | 0.9894 | SynAck ile aynı tür (ortam/konum izi). |
| 5G-NIDD | SynAck | 2/9 | 0.8515 | 0.9973 | HTTPFlood, SlowrateDoS ~0.99. RTT tabanlı: saldırgan konumu/ortam izi olabilir. |
| 5G-NIDD | TcpRtt | 2/9 | 0.8402 | 0.9929 | SynAck ile aynı tür (ortam/konum izi). |
| 5G-NIDD | sTtl | 2/9 | 0.7363 | 0.9975 | UDPScan 0.997. Saldırganın ağdaki konumu (hop sayısı); UNSW/CIC2018 TTL artefaktının benzeri. |
| TII-SSRC-23 | FWD Init Win Bytes | 2/5 | 0.8554 | 0.9889 | Information Gathering 0.989, DoS 0.982. CICIDS2017'deki Init_Win_bytes_forward artefaktıyla aynı feature → gruplar arası ortak bulgu. |
| TII-SSRC-23 | Dst Port | 1/5 | 0.7965 | 0.9987 | Bruteforce 0.999 (SSH/FTP/Telnet hedef portları). Kılıç & Şengül'deki port shortcut'ıyla örtüşüyor. |
| TII-SSRC-23 | Src Port | 1/5 | 0.8354 | 0.9674 | Information Gathering 0.967; tarama aracının kaynak portu. |

## Gruptaki tüm dataset'lerde şüpheli olan feature'lar

(yok – feature adları/uzayları farklı)

## Sayılar

- 5G-NIDD: 21 şüpheli feature (Tier 1: 5, Tier 2: 16)
- TII-SSRC-23: 6 şüpheli feature (Tier 1: 3, Tier 2: 3)

## Injection set-up

- 5G-NIDD: train 0.9901 / val 0.99 / test 0.6727
- TII-SSRC-23: train 0.9899 / val 0.99 / test 0.9997

Not: Proposal'da iki dataset'in de fixed CICFlowMeter ile yeniden çıkarılması planlanıyor. Şu anki 5G-NIDD EDA'sı yayınlanmış Argus feature'larıyla yapıldı, bu yüzden TII ile ortak feature uzayı yok. Yeniden çıkarma sonrası A3 tekrar çalıştırılmalı.

## Dataset'e özgü uyarılar

- **5G-NIDD:** 632,401 çelişkili satır (UDPFlood ↔ Benign); zaman sütunu yok, split dosya sırasına göre. `Seq`/`Offset` kayıt kimlikleri çıkarıldı (makaledeki önem sıralamasında üstteydiler).
- **TII-SSRC-23:** Benign sadece 1,301 flow (%0.015). Injection testi bu sette işlemiyor (test uyumu 0.9997, çünkü saldırı oranı ~1). Mirai farklı saat ve kayıt noktasından (2023 vs 1970 göreli saat).

## Açık kararlar

1. UDPScan: çıkarılsın mı, scan sınıfları birleştirilsin mi?
2. UDPFlood–Benign çelişkili satırları.
3. 5G-NIDD NaN'leri (protokole bağlı): doldurma + 'NaN mı' feature'ı?
4. TII injection testi: saldırı sınıfları arasında, multi-class etikete bağlı enjeksiyon.
5. TII binary analizde kullanılsın mı?
