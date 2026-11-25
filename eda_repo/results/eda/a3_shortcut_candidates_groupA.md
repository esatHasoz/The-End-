# A3 – Shortcut candidate list (Group A: CICIDS2017 original vs corrected)

Kaynak: `eda-v2` çıktıları (`shortcut_candidates.csv`, train split, single-feature AUROC + depth-3 tree skoru, eşik 0.95) ve ekip notları (`notes.md`). Tam tablo: `a3_shortcut_candidates_groupA.csv`. Tier ataması yorumdur; toplantıda gözden geçirilecek.

## Tier 1 – güçlü artefakt adayları (ablation'da öncelikli)

| dataset | feature | şüpheli kapsam | binary skor | max skor | gerekçe |
|---|---|---|---|---|---|
| CICIDS2017 (corrected) | Bwd Init Win Bytes | 10/18 | 0.8661 | 0.9991 | 10 sınıfta (orijinalde 5); XSS-Attempted'ı tek başına 0.999 ayırıyor. Saldırılar aynı hedef sunucuya → model hedef sunucuyu tanıyor olabilir. |
| CICIDS2017 (corrected) | Dst Port | 6/18 | 0.954 | 0.9999 | Binary'de de şüpheli (0.954); Bot 1.000, FTP/SSH-Patator, PortScan. |
| CICIDS2017 (corrected) | Src Port | 5/18 | 0.7304 | 0.9853 | Bot, Slowhttptest (0.985), SSH-Patator, iki Attempted sınıfı. Araç düzeltmesinden etkilenmiyor → araç/makine izi. |
| CICIDS2017 (corrected) | FWD Init Win Bytes | 2/18 | 0.876 | 0.9575 | 2 sınıfta (orijinalde 6). Orijinal–corrected farkı extractor artefaktının kısmi kanıtı. |
| CICIDS2017 (original) | Init_Win_bytes_forward | 6/12 | 0.7906 | 0.9652 | 6 sınıfta; 1.0M satırda negatif yer tutucu. Corrected'da 2 sınıfa düşüyor → kısmen CICFlowMeter hatası (Engelen et al. 2021). |
| CICIDS2017 (original) | Init_Win_bytes_backward | 5/12 | 0.8654 | 0.9978 | 5 sınıfta (SSH-Patator 0.998). Hedef sunucunun TCP ayarı; ayrıca 1.44M satırda negatif yer tutucu değer. |
| CICIDS2017 (original) | Destination Port | 4/12 | 0.8792 | 0.9988 | FTP-Patator 0.999, SSH-Patator 0.998, Bot 0.980. 21/22 saldırının tanımı ama model 'port 22 = saldırı' öğrenirse normal SSH'yi de saldırı sayar. |
| CICIDS2017 (original) | Source Port | 4/12 | 0.7698 | 0.9812 | Bot, Slowhttptest (0.981), GoldenEye, SSH-Patator. Kaynak port OS tarafından rastgele atanır; ayırıcı olması araç/makine izi. |

## Gruptaki tüm dataset'lerde şüpheli olan feature'lar

Bwd Header Length, Bwd Packet Length Max, Bwd Packet Length Mean, Bwd Packets/s, Flow Bytes/s, Flow Duration, Flow IAT Max, Flow IAT Mean, Flow IAT Min, Flow IAT Std, Flow Packets/s, Fwd Header Length, Fwd IAT Max, Fwd IAT Mean, Fwd IAT Min, Fwd IAT Std, Fwd IAT Total, Fwd Packet Length Max, Fwd Packet Length Mean, Fwd Packet Length Std, Fwd Packets/s, Packet Length Mean, Packet Length Std, Packet Length Variance, Subflow Bwd Bytes, Subflow Fwd Bytes

## Sayılar

- CICIDS2017 (original): 36 şüpheli feature (Tier 1: 4, Tier 2: 32)
- CICIDS2017 (corrected): 58 şüpheli feature (Tier 1: 4, Tier 2: 54)

## Injection set-up

- CICIDS2017 (original): train 0.99 / val 0.99 / test 0.6857
- CICIDS2017 (corrected): train 0.99 / val 0.99 / test 0.6652

Not: Orijinalde 65, corrected'da 76 model feature'ı var ve isimler farklı (ör. `Destination Port` ↔ `Dst Port`, `Init_Win_bytes_backward` ↔ `Bwd Init Win Bytes`). Port ve TCP pencere feature'larının adları iki sürümde farklı olduğu için yukarıdaki ortak listede görünmüyorlar; eşleme aşağıda.

| kavram | original | corrected |
|---|---|---|
| Destination port | Destination Port | Dst Port |
| Source port | Source Port | Src Port |
| TCP init window (bwd) | Init_Win_bytes_backward | Bwd Init Win Bytes |
| TCP init window (fwd) | Init_Win_bytes_forward | FWD Init Win Bytes |

Her iki sürümde Tier 1: port ve TCP init window. Corrected'da binary'de 11 feature eşiği geçiyor (orijinalde 0) ve şüpheli çift sayısı 122 → 549: temizlik sonrası sınıflar daha kolay ayrışıyor.

## Açık kararlar

1. Heartbleed, SQL Injection, Infiltration (ve corrected'daki 9 yetersiz sınıf) için ortak kural.
2. Attempted politikası (keep / benign / drop); Attempted akışlarını `Bwd Init Win Bytes` ayırıyor → makine/bağlantı izi.
3. Test BENIGN'i tek günden (cuma öğleden sonra) → gün/ortam shortcut'ı riski.
4. `Bwd Init Win Bytes` hipotezi için hedef IP bazında ek kontrol.
5. Portlu/portsuz varyant karşılaştırması (RQ1).
