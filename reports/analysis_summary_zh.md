# DarkSec 威胁情报分析摘要

## 数据集概览
- 总样本数：20
- 总字段数：9
- 自动识别标签列：`Label`
- 清洗后剩余缺失值数量：0
- 清洗后重复记录数量：0

## 正常流量与攻击流量
- 正常流量：5
- 攻击流量：15

## 攻击类型分布
| 标签 | 数量 |
| --- | --- |
| BENIGN | 5 |
| DDoS | 3 |
| PortScan | 3 |
| Bot | 3 |
| FTP-Patator | 3 |
| SSH-Patator | 3 |

## Top 10 高风险攻击类型
| 标签 | 数量 |
| --- | --- |
| BENIGN | 5 |
| DDoS | 3 |
| PortScan | 3 |
| Bot | 3 |
| FTP-Patator | 3 |
| SSH-Patator | 3 |

## 相关性分析亮点
- `Flow Duration` 与 `Total Fwd Packets` 的相关系数为 `0.996`
- `Flow Bytes/s` 与 `Packet Length Mean` 的相关系数为 `0.994`
- `Total Fwd Packets` 与 `Flow Bytes/s` 的相关系数为 `0.990`
- `Flow Duration` 与 `Flow Bytes/s` 的相关系数为 `0.990`
- `Flow Duration` 与 `Packet Length Mean` 的相关系数为 `0.984`
- `Total Fwd Packets` 与 `Packet Length Mean` 的相关系数为 `0.984`
- `Flow Duration` 与 `Total Backward Packets` 的相关系数为 `0.977`
- `Total Backward Packets` 与 `Packet Length Mean` 的相关系数为 `0.976`
- `Total Backward Packets` 与 `Flow Bytes/s` 的相关系数为 `0.965`
- `Total Fwd Packets` 与 `Total Backward Packets` 的相关系数为 `0.962`

## 关键特征统计
| 指标 | Flow Duration | Total Fwd Packets | Total Backward Packets | Flow Bytes/s | Flow Packets/s |
| --- | --- | --- | --- | --- | --- |
| count | 20.0 | 20.0 | 20.0 | 20.0 | 20.0 |
| mean | 915.75 | 36.0 | 24.05 | 2940.94 | 74.7 |
| std | 838.685 | 33.862 | 25.777 | 2367.439 | 27.439 |
| min | 90.0 | 4.0 | 2.0 | 980.1 | 52.5 |
| 25% | 527.5 | 16.75 | 10.75 | 1800.425 | 58.9 |
| 50% | 697.5 | 25.5 | 15.5 | 2033.2 | 67.1 |
| 75% | 877.5 | 38.5 | 21.25 | 3018.825 | 69.825 |
| max | 3000.0 | 120.0 | 88.0 | 8600.2 | 142.8 |

## 核心结论
- 数据集中同时包含正常流量和多种攻击流量，适合用于构建网络安全威胁情报分析平台。
- 从监控视角看，将流量分为 `Normal` 与 `Attack` 的二分类方式，适合用于高层安全态势展示。
- 从分析视角看，保留原始攻击标签进行多分类，更适合识别具体攻击类型与威胁归因。
- 多个关键数值特征之间存在较强相关性，可为后续特征筛选、降维与模型压缩提供依据。
- 当前清洗后的数据已经可以直接用于建模训练与安全大屏分析。
