# Data card: 5g_nidd

- Group / owner: C / Selim
- Source URL: https://etsin.fairdata.fi/dataset/9d13ef28-2ca7-44b0-9950-225359afac65
- Version: published Argus features (Combined.csv)
- License: CC BY 4.0
- Feature family: cicflowmeter
- Label column: `Class`, benign label: `Benign`, time column: `__row_order__`
- Sampling at load: none
- Created: 2026-11-11T19:49:42+00:00
- EDA version: eda-v2
- Notes: Flows must be labelled before EDA (CICFlowMeter writes 'NeedManualLabel'). Use BENIGN for benign flows. Plan B (published Argus features): --time-col __row_order__ and drop the extra label columns with --extra-drop.

| file | size_bytes | sha256 |
|---|---|---|
| 5g_nidd_published.parquet | 46,262,033 | 988daadd1bd3cfa411effa1fcc52543a1c1a2963093a2acc15640f00f19d3eab |
