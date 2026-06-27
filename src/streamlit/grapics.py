"""
esta wea de acá es para graficar en 3d, te genera un sol qlo y se mueve pa cachar ma o ma despues como varia dependiendo de la posicion del sol
"""

import numpy as np
import plotly.graph_objects as go

import streamlit as st


def rotar_puntos(x, y, z, theta, phi):
    """
    Rotación 3D simple del panel
    """

    theta = np.radians(theta)
    phi = np.radians(phi)

    # Rotación en Y (inclinación)
    R_theta = np.array(
        [
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)],
        ]
    )

    # Rotación en Z (orientación)
    R_phi = np.array(
        [[np.cos(phi), -np.sin(phi), 0], [np.sin(phi), np.cos(phi), 0], [0, 0, 1]]
    )

    R = R_phi @ R_theta

    puntos = np.vstack([x, y, z])
    rotados = R @ puntos

    return rotados[0], rotados[1], rotados[2]


def posicion_sol(hora):
    """
    Movimiento circular del sol en el cielo (modelo visual)
    """

    # Convertimos hora a ángulo (0 a 2π)
    angulo = (hora / 24) * 2 * np.pi

    # Radio del "cielo"
    R = 5

    # Movimiento en arco
    x = R * np.cos(angulo)
    y = R * np.sin(angulo)

    # Altura (sube al mediodía)
    z = max(0, R * np.sin(angulo))

    return x, y, z


def grafico_panel_3d(
    ancho, alto, theta: float = 30.0, phi: float = 180.0, hora: float = 12.0
):
    # ---------------------------
    # Panel base (rectángulo)
    # ---------------------------

    x = np.array([-ancho / 2, ancho / 2, ancho / 2, -ancho / 2])
    y = np.array([0, 0, 0, 0])
    z = np.array([0, 0, alto, alto])

    xr, yr, zr = rotar_puntos(x, y, z, theta, phi)

    fig = go.Figure()

    fig.add_trace(
        go.Mesh3d(x=xr, y=yr, z=zr, color="royalblue", opacity=0.85, name="Panel")
    )

    # ---------------------------
    # Sol
    # ---------------------------

    sun_x, sun_y, sun_z = posicion_sol(hora)

    fig.add_trace(
        go.Scatter3d(
            x=[sun_x],
            y=[sun_y],
            z=[sun_z],
            mode="markers",
            marker=dict(size=8, color="yellow"),
            name="Sol",
        )
    )

    # ---------------------------
    # Rayos solares
    # ---------------------------

    fig.add_trace(
        go.Scatter3d(
            x=[sun_x, 0],
            y=[sun_y, 0],
            z=[sun_z, 0],
            mode="lines",
            line=dict(color="orange", width=4),
            name="Radiación",
        )
    )

    fig.update_layout(
        scene=dict(
            xaxis_title="X", yaxis_title="Y", zaxis_title="Z", aspectmode="data"
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        title="Panel Solar 3D",
    )

    st.plotly_chart(fig, use_container_width=True)
