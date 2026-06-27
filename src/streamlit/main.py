import pandas as pd
import plotly.express as px

import streamlit as st
from api import calcular, simular

st.set_page_config(
    page_title="Simulación Paneles Solares", page_icon="☀️", layout="wide"
)

st.title("Simulación Paneles Solares")
st.caption("Simulación de generación energética mediante integración matemática")
st.divider()

col_param, col_view = st.columns([1, 2])

# =======================
# INPUTS
# =======================

with col_param:
    st.subheader("⚙️ Parámetros")

    latitud = st.number_input("Latitud", value=0.0, format="%.6f", step=0.0001)
    longitud = st.number_input("Longitud", value=-0.0, format="%.6f", step=0.0001)

    ancho = st.number_input("Ancho del panel (m)", min_value=0.01, value=1.0, step=0.1)

    alto = st.number_input("Alto del panel (m)", min_value=0.01, value=1.0, step=0.1)
    power_gen_kw = st.number_input(
        "Potencia nominal del panel (kW)", min_value=0.1, value=1.0, step=0.1
    )

    estacion = st.selectbox("Estación", ["summer", "autumn", "winter", "spring"])

    ejecutar = st.button("☀️ Simular", use_container_width=True)

# =======================
# SIMULACIÓN
# =======================

if ejecutar:
    st.session_state["data"] = simular(
        latitude=latitud,
        longitude=longitud,
        width=ancho,
        height=alto,
        season=estacion,
        power_gen_kw=power_gen_kw,
    )

# =======================
# USAR DATA SI EXISTE
# =======================

if "data" in st.session_state:
    data = st.session_state["data"]

    st.success("Simulación lista")

    # =======================
    # GRÁFICO
    # =======================

    with col_view:
        st.subheader("📈 Potencia generada durante el día")

        df = pd.DataFrame(data["plot_data"])
        fig = px.line(df, x="time", y="power", markers=True)

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # =======================
    # MÉTRICAS
    # =======================

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Energía diaria", f"{data['results']['total_daily_energy_kwh']:.2f} kWh"
        )
    with c2:
        st.metric("Potencia pico", f"{data['results']['peak_power_kw']:.2f} kW")

    with c3:
        st.metric("Inclinación", f"{data['optimal_configuration']['tilt_angle_deg']}°")

    with c4:
        st.metric("Dirección", data["optimal_configuration"]["facing_direction"])

    st.divider()

    # =======================
    # INCERTIDUMBRE
    # =======================

    st.subheader("⚙️ Análisis de incertidumbre")

    delta_theta = st.slider("Error θ (°)", 0.0, 20.0, 5.0, key="theta")
    delta_phi = st.slider("Error φ (°)", 0.0, 20.0, 5.0, key="phi")
    power_gen = st.number_input(
        "Capacidad de energia", min_value=0.1, value=1.0, step=0.1
    )

    if st.button("Calcular incertidumbre"):
        st.session_state["calc_data"] = calcular(
            latitude=latitud,
            longitude=longitud,
            delta_theta=delta_theta,
            delta_phi=delta_phi,
            power_gen=power_gen,
        )

    if "calc_data" in st.session_state:
        calc_data = st.session_state["calc_data"]

        st.metric("Poder ideal", calc_data["results"]["ideal_peak_power_kw"])
        st.metric("Poder esperado", calc_data["results"]["expected_avg_power_kw"])

        loss = (
            calc_data["results"]["ideal_peak_power_kw"]
            - calc_data["results"]["expected_avg_power_kw"]
        )

        st.metric("Pérdida por error angular", f"{loss:.3f} kW")

# =======================
# AMBIENTE
# =======================

if "data" in st.session_state:
    data = st.session_state["data"]

    st.subheader("Información Ambiental")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("Radiación:", data["environment"]["radiation_mj_m2"])

    with col2:
        st.write("Amanecer:", data["environment"]["calculated_sunrise"])

    with col3:
        st.write("Atardecer:", data["environment"]["calculated_sunset"])
