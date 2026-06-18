"""Isolation Forest 异常检测模块。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.preprocessing import StandardScaler


EXCLUDE_COLUMNS = {
    "Label",
    "label",
    "attack_category",
    "protocol_name",
}


def load_sample_data(sample_path: str | Path) -> pd.DataFrame:
    return pd.read_csv(sample_path)


def prepare_anomaly_features(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    data = df.copy()
    data = data.replace([np.inf, -np.inf], np.nan)

    numeric_df = data.select_dtypes(include=[np.number]).copy()
    drop_cols = [col for col in numeric_df.columns if col in EXCLUDE_COLUMNS]
    numeric_df = numeric_df.drop(columns=drop_cols, errors="ignore")

    imputer = SimpleImputer(strategy="median")
    filled = imputer.fit_transform(numeric_df)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(filled)
    prepared_df = pd.DataFrame(scaled, columns=numeric_df.columns)
    return prepared_df, scaled


def run_isolation_forest(
    df: pd.DataFrame,
    n_estimators: int = 100,
    contamination: float = 0.1,
    random_state: int = 42,
) -> tuple[pd.DataFrame, dict]:
    features_df, feature_matrix = prepare_anomaly_features(df)
    model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(feature_matrix)

    result = df.copy()
    result["anomaly_score"] = -model.score_samples(feature_matrix)
    raw_pred = model.predict(feature_matrix)
    result["anomaly_pred"] = np.where(raw_pred == -1, 1, 0)

    metrics = {
        "anomaly_count": int(result["anomaly_pred"].sum()),
        "anomaly_ratio": float(result["anomaly_pred"].mean()),
    }
    if "is_attack" in result.columns:
        metrics["attack_hit_ratio"] = float(
            result.loc[result["anomaly_pred"] == 1, "is_attack"].mean()
        ) if metrics["anomaly_count"] else 0.0
        metrics["precision"] = float(
            precision_score(result["is_attack"], result["anomaly_pred"], zero_division=0)
        )
        metrics["recall"] = float(
            recall_score(result["is_attack"], result["anomaly_pred"], zero_division=0)
        )
        metrics["f1_score"] = float(
            f1_score(result["is_attack"], result["anomaly_pred"], zero_division=0)
        )
        metrics["confusion_matrix"] = confusion_matrix(
            result["is_attack"], result["anomaly_pred"]
        ).tolist()
    else:
        metrics["attack_hit_ratio"] = None

    return result, metrics
