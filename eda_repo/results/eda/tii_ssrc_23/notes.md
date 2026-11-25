# tii_ssrc_23: yorum notu (Selim)

Girdi: Kaggle'da yayınlanmış `tii_ssrc_23.csv` (CICFlowMeter özellikleri, 8,656,767 flow, 5 GB), `scripts/prep_group_c.py` ile hazırlandı.
Etiket: `Class` = benign ise `Benign`, değilse `Traffic Type` (Bruteforce, DoS, Information Gathering, Mirai). Benign trafiğin `Traffic Type` değerleri Audio, Background, Text, Video olduğu için `Label` ile birleştirildi. `Flow ID`, `Src IP`, `Dst IP` hazırlıkta çıkarıldı (bellek için; EDA da çıkarıyor). Tam veriyle çalıştırıldı, `--frac` kullanılmadı.

## 1. Veri kalitesi
- Çok temiz: 2,769 tekrar (çoğu Mirai), 35 çelişkili satır (Mirai 19, DoS 16; Mirai botları da flood yaptığı için doğal). NaN ve inf yok.
- 7 sabit veya kopya sütun otomatik çıkarıldı (CICFlowMeter'ın bulk/flag alanları; `Fwd/Bwd Segment Size Avg` = `Packet Length Mean`).
- **Zaman damgaları:** Benign, Bruteforce, DoS ve Information Gathering'in **tamamı 1970-01-01/03** tarihli (cihaz saati ayarlanmamış; göreli saat). **Sadece Mirai 2023-02-07/08** tarihli (makaleye göre Mirai, access point üzerinde ayrı kaydedildi). Zaman damgası tek başına Mirai'yi diğer her şeyden ayırıyor: kayıt düzeninden gelen bir artefakt. `Timestamp` modelden çıkarıldığı için doğrudan sızıntı yok; ama kayıt noktasının farklı olması Mirai'nin diğer özelliklerini de etkilemiş olabilir.

## 2. Sınıflar ve zaman
- **Benign sadece 1,301 flow (%0.015).** DoS %86.6, Information Gathering %12.0, Mirai %1.0, Bruteforce %0.4. Benign uzun süreli ses/video/metin bağlantılarından oluştuğu için az flow üretmiş.
- Sonuç: binary accuracy anlamsız (hep "saldırı" diyen model %99.985). Benign recall, sınıf bazında metrikler ve MCC kullanılmalı.
- Sahte özellik testi bu sette işlemiyor: saldırı oranı ~1 olduğu için test'te de özellik neredeyse hep "saldırı" değerini alıyor (uyum 0.9997).
- Bütün sınıflar bölmeye yetiyor (Benign: train 910, val 195, test 184). Bölme her sınıfın kendi saatine göre; Mirai dışındaki sınıfların saati göreli olduğu için sınıflar arası zaman karşılaştırması anlamsız.

## 3. Şüpheli özellikler
- Binary'de > 0.95 yok (en yüksek `Packet Length Max` 0.90). Sınıf bazında 7 şüpheli çift:
  - **Port:** Bruteforce `Dst Port` 0.999 (SSH, FTP, Telnet vb. hedef servis portları), Information Gathering `Src Port` 0.967 (tarama aracının kaynak portu). Kılıç & Şengül'deki port shortcut'ıyla örtüşüyor.
  - **TCP başlangıç penceresi:** `FWD Init Win Bytes`: Information Gathering 0.989, DoS 0.982. **CICIDS2017'deki `Init_Win_bytes_forward` artefaktıyla aynı özellik** (Engelen vd., Subasi vd.); araçların sabit pencere değeri kullanmasından geliyor olabilir. Gruplar arası ortak bulgu olarak tabloya girmeli.
  - **Paket boyutu / zamanlama:** Bruteforce `Fwd Packet Length Max` 0.956, `Total Length of Fwd Packet` 0.955 (sabit giriş denemesi boyutu); Information Gathering `Flow IAT Min` 0.952.
- Sınırın hemen altında: DoS ve Mirai'de paket boyutu (0.92–0.94).

## 4. Uyarılar
- Terminalde UYARI yok. Zaman damgası sorunu (bölüm 1) uyarı üretmiyor, çünkü 1970 tarihleri geçerli tarih olarak okunuyor.
- `--frac` kullanılmadı (16 GB RAM'de tam veri ~4 dakikada çalıştı).

## 5. Toplantıda karar gerekenler
1. Benign'in 1,301 flow olması: TII binary analizde kullanılsın mı, yoksa sadece saldırı türleri arası (multi-class) ve cross-dataset testlerde mi?
2. Mirai'nin farklı saat ve kayıt noktası: Mirai cross-dataset testlerinde ayrı mı değerlendirilsin?
3. `FWD Init Win Bytes`: CICIDS2017 ile ortak shortcut adayı olarak ortak tabloya alınması ve portlu/portsuz varyantların karşılaştırılması.
4. Sahte özellik testi TII'de nasıl yapılacak (ör. sadece saldırı sınıfları arasında, multi-class etikete bağlı enjeksiyon)?