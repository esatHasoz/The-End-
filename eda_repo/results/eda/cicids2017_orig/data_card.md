# Data card: cicids2017_orig

- Group / owner: A / Ahmet
- Source URL: https://www.unb.ca/cic/datasets/ids-2017.html
- Version: GeneratedLabelledFlows / TrafficLabelling CSVs
- License: CIC/UNB dataset terms; cite Sharafaldin et al. 2018
- Feature family: cicflowmeter
- Label column: `Label`, benign label: `BENIGN`, time column: `Timestamp`
- Sampling at load: none
- Created: 2026-11-07T14:10:01+00:00
- EDA version: eda-v2
- Notes: Use the TrafficLabelling CSVs. MachineLearningCVE CSVs have no Timestamp or IP columns and will stop at step 1. Timestamps use a 12-hour clock without AM/PM; ampm_fix=auto detects this and shifts hours 1-7 by 12.

| file | size_bytes | sha256 |
|---|---|---|
| Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv | 96,101,069 | 1f779b4f0d78f9225554c4de53b5a2c07912b60dcd136ee4c5c1d0d2496b7cc4 |
| Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv | 101,874,777 | 7e2ddaa80a5849ba629463296b6128436c161b4a32e8034bb5beae06b0c45e08 |
| Friday-WorkingHours-Morning.pcap_ISCX.csv | 75,386,737 | c061cd98f39d8054aeaed6244a5129a20b3985983d0d022b860ae8aa07fe8d21 |
| Monday-WorkingHours.pcap_ISCX.csv | 268,649,908 | 96f26aea87d513073769b48ce204c2921791149e1c6225f7db65a3fed7973820 |
| Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv | 108,723,183 | d74238e054023c8bd4d8056650463cadb25c100fb0e26ebd4272c07b5c022c4b |
| Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv | 92,030,223 | e3deaff483d18b53b100a441dff9b8919416df8876b4edcc0f0d1e4bf48397d0 |
| Tuesday-WorkingHours.pcap_ISCX.csv | 174,696,560 | ae9c88e10c41a8eb1ff454ae98bc513454925097d0b0b57180f94e79de445815 |
| Wednesday-workingHours.pcap_ISCX.csv | 285,642,925 | ed538e85b84181e8897dedb3d37d365982f44b27eccd67c477581a8b65f3d170 |
