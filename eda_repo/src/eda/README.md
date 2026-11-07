# Ortak EDA kodu (eda-v2)

6 veri setinin hepsi bu kodla ve aynı ayarlarla çalıştırılır. Kod kişisel olarak değiştirilmez. Değişiklik gerekirse PR açılır, `config.py` içindeki `VERSION` artırılır ve herkes kendi setlerini yeni sürümle yeniden çalıştırır. Tüm sayısal ayarlar `config.py` dosyasındadır.

## Kurulum

```
pip install -r requirements-eda.txt
python tests/test_eda_smoke.py smoke_out
```

Son satırda `SMOKE TEST OK` görünmelidir. Test, 6 veri setinin her biri için gerçek formatı taklit eden sentetik bir dosya üretip kodu üzerinde çalıştırır. pandas 2.2 ve 3.0 ile test edilmiştir.

## Çalıştırma (repo kökünden)

Her veri setinin hazır bir ayarı (preset) vardır. Etiket sütunu, benign etiketi, zaman sütunu, kaynak ve lisans bilgisi bu ayardan gelir.

| Grup | Sorumlu | Komut |
|---|---|---|
| A | Ahmet | `PYTHONPATH=src python -m eda --dataset cicids2017_orig --inputs data/raw/cicids2017_orig/*.csv --out results/eda/cicids2017_orig` |
| A | Ahmet | `PYTHONPATH=src python -m eda --dataset cicids2017_corrected --inputs data/raw/cicids2017_corrected/*.csv --out results/eda/cicids2017_corrected` |
| B | Esad | `PYTHONPATH=src python -m eda --dataset nf3_unsw_nb15 --inputs data/raw/groupB/NF-UNSW-NB15-v3.csv --out results/eda/nf3_unsw_nb15` |
| B | Esad | `PYTHONPATH=src python -m eda --dataset nf3_cse_cic_ids2018 --inputs data/raw/groupB/NF-CSE-CIC-IDS2018-v3.csv --out results/eda/nf3_cse_cic_ids2018 --frac 0.25` |
| C | Selim | `PYTHONPATH=src python -m eda --dataset 5g_nidd --inputs data/interim/5g_nidd/*.csv --out results/eda/5g_nidd` |
| C | Selim | `PYTHONPATH=src python -m eda --dataset tii_ssrc_23 --inputs data/interim/tii_ssrc_23/*.csv --out results/eda/tii_ssrc_23` |

Herhangi bir ayar komut satırından değiştirilebilir: `--label-col`, `--time-col`, `--benign-label`, `--extra-drop`, `--ampm-fix`, `--attempted`, `--frac`. Komut satırında verilen değer preset'teki değerin önüne geçer. Girdi olarak CSV veya parquet kabul edilir.

### Veri setine özel notlar

- **CICIDS2017 orijinal:** `TrafficLabelling` (GeneratedLabelledFlows) CSV'leri kullanılmalı. `MachineLearningCVE` dosyalarında Timestamp ve IP sütunları yok, kod 1. adımda durur. Timestamp'ler 12 saatlik ve AM/PM içermiyor (öğleden sonra 2, `2:05` olarak yazılı). `--ampm-fix auto` bunu kendisi algılar: AM/PM işareti yoksa ve hiçbir saat 13 veya üstü değilse, 1–7 arasındaki saatlere 12 ekler. Kaç satırın kaydırıldığı `summary.md` dosyasına yazılır. `label_timeline.png` grafiğinde öğleden sonraki saldırıların (Cuma DDoS/PortScan) öğleden sonra göründüğünü kontrol edin. Thursday WebAttacks dosyasındaki boş satırlar etiketsiz oldukları için otomatik çıkarılır.
- **CICIDS2017 düzeltilmiş:** `"<saldırı> - Attempted"` sınıfları için `--attempted keep|benign|drop` seçeneği var. Varsayılan `keep`: bu sınıflar ayrı sınıf olarak kalır, binary analizde saldırı sayılır. `Attempted Category` ve `id` sütunları otomatik çıkarılır. Kaynak URL preset'te boş, `--source-url` ile verin.
- **NF3 setleri:** `FLOW_START/END_MILLISECONDS` ve IP'ler çıkarılır, `*_IAT_*` özellikleri kalır. Zaman sütunu float32'ye çevrilmez (milisaniye hassasiyeti korunur). CIC2018 (yaklaşık 20M satır) 16 GB RAM'de önce `--frac 0.25` ile çalıştırılmalı. Kullanılan oran `data_card.md` ve `manifest.json` dosyalarına yazılır.
- **5G-NIDD ve TII-SSRC-23 (CICFlowMeter ile yeniden çıkarılmış):** Flow'lar EDA'dan önce etiketlenmiş olmalı. CICFlowMeter'ın yazdığı `NeedManualLabel` etiketi görülürse kod durur. Benign flow'lar `BENIGN` olarak etiketlenmeli. Büyük/küçük harf farkı (`Benign` gibi) otomatik eşlenir ve uyarı verilir.
- **Plan B (yayınlanmış özellik dosyaları):** Timestamp yoksa `--time-col __row_order__` verilir. Bu durumda dosyadaki satır sırası zaman yerine kullanılır ve raporda uyarı çıkar. Etiket sütunu `--label-col` ile seçilir. Diğer etiket sütunları (`Label`, `Traffic Type`, `Traffic Subtype`, `Attack Type`, `Attack Tool`) otomatik çıkarılır. Başka sütunlar `--extra-drop` ile çıkarılabilir.

## Çıktılar (`--out` klasörü)

| Adım | Dosya |
|---|---|
| 0 | `data_card.md` (grup, sorumlu, URL, sürüm, lisans, boyut, sha256, notlar) |
| 1 | `raw.parquet`, `load_info.json` |
| 2 | `quality_columns.csv`, `quality_summary.json` |
| 3 | `label_distribution.csv`, `label_bar.png`, `label_timeline.png` |
| 4 | `drop_cols.json` (`model_features` modele girecek özelliklerdir, `metadata` zaman ve etiket sütunlarıdır) |
| 5 | `split_report.csv`, `splits.parquet`, `clean.parquet` |
| 6 | `class_stats.csv`, `skewness.csv`, `feature_hists.png` |
| 7 | `correlated_groups.json` |
| 8 | `shortcut_candidates.csv` |
| 9 | `injected_feature.parquet`, `injected_feature_check.json` |
| 10 | `sampling_config.json`, `sample_index.parquet` |
| özet | `summary.md` (uyarılar dahil), `manifest.json` |

`clean.parquet` içindeki `row_id`, `splits.parquet`, `sample_index.parquet` ve `injected_feature.parquet` dosyalarındaki `row_id` ile eşleşir.

## Kurallar

- Etiketi boş olan satırlar yüklemede çıkarılır ve sayısı raporlanır.
- Tekrar eden satırlar (özellikler ve etiket aynı) bölmeden önce silinir. Çelişkili satırlar (özellikler aynı, etiket farklı) silinmez. `_conflicting` sütunuyla işaretlenir ve raporlanır.
- Bölme sınıf bazında ve zamana göre yapılır (70/15/15, aralarda küçük boşluk). Bir sınıfta bölmelerden biri `MIN_PER_SPLIT` altında kalırsa zaman blokları yöntemine geçilir. Yine yetmezse `split_report.csv` içinde `ok = False` olur, ekip karar verir.
- Zaman sütunu modelden çıkarılır ama bölme ve timeline için saklanır.
- Adım 6, 7 ve 8 sadece train üzerinde ve sınıf başına `ANALYSIS_CAP_PER_CLASS` satırlık bir örnekle çalışır.
- Kısayol skoru iki ölçünün büyüğüdür: ham AUROC (`max(a, 1-a)`) ve tek özellikli sığ karar ağacının 3 katlı AUROC'u. `score > 0.95` şüpheli sayılır.
- Port sütunları modelden çıkarılmaz, `port_candidates` olarak işaretlenir.
- `review_manually`: adı kimlik gibi görünen ama config'te listelenmeyen sütunlar. Ekip kontrol eder.
- **Sahte özellik (adım 9):** train ve val'de `INJECT_STRENGTH` (0.99) olasılıkla binary etikete eşittir. Test'te etiketten bağımsız ve aynı taban oranla üretilir. Böylece modelin bu özelliğe dayanıp dayanmadığı test performansından anlaşılır. `injected_feature_check.json` her bölmedeki uyumu gösterir. Train ve val'de uyum yaklaşık 0.99 olmalı. Test'te uyum etiketten bağımsızdır, yaklaşık `1 - 2p(1-p)` (p = saldırı payı).
- Örnekleme sadece train ve validation'a uygulanır. Test doğal sınıf oranında kalır.
