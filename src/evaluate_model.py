"""Load the saved classifier bundle and evaluate it on a cleaned dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

from feature_engineering import (
    DATA_CLEANED_DIR,
    MODELS_DIR,
    align_features_for_inference,
    build_binary_target,
    clean_dataset,
    detect_label_column,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Evaluate the saved DarkSec model bundle.")
    parser.add_argument(
        "--input-file",
        type=Path,
        default=DATA_CLEANED_DIR / "cleaned_dataset.csv",
        help="Path to the cleaned dataset CSV.",
    )
    parser.add_argument(
        "--model-file",
        type=Path,
        default=MODELS_DIR / "attack_classifier.pkl",
        help="Path to the saved model bundle.",
    )
    return parser.parse_args()


def main() -> None:
    """Run binary and multi-class evaluation using the saved bundle."""
    args = parse_args()
    if not args.input_file.exists():
        raise FileNotFoundError(
            f"Input dataset not found at '{args.input_file}'. Run 'python src/data_cleaning.py' first."
        )
    if not args.model_file.exists():
        raise FileNotFoundError(
            f"Model bundle not found at '{args.model_file}'. Run 'python src/train_model.py' first."
        )

    bundle = joblib.load(args.model_file)
    df = pd.read_csv(args.input_file, low_memory=False)
    df, label_column = clean_dataset(df, detect_label_column(df))

    feature_columns = bundle["feature_columns"]
    X = align_features_for_inference(df, feature_columns, label_column=label_column)

    print("[DarkSec] Binary Evaluation")
    y_binary = build_binary_target(df[label_column])
    binary_predictions = bundle["binary_pipeline"].predict(X)
    print(classification_report(y_binary, binary_predictions, zero_division=0))
    print("Confusion Matrix:")
    print(confusion_matrix(y_binary, binary_predictions))

    print("\n[DarkSec] Multi-class Evaluation")
    multiclass_predictions_encoded = bundle["multiclass_pipeline"].predict(X)
    multiclass_predictions = bundle["multiclass_label_encoder"].inverse_transform(
        multiclass_predictions_encoded
    )
    print(classification_report(df[label_column].astype(str), multiclass_predictions, zero_division=0))
    print("Confusion Matrix:")
    print(confusion_matrix(df[label_column].astype(str), multiclass_predictions))


if __name__ == "__main__":
    main()
