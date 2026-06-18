from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
SAMPLE_PATH = BASE_DIR / "data" / "sample" / "cicids2017_sample.csv"
ATTACK_PATH = BASE_DIR / "data" / "processed" / "attack_distribution.csv"
PROTOCOL_PATH = BASE_DIR / "data" / "processed" / "protocol_distribution.csv"
PORT_PATH = BASE_DIR / "data" / "processed" / "top_attack_ports.csv"
ANOMALY_PATH = BASE_DIR / "data" / "processed" / "anomaly_detection_result.csv"


st.set_page_config(
    page_title="SOC网络流量异常检测与安全分析平台",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_csv(path: Path, name: str) -> pd.DataFrame | None:
    if not path.exists():
        st.warning(f"未找到 {name}：{path}")
        return None
    return pd.read_csv(path)


def style_page() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0a0f1f 0%, #10192e 45%, #0b1320 100%);
            color: #e8f0ff;
        }
        [data-testid="stMetric"] {
            background: rgba(18, 31, 53, 0.85);
            border: 1px solid rgba(89, 176, 255, 0.25);
            padding: 12px;
            border-radius: 14px;
        }
        h1, h2, h3 {
            color: #d7f1ff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_kpis(sample_df: pd.DataFrame | None, anomaly_df: pd.DataFrame | None) -> None:
    total = int(len(sample_df)) if sample_df is not None else 0
    attack = int(sample_df["is_attack"].sum()) if sample_df is not None and "is_attack" in sample_df.columns else 0
    benign = total - attack
    ratio = attack / total if total else 0
    anomaly_count = int(anomaly_df["anomaly_pred"].sum()) if anomaly_df is not None and "anomaly_pred" in anomaly_df.columns else 0

    cols = st.columns(5)
    cols[0].metric("总流量数", f"{total:,}")
    cols[1].metric("攻击流量数", f"{attack:,}")
    cols[2].metric("正常流量数", f"{benign:,}")
    cols[3].metric("攻击占比", f"{ratio:.2%}")
    cols[4].metric("异常检测数量", f"{anomaly_count:,}")


def plot_attack_distribution(df: pd.DataFrame) -> None:
    fig = px.bar(
        df,
        x="attack_category",
        y="count",
        color="attack_category",
        title="攻击类型分布",
        template="plotly_dark",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def plot_protocol_distribution(df: pd.DataFrame) -> None:
    if df["protocol_name"].nunique() == 1 and df["protocol_name"].iloc[0] == "Unknown":
        st.info("当前导入的 CICIDS2017 CSV 版本不包含原始 Protocol 字段，因此无法给出真实协议分布。")
        return
    fig = px.pie(
        df,
        names="protocol_name",
        values="count",
        title="协议分布",
        template="plotly_dark",
        hole=0.45,
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_top_ports(df: pd.DataFrame) -> None:
    fig = px.bar(
        df,
        x="count",
        y="destination_port",
        orientation="h",
        title="TOP攻击端口",
        template="plotly_dark",
        color="count",
        color_continuous_scale="OrRd",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)


def plot_anomaly(df: pd.DataFrame) -> None:
    summary = df["anomaly_pred"].value_counts().rename_axis("anomaly_pred").reset_index(name="count")
    summary["label"] = summary["anomaly_pred"].map({0: "正常", 1: "异常"})
    fig = px.bar(
        summary,
        x="label",
        y="count",
        color="label",
        title="异常检测结果",
        template="plotly_dark",
    )
    st.plotly_chart(fig, use_container_width=True)

    if {"is_attack", "anomaly_pred"}.issubset(df.columns):
        cm = pd.crosstab(df["is_attack"], df["anomaly_pred"])
        heatmap = go.Figure(
            data=go.Heatmap(
                z=cm.values,
                x=["预测正常", "预测异常"][: len(cm.columns)],
                y=["真实正常", "真实攻击"][: len(cm.index)],
                colorscale="Blues",
                text=cm.values,
                texttemplate="%{text}",
            )
        )
        heatmap.update_layout(title="异常检测混淆矩阵", template="plotly_dark")
        st.plotly_chart(heatmap, use_container_width=True)


def show_conclusion(sample_df: pd.DataFrame | None, port_df: pd.DataFrame | None, anomaly_df: pd.DataFrame | None) -> None:
    conclusions = []
    if sample_df is not None and "attack_category" in sample_df.columns:
        top_attack = sample_df["attack_category"].value_counts().head(3).index.tolist()
        conclusions.append(f"主要攻击类别集中在：{', '.join(top_attack)}。")
    if port_df is not None and not port_df.empty:
        top_ports = ", ".join(map(str, port_df["destination_port"].head(5).tolist()))
        conclusions.append(f"高风险目的端口优先关注：{top_ports}。")
    if anomaly_df is not None and {"anomaly_pred", "is_attack"}.issubset(anomaly_df.columns):
        hit_ratio = anomaly_df.loc[anomaly_df["anomaly_pred"] == 1, "is_attack"].mean()
        conclusions.append(f"异常检测命中的真实攻击占比约为：{hit_ratio:.2%}。")
    conclusions.append("Isolation Forest 适合用作 SOC 异常流量辅助发现工具，但不能替代规则告警、特征工程和人工研判。")

    for item in conclusions:
        st.markdown(f"- {item}")


def main() -> None:
    style_page()
    st.title("SOC网络流量异常检测与安全分析平台")
    st.caption("面向 SOC 安全运营场景的 CICIDS2017 流量分析、攻击画像与异常检测展示平台")

    sample_df = load_csv(SAMPLE_PATH, "抽样数据")
    attack_df = load_csv(ATTACK_PATH, "攻击类型分布数据")
    protocol_df = load_csv(PROTOCOL_PATH, "协议分布数据")
    port_df = load_csv(PORT_PATH, "攻击端口数据")
    anomaly_df = load_csv(ANOMALY_PATH, "异常检测结果数据")

    st.subheader("KPI总览")
    build_kpis(sample_df, anomaly_df)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("攻击类型分布")
        if attack_df is not None and not attack_df.empty:
            plot_attack_distribution(attack_df)
    with col2:
        st.subheader("协议分布")
        if protocol_df is not None and not protocol_df.empty:
            plot_protocol_distribution(protocol_df)

    st.subheader("TOP攻击端口")
    if port_df is not None and not port_df.empty:
        plot_top_ports(port_df)

    st.subheader("异常检测结果")
    if anomaly_df is not None and not anomaly_df.empty:
        plot_anomaly(anomaly_df)

    st.subheader("原始数据预览")
    if sample_df is not None:
        st.dataframe(sample_df.head(50), use_container_width=True)

    st.subheader("安全分析结论")
    show_conclusion(sample_df, port_df, anomaly_df)


if __name__ == "__main__":
    main()
