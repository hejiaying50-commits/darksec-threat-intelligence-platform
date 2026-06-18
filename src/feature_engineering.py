"""CICIDS2017 特征处理工具。"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


ATTACK_CATEGORY_RULES = {
    "benign": "Benign",
    "dos": "DoS",
    "ddos": "DDoS",
    "portscan": "PortScan",
    "bot": "Bot",
    "ftp-patator": "BruteForce",
    "ssh-patator": "BruteForce",
    "bruteforce": "BruteForce",
    "brute force": "BruteForce",
    "web attack": "WebAttack",
    "sql injection": "WebAttack",
    "xss": "WebAttack",
    "infiltration": "Infiltration",
    "heartbleed": "Heartbleed",
}

PROTOCOL_MAP = {6: "TCP", 17: "UDP", 1: "ICMP"}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """标准化字段名，便于后续 SQL / BI / Python 统一处理。"""
    renamed = {
        col: col.strip().replace(" ", "_").replace("/", "_per_")
        for col in df.columns
    }
    df = df.rename(columns=renamed)
    return df


def infer_label_column(df: pd.DataFrame) -> str:
    for candidate in ["Label", "label"]:
        if candidate in df.columns:
            return candidate
    raise KeyError("未找到 Label 字段，请检查原始 CICIDS2017 CSV 文件。")


def find_column(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    normalized = {col.lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]
    return None


def map_attack_category(label: str) -> str:
    if pd.isna(label):
        return "Other"
    raw = str(label).strip().lower()
    for keyword, category in ATTACK_CATEGORY_RULES.items():
        if keyword in raw:
            return category
    return "Other"


def map_protocol_name(protocol_value: object) -> str:
    try:
        protocol_num = int(float(protocol_value))
    except (TypeError, ValueError):
        return "Other"
    return PROTOCOL_MAP.get(protocol_num, "Other")


def enrich_security_fields(df: pd.DataFrame) -> pd.DataFrame:
    """补充 SOC 分析常用标签字段。"""
    label_col = infer_label_column(df)
    df[label_col] = df[label_col].astype(str).str.strip()
    df["is_attack"] = df[label_col].str.lower().ne("benign").astype(int)
    df["attack_category"] = df[label_col].apply(map_attack_category)

    protocol_col = find_column(df, ["Protocol"])
    if protocol_col:
        df["protocol_name"] = df[protocol_col].apply(map_protocol_name)
    else:
        # 当前这份 CICIDS2017 MachineLearningCSV 不一定包含 Protocol 字段
        # 没有原始协议编号时不应伪造 TCP/UDP/ICMP 结论，因此标记为 Unknown
        df["protocol_name"] = "Unknown"
    return df


def clean_numeric_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """替换无穷值并删除缺失/重复数据。"""
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()
    df = df.drop_duplicates()
    return df
