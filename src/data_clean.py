"""CICIDS2017 数据清洗脚本。

运行方式:
    python src/data_clean.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from feature_engineering import (
    clean_numeric_anomalies,
    enrich_security_fields,
    infer_label_column,
    normalize_columns,
)


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SAMPLE_DIR = BASE_DIR / "data" / "sample"
CHUNK_SIZE = 100_000
MAX_SAMPLE_ROWS = 500_000


def list_csv_files(raw_dir: Path) -> list[Path]:
    # 支持 data/raw 下直接放 CSV，也支持解压后放在子目录中
    return sorted(raw_dir.rglob("*.csv"))


def clean_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """对分块数据执行字段标准化与异常值处理。"""
    chunk = normalize_columns(chunk)
    chunk = enrich_security_fields(chunk)
    chunk = clean_numeric_anomalies(chunk)
    return chunk


def merge_and_clean(csv_files: list[Path]) -> tuple[pd.DataFrame, int]:
    cleaned_frames: list[pd.DataFrame] = []
    total_rows = 0

    for csv_file in csv_files:
        print(f"[INFO] 正在处理文件: {csv_file.name}")
        for chunk in pd.read_csv(csv_file, chunksize=CHUNK_SIZE, low_memory=False):
            total_rows += len(chunk)
            cleaned_chunk = clean_chunk(chunk)
            if not cleaned_chunk.empty:
                cleaned_frames.append(cleaned_chunk)

    if not cleaned_frames:
        raise ValueError("没有可用的数据被读取，请确认 data/raw 中已放入 CICIDS2017 CSV 文件。")

    merged_df = pd.concat(cleaned_frames, ignore_index=True)
    merged_df = merged_df.drop_duplicates().reset_index(drop=True)
    return merged_df, total_rows


def stratified_sample(df: pd.DataFrame, max_rows: int = MAX_SAMPLE_ROWS) -> pd.DataFrame:
    """在大样本场景下尽量保持 Label 分布均衡。"""
    if len(df) <= max_rows:
        return df.copy()

    label_col = infer_label_column(df)
    label_counts = df[label_col].value_counts()
    group_count = len(label_counts)
    base_quota = max(max_rows // max(group_count, 1), 1)
    sampled_parts: list[pd.DataFrame] = []
    allocated = 0

    for label, count in label_counts.items():
        group = df[df[label_col] == label]
        quota = min(count, max(base_quota, int(max_rows * (count / len(df)))))
        if count <= base_quota:
            quota = count
        sampled = group.sample(n=quota, random_state=42) if quota < count else group
        sampled_parts.append(sampled)
        allocated += len(sampled)

    sampled_df = pd.concat(sampled_parts, ignore_index=True)
    if allocated > max_rows:
        # 再次按标签缩减样本，避免 groupby.apply 在部分 pandas 版本中丢失标签列
        adjusted_parts: list[pd.DataFrame] = []
        for label, part in sampled_df.groupby(label_col):
            adjusted_n = max(1, int(len(part) * max_rows / allocated))
            adjusted_n = min(adjusted_n, len(part))
            adjusted_parts.append(part.sample(n=adjusted_n, random_state=42))
        sampled_df = pd.concat(adjusted_parts, ignore_index=True)

    if len(sampled_df) > max_rows:
        sampled_df = sampled_df.sample(n=max_rows, random_state=42).reset_index(drop=True)
    return sampled_df


def print_summary(raw_file_count: int, raw_rows: int, clean_df: pd.DataFrame, sample_df: pd.DataFrame) -> None:
    label_col = infer_label_column(clean_df)
    attack_ratio = sample_df["is_attack"].mean() if not sample_df.empty else 0

    print("\n================ 处理结果汇总 ================")
    print(f"原始文件数量: {raw_file_count}")
    print(f"合并后数据量: {raw_rows}")
    print(f"清洗后数据量: {len(clean_df)}")
    print(f"抽样后数据量: {len(sample_df)}")
    print("\nLabel 分布:")
    print(sample_df[label_col].value_counts())
    print(f"\n攻击流量占比: {attack_ratio:.2%}")


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = list_csv_files(RAW_DIR)
    if not csv_files:
        raise FileNotFoundError(
            f"未在 {RAW_DIR} 找到 CSV 文件。请先下载并解压 CICIDS2017 MachineLearningCSV 数据。"
        )

    clean_df, raw_rows = merge_and_clean(csv_files)
    sample_df = stratified_sample(clean_df, MAX_SAMPLE_ROWS)

    clean_output = PROCESSED_DIR / "clean_cicids2017.csv"
    sample_output = SAMPLE_DIR / "cicids2017_sample.csv"
    clean_df.to_csv(clean_output, index=False)
    sample_df.to_csv(sample_output, index=False)

    print_summary(len(csv_files), raw_rows, clean_df, sample_df)
    print(f"\n清洗数据已保存: {clean_output}")
    print(f"抽样数据已保存: {sample_output}")


if __name__ == "__main__":
    main()
