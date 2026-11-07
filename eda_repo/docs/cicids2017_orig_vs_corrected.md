# CICIDS2017: orijinal ve düzeltilmiş sürüm karşılaştırması (Grup A, Ahmet)

Kaynaklar:
- Orijinal: CIC/UNB, GeneratedLabelledFlows (TrafficLabelling) CSV'leri. https://www.unb.ca/cic/datasets/ids-2017.html
- Düzeltilmiş: G. Engelen, V. Rimmer, W. Joosen, "Troubleshooting an Intrusion Detection Dataset: the CICIDS2017 Case Study", IEEE Security and Privacy Workshops (SPW), 2021, s. 7–12. https://intrusion-detection.distrinet-research.be/WTMC2021/
- Her iki set de `eda-v2` ile işlendi. Sayılar tekrar eden satırlar silindikten sonraki değerlerdir.

## 1. Genel fark tablosu

| | Orijinal | Düzeltilmiş |
|---|---|---|
| Satır (etiketli) | 2.830.743 | 2.100.814 |
| Temizlik sonrası | 2.812.414 | 2.084.929 |
| Tekrar eden satır | 18.329 | 15.885 |
| Çelişkili satır | 0 | 4 |
| Sınıf sayısı | 15 | 25 (15 + 10 Attempted) |
| Saldırı oranı | %19,6 | %21,3 |
| Model özelliği | 65 | 76 |
| Sabit sütun | 8 | 0 |
| inf (`Flow Bytes/s` + `Flow Packets/s`) | 1.509 + 2.867 | 191 + 793 |
| Zaman damgası | 12 saat, AM/PM yok | 12 saat, AM/PM var, +5 saat |
| Yetersiz sınıf (bölme başına < 50) | 3 | 9 |
| İkili sınıflandırmada skor > 0,95 olan özellik | 0 | 11 |
| Şüpheli (özellik, sınıf) çifti | 122 | 549 |

## 2. Sınıf bazında akış sayıları

| Sınıf | Orijinal | Düzeltilmiş | Düzeltilmiş - Attempted |
|---|---|---|---|
| BENIGN | 2.262.380 | 1.641.843 | - |
| DoS Hulk | 223.488 | 158.469 | 593 |
| PortScan | 158.930 | 159.144 | - |
| DDoS | 128.027 | 95.123 | 0 |
| DoS GoldenEye | 10.293 | 7.567 | 80 |
| FTP-Patator | 7.938 | 3.973 | 11 |
| SSH-Patator | 5.897 | 2.980 | 8 |
| DoS slowloris | 5.769 | 3.974 | 1.731 |
| DoS Slowhttptest | 5.499 | 1.742 | 3.369 |
| Bot | 1.966 | 738 | 1.469 |
| Web Attack - Brute Force | 1.507 | 151 | 1.214 |
| Web Attack - XSS | 652 | 27 | 652 |
| Infiltration | 36 | 32 | 16 |
| Web Attack - SQL Injection | 21 | 12 | 0 |
| Heartbleed | 11 | 11 | 0 |

Okuma:
- BENIGN, DoS Hulk ve DDoS'ta yaklaşık %27 azalma: düzeltilmiş CICFlowMeter TCP akışını tek FIN paketinde değil karşılıklı FIN ya da RST ile kapatıyor. Orijinalde tek bağlantı birden fazla akışa bölünüyordu.
- Web saldırıları, Bot ve Slowhttptest'te orijinal etiketlerin çoğu payload'ı olmayan başarısız denemeler. Ör. orijinaldeki 652 XSS akışından düzeltilmiş sürümde yalnız 27'si gerçek saldırı, 652 akış Attempted. Orijinal veriyle eğitilen bir modelin "XSS tespiti" büyük ölçüde payload'sız akışları tanımak demek.
- FTP-Patator ve SSH-Patator yaklaşık yarıya iniyor; muhtemelen bölünmüş akışlar birleştiği için.

## 3. Özellik düzeyinde artefakt listesi (RQ2 için referans)

### 3a. CICFlowMeter hatası olduğu veriyle doğrulananlar (orijinalde var, düzeltilmişte yok)

| Özellik | Orijinaldeki durum | Düzeltilmişte |
|---|---|---|
| `Fwd/Bwd Avg Bytes/Bulk`, `Fwd/Bwd Avg Packets/Bulk`, `Fwd/Bwd Avg Bulk Rate` | Tüm satırlarda sabit (0) | Değişken |
| `Bwd PSH Flags`, `Bwd URG Flags` | Tüm satırlarda sabit | İkisi de değişken |
| `SYN Flag Count` | `Fwd PSH Flags` ile birebir aynı | Bağımsız |
| `CWE Flag Count` | `Fwd URG Flags` ile birebir aynı | Adı doğru TCP bayrağı olan `CWR Flag Count` olarak düzeltilmiş, eşlik yok |
| `Fwd Header Length` | İki kez geçiyor | Bir kez |
| `Fwd Header Length`, `Bwd Header Length`, `min_seg_size_forward` | Negatif değerler (35, 22, 35 satır); başlık uzunluğu negatif olamaz | Negatif yok |
| `Init_Win_bytes_forward`, `Init_Win_bytes_backward` | Sırasıyla 1.001.189 ve 1.441.552 satırda negatif (pencere değeri gözlenemeyince yazılan yer tutucu değer) | Negatif yok |
| `Flow Duration` ve `Flow IAT` özellikleri | 115 satırda negatif süre | 31 satırda negatif süre; düzeltmede de tamamen gitmemiş |
| `Flow IAT Min` | 2.891 satırda negatif | 2.922 satırda negatif; iki sürümde de var |
| `Init_Win_bytes_forward` | 6 sınıfta şüpheli | 2 sınıfta şüpheli |

Negatif süre ve paketler arası süre iki sürümde de görülüyor; bu, araçtan çok kayıttaki paket zaman damgalarının sırasından kaynaklanıyor olabilir. Modelde bu satırlar için ortak bir kural gerekli (ör. sıfıra çekmek ya da işaretlemek).

### 3b. İki sürümde de duran, anlamca şüpheli adaylar (kısayol hipotezi)

| Özellik | Orijinal | Düzeltilmiş | Neden şüpheli |
|---|---|---|---|
| Kaynak port | Bot, Slowhttptest (0,981), GoldenEye, SSH-Patator | Bot, Slowhttptest (0,985), SSH-Patator, 2 Attempted sınıfı | İşletim sisteminin rastgele verdiği sayı; ayırt edici olması saldırı aracı ya da makine izi |
| Sunucu tarafı başlangıç TCP penceresi (`Init_Win_bytes_backward` / `Bwd Init Win Bytes`) | 5 sınıf | 10 sınıf | Cevap veren makinenin ayarına bağlı; saldırıların çoğu aynı hedef sunucuya yapıldığı için hedef sunucuyu tanıtıyor olabilir |
| Hedef port | FTP 0,999, SSH 0,998, Bot 0,980 | Bot 1,000, FTP, SSH, PortScan, ikili | Portun saldırının tanımı olduğu durumlar var; ama model normal trafiği de port ile yanlış sınıflayabilir |

Hipotezler EDA'da tek özellik skoruyla bulundu; modellerin bunlara gerçekten dayanıp dayanmadığı açıklama (SHAP, permutation) ve remove-and-retrain adımlarında test edilecek.

## 4. Beklenmeyen sonuç

Düzeltilmiş sürüm daha kolay ayrışıyor (şüpheli çift sayısı 122 → 549, ikilide 0 → 11). Temizlenmiş akışlarda saldırılar daha belirgin. Bu yüzden "skor > 0,95" tek başına kısayol göstergesi değil; ortak aday tablosunda her özellik için alan bilgisiyle karar verilmeli (`karar` sütunu).

## 5. Selim için: kullanılan CICFlowMeter

- Düzeltilmiş CICIDS2017, Engelen'in sabit CICFlowMeter sürümüyle üretilmiş: https://github.com/GintsEngelen/CICFlowMeter
- Sayfadaki güncellemeler: 20/10/2021 (Idle Time), 22/10/2021 (Bulk özellikleri), 24/11/2021 (Down/Up ratio ve akış uzunluğu özellikleri). Veri dosyaları 22/11/2021 tarihli.
- 5G-NIDD ve TII-SSRC-23 akışları bu reponun 24/11/2021 düzeltmesini içeren sürümüyle çıkarılmalı; kullanılan commit hash'i data card'a yazılmalı.

## 6. Not: 2022 sürümü

Aynı ekibin 2022 çalışması (L. Liu, G. Engelen ve diğerleri, "Error Prevalence in NIDS datasets: A Case Study on CIC-IDS-2017 and CSE-CIC-IDS-2018", IEEE CNS 2022, s. 254–262) etiketleri daha da iyileştiriyor ve düzeltilmiş bir CSE-CIC-IDS2018 sunuyor: https://intrusion-detection.distrinet-research.be/CNS2022/. Plan ve draft WTMC 2021 sürümüne göre kurulu olduğu için şimdilik onu kullanıyoruz; geçiş toplantıda konuşulacak.
