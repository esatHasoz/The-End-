# 5g_nidd: yorum notu (Selim)

Girdi: yayınlanmış `Combined.csv` (Argus özellikleri, 1,215,890 satır), `scripts/prep_group_c.py` ile hazırlandı.
Etiket: `Class` (= `Attack Type`, benign için `Benign`). Çıkarılan kimlikler: `Seq` (Argus kayıt sıra no), `Offset` (kaydın dosyadaki konumu), `Unnamed: 0`. IP, port ve zaman sütunları yayınlanmış dosyada zaten yok.

## 1. Veri kalitesi
- 821,310 birebir tekrar silindi (394,580 satır kaldı). Tekrarlar UDPScan (%98), SYNScan (%93), UDPFlood (%85) ve **Benign (%83)** sınıflarında. Benign trafiğin bu kadar tekdüze olması script'le üretildiğini düşündürüyor.
- **632,401 çelişkili satır** (aynı özellik, farklı etiket); neredeyse tamamı **UDPFlood (350,853) ve Benign (281,529)** arasında. Bu özelliklerle UDPFlood ile benign trafiğin büyük kısmı birbirinden ayırt edilemiyor. `Seq` ve `Offset` çıkarılmadan önce bu satırlar benzersizdi; makaledeki önem sıralamasında bu iki sütunun üstte çıkması, modelin kayıt sırasını öğrenmiş olabileceğine işaret ediyor.
- 14 sütunda NaN var (TTL, TCPBase, Win, Gap, Tos vb.). Muhtemelen protokole bağlı (UDP/ICMP'de TCP alanı yok); NaN'in kendisi sınıfı ele verebilir.
- `RunTime`, `Mean`, `Sum`, `Min`, `Max` = `Dur` (birebir aynı); `sVid`, `dVid` sabit. Otomatik çıkarıldı.

## 2. Sınıflar ve zaman
- Temizlik sonrası %79 saldırı; benign azınlıkta. En küçük sınıflar: UDPScan 329, ICMPFlood 619, SYNScan 1,342.
- UDPScan bölme için yetersiz (`ok = False`).
- Zaman sütunu yok; bölme dosyadaki satır sırasına göre (`__row_order__`). Dosyanın hangi sırayla birleştirildiği (BS1/BS2, saldırı oturumları) bilinmiyor, bu yüzden bölmenin zamansal anlamı belirsiz.

## 3. Şüpheli özellikler
- Binary'de > 0.95 skorlu özellik yok (en yüksek `Rate` 0.92).
- Sınıf bazında 61 şüpheli çift. Olası yorumlar (toplantıda doğrulanacak):
  - **Araç imzası:** ICMPFlood (`dMeanPktSz`, `DstBytes`, `SrcBytes` ≈ 1.00), SYNFlood/SYNScan (`SrcBytes`, `sMeanPktSz`, `SrcWin` ≈ 1.00), TCPConnectScan (`SrcWin` 0.99). hping3 ve nmap sabit paket boyutu ve pencere değeri kullanıyor; model saldırıyı değil aracı tanıyor olabilir.
  - **Ortam/konum izi:** UDPScan `sTtl` (0.997); HTTPFlood ve SlowrateDoS `SynAck`, `TcpRtt`, `AckDat` (0.99). Saldırganın ağdaki konumu (hop sayısı, gecikme) benign kullanıcılardan farklı olabilir.
- Literatürle örtüşme: TTL (Flood vd., UNSW-NB15). Yeni: `Seq`/`Offset` kayıt kimlikleri ve RTT tabanlı özellikler.

## 4. Uyarılar
- `No timestamp: file row order is used as time` — bkz. bölüm 2.
- `Classes with fewer than 50 rows in a split: UDPScan`.
- `--frac` kullanılmadı.

## 5. Toplantıda karar gerekenler
1. UDPScan: çıkarılsın mı, üç scan sınıfı tek `Scan` sınıfında birleştirilsin mi?
2. UDPFlood–Benign çelişkili satırları: silinsin mi, işaretli kalsın mı? (Silinirse UDPFlood'un çoğu gider.)
3. NaN'ler nasıl doldurulacak; "NaN mı" bilgisi ayrı bir özellik olsun mu?
4. Zaman bölmesi: satır sırası yerine baz istasyonu (BS1 → BS2) bazında bölme mümkün mü? (Yeniden çıkarmada pcap dosyaları ayrı olduğu için mümkün.)