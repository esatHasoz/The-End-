# Data card: tii_ssrc_23

- Group / owner: C / Selim
- Source URL: https://www.kaggle.com/datasets/daniaherzalla/tii-ssrc-23
- Version: published CICFlowMeter features (tii_ssrc_23.csv)
- License: see Kaggle page; cite Herzalla et al. 2023
- Feature family: cicflowmeter
- Label column: `Class`, benign label: `Benign`, time column: `Timestamp`
- Sampling at load: none
- Created: 2026-11-11T19:31:01+00:00
- EDA version: eda-v2
- Notes: About 8.6M flows. Flows must be labelled before EDA. Use BENIGN for benign flows. Plan B (published CSV): pass --label-col 'Traffic Type' or similar; the other label columns are removed automatically.

| file | size_bytes | sha256 |
|---|---|---|
| tii_published.parquet | 595,469,161 | d67c87eb4ae848d9a3af430da73e1bb1aceef2495d33bf461107afa6cf215e5f |
