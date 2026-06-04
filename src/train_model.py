"""Train binary and multi-class attack classifiers and persist the best usable artifact."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

from feature_engineering import (
    DATA_CLEANED_DIR,
    MODELS_DIR,
    NORMAL_LABELS,
    REPORTS_DIR,
    align_features_for_inference,
    build_binary_target,
    build_preprocessor,
    clean_dataset,
    detect_label_column,
    ensure_directories,
    save_json,
    select_feature_columns,
)

try:
    from xgboost import XGBClassifier

    XGBOOST_AVAILABLE = True
except Exception:
    XGBOOST_AVAILABLE = False


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for model training."""
    parser = argparse.ArgumentParser(description="Train DarkSec attack classifiers.")
    parser.add_argument(
        "--input-file",
        type=Path,
        default=DATA_CLEANED_DIR / "cleaned_dataset.csv",
        help="Path to cleaned dataset CSV.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Optional dataset sample size before train/test split.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Test split ratio.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed.",
    )
    return parser.parse_args()


def evaluate_predictions(y_true, y_pred, average: str = "weighted") -> dict[str, object]:
    """Compute common classification metrics."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average=average, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average=average, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, average=average, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(y_true, y_pred, zero_division=0),
    }


def resolve_stratify_target(y, test_size: float):
    """Use stratification only when the class distribution can support it."""
    value_counts = pd.Series(y).value_counts()
    if value_counts.empty:
        return None

    minimum_class_count = int(value_counts.min())
    estimated_test_rows = max(1, int(round(len(y) * test_size)))

    if minimum_class_count < 2 or estimated_test_rows < len(value_counts):
        return None

    return y


def build_estimators(random_state: int) -> dict[str, object]:
    """Create candidate estimators based on installed libraries."""
    estimators: dict[str, object] = {
        "RandomForest": RandomForestClassifier(
            n_estimators=250,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            n_jobs=-1,
            random_state=random_state,
            class_weight="balanced_subsample",
        )
    }

    if XGBOOST_AVAILABLE:
        estimators["XGBoost"] = XGBClassifier(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=random_state,
            tree_method="hist",
        )

    return estimators


def train_pipeline(
    X_train: pd.DataFrame,
    y_train,
    X_test: pd.DataFrame,
    y_test,
    estimator_name: str,
    estimator,
    task_type: str,
) -> tuple[Pipeline, dict[str, object]]:
    """Train a preprocessing + classifier pipeline and return evaluation metrics."""
    model_estimator = clone(estimator)
    if estimator_name == "XGBoost":
        if task_type == "binary":
            model_estimator.set_params(objective="binary:logistic", eval_metric="logloss")
        else:
            num_classes = int(pd.Series(y_train).nunique())
            model_estimator.set_params(
                objective="multi:softprob",
                eval_metric="mlogloss",
                num_class=num_classes,
            )

    preprocessor = build_preprocessor(X_train, X_train.columns.tolist())
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", model_estimator),
        ]
    )
    y_train_fit = y_train
    y_test_eval = y_test
    label_encoder = None

    # XGBoost expects numeric targets for classification in this workflow.
    if estimator_name == "XGBoost" and not pd.api.types.is_numeric_dtype(pd.Series(y_train)):
        label_encoder = LabelEncoder()
        y_train_fit = label_encoder.fit_transform(pd.Series(y_train).astype(str))

    pipeline.fit(X_train, y_train_fit)
    predictions = pipeline.predict(X_test)

    if label_encoder is not None:
        predictions = label_encoder.inverse_transform(predictions.astype(int))

    metrics = evaluate_predictions(y_test_eval, predictions)
    metrics["model_name"] = estimator_name
    return pipeline, metrics


def render_metrics_markdown(binary_metrics: dict[str, object], multiclass_metrics: dict[str, object]) -> str:
    """Render evaluation results into markdown for GitHub-friendly reporting."""
    return "\n".join(
        [
            "# DarkSec Model Evaluation",
            "",
            "## Binary Classification",
            f"- Model: `{binary_metrics['model_name']}`",
            f"- Accuracy: {binary_metrics['accuracy']:.4f}",
            f"- Precision: {binary_metrics['precision']:.4f}",
            f"- Recall: {binary_metrics['recall']:.4f}",
            f"- F1-score: {binary_metrics['f1_score']:.4f}",
            "",
            "### Classification Report",
            "```text",
            str(binary_metrics["classification_report"]).rstrip(),
            "```",
            "",
            "### Confusion Matrix",
            "```text",
            str(binary_metrics["confusion_matrix"]),
            "```",
            "",
            "## Multi-Class Classification",
            f"- Model: `{multiclass_metrics['model_name']}`",
            f"- Accuracy: {multiclass_metrics['accuracy']:.4f}",
            f"- Precision: {multiclass_metrics['precision']:.4f}",
            f"- Recall: {multiclass_metrics['recall']:.4f}",
            f"- F1-score: {multiclass_metrics['f1_score']:.4f}",
            "",
            "### Classification Report",
            "```text",
            str(multiclass_metrics["classification_report"]).rstrip(),
            "```",
            "",
            "### Confusion Matrix",
            "```text",
            str(multiclass_metrics["confusion_matrix"]),
            "```",
        ]
    )


def main() -> None:
    """Train binary and multi-class models and save the final classifier bundle."""
    args = parse_args()
    ensure_directories()

    if not args.input_file.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found at '{args.input_file}'. Run 'python src/data_cleaning.py' first."
        )

    print(f"[DarkSec] Loading cleaned dataset from: {args.input_file}")
    df = pd.read_csv(args.input_file, low_memory=False)
    df, label_column = clean_dataset(df, detect_label_column(df))

    if args.sample_size is not None and len(df) > args.sample_size:
        df = df.sample(n=args.sample_size, random_state=args.random_state).reset_index(drop=True)
        print(f"[DarkSec] Training sample applied: {len(df):,} rows")

    df["binary_label"] = build_binary_target(df[label_column])
    feature_columns = select_feature_columns(df, label_column)
    X = align_features_for_inference(df[feature_columns], feature_columns)

    y_binary = df["binary_label"]
    y_multiclass_raw = df[label_column].astype(str).str.strip()
    multiclass_encoder = LabelEncoder()
    y_multiclass = multiclass_encoder.fit_transform(y_multiclass_raw)

    X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(
        X,
        y_binary,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=resolve_stratify_target(y_binary, args.test_size),
    )
    X_train_m, X_test_m, y_train_m, y_test_m = train_test_split(
        X,
        y_multiclass,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=resolve_stratify_target(y_multiclass, args.test_size),
    )

    estimators = build_estimators(args.random_state)
    model_metrics: dict[str, object] = {"binary": {}, "multiclass": {}}
    best_binary_pipeline = None
    best_multiclass_pipeline = None
    best_binary_metrics = None
    best_multiclass_metrics = None

    print("[DarkSec] Training candidate models...")
    for model_name, estimator in estimators.items():
        try:
            print(f"[DarkSec] -> Binary model: {model_name}")
            binary_pipeline, binary_metrics = train_pipeline(
                X_train_b, y_train_b, X_test_b, y_test_b, model_name, estimator, "binary"
            )
            model_metrics["binary"][model_name] = binary_metrics

            if best_binary_metrics is None or binary_metrics["f1_score"] > best_binary_metrics["f1_score"]:
                best_binary_pipeline = binary_pipeline
                best_binary_metrics = binary_metrics
        except Exception as exc:
            print(f"[DarkSec] Skipped binary model '{model_name}' due to error: {exc}")

        try:
            print(f"[DarkSec] -> Multi-class model: {model_name}")
            multiclass_pipeline, multiclass_metrics = train_pipeline(
                X_train_m, y_train_m, X_test_m, y_test_m, model_name, estimator, "multiclass"
            )
            model_metrics["multiclass"][model_name] = multiclass_metrics

            if (
                best_multiclass_metrics is None
                or multiclass_metrics["f1_score"] > best_multiclass_metrics["f1_score"]
            ):
                best_multiclass_pipeline = multiclass_pipeline
                best_multiclass_metrics = multiclass_metrics
        except Exception as exc:
            print(f"[DarkSec] Skipped multi-class model '{model_name}' due to error: {exc}")

    if best_binary_pipeline is None or best_multiclass_pipeline is None:
        raise RuntimeError(
            "No valid model pipeline was trained successfully. Please inspect the logged training errors."
        )

    classifier_bundle = {
        "project_name": "DarkSec Threat Intelligence Platform",
        "task": "multiclass_attack_classification",
        "label_column": label_column,
        "feature_columns": feature_columns,
        "multiclass_pipeline": best_multiclass_pipeline,
        "binary_pipeline": best_binary_pipeline,
        "multiclass_label_encoder": multiclass_encoder,
        "normal_aliases": sorted(NORMAL_LABELS),
        "best_multiclass_model": best_multiclass_metrics["model_name"] if best_multiclass_metrics else None,
        "best_binary_model": best_binary_metrics["model_name"] if best_binary_metrics else None,
    }

    model_path = MODELS_DIR / "attack_classifier.pkl"
    feature_columns_path = MODELS_DIR / "feature_columns.pkl"
    metrics_json_path = REPORTS_DIR / "model_metrics.json"
    metrics_md_path = REPORTS_DIR / "model_evaluation.md"

    joblib.dump(classifier_bundle, model_path)
    joblib.dump(feature_columns, feature_columns_path)
    save_json(model_metrics, metrics_json_path)
    metrics_md_path.write_text(
        render_metrics_markdown(best_binary_metrics, best_multiclass_metrics),
        encoding="utf-8",
    )

    print(f"[DarkSec] Saved classifier bundle to: {model_path}")
    print(f"[DarkSec] Saved feature columns to: {feature_columns_path}")
    print(f"[DarkSec] Saved metrics JSON to: {metrics_json_path}")
    print(f"[DarkSec] Saved metrics report to: {metrics_md_path}")
    print(
        "[DarkSec] Best models: "
        f"binary={best_binary_metrics['model_name']} (F1={best_binary_metrics['f1_score']:.4f}), "
        f"multiclass={best_multiclass_metrics['model_name']} (F1={best_multiclass_metrics['f1_score']:.4f})"
    )


if __name__ == "__main__":
    main()
