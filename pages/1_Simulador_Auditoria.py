import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from config import get_page_title
from src.agent_based_simulation.runner import (
    _hashable_prophet,
    _hashable_sim_params,
    run_auditoria_simulation,
)
from ui.branding import (
    render_platform_footer,
    render_platform_header,
    render_sidebar_branding,
)

st.set_page_config(layout="wide", page_title=get_page_title("Auditoría Operativa"))
render_platform_header(
    "Simulador de Capacidad Institucional y Cuellos de Botella",
    "Módulo de auditoría operativa basado en datos SIVIGILA.",
)
render_sidebar_branding()

if "df_prophet" not in st.session_state or "sim_params" not in st.session_state:
    st.warning(
        "Genera el pronóstico en la página principal para cargar la matriz de datos."
    )
    render_platform_footer()
    st.stop()

df_prophet = st.session_state["df_prophet"]
sim_params = st.session_state["sim_params"]

st.markdown("""
**Auditoría Basada en Datos:** Modelo estricto de Teoría de Colas y Cadenas de Markov, alimentado por el pronóstico diario de Prophet y la matriz de remisiones reales extraída del SIVIGILA.
""")

with st.sidebar:
    st.header("1. Capacidad Base Diaria")
    cap_salud = st.slider("Cupos Salud Mental (Psicólogos)", 1, 50, 10)
    cap_prot = st.slider("Cupos Protección (Comisarías)", 1, 50, 15)

    st.header("2. Diseño de Turnos")
    pct_fin_semana = st.slider(
        "Retención Operativa Fines de Semana (%)",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        help="1.0 significa que trabajan al 100% sábados y domingos. 0.0 significa que las dependencias cierran por completo.",
    )


def _render_histogram_bins(hist_bins: dict) -> None:
    if not hist_bins or hist_bins.get("bin_edges") is None:
        return

    bin_edges = hist_bins["bin_edges"]
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    fig_hist = go.Figure()

    if hist_bins.get("alta") is not None:
        counts, _ = hist_bins["alta"]
        fig_hist.add_trace(
            go.Bar(
                x=bin_centers,
                y=counts,
                name="Alta Prioridad (Menores/Sexual)",
                marker_color="#D32F2F",
                opacity=0.7,
            )
        )

    if hist_bins.get("regular") is not None:
        counts, _ = hist_bins["regular"]
        fig_hist.add_trace(
            go.Bar(
                x=bin_centers,
                y=counts,
                name="Prioridad Regular",
                marker_color="#9E9E9E",
                opacity=0.7,
            )
        )

    fig_hist.update_layout(
        title="Distribución Real de Tiempos de Espera por Nivel de Vulnerabilidad",
        template="plotly_white",
        barmode="overlay",
        xaxis_title="Días hasta resolución total",
        yaxis_title="Cantidad de Víctimas",
    )
    st.plotly_chart(fig_hist, width="stretch")


def render_auditoria_results(resultados: dict) -> None:
    resultados_df = resultados["resultados"]
    fallos_administrativos = resultados["fallos_administrativos"]
    hist_bins = resultados.get("hist_bins", {})

    col1, col2 = st.columns(2)

    with col1:
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(
                x=resultados_df["Fecha"],
                y=resultados_df["Nuevos Casos (Prophet)"].cumsum(),
                mode="lines",
                name="Demanda Acumulada",
                line=dict(color="black", dash="dash"),
            )
        )
        fig1.add_trace(
            go.Scatter(
                x=resultados_df["Fecha"],
                y=resultados_df["Casos Completados"],
                mode="lines",
                name="Expedientes Resueltos",
                fill="tozeroy",
                fillcolor="rgba(46, 125, 50, 0.3)",
                line=dict(color="#2E7D32"),
            )
        )
        fig1.update_layout(
            title="Rendimiento Global del Sistema", template="plotly_white"
        )
        st.plotly_chart(fig1, width="stretch")

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=resultados_df["Fecha"],
                y=resultados_df["Backlog Salud Mental"],
                mode="lines",
                stackgroup="one",
                name="Represa: Salud Mental",
                fillcolor="#1976D2",
            )
        )
        fig2.add_trace(
            go.Scatter(
                x=resultados_df["Fecha"],
                y=resultados_df["Backlog Proteccion"],
                mode="lines",
                stackgroup="one",
                name="Represa: Comisarías (Protección)",
                fillcolor="#F57C00",
            )
        )
        fig2.update_layout(
            title="Evolución del Backlog (Nota el efecto 'dientes de sierra' por los fines de semana)",
            template="plotly_white",
        )
        st.plotly_chart(fig2, width="stretch")

    st.markdown("---")
    st.markdown("### Auditoría de Inequidad y Triage Institucional")

    if hist_bins.get("bin_edges") is not None:
        c1, c2 = st.columns([1, 2])

        with c1:
            st.metric(
                "Total Demanda (Prophet)",
                int(resultados_df["Nuevos Casos (Prophet)"].sum()),
            )
            st.metric(
                "Expedientes Atrapados (Sin Resolver)",
                int(resultados_df["Backlog Total"].iloc[-1]),
            )
            st.metric(
                "Fallos Administrativos (> 30 días)",
                fallos_administrativos,
                delta_color="inverse",
            )

        with c2:
            _render_histogram_bins(hist_bins)

        st.info(
            "**Análisis de Triage:** El modelo procesa primero a las víctimas de mayor vulnerabilidad (rojo). Sin embargo, si el sistema está muy colapsado, notarás que incluso la curva roja se desplaza hacia la derecha, demostrando que la falta de recursos vulnera hasta los casos más urgentes."
        )


if st.button("Ejecutar Auditoría Operativa", type="primary"):
    cache_key = (
        _hashable_prophet(df_prophet),
        _hashable_sim_params(sim_params),
        cap_salud,
        cap_prot,
        pct_fin_semana,
    )
    auditoria_cache = st.session_state.setdefault("auditoria_cache", {})

    if cache_key not in auditoria_cache:
        progress = st.progress(0, text="Inicializando simulación…")

        def _report_progress(value: float) -> None:
            pct = int(value * 100)
            progress.progress(value, text=f"Simulando día a día… {pct}%")

        with st.spinner("Procesando expedientes, triage empírico y calendario..."):
            auditoria_cache[cache_key] = run_auditoria_simulation(
                df_prophet=df_prophet,
                sim_params=sim_params,
                cap_salud=cap_salud,
                cap_prot=cap_prot,
                pct_fin_semana=pct_fin_semana,
                progress_callback=_report_progress,
            )

        progress.empty()
    else:
        st.toast("Resultados recuperados de caché en memoria.", icon="⚡")

    st.session_state["auditoria_results"] = auditoria_cache[cache_key]

if "auditoria_results" in st.session_state:
    render_auditoria_results(st.session_state["auditoria_results"])

render_platform_footer()
