# CICIDS2017-Traffic-Analysis

## 项目名称

网络流量异常检测与安全分析平台

## 项目背景

本项目基于 CICIDS2017 公开入侵检测数据集，围绕网络流量分析、攻击类型识别、协议与端口画像、异常检测和 SOC 安全运营可视化展开，构建一个面向安全运营场景的流量分析平台。

项目重点不只是“训练一个分类模型”，而是模拟 SOC 分析视角，体现从数据清洗、攻击画像、SQL 分析、异常检测到 BI / Streamlit 看板展示的完整流程。

## 数据来源

说明：CICIDS2017 由 Canadian Institute for Cybersecurity 发布，包含正常流量和多种攻击流量，并提供用于机器学习的 CSV 流量特征文件。

推荐数据源：

1. 官方 CICIDS2017：[https://www.unb.ca/cic/datasets/ids-2017.html](https://www.unb.ca/cic/datasets/ids-2017.html)
2. Kaggle 镜像：搜索关键词 `CICIDS2017 MachineLearningCSV Kaggle`

需要下载：

- `MachineLearningCSV.zip`
- 或包含多个 CSV 的 CICIDS2017 数据包

下载后放到：

`D:\DataAnalysis\CICIDS2017-Traffic-Analysis\data\raw`

如果是 zip，请手动解压到 `data/raw`。


## 项目结构

```text
D:\DataAnalysis\CICIDS2017-Traffic-Analysis
├── data
│   ├── raw
│   ├── processed
│   └── sample
├── notebook
│   ├── 01_data_clean.ipynb
│   ├── 02_traffic_analysis.ipynb
│   └── 03_anomaly_detection.ipynb
├── sql
│   └── traffic_analysis.sql
├── dashboard
│   └── powerbi_dashboard_guide.md
├── streamlit
│   └── app.py
├── screenshots
├── report
│   └── project_summary.md
├── src
│   ├── data_clean.py
│   ├── feature_engineering.py
│   └── model_train.py
├── README.md
├── requirements.txt
└── .gitignore
```

## 分析内容

1. 数据清洗与字段标准化
2. 攻击类型分布分析
3. 正常/攻击流量占比分析
4. 协议分布分析
5. TOP 攻击端口分析
6. Isolation Forest 异常流量检测
7. SOC 安全运营驾驶舱

## 核心成果

- 基于 CICIDS2017 数据集完成网络流量数据清洗与分析
- 提取 80+ 网络流量特征字段
- 构建正常/攻击流量识别标签
- 完成攻击类型、协议分布、端口画像分析
- 使用 Isolation Forest 实现异常流量检测
- 使用 Power BI 和 Streamlit 搭建 SOC 风格安全分析看板

## 运行方式

1. 下载 CICIDS2017 MachineLearningCSV 数据
2. 解压到 `data/raw`
3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 数据清洗：

```bash
python src/data_clean.py
```

5. 启动 Notebook 分析：

```bash
jupyter notebook
```

6. 启动 Streamlit：

```bash
streamlit run streamlit/app.py
```

