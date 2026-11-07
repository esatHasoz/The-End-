# cicids2017_orig: yorum notu (Ahmet)

## 1. Veri kalitesi
- GeneratedLabelledFlows (TrafficLabelling) CSV'leri, 8 dosya. MD5 kontrolü yayınlanan değerle aynı.
- 3.119.345 satır okundu, 288.602'si etiketsiz boş satır olduğu için atıldı. Bu satırlar perşembe sabahı Web Attacks dosyasının sonundaki bilinen boş satırlar; veri kaybı yok. Kalan 2.830.743 satır ve BENIGN sayısı (2.273.097) literatürdeki CICIDS2017 sayılarıyla aynı.
- 18.329 tekrar eden satır silindi: BENIGN 10.717, DoS Hulk 7.585, DoS slowloris 27. Çelişkili satır yok.
- `Flow Bytes/s` sütununda 1.509 inf ve 1.358 NaN, `Flow Packets/s` sütununda 2.867 inf var.
- 8 sütun tamamen sabit: tüm Bulk özellikleri (`Fwd/Bwd Avg Bytes/Bulk`, `Fwd/Bwd Avg Packets/Bulk`, `Fwd/Bwd Avg Bulk Rate`), `Bwd PSH Flags`, `Bwd URG Flags`.
- Anlamca farklı ama değerleri birebir aynı sütunlar: `SYN Flag Count` = `Fwd PSH Flags`, `CWE Flag Count` = `Fwd URG Flags`. İki farklı bayrağın her satırda aynı olması mümkün değil; bu CICFlowMeter hatası. Düzeltilmiş sürümde bu eşlikler yok (bkz. `docs/cicids2017_orig_vs_corrected.md`).
- Olamayacak negatif değerler: `Flow Duration` 115 satırda, `Flow IAT Min` 2.891 satırda, `Fwd/Bwd Header Length` 35 ve 22 satırda, `min_seg_size_forward` 35 satırda negatif. `Init_Win_bytes_forward` 1.001.189 satırda, `Init_Win_bytes_backward` 1.441.552 satırda negatif: pencere gözlenemeyince yazılan yer tutucu değer. Bu yer tutucu, bu iki sütunun şüpheli çıkmasının bir nedeni olabilir.
- Beklenen kopyalar: `Fwd Header Length` iki kez geçiyor, `Subflow Fwd/Bwd Packets` = `Total Fwd/Backward Packets`, `Avg Fwd/Bwd Segment Size` = `Fwd/Bwd Packet Length Mean`.
- Sabit ve kopya sütunlar çıkarıldıktan sonra 65 model özelliği kaldı.

## 2. Sınıflar ve zaman
- 15 sınıf, saldırı oranı %19,6. En küçük sınıflar: Heartbleed 11, SQL Injection 21, Infiltration 36 satır. Bu üçü her bölmeye 50 satır veremiyor (`split_report.csv`, ok = False).
- Zaman damgaları 12 saatlik ve AM/PM işaretsiz. Kod 1.466.965 satırı (saat 1–7) 12 saat ileri aldı. Zaman grafiği saldırıları belgelenen saatlerde gösteriyor (salı FTP sabah, SSH öğleden sonra; çarşamba DoS sabah, Heartbleed öğleden sonra; perşembe web saldırıları sabah, Infiltration öğleden sonra; cuma Bot, PortScan, DDoS). Düzeltme doğru çalışıyor.
- Tek kayıt oturumu: 3–7 Temmuz 2017, her gün mesai saatleri. Saldırıların her biri kendi gününde tek bir zaman penceresinde.
- Bölme sınıf bazında zamana göre olduğu için test setindeki BENIGN trafiğin tamamı cuma öğleden sonradan, saldırıların test kısmı ise kendi günlerinden geliyor. Test'te BENIGN ile saldırılar farklı günlerden; modelin gün farkını öğrenme ihtimali yorumda akılda tutulmalı.

## 3. Şüpheli özellikler
- İkili sınıflandırmada tek başına 0,95'i geçen özellik yok; en yükseği `Average Packet Size` (0,947).
- Sınıf bazında 122 şüpheli (özellik, sınıf) çifti var. Çoğu paket boyutu ve zamanlama özellikleri; DDoS ve PortScan gibi saldırılarda bunlar meşru sinyal olabilir. Eşik "kolay ayrışıyor" demek, "kısayol" demek değil.
- Anlamca şüpheli olanlar:
  - `Source Port`: Bot, DoS Slowhttptest (0,981), DoS GoldenEye, SSH-Patator. Kaynak port işletim sisteminin rastgele verdiği bir sayı; ayırt edici olması saldırı aracının ya da saldırgan makinenin izi.
  - `Init_Win_bytes_backward`: 5 sınıfta (SSH-Patator 0,998, Web Attack Brute Force 0,989). Cevap veren makinenin TCP ayarına bağlı; model saldırı yerine hedef sunucuyu tanıyor olabilir.
  - `Init_Win_bytes_forward`: 6 sınıfta. Düzeltilmiş sürümde 2 sınıfa düşüyor, kısmen araç hatası.
  - `Destination Port`: FTP-Patator 0,999, SSH-Patator 0,998, Bot 0,980. Port 21 ve 22 bu saldırıların tanımı; ama model "port 22 = saldırı" öğrenirse normal SSH trafiğini de saldırı sayar.

## 4. Uyarılar
- 288.602 etiketsiz satır silindi: boş satırlar, sorun değil.
- 1.466.965 satır 12 saat kaydırıldı: AM/PM düzeltmesi, zaman grafiğiyle doğrulandı.
- Heartbleed, Infiltration, SQL Injection yetersiz: karar gerekli.
- `--frac` kullanılmadı, tüm veri işlendi.
- Sahte özellik kontrolü: train ve val'de uyum 0,99, test'te 0,686 (saldırı oranına göre beklenen değer).

## 5. Toplantıda karar gerekenler
1. Heartbleed (11), SQL Injection (21) ve Infiltration (36) çıkarılsın mı, "Other attack" gibi bir sınıfta birleştirilsin mi?
2. Kaynak port modelde tutulsun mu? Önerimiz: tutup portlu ve portsuz iki varyantla karşılaştırmak (RQ1 için doğal test).
3. Test BENIGN'inin tek günden gelmesi sorun mu? Alternatif: BENIGN'i gün bazında bölmek.
4. `Flow Bytes/s` ve `Flow Packets/s` için inf ve NaN doldurma yöntemi (dolgu değerleri sadece train'den).
