# nf3_unsw_nb15: yorum notu (Esad)

Tam veri (2,365,424 flow), `eda-v2`, örnekleme yok.

## 1. Veri kalitesi
- 225,997 tekrar satır (%9.6) silindi: 213,271 Benign, 11,585 **Generic** (Generic'in %59'u tekrar).
- 3,647 çelişkili satır var (en çok Generic 409, Exploits 297, Backdoor 279). Tutuldu, işaretlendi.
- `SRC_TO_DST_SECOND_BYTES` ve `DST_TO_SRC_SECOND_BYTES` sütunlarında inf var, birinde NaN da var. Modelde imputation gerekecek.
- `MAX_IP_PKT_LEN`, `LONGEST_FLOW_PKT` ile birebir aynı ve çıkarıldı. Sabit sütun yok.

## 2. Sınıflar ve zaman
- Saldırı oranı %5.4. Dengesizlik çok yüksek: Benign/Worms oranı 12,813.
- **Worms** (158 satır) yetersiz: zaman blokları ile bile val'e 19, test'e 18 satır düşüyor (`ok = False`).
- Veri iki kayıt oturumundan geliyor: 22–23 Ocak ve 18 Şubat 2015 (UTC). Her saldırı sınıfının %78–99'u ikinci oturumda. Sınıf bazında zaman bölmesi sonucunda train iki oturumu da içeriyor. Val ve test yalnızca 18 Şubat'ın son saatlerinden geliyor. Test, ilk oturumdaki trafiği hiç görmüyor.

## 3. Şüpheli özellikler
- **TTL (literatürle örtüşüyor, en güçlü aday):** `MIN_TTL` ve `MAX_TTL` binary'de 0.9986 skor alıyor, 9 saldırı sınıfının hepsinde şüpheli, 8'inde 1.000. Benign flow'ların %99.7'sinde TTL 31, saldırıların %72'sinde 254, %28'inde 62. Bu ayrım saldırı davranışından değil, testbed topolojisinden (saldırgan ve kurban ağı) kaynaklanıyor. UNSW-NB15'in bilinen bir artefaktı.
- **Aynı türden adaylar:** `MIN_IP_PKT_LEN` (0.9995) ve `SHORTEST_FLOW_PKT` (0.98) neredeyse her sınıfta şüpheli. `TCP_WIN_MAX_IN/OUT` (0.96–0.97) histogramda saldırılar için tek bir değerde yığılıyor, bu da saldırgan makinelerin TCP stack'inin izi olabilir.
- Toplam 102 (özellik, kapsam) çifti şüpheli. Sınıf bazında en çok TTL, paket boyu ve TCP pencere özellikleri öne çıkıyor.
- **Portlar:** `L4_DST_PORT` sadece 1 kapsamda şüpheli. Bu sette ana kısayol port değil, TTL.

## 4. Uyarılar
- Tek uyarı: `Classes with fewer than 50 rows in a split: Worms`.
- Sahte özellik kontrolü: etiketle uyum train 0.990, val 0.990, test 0.899. Test değeri etiketten bağımsız bir özellik için beklenen 1 − 2p(1−p) = 0.898 ile tutuyor (p = 0.054).

## 5. Toplantıda karar gerekenler
1. **Worms:** Binary'de kalsın. Multi-class'ta çıkarılsın mı, yoksa "yetersiz" diye mi raporlansın?
2. **`DNS_QUERY_ID`** (`review_manually`): Rastgele üretilen DNS transaction ID'si. Tek başına AUROC ~0.53, yani bilgi taşımıyor. Önerim: kimlik olarak kabul edilsin ve config'teki drop listesine eklensin (PR ile).
3. **TTL:** Ana modelde tutulsun mu, yoksa TTL'siz bir varyant da mı eğitilsin? TTL'yi tutmak RQ1 için doğal bir test olur.
4. İki oturumlu zaman yapısı raporda nasıl anlatılacak? Test yalnızca ikinci oturumun sonundan geliyor.
