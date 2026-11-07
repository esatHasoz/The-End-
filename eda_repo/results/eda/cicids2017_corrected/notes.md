# cicids2017_corrected: yorum notu (Ahmet)

## 1. Veri kalitesi
- Engelen ve diğerleri (WTMC 2021) düzeltilmiş sürüm, 5 günlük CSV, 24/11/2021 güncellemesi dahil (dosya tarihleri 22/11/2021). Kaynak: https://intrusion-detection.distrinet-research.be/WTMC2021/tools_datasets.html
- 2.100.814 satır, hepsi etiketli. Sınıf sayıları yayınlanan tabloyla örtüşüyor: DoS Hulk, FTP-Patator, SSH-Patator, DoS Slowhttptest, Bot ve DDoS birebir aynı. BENIGN'de 624 satır fark var (bizde 1.657.693, tabloda 1.657.069); yazarlar NaN içeren satırları silmiş, biz silmedik.
- 15.885 tekrar eden satır silindi: BENIGN 15.850, DoS slowloris 27, PortScan 7, Bot - Attempted 1.
- 4 çelişkili satır (PortScan 2, BENIGN 2): tutuldu, `_conflicting` ile işaretli.
- `Flow Bytes/s` sütununda 191 inf ve 602 NaN, `Flow Packets/s` sütununda 793 inf var. Orijinalden çok daha az.
- Yeni: 252 satırda `Flow IAT Mean/Std/Max/Min` boş. Muhtemelen tek paketli akışlar (paketler arası süre tanımsız).
- Negatif değerler orijinalden çok daha az: `Flow Duration` 31 satırda, `Flow IAT Min` 2.922 satırda negatif. Başlık uzunluğu ve TCP penceresi sütunlarında negatif yok; orijinaldeki pencere yer tutucu değeri burada kullanılmamış.
- Sabit sütun yok. `CWE Flag Count` sütunu doğru adıyla `CWR Flag Count` olmuş. Orijinaldeki `SYN Flag Count` = `Fwd PSH Flags` ve `CWE Flag Count` = `Fwd URG Flags` eşlikleri yok. Kalan kopyalar beklenen türden: `Average Packet Size` = `Packet Length Mean`, `Fwd/Bwd Segment Size Avg` = `Fwd/Bwd Packet Length Mean`.
- 76 model özelliği kaldı (orijinalde 65).

## 2. Sınıflar ve zaman
- 25 sınıf (15 asıl sınıf + 10 "- Attempted"), saldırı oranı %21,3. Attempted satırı toplam 9.144; politika: keep (ayrı sınıf, ikili analizde saldırı).
- 9 sınıf her bölmeye 50 satır veremiyor: Heartbleed, Infiltration, Infiltration - Attempted, SQL Injection, XSS, Brute Force, DoS GoldenEye - Attempted, FTP-Patator - Attempted, SSH-Patator - Attempted.
- Zaman damgalarında AM/PM var, düzeltme uygulanmadı. Saatler orijinalden 5 saat ileride (pazartesi kaydı 13:56'da başlıyor, orijinalde 08:56). Sürüm Belçika'da yeniden üretildiği için Orta Avrupa saatine göre yazılmış olmalı. Her set kendi içinde bölündüğü için EDA'yı etkilemez; iki zaman grafiğini karşılaştırırken kayma görülür.
- Orijinaldeki gibi test BENIGN'i cuma öğleden sonradan geliyor.

## 3. Şüpheli özellikler
- İkili sınıflandırmada 11 özellik tek başına 0,95'i geçiyor (orijinalde hiç yok). En yükseği `Total Length of Bwd Packet` (0,980); `Dst Port` da listede (0,954).
- Sınıf bazında 549 şüpheli çift (orijinalde 122). Akışlar temizlenince saldırılar daha kolay ayrışıyor. DDoS, DoS Hulk, FTP-Patator gibi sınıflarda tek bir paket boyutu özelliği 1,000'a ulaşıyor.
- Attempted sınıfları da BENIGN'den çok kolay ayrışıyor: ör. XSS - Attempted'ı `Bwd Init Win Bytes` tek başına 0,999 ile ayırıyor. Payload'ı olmayan bu akışları ayıran şey saldırının kendisi olamaz; ayıran şey makine ve bağlantı özellikleri.
- İki sürümde de duran, anlamca şüpheli adaylar:
  - `Src Port`: Bot, DoS Slowhttptest (0,985), SSH-Patator ve iki Attempted sınıfı. Araç düzeltmesinden etkilenmiyor; saldırı aracı ya da makine izi.
  - `Bwd Init Win Bytes`: 10 sınıfta (orijinalde 5). Hedef sunucunun TCP ayarına bağlı; saldırıların çoğu aynı hedef sunucuya yapıldığı için model "hedef sunucuya giden trafik" öğreniyor olabilir. Hedef IP'ye göre kontrol edilmeli.
  - `Dst Port`: Bot'ta 1,000, ayrıca FTP-Patator, SSH-Patator, PortScan ve ikili sınıflandırmada şüpheli.
- `FWD Init Win Bytes` 2 sınıfa düştü (orijinalde 6).

## 4. Uyarılar
- 9.144 Attempted satırı, politika keep.
- 9 yetersiz sınıf: karar gerekli.
- `--frac` kullanılmadı, tüm veri işlendi.
- Sahte özellik kontrolü: train ve val'de uyum 0,99, test'te 0,665 (beklenen değer).

## 5. Toplantıda karar gerekenler
1. Attempted politikası: keep, benign ya da drop. Öneri: EDA ve RQ1 analizinde keep; ana modelde ikili sınıflandırma için benign ya da drop seçeneği karşılaştırılsın. Payload'ı olmayan akışın "saldırı" sayılması tartışmalı.
2. Yetersiz 9 sınıf için ortak kural (orijinal setle aynı kural).
3. `Bwd Init Win Bytes` hipotezini test etmek için hedef IP'lere göre ek analiz yapılsın mı (ör. aynı sunucuya giden BENIGN ile saldırı karşılaştırması)?
4. Saat dilimi farkı raporda belirtilecek; başka işlem gerekmiyor.
