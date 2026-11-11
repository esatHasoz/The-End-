# nf3_cse_cic_ids2018: yorum notu (Esad)

**%10 örneklem** (2,011,291 / 20,115,529 flow), `eda-v2`. Örneklem `awk 'BEGIN{srand(42)} NR==1 || rand()<0.1'` ile çıkarıldı (`data/interim/NF-CICIDS2018-v3_frac0.1_seed42.csv`). Nedeni: EDA'nın çalıştığı ortamda RAM 3.9 GB. Tekrar ve çelişki sayıları tam veriyle doğrudan karşılaştırılamaz.

## 1. Veri kalitesi
- 121,554 tekrar satır silindi. **FTP-BruteForce'un %66'sı** (25,350/38,682), Slowloris'in %29'u, SlowHTTPTest'in %27'si tekrar.
- 36,085 çelişkili satır var. Bunların neredeyse tamamı **FTP-BruteForce ile DoS_attacks-SlowHTTPTest arasında**: 7,237 özellik vektörü iki sınıfta da birebir aynı.
- **Etiket hatası (aşağıda ayrıntı):** FTP-BruteForce ve SlowHTTPTest satırlarının %100'ü tek paketli, port 21'e giden, `TCP_FLAGS = 22` (SYN + RST + ACK) olan bağlantılar. Yani bunlar reddedilmiş FTP bağlantı denemeleri. SlowHTTPTest bir HTTP saldırısı olduğu için port 21'de görünmemeli. Bu sınıftaki flow'lar büyük ihtimalle yanlış etiketlenmiş FTP trafiği. CSE-CIC-IDS2018'deki etiket hatalarını inceleyen bir çalışma var: L. Liu, G. Engelen, T. Lynar, D. Essam, W. Joosen, "Error Prevalence in NIDS datasets: A Case Study on CIC-IDS-2017 and CSE-CIC-IDS-2018", IEEE CNS 2022. Bu iki sınıf için ne bulduklarını makaleden kontrol etmek ve referans listesine eklemek gerekiyor.
- **Infilteration** gürültülü: flow'ların %56'sı port 53'e (DNS) gidiyor ve tek feature ile en iyi AUROC sadece 0.73. Muhtemelen kurban makinenin tüm trafiği saldırı diye etiketlenmiş.
- inf ve NaN yok. Sabit sütun `FTP_COMMAND_RET_CODE` (örneklemde). `MAX_IP_PKT_LEN`, `LONGEST_FLOW_PKT` ile birebir aynı.

## 2. Sınıflar ve zaman
- 14 saldırı sınıfı, saldırı oranı %12. Her saldırı sınıfı **tek bir günde** gerçekleşmiş (14 Şubat – 2 Mart 2018). Bu yüzden sınıf bazında zaman bölmesi aynı günün içinde yapılıyor.
- Zaman grafiği beklendiği gibi: benign trafik 10 gün boyunca dağınık, her saldırı sınıfı kendi gününde. Buradan çıkan bir sonuç var: sınıf bazında zaman bölmesinde benign test satırları son günlerden (1–2 Mart) geliyor, saldırı test satırları ise her sınıfın kendi gününden. Yani test setinde benign ve saldırı satırları farklı günlerden geliyor, gün ya da ortam farkı modelde bir kısayol olarak işe yarayabilir. Toplantıda konuşulmalı.
- Örneklemde yetersiz kalan sınıflar: SQL_Injection (19), Brute_Force_-XSS (16), Brute_Force_-Web (138), DDOS_attack-LOIC-UDP (328). Tam veride bu sınıfların ham sayıları 440, 480, 1,618 ve 3,450. LOIC-UDP ve Web brute force tam veriyle muhtemelen yeterli olur. XSS ve SQL Injection tekrarlar silinince tam veride de sınırda kalabilir.

## 3. Şüpheli özellikler
- Binary'de tek feature ile ayrım UNSW kadar kolay değil: sadece `LONGEST_FLOW_PKT` (0.96) eşiği geçiyor. Buna karşın 14 sınıfın 10'unda en az bir özellik 0.999–1.000 skor alıyor. Toplam 180 şüpheli (özellik, kapsam) çifti var.
- **Portlar (sınıf bazında çok güçlü):** FTP-BruteForce ve SlowHTTPTest'te port 21, SSH'ta port 22, Bot'ta port 8080, her biri %100. Port, 10 sınıf kapsamında şüpheli çıkıyor. Bunların bir kısmı gerçek bir işaret (SSH brute force zaten port 22'ye gider). SlowHTTPTest'teki port 21 ise etiket hatası.
- **TTL (UNSW'deki artefaktın benzeri):** HOIC flow'larının %100'ünde TTL 127, Hulk'ta %100'ünde TTL 63. Benign'de TTL dağınık. 6 sınıfta şüpheli.
- Bunlara ek olarak `TCP_WIN_MAX_IN/OUT`, `LONGEST_FLOW_PKT`, `IN/OUT_BYTES` birçok DoS sınıfında 1.000 skor alıyor. Bu DoS araçlarının sabit paket şablonu kullanmasından kaynaklanıyor olabilir. Gerçek saldırı işareti mi, araç artefaktı mı, ablation ile ayrılmalı.

## 4. Uyarılar
- `Classes with fewer than 50 rows in a split: Brute_Force_-Web, Brute_Force_-XSS, DDOS_attack-LOIC-UDP, SQL_Injection` (örneklem kaynaklı).
- Sahte özellik kontrolü: etiketle uyum train 0.990, val 0.990, test 0.789. Beklenen değer 1 − 2p(1−p) = 0.789 (p = 0.12), tutuyor.
- `--frac` yerine önceden çıkarılmış %10 örneklem kullanıldı. Bu nedenle `data_card.md`'de "Sampling at load: none" yazıyor. Örneklemin nasıl çıkarıldığı bu notta ve `data_card.md`'nin sonundaki notta belirtildi.

## 5. Toplantıda karar gerekenler
1. **SlowHTTPTest:** Etiketi hatalı görünüyor. Çıkarılsın mı, "FTP denemesi" olarak yeniden mi etiketlensin? Bu konu Ahmet'in CICIDS2017'deki Attempted kararıyla birlikte konuşulmalı.
2. **FTP-BruteForce:** Tamamı başarısız bağlantı denemesi. Saldırı mı sayılsın, "attempted" gibi mi ele alınsın?
3. **Infilteration** gürültülü etiketli: modelde tutulsun mu?
4. CIC2018 tam veriyle mi analiz edilecek? Tam veri ~20M satır ve bu ortamda sığmıyor. 16 GB'lık bir makinede `--frac 0.25` ya da tam veri denenebilir.
5. `DNS_QUERY_ID`: UNSW'deki ile aynı karar (kimlik olarak drop listesine eklenmesi öneriliyor).
6. SQL_Injection ve XSS: tam veride de yetersiz kalırlarsa "Web Attack" altında birleştirilsin mi?
