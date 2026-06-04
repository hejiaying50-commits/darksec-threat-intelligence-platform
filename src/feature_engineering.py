"""Utility functions for cleaning, label handling, feature preparation, and reporting."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

LABEL_CANDIDATES = [
    "label",
    "labels",
    "attack",
    "attack_type",
    "attacktype",
    "class",
    "target",
    "category",
]

NORMAL_LABELS = {"benign", "normal", "normaltraffic", "normal_traffic"}


def ensure_directories() -> None:
    """Create key project directories if they do not exist."""
    for directory in [DATA_RAW_DIR, DATA_CLEANED_DIR, MODELS_DIR, REPORTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def markdown_table_from_frame(df: pd.DataFrame) -> str:
    """Render a small markdown table without requiring optional dependencies."""
    if df.empty:
        return "No data available."

    headers = [str(column) for column in df.columns]
    separator = ["---"] * len(headers)
    rows = ["| " + " | ".join(headers) + " |", "| " + " | ".join(separator) + " |"]

    for _, row in df.iterrows():
        values = [str(value) for value in row.tolist()]
        rows.append("| " + " | ".join(values) + " |")

    return "\n".join(rows)


def read_and_concat_csvs(input_dir: Path, sample_size: int | None = None) -> pd.DataFrame:
    """Read all CSV files from a directory and concatenate them safely."""
    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files were found in '{input_dir}'. Please place CICIDS2017 CSV files there."
        )

    frames: list[pd.DataFrame] = []
    for csv_file in csv_files:
        frame = pd.read_csv(csv_file, low_memory=False)
        frame.columns = [str(column).strip() for column in frame.columns]

        if sample_size is not None and len(frame) > sample_size:
            frame = frame.sample(n=sample_size, random_state=42)

        frame["source_file"] = csv_file.name
        frames.append(frame)

    return pd.concat(frames, ignore_index=True)


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from column names and deduplicate collisions."""
    cleaned_columns: list[str] = []
    seen: dict[str, int] = {}
    for column in df.columns:
        base_name = str(column).strip()
        if base_name not in seen:
            seen[base_name] = 0
            cleaned_columns.append(base_name)
        else:
            seen[base_name] += 1
            cleaned_columns.append(f"{base_name}_{seen[base_name]}")

    output = df.copy()
    output.columns = cleaned_columns
    return output


def detect_label_column(df: pd.DataFrame) -> str:
    """Automatically detect the target label column from common naming patterns."""
    lowercase_map = {column.lower(): column for column in df.columns}

    for candidate in LABEL_CANDIDATES:
        if candidate in lowercase_map:
            return lowercase_map[candidate]

    for column in df.columns:
        lowered = column.lower()
        if "label" in lowered or "attack" in lowered or lowered.endswith("class"):
            return column

    raise ValueError(
        "Unable to detect a label column. Expected names like Label, Attack, attack_type, class, or target."
    )


def clean_dataset(df: pd.DataFrame, label_column: str | None = None) -> tuple[pd.DataFrame, str]:
    """Clean duplicate rows, infinities, NaNs, and label formatting."""
    cleaned = normalize_column_names(df)
    detected_label = label_column or detect_label_column(cleaned)

    cleaned = cleaned.drop_duplicates().copy()
    cleaned = cleaned.replace([np.inf, -np.inf], np.nan)

    for column in cleaned.columns:
        if cleaned[column].dtype == object:
            cleaned[column] = cleaned[column].astype(str).str.strip()
            cleaned[column] = cleaned[column].replace({"nan": np.nan, "None": np.nan, "": np.nan})

    numeric_columns = cleaned.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = [column for column in cleaned.columns if column not in numeric_columns]

    if numeric_columns:
        cleaned[numeric_columns] = cleaned[numeric_columns].apply(pd.to_numeric, errors="coerce")
        cleaned[numeric_columns] = cleaned[numeric_columns].fillna(cleaned[numeric_columns].median())

    for column in categorical_columns:
        if column == detected_label:
            cleaned[column] = cleaned[column].fillna("Unknown")
        else:
            mode_series = cleaned[column].mode(dropna=True)
            fallback = mode_series.iloc[0] if not mode_series.empty else "Unknown"
            cleaned[column] = cleaned[column].fillna(fallback)

    cleaned[detected_label] = cleaned[detected_label].astype(str).str.strip()
    return cleaned, detected_label


def build_binary_target(series: pd.Series) -> pd.Series:
    """Map BENIGN/Normal-style labels to Normal and everything else to Attack."""
    normalized = (
        series.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[\s\-]+", "", regex=True)
    )
    return np.where(normalized.isin(NORMAL_LABELS), "Normal", "Attack")


def select_feature_columns(df: pd.DataFrame, label_column: str) -> list[str]:
    """Choose model feature columns while avoiding obvious leakage columns."""
    excluded = {label_column.lower(), "binary_label", "source_file", "prediction", "predicted_label"}
    return [column for column in df.columns if column.lower() not in excluded]


def build_preprocessor(df: pd.DataFrame, feature_columns: list[str]) -> ColumnTransformer:
    """Create a preprocessing pipeline for numeric and categorical columns."""
    X = df[feature_columns]
    numeric_columns = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = [column for column in feature_columns if column not in numeric_columns]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ],
        remainder="drop",
    )


def summarize_eda(df: pd.DataFrame, label_column: str, report_path: Path) -> dict[str, Any]:
    """Generate key EDA summaries and write a markdown report."""
    binary_target = build_binary_target(df[label_column])
    attack_counts = df[label_column].value_counts(dropna=False)
    binary_counts = pd.Series(binary_target).value_counts()

    numeric_df = df.select_dtypes(include=[np.number])
    correlation_pairs: list[tuple[str, str, float]] = []
    if numeric_df.shape[1] >= 2:
        corr_matrix = numeric_df.corr(numeric_only=True)
        for left_idx, left_col in enumerate(corr_matrix.columns):
            for right_col in corr_matrix.columns[left_idx + 1 :]:
                value = corr_matrix.loc[left_col, right_col]
                if pd.notna(value):
                    correlation_pairs.append((left_col, right_col, float(value)))
        correlation_pairs = sorted(correlation_pairs, key=lambda item: abs(item[2]), reverse=True)

    key_numeric_columns = numeric_df.columns[:5].tolist()
    key_stats = (
        markdown_table_from_frame(df[key_numeric_columns].describe().round(3).reset_index())
        if key_numeric_columns
        else "No numeric columns found."
    )

    top_10_attacks = attack_counts.head(10)
    duplicate_count = int(df.duplicated().sum())
    missing_after_clean = int(df.isna().sum().sum())

    lines = [
        "# DarkSec Threat Intelligence Analysis Summary",
        "",
        "## Dataset Overview",
        f"- Total rows: {len(df):,}",
        f"- Total columns: {df.shape[1]:,}",
        f"- Label column detected: `{label_column}`",
        f"- Remaining missing values after cleaning: {missing_after_clean:,}",
        f"- Duplicate rows after cleaning: {duplicate_count:,}",
        "",
        "## Normal vs Attack Traffic",
        f"- Normal traffic: {int(binary_counts.get('Normal', 0)):,}",
        f"- Attack traffic: {int(binary_counts.get('Attack', 0)):,}",
        "",
        "## Attack Type Distribution",
        markdown_table_from_frame(attack_counts.to_frame("count").reset_index(names=label_column)),
        "",
        "## Top 10 High-Risk Attack Types",
        markdown_table_from_frame(top_10_attacks.to_frame("count").reset_index(names=label_column)),
        "",
        "## Correlation Highlights",
    ]

    if correlation_pairs:
        for left_col, right_col, corr_value in correlation_pairs[:10]:
            lines.append(f"- `{left_col}` vs `{right_col}`: correlation = {corr_value:.3f}")
    else:
        lines.append("- Not enough numeric features for correlation analysis.")

    lines.extend(
        [
            "",
            "## Key Feature Statistics",
            key_stats,
            "",
            "## Core Conclusions",
            "- The dataset contains both benign traffic and multiple intrusion categories suitable for SOC-style threat analytics.",
            "- A binary Normal/Attack view is appropriate for high-level monitoring, while the original labels support detailed attack attribution.",
            "- Strongly correlated features may indicate redundant measurements and can guide future feature selection or model compression.",
            "- The cleaned dataset is ready for downstream training and dashboard exploration.",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "total_rows": int(len(df)),
        "total_columns": int(df.shape[1]),
        "label_column": label_column,
        "normal_count": int(binary_counts.get("Normal", 0)),
        "attack_count": int(binary_counts.get("Attack", 0)),
        "attack_distribution": {str(key): int(value) for key, value in attack_counts.items()},
        "top_correlations": correlation_pairs[:10],
    }


def align_features_for_inference(
    df: pd.DataFrame,
    feature_columns: list[str],
    label_column: str | None = None,
) -> pd.DataFrame:
    """Align incoming data to the training feature schema without crashing on mismatches."""
    aligned = normalize_column_names(df)
    if label_column and label_column in aligned.columns:
        aligned = aligned.drop(columns=[label_column])

    for column in feature_columns:
        if column not in aligned.columns:
            aligned[column] = np.nan

    aligned = aligned[feature_columns].copy()
    for column in aligned.columns:
        if aligned[column].dtype == object:
            aligned[column] = aligned[column].astype(str).str.strip()

    return aligned


def save_json(data: dict[str, Any], path: Path) -> None:
    """Persist JSON data with UTF-8 encoding."""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
