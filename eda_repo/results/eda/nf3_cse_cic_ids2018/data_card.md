# Data card: nf3_cse_cic_ids2018

- Group / owner: B / Esad
- Source URL: https://rdm.uq.edu.au/files/4ac221b1-6bd6-42b1-bdf7-03f4fc7efb22
- Version: NetFlow v3 (Luay et al. 2025)
- License: Permitted Re-Use with Commercial Use Restriction (UQ RDM)
- Feature family: netflow_v3
- Label column: `Attack`, benign label: `Benign`, time column: `FLOW_START_MILLISECONDS`
- Sampling at load: none
- Created: 2026-11-07T13:45:33+00:00
- EDA version: eda-v2
- Notes: About 20M flows. Start with --frac 0.25 on a 16 GB machine.

| file | size_bytes | sha256 |
|---|---|---|
| NF-CICIDS2018-v3_frac0.1_seed42.csv | 422,220,527 | fa4e25966b9c6c54ec2b950d2b3bdb9b88598b8e5ced1dcf6fa4fa2647c8fd73 |

- Pre-sampling: 10% random sample of NF-CICIDS2018-v3.csv (20,115,529 flows, sha1 ddcad6d826b73a128a447a0189137efd6c8f70c9) made with awk srand(42), rand()<0.1 -> 2,011,291 flows. The table above lists the sample file. Full-data class counts: data/interim/NF-CICIDS2018-v3_full_class_counts.tsv and notes.md.
