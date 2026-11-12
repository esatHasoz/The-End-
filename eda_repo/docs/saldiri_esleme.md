# Saldırı eşleme tablosu (Esad)

Amaç: cross-dataset testlerinde hangi saldırı sınıflarının karşılaştırılabileceğini belirlemek. Sınıflar ortak, kaba bir taksonomiye eşlenir. Bir kategori iki sette de varsa o kategoride cross-dataset test yapılabilir.

**Kaynak durumu:**
- NF3 setlerinin sınıf adları ve sayıları gerçek dosyalardan alındı. CIC2018 için sayılar tam dosyadan (awk ile), UNSW için EDA'dan.
- CICIDS2017, 5G-NIDD ve TII-SSRC-23 sınıfları ilgili makalelerden derlendi. **Ahmet ve Selim kendi EDA'larını çalıştırınca `label_distribution.csv` dosyalarıyla doğrulanmalı.**

## Ortak taksonomi

| Kategori | Tanım |
|---|---|
| DoS-L7 | Tek kaynaklı, uygulama katmanı DoS (HTTP flood, slow-rate) |
| DoS-L3/4 | SYN/UDP/ICMP flood gibi ağ ve taşıma katmanı flood'ları |
| DDoS | Çok kaynaklı DoS |
| Scan | Port tarama, keşif |
| BruteForce | FTP, SSH, Telnet, HTTP parola denemesi |
| WebAttack | XSS, SQL injection, web form brute force |
| Botnet | Bot trafiği, C&C |
| Infiltration/Exploit | Exploit, backdoor, sızma |
| Diğer | Hiçbir sette karşılığı olmayanlar |

## 1. Group B: NF3-CSE-CIC-IDS2018 ↔ NF3-UNSW-NB15 (aynı NetFlow v3 özellikleri)

| Kategori | NF3-CSE-CIC-IDS2018 (tam veri ham sayı) | NF3-UNSW-NB15 (temizlenmiş) | Cross-dataset? |
|---|---|---|---|
| DoS-L7 | DoS_attacks-Hulk (100,076), GoldenEye (61,300), Slowloris (36,040), SlowHTTPTest (105,550)\* | – | – |
| DoS (genel) | (yukarıdakiler) | DoS (5,945) | **Evet, kaba düzeyde** (bkz. not 1) |
| DDoS | DDOS_attack-HOIC (1,032,311), DDoS_attacks-LOIC-HTTP (288,589), DDOS_attack-LOIC-UDP (3,450) | – | Hayır |
| Scan | – | Reconnaissance (16,878) | Hayır |
| BruteForce | FTP-BruteForce (386,720)\*, SSH-Bruteforce (188,474) | – | Hayır |
| WebAttack | Brute_Force_-Web (1,618), Brute_Force_-XSS (480), SQL_Injection (440) | – | Hayır |
| Botnet | Bot (207,703) | – | Hayır |
| Infiltration/Exploit | Infilteration (188,152)\* | Exploits (42,651), Backdoor (4,621), Shellcode (2,378), Worms (158) | Zayıf (bkz. not 2) |
| Diğer | – | Fuzzers (33,044), Generic (8,066), Analysis (1,226) | – |

\* Etiket sorunu var (bkz. `results/eda/nf3_cse_cic_ids2018/notes.md`): FTP-BruteForce ve SlowHTTPTest flow'larının tamamı port 21'e reddedilmiş bağlantı denemeleri. Infilteration gürültülü etiketli.

**Notlar:**
1. Ortak tek kategori **DoS**, ve o da yalnızca kaba düzeyde ortak. UNSW'nin DoS sınıfı farklı araçlarla üretilmiş genel DoS trafiği. CIC2018'in DoS sınıfları ise belirli HTTP DoS araçlarından geliyor. SlowHTTPTest hatalı olduğu için CIC2018 tarafı Hulk, GoldenEye ve Slowloris ile sınırlanmalı.
2. Infilteration ↔ Exploits/Backdoor eşlemesi anlamsal olarak zayıf ve CIC2018 tarafı gürültülü. Ana testte kullanılmamalı.
3. **Sonuç:** Proposal'daki NF3-CSE-CIC-IDS2018 → NF3-UNSW-NB15 testi sınıf bazında neredeyse yapılamıyor. Önerim: Group B cross-dataset testi **binary** (benign vs. saldırı) yapılsın, ek olarak **DoS-only** bir alt test eklensin. Bu kapsam daraltmasının hocaya bildirilmesi gerekiyor (proposal R3 riski gerçekleşmiş durumda).

## 2. Group A/C: düzeltilmiş CICIDS2017 ↔ 5G-NIDD ↔ TII-SSRC-23 (aynı CICFlowMeter özellikleri)

| Kategori | CICIDS2017 (düzeltilmiş) | 5G-NIDD | TII-SSRC-23 | Cross-dataset? |
|---|---|---|---|---|
| DoS-L7 (HTTP flood) | DoS Hulk, DoS GoldenEye | HTTP Flood | DoS HTTP flood | **Evet, üçü** |
| DoS-L7 (slow-rate) | DoS slowloris, DoS Slowhttptest | Slowrate DoS | – | 2017 ↔ 5G-NIDD |
| DoS-L3/4 (SYN/UDP/ICMP flood) | – | SYN Flood, UDP Flood, ICMP Flood | DoS SYN/UDP/ICMP… (Mirai flood'ları ayrıca) | **5G-NIDD ↔ TII** |
| DDoS | DDoS (LOIC, HTTP) | – | Mirai DDoS türleri | Zayıf (bkz. not 3) |
| Scan | PortScan | SYN Scan, TCP Connect Scan, UDP Scan | Information Gathering | **Evet, üçü** |
| BruteForce | FTP-Patator, SSH-Patator | – | Bruteforce (FTP, SSH, Telnet, HTTP, DNS) | **2017 ↔ TII** (FTP, SSH) |
| WebAttack | Web Attack (Brute Force, XSS, SQL Injection) | – | – | Hayır |
| Botnet | Bot (ARES) | – | Mirai | Zayıf (bkz. not 3) |
| Infiltration/Exploit | Infiltration, Heartbleed | – | – | Hayır |

**Notlar:**
1. Proposal'daki ortak türler (DoS/DDoS flood, port scan, SSH ve FTP brute force) tabloyla örtüşüyor. En güçlü üçlü eşlemeler **HTTP-flood DoS** ve **Scan**.
2. CICIDS2017'de L3/4 flood (SYN, UDP) ayrı bir sınıf olarak yok, bu kategoride test yalnızca 5G-NIDD ↔ TII arasında yapılabilir.
3. Botnet ve DDoS eşlemeleri aynı kategoride görünse de araçlar çok farklı (ARES vs. Mirai, LOIC vs. Mirai). Ayrı bir "zayıf eşleme" testi olarak raporlanmalı, ana sonuca katılmamalı.
4. Düzeltilmiş CICIDS2017'deki "- Attempted" sınıflarının nasıl ele alınacağı (keep/benign/drop) bu eşlemeyi doğrudan etkiliyor. CIC2018'deki FTP-BruteForce sorunu da aynı türden. İkisi toplantıda birlikte karara bağlanmalı.
5. 5G-NIDD ve TII-SSRC-23 sınıf adları makalelerden alındı. Selim'in yeniden etiketlediği flow'lardaki gerçek adlarla eşleme sütunu güncellenmeli.

## Sonraki adım

Bu tablonun makine tarafından okunabilir hali (`docs/saldiri_esleme.csv`: `dataset, sinif, kategori, cross_dataset_kullan`) altı setin EDA'sı tamamlanınca üretilecek. Böylece modelleme kodu sınıfları doğrudan bu tablodan eşleyebilir.
