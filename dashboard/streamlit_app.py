"""Streamlit dashboard for SOC-style threat intelligence monitoring and CSV prediction."""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from feature_engineering import (  # noqa: E402
    DATA_CLEANED_DIR,
    MODELS_DIR,
    align_features_for_inference,
    build_binary_target,
    clean_dataset,
    detect_label_column,
)


st.set_page_config(
    page_title="DarkSec Threat Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
)


SOC_CSS = """
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(0, 255, 170, 0.16), transparent 28%),
            radial-gradient(circle at top right, rgba(0, 153, 255, 0.18), transparent 22%),
            linear-gradient(135deg, #06131f 0%, #081a2d 45%, #031018 100%);
        color: #e8f7ff;
    }
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: 0.03em;
        color: #d9fbff;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        color: #8dddf0;
        margin-bottom: 1.25rem;
    }
    .metric-card {
        background: linear-gradient(180deg, rgba(7, 35, 55, 0.95), rgba(4, 18, 31, 0.96));
        border: 1px solid rgba(93, 238, 255, 0.22);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 0 24px rgba(0, 204, 255, 0.08);
    }
    .metric-label {
        color: #86bed1;
        font-size: 0.95rem;
        margin-bottom: 0.2rem;
    }
    .metric-value {
        color: #f2feff;
        font-size: 1.8rem;
        font-weight: 800;
    }
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }
</style>
"""


@st.cache_data(show_spinner=False)
def load_cleaned_data() -> tuple[pd.DataFrame, str]:
    """Load the cleaned dataset if present."""
    cleaned_path = DATA_CLEANED_DIR / "cleaned_dataset.csv"
    if not cleaned_path.exists():
        raise FileNotFoundError(
            "Cleaned dataset not found. Please run `python src/data_cleaning.py` first."
        )

    df = pd.read_csv(cleaned_path, low_memory=False)
    df, label_column = clean_dataset(df, detect_label_column(df))
    return df, label_column


@st.cache_resource(show_spinner=False)
def load_model_bundle() -> dict:
    """Load the saved classifier bundle if present."""
    model_path = MODELS_DIR / "attack_classifier.pkl"
    if not model_path.exists():
        raise FileNotFoundError(
            "Model file not found. Please run `python src/train_model.py` first."
        )
    return joblib.load(model_path)


def render_metric_card(label: str, value: str) -> None:
    """Render a styled metric card."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_key_features(df: pd.DataFrame, label_column: str) -> list[str]:
    """Pick up to three useful numeric features for quick dashboard visuals."""
    candidate_names = [
        "Flow Duration",
        "Total Fwd Packets",
        "Total Backward Packets",
        "Flow Bytes/s",
        "Flow Packets/s",
        "Packet Length Mean",
        "Destination Port",
    ]
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    existing_candidates = [column for column in candidate_names if column in df.columns]
    fallback = [column for column in numeric_columns if column != label_column]
    return (existing_candidates + fallback)[:3]


def main() -> None:
    """Run the Streamlit dashboard."""
    st.markdown(SOC_CSS, unsafe_allow_html=True)
    st.markdown('<div class="main-title">DarkSec Threat Intelligence Platform</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">SOC-style analytics for intrusion trend monitoring, attack distribution, and model-assisted threat classification.</div>',
        unsafe_allow_html=True,
    )

    try:
        df, label_column = load_cleaned_data()
    except Exception as exc:
        st.error(f"Failed to load cleaned dataset: {exc}")
        st.stop()

    df["binary_label"] = build_binary_target(df[label_column])
    total_count = len(df)
    attack_count = int((df["binary_label"] == "Attack").sum())
    normal_count = int((df["binary_label"] == "Normal").sum())
    attack_ratio = (attack_count / total_count * 100) if total_count else 0.0

    kpi_columns = st.columns(4)
    with kpi_columns[0]:
        render_metric_card("Total Traffic", f"{total_count:,}")
    with kpi_columns[1]:
        render_metric_card("Attack Traffic", f"{attack_count:,}")
    with kpi_columns[2]:
        render_metric_card("Normal Traffic", f"{normal_count:,}")
    with kpi_columns[3]:
        render_metric_card("Attack Ratio", f"{attack_ratio:.2f}%")

    attack_distribution = (
        df[label_column]
        .astype(str)
        .value_counts()
        .rename_axis("attack_type")
        .reset_index(name="count")
    )
    feature_choices = safe_key_features(df, label_column)

    chart_col_1, chart_col_2 = st.columns(2)
    with chart_col_1:
        pie_fig = px.pie(
            attack_distribution,
            names="attack_type",
            values="count",
            title="Attack Type Distribution",
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Tealgrn,
        )
        pie_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#E8F7FF")
        st.plotly_chart(pie_fig, use_container_width=True)

    with chart_col_2:
        bar_fig = px.bar(
            attack_distribution.head(12),
            x="attack_type",
            y="count",
            title="Top Attack Types",
            color="count",
            color_continuous_scale="Turbo",
        )
        bar_fig.update_layout(
            xaxis_title="Attack Type",
            yaxis_title="Traffic Count",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E8F7FF",
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    if feature_choices:
        st.subheader("Key Feature Distribution")
        selected_feature = st.selectbox("Select a feature", feature_choices)
        if selected_feature in df.columns:
            sampled_df = df[[selected_feature, "binary_label"]].copy()
            if len(sampled_df) > 30000:
                sampled_df = sampled_df.sample(30000, random_state=42)
            hist_fig = px.histogram(
                sampled_df,
                x=selected_feature,
                color="binary_label",
                barmode="overlay",
                nbins=50,
                title=f"{selected_feature} Distribution by Traffic Type",
                color_discrete_map={"Normal": "#22c55e", "Attack": "#ef4444"},
            )
            hist_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#E8F7FF",
            )
            st.plotly_chart(hist_fig, use_container_width=True)

    st.subheader("Model Prediction Module")
    st.caption("Upload a CSV file with CICIDS-style feature columns to predict attack types.")

    uploaded_file = st.file_uploader("Upload CSV for prediction", type=["csv"])
    if uploaded_file is not None:
        try:
            model_bundle = load_model_bundle()
            inference_df = pd.read_csv(uploaded_file, low_memory=False)
            feature_columns = model_bundle.get("feature_columns", [])
            training_label_column = model_bundle.get("label_column")

            aligned_df = align_features_for_inference(
                inference_df,
                feature_columns=feature_columns,
                label_column=training_label_column,
            )
            predictions_encoded = model_bundle["multiclass_pipeline"].predict(aligned_df)
            predictions = model_bundle["multiclass_label_encoder"].inverse_transform(predictions_encoded)

            result_df = inference_df.copy()
            result_df["predicted_attack_type"] = predictions
            result_df["predicted_binary_label"] = build_binary_target(result_df["predicted_attack_type"])

            st.success("Prediction completed successfully.")
            st.dataframe(result_df.head(100), use_container_width=True)

            download_df = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download prediction results",
                data=download_df,
                file_name="darksec_predictions.csv",
                mime="text/csv",
            )
        except Exception as exc:
            st.error(
                "Prediction failed. Please check whether the uploaded CSV has CICIDS-style feature columns. "
                f"Details: {exc}"
            )


if __name__ == "__main__":
    main()
