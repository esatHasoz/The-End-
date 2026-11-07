# EDA teslim listesi (hafta 3–4)

Son tarih: hafta 4 sonu, karşılaştırma toplantısından önce (tarih: ____)

Her kişi kendi iki veri seti için aşağıdakileri repoya PR ile ekler.

## Kim, hangi set

| Grup | Kişi | Veri setleri |
|---|---|---|
| A | Ahmet | cicids2017_orig, cicids2017_corrected |
| B | Esad | nf3_unsw_nb15, nf3_cse_cic_ids2018 |
| C | Selim | 5g_nidd, tii_ssrc_23 |

Komutlar: `src/eda/README.md`

## Başlamadan önce

- Herkes `eda-v2` koduyla çalışır. Önce `python tests/test_eda_smoke.py smoke_out` çalıştırılır ve son satırda `SMOKE TEST OK` görülür.
- Teslimden önce kontrol: `manifest.json` içindeki `eda_version` herkeste `eda-v2` olmalı. Eski sürümle üretilmiş sonuçlar kabul edilmez (v1'de sahte özellik test setinde de koreleydi).

## Repoya eklenecekler (her veri seti için)

`results/eda/<set_adi>/` klasöründen sadece küçük dosyalar:

- `summary.md`
- `data_card.md` (URL, sürüm, lisans alanlarında TODO kalmasın)
- `manifest.json`
- `load_info.json`, `quality_summary.json`, `quality_columns.csv`
- `label_distribution.csv`, `label_bar.png`, `label_timeline.png`
- `drop_cols.json`
- `split_report.csv`
- `class_stats.csv`, `skewness.csv`, `feature_hists.png`
- `correlated_groups.json`
- `shortcut_candidates.csv`
- `injected_feature_check.json`
- `sampling_config.json`

Repoya eklenmeyecekler: tüm `.parquet` dosyaları ve ham veri. Bunlar herkesin kendi bilgisayarında kalır. Aynı kod, aynı seed ve aynı dosya (sha256 `data_card.md` içinde) ile yeniden üretilebilirler.

## Yorum notu

Her veri seti için `results/eda/<set_adi>/notes.md`, en fazla yarım sayfa. Başlıklar şunlar:

```
# <set_adi>: yorum notu (<isim>)

## 1. Veri kalitesi
Tekrar ve çelişkili satır sayısı, inf ve NaN olan sütunlar. Beklenmedik bir şey var mı?

## 2. Sınıflar ve zaman
Dengesizlik, yetersiz sınıflar (split_report ok = False). Zaman grafiği mantıklı mı?
Veri birden fazla kayıt oturumundan mı oluşuyor? Train, val ve test hangi oturumlardan geliyor?

## 3. Şüpheli özellikler
shortcut_candidates.csv'de score > 0.95 olanlar: hem binary'de hem sınıf bazında
(kaç sınıfta şüpheli çıktığı). Hangileri literatürdeki artefaktlarla örtüşüyor,
hangileri yeni? Portlar şüpheli mi?

## 4. Uyarılar
Terminaldeki UYARI satırları ve ne anlama geldikleri.
--frac kullanıldıysa oranı ve nedeni (sayılar tam veriyle karşılaştırılamaz).

## 5. Toplantıda karar gerekenler
Ekipçe karar verilmesi gereken sorular (ör. şu sınıf çıkarılsın mı, şu sütun kimlik mi).
```

## Grup ek işleri (EDA_PLAN.md'deki maddeler)

- Ahmet: iki CICIDS2017 sürümü arasındaki fark tablosu (flow sayısı, değişen etiketler, Attempted, TCP appendix) ve özellik düzeyinde artefakt listesi. Kullanılan CICFlowMeter build'i Selim'e iletilir.
- Esad: saldırı eşleme tablosu (CIC2018 ↔ UNSW ve CICIDS2017 ↔ 5G-NIDD ↔ TII-SSRC-23).
- Selim: yeniden çıkarılan flow'ların sınıf sayılarının yayınlanmış dosyalarla karşılaştırması.
- **Selim, Plan B tarihi:** akış çıkarma ve etiketleme hafta 4 ortasına kadar bitmezse, yayınlanmış özellik dosyalarıyla `--time-col __row_order__` kullanılarak EDA çalıştırılır. Toplantıya her durumda sonuçla gelinir.

Bunlar `docs/` altına markdown olarak eklenir.

## Ortak shortcut aday tablosu (O3 çıktısı)

- Sorumlu: Selim (açıklama lideri; tabloyu ileride en çok o kullanacak)
- Girdi: 6 setin `shortcut_candidates.csv` dosyaları ve notlardaki 3. başlık
- Dosya: `docs/shortcut_candidates_all.csv`
- Sütunlar: `dataset, feature, scope, score, literatürde_var (evet/hayır + kaynak), karar (aday / kimlik / gerçek özellik)`
- `karar` sütunu toplantıda doldurulur.

## Toplantıda karar verilecekler

1. Yetersiz sınıflar (çıkarılsın mı, birleştirilsin mi; ör. UNSW Worms)
2. Attempted satırları modelde nasıl kullanılacak (keep, benign, drop)
3. `review_manually` sütunları kimlik mi, özellik mi (ör. UNSW `DNS_QUERY_ID`)
4. Çelişkili satırlar silinsin mi
5. inf ve NaN değerleri modelde nasıl doldurulacak
6. CIC2018 (ve gerekirse TII-SSRC-23) tam veriyle mi, örneklemle mi analiz edilecek; tam veri kimin bilgisayarında çalışacak
7. Birden fazla kayıt oturumu olan setlerde zaman bölmesi nasıl yorumlanacak (ör. UNSW: 22 Ocak ve 17–18 Şubat)
8. Ortak shortcut aday tablosunun `karar` sütunu
