# DarkSec 威胁情报分析平台

DarkSec Threat Intelligence Platform 是一个基于 CICIDS2017 / Network Intrusion Dataset 构建的端到端网络安全数据分析项目。项目覆盖数据清洗、探索性分析、攻击分类建模，以及基于 Streamlit 的 SOC 安全运营大屏展示。

## 1. 项目介绍

该项目定位为一个适合作品集展示、课程汇报和简历包装的真实风格网络安全分析平台，帮助使用者快速理解：

- 网络流量总体规模与攻击趋势
- 正常流量与恶意流量分布情况
- 主要入侵攻击类型构成
- 异常流量相关关键特征模式
- 基于机器学习的攻击识别能力
- 面向 SOC 场景的安全态势可视化

## 2. 数据来源说明

推荐数据来源：

- Kaggle：CICIDS2017 / Network Intrusion Dataset
- 下载后将一个或多个 CSV 文件放入 `data/raw/` 目录即可

该数据集常见标签包括 `BENIGN`，以及多种攻击类型，例如 DoS、PortScan、Bot、Brute Force、Web Attack、DDoS 等，具体以实际下载版本为准。

为了便于项目开箱即用，仓库中额外提供了一份小型演示数据：

- `data/raw/sample_network_data.csv`

即使你还没有下载 Kaggle 全量数据，也可以先直接跑通整个项目流程。

## 3. 项目功能

- 自动读取 `data/raw/` 下全部 CSV 文件
- 自动清理字段名前后空格
- 删除重复值
- 处理 `NaN`、`Infinity`、`-Infinity`
- 自动识别标签列，例如 `Label`、`Attack`、`attack_type`
- 输出清洗后的数据集
- 自动生成 EDA 分析摘要报告
- 支持二分类：
  - `Normal`
  - `Attack`
- 支持按原始攻击类型进行多分类
- 使用 `RandomForestClassifier` 训练基础模型
- 环境支持时自动加入 `XGBoost`
- 使用 `Joblib` 保存模型和特征列
- 提供 Streamlit SOC 风格安全态势大屏
- 支持上传 CSV 并进行攻击预测

## 4. 项目结构

```text
DarkSec-Threat-Intel/
|-- data/
|   |-- raw/
|   `-- cleaned/
|-- notebooks/
|   `-- 01_eda_analysis.ipynb
|-- src/
|   |-- data_cleaning.py
|   |-- feature_engineering.py
|   |-- train_model.py
|   `-- evaluate_model.py
|-- dashboard/
|   `-- streamlit_app.py
|-- models/
|   |-- attack_classifier.pkl
|   `-- feature_columns.pkl
|-- reports/
|   |-- analysis_summary.md
|   |-- analysis_summary_zh.md
|   |-- model_evaluation.md
|   `-- model_evaluation_zh.md
|-- README.md
|-- README_CN.md
`-- requirements.txt
```

## 5. 安装依赖方法

```bash
pip install -r requirements.txt
```

## 6. 数据放置方法

1. 保持项目目录结构不变。
2. 从 Kaggle 下载 CICIDS2017 / Network Intrusion Dataset 的 CSV 文件。
3. 将数据文件放到以下目录：

```text
data/raw/
```

示例：

```text
data/raw/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
data/raw/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
...
```

## 7. 数据清洗命令

```bash
python src/data_cleaning.py
```

如果数据量较大，可使用采样模式：

```bash
python src/data_cleaning.py --sample-size 50000
```

输出结果：

- 清洗后数据：`data/cleaned/cleaned_dataset.csv`
- 分析报告：`reports/analysis_summary.md`

## 8. 模型训练命令

```bash
python src/train_model.py
```

可选参数示例：

```bash
python src/train_model.py --sample-size 100000 --test-size 0.2 --random-state 42
```

输出结果：

- `models/attack_classifier.pkl`
- `models/feature_columns.pkl`
- `reports/model_evaluation.md`
- `reports/model_metrics.json`

## 9. 模型评估命令

```bash
python src/evaluate_model.py
```

## 10. 启动 Streamlit 大屏

```bash
streamlit run dashboard/streamlit_app.py
```

## 11. 可视化大屏说明

- SOC 风格安全态势界面
- 顶部 KPI 指标卡片
- 攻击类型饼图
- 攻击类型柱状图
- 关键特征分布图
- CSV 上传预测模块
- 对缺失字段和字段不一致情况进行异常处理，避免直接崩溃

## 12. 项目截图占位说明

运行完成后可以将截图保存到 `docs/` 目录，例如：

- `docs/dashboard-home.png`
- `docs/attack-distribution.png`
- `docs/prediction-panel.png`

然后在 README 中引用：

```markdown
![平台首页](docs/dashboard-home.png)
![攻击类型分布](docs/attack-distribution.png)
![预测模块](docs/prediction-panel.png)
```

## 13. 简历项目描述

可直接用于中文简历的项目描述如下：

> 基于 CICIDS2017 网络入侵检测数据集，使用 Python、Pandas、Scikit-learn、Plotly 与 Streamlit 搭建网络安全威胁情报分析平台，完成原始流量数据清洗、攻击趋势分析、二分类与多分类攻击识别建模，并构建 SOC 风格交互式安全态势大屏，实现网络攻击监测与 CSV 批量预测。

## 14. 说明与建议

- `xgboost` 为增强选项，若本地环境不支持，训练流程会自动回退到 `RandomForest`
- 默认保存的主模型面向多分类预测，更适合威胁情报细粒度分析
- 若真实数据集较大，建议使用 `--sample-size` 控制实验规模，降低内存压力

## 15. 快速开始

```bash
pip install -r requirements.txt
python src/data_cleaning.py
python src/train_model.py
streamlit run dashboard/streamlit_app.py
```
