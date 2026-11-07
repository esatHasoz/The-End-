# Ortak EDA kodu (eda-v1)

6 veri setinin hepsi bu kodla, aynı ayarlarla çalıştırılır. Kod kişisel olarak değiştirilmez; değişiklik PR ile girer ve herkes kendi setlerini yeni sürümle yeniden çalıştırır. Tüm ayarlar `config.py` içindedir.

## Kurulum

```
pip install -r requirements-eda.txt
python tests/test_eda_smoke.py smoke_out
```

Son satırda `SMOKE TEST OK` görünmelidir.

## Çalıştırma

Repo kökünden:

```
PYTHONPATH=src python -m eda --name <set_adi> --family <cicflowmeter|netflow_v3> --inputs <dosya1.csv> [dosya2.csv ...] --out results/eda/<set_adi> --source-url <url> --version <surum> --license <lisans> --inject
```

Örnekler:

```
PYTHONPATH=src python -m eda --name nf3_unsw_nb15 --family netflow_v3 --inputs data/raw/NF-UNSW-NB15-v3.csv --out results/eda/nf3_unsw_nb15 --inject

PYTHONPATH=src python -m eda --name cicids2017_orig --family cicflowmeter --inputs data/raw/cicids2017/*.csv --out results/eda/cicids2017_orig --inject
```

Çok büyük setlerde (NF3-CSE-CIC-IDS2018) yüklemede örnekleme için `--frac 0.25` eklenebilir; kullanılan oran `data_card.md` ve `manifest.json` dosyalarına yazılır.

Sütun adları aileden farklıysa `--label-col`, `--time-col`, `--benign-label` ile verilir. Ek olarak çıkarılacak sütunlar `--extra-drop` ile verilir.

## Çıktılar (`--out` klasörü)

| Adım | Dosya |
|---|---|
| 0 | `data_card.md` (URL, sürüm, lisans, boyut, sha256) |
| 1 | `raw.parquet`, `load_info.json` |
| 2 | `quality_columns.csv`, `quality_summary.json` |
| 3 | `label_distribution.csv`, `label_bar.png`, `label_timeline.png` |
| 4 | `drop_cols.json` (`model_features` modele girecek özelliklerdir) |
| 5 | `split_report.csv`, `splits.parquet`, `clean.parquet` |
| 6 | `class_stats.csv`, `skewness.csv`, `feature_hists.png` |
| 7 | `correlated_groups.json` |
| 8 | `shortcut_candidates.csv` |
| 9 | `injected_feature.parquet` (`--inject` ile) |
| 10 | `sampling_config.json`, `sample_index.parquet` |
| özet | `summary.md`, `manifest.json` |

`clean.parquet` içindeki `row_id`, `splits.parquet`, `sample_index.parquet` ve `injected_feature.parquet` dosyalarındaki `row_id` ile eşleşir.

## Kurallar

- Tekrar eden satırlar (özellikler + etiket aynı) bölmeden önce silinir. Çelişkili satırlar (özellikler aynı, etiket farklı) silinmez, `_conflicting` sütunuyla işaretlenir ve raporlanır.
- Bölme sınıf bazında ve zamana göredir (70/15/15, aralarda küçük boşluk). Bir sınıfta bölmelerden biri `MIN_PER_SPLIT` altında kalırsa zaman blokları yöntemine geçilir; yine yetmezse `split_report.csv` içinde `ok = False` olur ve ekipçe karar verilir.
- Adım 6, 7 ve 8 sadece train üzerinde, sınıf başına `ANALYSIS_CAP_PER_CLASS` satırlık örnekte çalışır.
- Kısayol skoru iki ölçünün büyüğüdür: ham AUROC (tek yönlü ayrım) ve tek özellikli sığ karar ağacının 3 katlı AUROC'u (ortada kalan değerleri de yakalar, ör. saldırıların hep port 80 kullanması). `score > 0.95` şüphelidir.
- Port sütunları modelden çıkarılmaz, `port_candidates` olarak işaretlenir.
- `review_manually` listesindeki sütunlar adına bakılarak işaretlenmiştir (ör. `MIN_IP_PKT_LEN`); kimlik mi özellik mi olduğuna ekip karar verir.
- Örnekleme sadece train ve validation'a uygulanır, test doğal sınıf oranında kalır.
