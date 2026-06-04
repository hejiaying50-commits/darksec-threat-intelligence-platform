# DarkSec Threat Intelligence Platform

DarkSec Threat Intelligence Platform is a portfolio-ready cybersecurity analytics project built on the CICIDS2017 / Network Intrusion Dataset. It combines data cleaning, exploratory threat analysis, machine learning-based attack classification, and a Streamlit-powered SOC dashboard for security posture monitoring and interactive prediction.

## Project Introduction

This project is designed to simulate a practical threat intelligence workflow for network security analysis. It helps users explore attack traffic patterns, identify high-risk categories, compare benign versus malicious flows, and operationalize model predictions in a dashboard environment.

## Project Architecture

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
|-- reports/
|-- README.md
`-- requirements.txt
```

## Tech Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Plotly
- Streamlit
- Joblib
- Matplotlib

## Dataset Source

- Kaggle: CICIDS2017 / Network Intrusion Dataset
- Place the downloaded CSV files into `data/raw/`

The repository is prepared for CICIDS-style traffic labels such as `BENIGN`, `DDoS`, `PortScan`, `Bot`, `FTP-Patator`, and `SSH-Patator`.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Put one or more dataset CSV files into `data/raw/`
2. Run data cleaning
3. Train the model
4. Launch the dashboard

### Data Cleaning

```bash
python src/data_cleaning.py
```

Optional sampling mode:

```bash
python src/data_cleaning.py --sample-size 50000
```

### Model Training

```bash
python src/train_model.py
```

### Model Evaluation

```bash
python src/evaluate_model.py
```

## Streamlit Launch

```bash
streamlit run dashboard/streamlit_app.py
```

## Screenshot Location

Recommended screenshot directory:

- `docs/dashboard-home.png`
- `docs/attack-distribution.png`
- `docs/prediction-panel.png`

After adding screenshots, reference them in this README for a stronger GitHub presentation.

## Project Highlights

- Automatically reads all CSV files from `data/raw/`
- Cleans whitespace, duplicates, missing values, and infinite values
- Detects label columns automatically
- Supports both binary and multi-class classification
- Uses RandomForest as a robust baseline and XGBoost when available
- Saves reusable model artifacts with Joblib
- Provides a SOC-style Streamlit dashboard with KPI cards, charts, and CSV upload prediction
- Includes defensive error handling for schema mismatch during inference

## Resume Project Description

> Built a cybersecurity threat intelligence analytics platform based on the CICIDS2017 intrusion detection dataset using Python, Pandas, Scikit-learn, Plotly, and Streamlit. Implemented automated data cleaning, threat trend analysis, binary and multi-class attack classification, and a SOC-style interactive dashboard for network attack monitoring and CSV-based prediction.
