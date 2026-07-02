import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import streamlit as st
from api import obtener_superficie


def surface_plot_E(A, theta0, phi0, res=40, current_point=None):

    data = obtener_superficie(A, theta0, phi0, res)
    if data.get("status") != "success":
        st.error("No se pudo generar la superficie")
        return

    Theta, Phi = np.meshgrid(data["theta"], data["phi"])
    E = np.array(data["E"])

    fig = go.Figure()

    fig.add_trace(
        go.Surface(
            z=E,
            x=Phi,
            y=Theta,
            colorscale="viridis",
            opacity=0.9,
            colorbar=dict(title="E (kW)"),
        )
    )

    if current_point:
        theta_c, phi_c, E_c = current_point
        fig.add_trace(
            go.Scatter3d(
                x=[phi_c],
                y=[theta_c],
                z=[E_c],
                mode="markers",
                marker=dict(size=8, color="red", symbol="circle"),
                name="Configuración actual",
            )
        )

    fig.update_layout(
        scene=dict(
            xaxis_title="φ — Orientación (°)",
            yaxis_title="θ — Inclinación (°)",
            zaxis_title="E — Energía (kW)",
            aspectmode="manual",
            aspectratio=dict(x=1.5, y=0.5, z=0.5),
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        title="Superficie de Energía E(θ, φ)",
    )

    st.plotly_chart(fig, use_container_width=True)


def contour_plot_E(A, theta0, phi0, res=40, current_point=None, grad_point=None):

    data = obtener_superficie(A, theta0, phi0, res)
    if data.get("status") != "success":
        st.error("No se pudo generar el contorno")
        return

    Theta, Phi = np.meshgrid(data["theta"], data["phi"])
    E = np.array(data["E"])

    fig = go.Figure()

    fig.add_trace(
        go.Contour(
            z=E,
            x=data["phi"],
            y=data["theta"],
            colorscale="viridis",
            contours=dict(showlabels=True),
            colorbar=dict(title="E (kW)"),
        )
    )

    if current_point:
        theta_c, phi_c = current_point
        fig.add_trace(
            go.Scatter(
                x=[phi_c],
                y=[theta_c],
                mode="markers",
                marker=dict(size=10, color="red", symbol="x", line=dict(width=2)),
                name="Config. actual",
            )
        )

    if grad_point and current_point:
        g_theta, g_phi = grad_point
        g_mag = math.sqrt(g_theta**2 + g_phi**2)
        if g_mag > 1e-10:
            theta_c, phi_c = current_point
            scale = 15
            g_theta_norm = g_theta / g_mag
            g_phi_norm = g_phi / g_mag
            fig.add_annotation(
                x=phi_c + g_phi_norm * scale,
                y=theta_c + g_theta_norm * scale,
                ax=phi_c,
                ay=theta_c,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowcolor="red",
                text=f"∇E ({g_mag:.3f})",
                font=dict(size=10, color="red"),
            )

    fig.update_layout(
        xaxis_title="φ — Orientación (°)",
        yaxis_title="θ — Inclinación (°)",
        title="Curvas de Nivel de E(θ, φ)",
        margin=dict(l=0, r=0, t=30, b=0),
    )

    st.plotly_chart(fig, use_container_width=True)


def simulation_chart(plot_data, shadows=None):
    df = pd.DataFrame(plot_data)
    fig = px.line(df, x="time", y="power", markers=True)
    if "power_ideal" in df.columns:
        fig.add_scatter(
            x=df["time"], y=df["power_ideal"],
            mode="lines", line=dict(dash="dot", color="orange"),
            name="Potencia ideal (sin sombra)"
        )
    if shadows:
        for s in shadows:
            fig.add_vrect(
                x0=s["start_hour"], x1=s["end_hour"],
                fillcolor="red", opacity=0.1,
                annotation_text=f"{s.get('shade_factor', 0)*100:.0f}% sombra",
                annotation_position="top left",
                line_width=0,
            )
    fig.update_layout(
        xaxis_title="Hora del dia",
        yaxis_title="Potencia (kW)",
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)


def accumulated_energy_chart(plot_data):
    df = pd.DataFrame(plot_data)
    dt = df["time"].diff().bfill().iloc[0]
    df["energy_kwh"] = df["power"] * dt
    df["energy_cumulative"] = df["energy_kwh"].cumsum()
    if "power_ideal" in df.columns:
        df["energy_ideal_kwh"] = df["power_ideal"] * dt
        df["energy_ideal_cumulative"] = df["energy_ideal_kwh"].cumsum()

    fig = go.Figure()
    fig.add_scatter(
        x=df["time"], y=df["energy_cumulative"],
        mode="lines", fill="tozeroy", name="Energia acumulada (real)"
    )
    if "energy_ideal_cumulative" in df.columns:
        fig.add_scatter(
            x=df["time"], y=df["energy_ideal_cumulative"],
            mode="lines", line=dict(dash="dot", color="orange"),
            name="Energia acumulada (ideal)"
        )
    fig.update_layout(
        xaxis_title="Hora del dia",
        yaxis_title="Energia acumulada (kWh)",
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)


def shadow_timeline_chart(shadows):
    if not shadows:
        st.info("No hay eventos de sombra registrados para este panel.")
        return
    fig = go.Figure()
    for s in shadows:
        alpha = min(s["shade_factor"] * 0.8 + 0.1, 1.0)
        fig.add_vrect(
            x0=s["start_hour"], x1=s["end_hour"],
            fillcolor=f"rgba(200, 0, 0, {alpha:.2f})",
            line_width=1, line_color="darkred",
            annotation_text=f"{s['shade_factor']*100:.0f}%",
            annotation_position="top left",
        )
    fig.update_layout(
        xaxis=dict(title="Hora del dia", range=[0, 24]),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=10, b=0),
        height=80,
    )
    st.plotly_chart(fig, use_container_width=True)


def shadow_effect_chart(plot_data):
    df = pd.DataFrame(plot_data)
    if "power_ideal" not in df.columns:
        st.info("No hay datos de potencia ideal para comparar.")
        return
    fig = go.Figure()
    fig.add_scatter(
        x=df["time"], y=df["power_ideal"],
        mode="lines", line=dict(color="orange", dash="dot"),
        name="Sin sombra"
    )
    fig.add_scatter(
        x=df["time"], y=df["power"],
        mode="lines", fill="tonexty", line=dict(color="blue"),
        name="Con sombra"
    )
    fig.update_layout(
        xaxis_title="Hora del dia",
        yaxis_title="Potencia (kW)",
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)


def comparison_energy_chart(df):
    fig = px.bar(
        df,
        x="Panel",
        y=["E (kW)", "E_max (kW)"],
        barmode="group",
        title="Energia Actual vs Maxima por Panel",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)


def comparison_efficiency_chart(df):
    fig = px.bar(
        df,
        x="Panel",
        y="Rend. (%)",
        title="Rendimiento Relativo por Panel",
        color="Rend. (%)",
        color_continuous_scale="RdYlGn",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)
