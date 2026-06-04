"""Read raw CICIDS-style CSV files, clean them, and generate an EDA summary report."""

from __future__ import annotations

import argparse
from pathlib import Path

from feature_engineering import (
    DATA_CLEANED_DIR,
    DATA_RAW_DIR,
    REPORTS_DIR,
    clean_dataset,
    ensure_directories,
    read_and_concat_csvs,
    summarize_eda,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Clean CICIDS2017 raw CSV files.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DATA_RAW_DIR,
        help="Directory containing raw CSV files.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=DATA_CLEANED_DIR / "cleaned_dataset.csv",
        help="Path to save the cleaned dataset.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Optional per-file sample size for faster experimentation.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute data cleaning and EDA report generation."""
    args = parse_args()
    ensure_directories()

    print(f"[DarkSec] Reading raw CSV files from: {args.input_dir}")
    raw_df = read_and_concat_csvs(args.input_dir, sample_size=args.sample_size)

    print("[DarkSec] Cleaning dataset...")
    cleaned_df, label_column = clean_dataset(raw_df)

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(args.output_file, index=False)
    print(f"[DarkSec] Cleaned dataset saved to: {args.output_file}")

    report_path = REPORTS_DIR / "analysis_summary.md"
    summary = summarize_eda(cleaned_df, label_column, report_path)

    print(f"[DarkSec] Analysis summary saved to: {report_path}")
    print(
        "[DarkSec] Summary: "
        f"rows={summary['total_rows']:,}, "
        f"columns={summary['total_columns']:,}, "
        f"normal={summary['normal_count']:,}, "
        f"attack={summary['attack_count']:,}"
    )


if __name__ == "__main__":
    main()
