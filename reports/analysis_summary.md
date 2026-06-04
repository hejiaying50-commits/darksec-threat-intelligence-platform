# DarkSec Threat Intelligence Analysis Summary

## Dataset Overview
- Total rows: 78,247
- Total columns: 80
- Label column detected: `Label`
- Remaining missing values after cleaning: 0
- Duplicate rows after cleaning: 0

## Normal vs Attack Traffic
- Normal traffic: 63,667
- Attack traffic: 14,580

## Attack Type Distribution
| Label | count |
| --- | --- |
| BENIGN | 63667 |
| DDoS | 5759 |
| PortScan | 5460 |
| DoS Hulk | 2623 |
| FTP-Patator | 152 |
| DoS GoldenEye | 115 |
| SSH-Patator | 112 |
| Bot | 87 |
| Web Attack � Brute Force | 84 |
| DoS slowloris | 76 |
| DoS Slowhttptest | 73 |
| Web Attack � XSS | 38 |
| Web Attack � Sql Injection | 1 |

## Top 10 High-Risk Attack Types
| Label | count |
| --- | --- |
| BENIGN | 63667 |
| DDoS | 5759 |
| PortScan | 5460 |
| DoS Hulk | 2623 |
| FTP-Patator | 152 |
| DoS GoldenEye | 115 |
| SSH-Patator | 112 |
| Bot | 87 |
| Web Attack � Brute Force | 84 |
| DoS slowloris | 76 |

## Correlation Highlights
- `Total Fwd Packets` vs `Subflow Fwd Packets`: correlation = 1.000
- `Total Backward Packets` vs `Subflow Bwd Packets`: correlation = 1.000
- `Total Length of Fwd Packets` vs `Subflow Fwd Bytes`: correlation = 1.000
- `Fwd Packet Length Mean` vs `Avg Fwd Segment Size`: correlation = 1.000
- `Bwd Packet Length Mean` vs `Avg Bwd Segment Size`: correlation = 1.000
- `Fwd PSH Flags` vs `SYN Flag Count`: correlation = 1.000
- `Fwd URG Flags` vs `CWE Flag Count`: correlation = 1.000
- `Fwd Header Length` vs `Fwd Header Length.1`: correlation = 1.000
- `RST Flag Count` vs `ECE Flag Count`: correlation = 1.000
- `Total Length of Bwd Packets` vs `Subflow Bwd Bytes`: correlation = 1.000

## Key Feature Statistics
| index | Destination Port | Flow Duration | Total Fwd Packets | Total Backward Packets | Total Length of Fwd Packets |
| --- | --- | --- | --- | --- | --- |
| count | 78247.0 | 78247.0 | 78247.0 | 78247.0 | 78247.0 |
| mean | 8332.133 | 13089733.692 | 5.869 | 5.746 | 528.743 |
| std | 18403.995 | 31789329.791 | 41.357 | 49.134 | 3106.618 |
| min | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 |
| 25% | 53.0 | 160.0 | 1.0 | 1.0 | 12.0 |
| 50% | 80.0 | 31850.0 | 2.0 | 2.0 | 58.0 |
| 75% | 465.0 | 1877510.5 | 4.0 | 4.0 | 135.0 |
| max | 65520.0 | 119999909.0 | 8304.0 | 7879.0 | 343213.0 |

## Core Conclusions
- The dataset contains both benign traffic and multiple intrusion categories suitable for SOC-style threat analytics.
- A binary Normal/Attack view is appropriate for high-level monitoring, while the original labels support detailed attack attribution.
- Strongly correlated features may indicate redundant measurements and can guide future feature selection or model compression.
- The cleaned dataset is ready for downstream training and dashboard exploration.