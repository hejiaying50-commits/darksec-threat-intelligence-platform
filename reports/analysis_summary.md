# DarkSec Threat Intelligence Analysis Summary

## Dataset Overview
- Total rows: 20
- Total columns: 9
- Label column detected: `Label`
- Remaining missing values after cleaning: 0
- Duplicate rows after cleaning: 0

## Normal vs Attack Traffic
- Normal traffic: 5
- Attack traffic: 15

## Attack Type Distribution
| Label | count |
| --- | --- |
| BENIGN | 5 |
| DDoS | 3 |
| PortScan | 3 |
| Bot | 3 |
| FTP-Patator | 3 |
| SSH-Patator | 3 |

## Top 10 High-Risk Attack Types
| Label | count |
| --- | --- |
| BENIGN | 5 |
| DDoS | 3 |
| PortScan | 3 |
| Bot | 3 |
| FTP-Patator | 3 |
| SSH-Patator | 3 |

## Correlation Highlights
- `Flow Duration` vs `Total Fwd Packets`: correlation = 0.996
- `Flow Bytes/s` vs `Packet Length Mean`: correlation = 0.994
- `Total Fwd Packets` vs `Flow Bytes/s`: correlation = 0.990
- `Flow Duration` vs `Flow Bytes/s`: correlation = 0.990
- `Flow Duration` vs `Packet Length Mean`: correlation = 0.984
- `Total Fwd Packets` vs `Packet Length Mean`: correlation = 0.984
- `Flow Duration` vs `Total Backward Packets`: correlation = 0.977
- `Total Backward Packets` vs `Packet Length Mean`: correlation = 0.976
- `Total Backward Packets` vs `Flow Bytes/s`: correlation = 0.965
- `Total Fwd Packets` vs `Total Backward Packets`: correlation = 0.962

## Key Feature Statistics
| index | Flow Duration | Total Fwd Packets | Total Backward Packets | Flow Bytes/s | Flow Packets/s |
| --- | --- | --- | --- | --- | --- |
| count | 20.0 | 20.0 | 20.0 | 20.0 | 20.0 |
| mean | 915.75 | 36.0 | 24.05 | 2940.94 | 74.7 |
| std | 838.685 | 33.862 | 25.777 | 2367.439 | 27.439 |
| min | 90.0 | 4.0 | 2.0 | 980.1 | 52.5 |
| 25% | 527.5 | 16.75 | 10.75 | 1800.425 | 58.9 |
| 50% | 697.5 | 25.5 | 15.5 | 2033.2 | 67.1 |
| 75% | 877.5 | 38.5 | 21.25 | 3018.825 | 69.825 |
| max | 3000.0 | 120.0 | 88.0 | 8600.2 | 142.8 |

## Core Conclusions
- The dataset contains both benign traffic and multiple intrusion categories suitable for SOC-style threat analytics.
- A binary Normal/Attack view is appropriate for high-level monitoring, while the original labels support detailed attack attribution.
- Strongly correlated features may indicate redundant measurements and can guide future feature selection or model compression.
- The cleaned dataset is ready for downstream training and dashboard exploration.