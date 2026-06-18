# SOC安全运营分析驾驶舱

## 1. 看板目标

本项目的 Power BI 看板不是普通的分类结果展示页，而是按照 SOC 安全运营场景设计，强调攻击画像、协议风险、端口风险、异常检测辅助研判与高层汇报展示。

## 2. 数据准备

先执行以下步骤：

1. 下载 CICIDS2017 MachineLearningCSV 数据集。
2. 解压后的 CSV 放入 `D:\DataAnalysis\CICIDS2017-Traffic-Analysis\data\raw`
3. 运行：

```bash
python src/data_clean.py
```

4. 再运行 Notebook：

```bash
jupyter notebook
```

建议先执行：

- `notebook/02_traffic_analysis.ipynb`
- `notebook/03_anomaly_detection.ipynb`

这样会生成 Power BI 可直接导入的数据文件：

- `data/processed/attack_distribution.csv`
- `data/processed/protocol_distribution.csv`
- `data/processed/top_attack_ports.csv`
- `data/processed/feature_summary.csv`
- `data/processed/anomaly_detection_result.csv`

## 3. Power BI 导入建议

在 Power BI Desktop 中通过“获取数据 -> 文本/CSV”导入以上文件。若需要总览 KPI，也可以额外导入：

- `data/sample/cicids2017_sample.csv`

## 4. 页面设计

### 页面1：安全运营总览

看板名称：`SOC安全运营分析驾驶舱`

KPI 卡片建议：

- 总流量数
- 攻击流量数
- 正常流量数
- 攻击占比
- 异常检测数量

建议补充：

- 切片器：`attack_category`
- 切片器：`protocol_name`

### 页面2：攻击类型分布

图表建议：

- 柱状图：`attack_category` vs `count`
- 饼图：正常 vs 攻击

目的：

- 展示主要攻击类别
- 区分基线正常流量与异常攻击流量

### 页面3：协议与端口分析

图表建议：

- 协议分布柱状图：`protocol_name` vs `count`
- TOP20 攻击端口条形图：`destination_port` vs `count`

目的：

- 识别攻击主要承载协议
- 定位高风险目的端口

### 页面4：异常检测结果

图表建议：

- 异常/正常检测数量柱状图
- 异常检测混淆矩阵热力图
- 异常流量样本表

建议展示字段：

- `Label`
- `attack_category`
- `protocol_name`
- `Destination_Port`
- `anomaly_score`
- `anomaly_pred`

### 页面5：安全分析结论

建议用文本框展示：

- 主要攻击类型
- 高风险端口
- 攻击占比
- 模型检测效果
- SOC 研判建议

## 5. DAX 指标建议

```DAX
Total Traffic = COUNTROWS(cicids2017_sample)
Attack Traffic = CALCULATE(COUNTROWS(cicids2017_sample), cicids2017_sample[is_attack] = 1)
Benign Traffic = CALCULATE(COUNTROWS(cicids2017_sample), cicids2017_sample[is_attack] = 0)
Attack Ratio = DIVIDE([Attack Traffic], [Total Traffic], 0)
Anomaly Count = CALCULATE(COUNTROWS(anomaly_detection_result), anomaly_detection_result[anomaly_pred] = 1)
```

## 6. 可视化风格建议

- 背景色：深色系
- 主色：蓝青色 + 橙红色
- 攻击流量：红色或橙色
- 正常流量：蓝色或绿色
- 标题风格：偏 SOC 控制台、驾驶舱风格

## 7. 截图要求

最终手动截图后，请放入：

- `screenshots/dashboard.png`
- `screenshots/attack_distribution.png`
- `screenshots/top_attack_ports.png`
- `screenshots/anomaly_result.png`

## 8. 展示建议

面试演示时可以按以下顺序介绍：

1. 先讲 CICIDS2017 数据清洗流程
2. 再讲攻击类型、协议、端口画像
3. 然后讲 Isolation Forest 如何发现未知异常流量
4. 最后展示 Power BI 与 Streamlit 双看板能力
