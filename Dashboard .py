import json
import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="TechStore Agent Monitor",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "../logs")
SUMMARY_FILE = os.path.join(LOG_DIR, "metrics_summary.json")
LOG_FILE = os.path.join(LOG_DIR, "agent_execution.jsonl")

@st.cache_data(ttl=10)
def load_data():

    metrics = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    metrics.append(json.loads(line))

    summary = {}
    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            summary = data.get("summary", {})

    return metrics, summary

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("TechStore Agent")
    st.caption("Sistema de Monitoreo — EP3 ISY0101")
    st.divider()

    st.markdown("**Asignatura:** ISY0101")
    st.markdown("**Evaluación:** Parcial N°3")
    st.markdown("**Módulo:** Observabilidad")
    st.divider()

    if st.button(" Actualizar datos"):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")

metrics, summary = load_data()

if not metrics:
    st.error("️ No se encontraron datos. Ejecuta primero `observability_metrics.py`.")
    st.code("python3 RA3/IL3.1/observability_metrics.py", language="bash")
    st.stop()

df = pd.DataFrame(metrics)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["latency_ms"] = df["latency_seconds"] * 1000

st.title(" Dashboard de Observabilidad — Agente TechStore")
st.caption("Monitoreo de métricas de precisión, latencia, consistencia y uso de recursos")
st.divider()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Consultas",
        value=summary.get("total_queries", len(df)),
        delta=None,
    )

with col2:
    error_rate = summary.get("error_rate", 0)
    st.metric(
        label="Tasa de Errores",
        value=f"{error_rate:.1%}",
        delta=f"{' Sin errores' if error_rate == 0 else '️ Ver logs'}",
        delta_color="normal" if error_rate == 0 else "inverse",
    )

with col3:
    precision = summary.get("avg_precision", 0)
    st.metric(
        label="Precisión Promedio",
        value=f"{precision:.1%}",
        delta="Objetivo: ≥80%",
        delta_color="normal" if precision >= 0.80 else "inverse",
    )

with col4:
    consistency = summary.get("consistency_score", 0)
    st.metric(
        label="Consistencia",
        value=f"{consistency:.1%}",
        delta=" Alta" if consistency >= 0.9 else "️ Revisar",
    )

with col5:
    avg_tokens = summary.get("avg_tokens", 0)
    st.metric(
        label="Tokens/Consulta",
        value=f"{avg_tokens:.0f}",
        delta=f"Total: {summary.get('total_tokens', 0)}",
    )

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader(" Precisión por Consulta")
    fig_prec = px.bar(
        df,
        x="query_id",
        y="precision_score",
        color="precision_score",
        color_continuous_scale=["#ef4444", "#f97316", "#22c55e"],
        range_color=[0, 1],
        labels={"query_id": "ID Consulta", "precision_score": "Score de Precisión"},
        height=300,
    )
    fig_prec.add_hline(y=0.80, line_dash="dash", line_color="blue",
                       annotation_text="Objetivo 80%", annotation_position="top left")
    fig_prec.update_layout(showlegend=False, margin=dict(t=20))
    st.plotly_chart(fig_prec, use_container_width=True)

with col_right:
    st.subheader("⏱️ Distribución de Latencia")
    fig_lat = px.histogram(
        df,
        x="latency_ms",
        nbins=8,
        labels={"latency_ms": "Latencia (ms)", "count": "Frecuencia"},
        color_discrete_sequence=["#6366f1"],
        height=300,
    )
    p95 = summary.get("p95_latency_s", 0) * 1000
    fig_lat.add_vline(x=p95, line_dash="dash", line_color="red",
                      annotation_text=f"P95: {p95:.2f}ms")
    fig_lat.update_layout(margin=dict(t=20))
    st.plotly_chart(fig_lat, use_container_width=True)

col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("🪙 Tokens Usados por Consulta")
    fig_tok = px.line(
        df,
        x="query_id",
        y="tokens_used",
        markers=True,
        labels={"query_id": "ID Consulta", "tokens_used": "Tokens Usados"},
        color_discrete_sequence=["#f59e0b"],
        height=280,
    )
    avg_tok = summary.get("avg_tokens", df["tokens_used"].mean())
    fig_tok.add_hline(y=avg_tok, line_dash="dot", line_color="gray",
                      annotation_text=f"Avg: {avg_tok:.0f}")
    fig_tok.update_layout(margin=dict(t=20))
    st.plotly_chart(fig_tok, use_container_width=True)

with col_right2:
    st.subheader(" Uso de Herramientas")
    tool_dist = df["tool_calls"].value_counts().reset_index()
    tool_dist.columns = ["Herramientas Usadas", "Frecuencia"]
    tool_dist["Herramientas Usadas"] = tool_dist["Herramientas Usadas"].astype(str)
    fig_tools = px.pie(
        tool_dist,
        values="Frecuencia",
        names="Herramientas Usadas",
        color_discrete_sequence=["#22c55e", "#6366f1", "#f97316"],
        height=280,
    )
    fig_tools.update_layout(margin=dict(t=20))
    st.plotly_chart(fig_tools, use_container_width=True)

st.divider()
st.subheader(" Métricas de Latencia Detalladas")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Mínima", f"{summary.get('min_latency_s', 0)*1000:.3f} ms")
col_m2.metric("Promedio", f"{summary.get('avg_latency_s', 0)*1000:.3f} ms")
col_m3.metric("P95", f"{summary.get('p95_latency_s', 0)*1000:.3f} ms")
col_m4.metric("Máxima", f"{summary.get('max_latency_s', 0)*1000:.3f} ms")

st.divider()
st.subheader("️ Salud General del Agente")

categories = ["Precisión", "Consistencia", "Disponibilidad",
              "Eficiencia\nTokens", "Uso de\nHerramientas"]
values = [
    summary.get("avg_precision", 0),
    summary.get("consistency_score", 0),
    1.0 - summary.get("error_rate", 0),
    min(1.0, 25 / max(summary.get("avg_tokens", 25), 1)),
    min(1.0, summary.get("tool_call_rate", 0)),
]

fig_radar = go.Figure(data=go.Scatterpolar(
    r=values + [values[0]],
    theta=categories + [categories[0]],
    fill="toself",
    fillcolor="rgba(99, 102, 241, 0.2)",
    line_color="#6366f1",
    name="Estado actual",
))
fig_radar.add_trace(go.Scatterpolar(
    r=[0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
    theta=categories + [categories[0]],
    line_color="#22c55e",
    line_dash="dash",
    name="Objetivo (90%)",
))
fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    showlegend=True,
    height=400,
    margin=dict(t=20),
)
st.plotly_chart(fig_radar, use_container_width=True)

st.divider()
st.subheader(" Registros de Ejecución")

display_df = df[[
    "query_id", "timestamp", "query", "latency_ms",
    "tokens_used", "tool_calls", "precision_score", "success"
]].copy()
display_df["timestamp"] = display_df["timestamp"].dt.strftime("%H:%M:%S")
display_df["latency_ms"] = display_df["latency_ms"].round(3)
display_df["precision_score"] = display_df["precision_score"].round(3)
display_df.columns = [
    "ID", "Hora", "Consulta", "Latencia (ms)",
    "Tokens", "Herramientas", "Precisión", "Éxito"
]

st.dataframe(display_df, use_container_width=True, height=350)

st.divider()
st.caption(
    "ISY0101 - Ingeniería de Soluciones con IA | DuocUC 2025 | "
    "Dashboard generado con Streamlit + Plotly"
)