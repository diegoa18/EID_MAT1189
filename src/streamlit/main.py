import math

import pandas as pd
from grapics import (
    comparison_efficiency_chart,
    comparison_energy_chart,
    contour_plot_E,
    simulation_chart,
    surface_plot_E,
)
from mapa import mapa_paneles
from sidebar import render_sidebar

import streamlit as st
from api import (
    calcular,
    obtener_derivada_direccional,
    obtener_energia,
    obtener_optimo,
    obtener_superficie,
)

if "paneles" not in st.session_state:
    from persistencia import cargar_paneles
    st.session_state.paneles = cargar_paneles()

if "panel_index" not in st.session_state:
    st.session_state.panel_index = None

if "next_uid" not in st.session_state:
    max_uid = 0
    for p in st.session_state.paneles:
        uid = p.get("uid", 0)
        if uid >= max_uid:
            max_uid = uid + 1
    st.session_state.next_uid = max(max_uid, 1)

st.set_page_config(
    page_title="Optimizacion Paneles Solares", page_icon="☀️", layout="wide"
)

st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        width: 400px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Optimización de Paneles Solares")
st.caption("Cálculo multivariable aplicado a energía solar")
st.divider()
render_sidebar()

# ===================
# MAIN
# ===================
if not st.session_state.paneles:
    st.info("Agrega un panel desde la barra lateral para comenzar.")
    st.stop()

if st.session_state.panel_index is None:
    st.warning("Selecciona un panel de la lista.")
    st.stop()

i = st.session_state.panel_index
p = st.session_state.paneles[i]

theta0_res = obtener_optimo(p["latitud"], p["potencia"])
theta0 = theta0_res["theta0"]
phi0 = theta0_res["phi0"]
E_max = theta0_res["E_max"]

energia_res = obtener_energia(p["theta"], p["phi"], p["potencia"], theta0, phi0)
E_actual = energia_res["E"]
dE_th = energia_res["dE_dtheta"]
dE_ph = energia_res["dE_dphi"]
grad_mag = energia_res["grad_magnitude"]
grad_angle = energia_res["grad_angle_deg"]

(
    tab_panel,
    tab_surface,
    tab_contour,
    tab_deriv,
    tab_optimal,
    tab_compare,
    tab_uncertainty,
    tab_map,
) = st.tabs(
    [
        "Panel",
        "Superficie",
        "Contorno",
        "Derivadas",
        "Optimo",
        "Comparar",
        "Incertidumbre",
        "Mapa",
    ]
)

# ===================
# TAB PANEL
# ===================
with tab_panel:
    st.subheader(p["nombre"])

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("E(θ, φ) actual", f"{E_actual:.4f} kW")
    with col_m2:
        eficiencia = (E_actual / E_max * 100) if E_max > 0 else 0
        st.metric("Rendimiento relativo", f"{eficiencia:.1f}%")
    with col_m3:
        st.metric("E_max optimo", f"{E_max:.2f} kW")

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.caption("Configuracion optima (θ₀, φ₀)")
        st.write(f"θ₀ = {theta0:.1f}°  |  φ₀ = {phi0:.1f}°")
    with col_right:
        st.caption("Parametros actuales")
        st.write(f"θ = {p['theta']:.1f}°  |  φ = {p['phi']:.1f}°")
        st.write(f"Latitud: {p['latitud']:.4f}°  |  Longitud: {p['longitud']:.4f}°")
        st.write(
            f"Dimensiones: {p['ancho']}m × {p['alto']}m  |  Estacion: {p['estacion']}"
        )

    if p["simulacion"] and p["simulacion"].get("status") == "success":
        st.divider()
        data = p["simulacion"]

        st.subheader("Simulacion diaria")

        col_chart, col_metrics = st.columns([2, 1])

        with col_chart:
            simulation_chart(data["plot_data"])

        with col_metrics:
            c1, c2 = st.columns(2)
            with c1:
                st.metric(
                    "Energia diaria",
                    f"{data['results']['total_daily_energy_kwh']:.2f} kWh",
                )
            with c2:
                st.metric(
                    "Potencia pico",
                    f"{data['results']['peak_power_kw']:.2f} kW",
                )

            st.divider()

            st.write("**Informacion ambiental**")
            env = data.get("environment", {})
            st.write(f"Radiacion: {env.get('radiation_mj_m2', 'N/A')} MJ/m²")
            st.write(f"Amanecer: {env.get('calculated_sunrise', 'N/A'):.1f}")
            st.write(f"Atardecer: {env.get('calculated_sunset', 'N/A'):.1f}")

            opt = data.get("optimal_configuration", {})
            st.write(f"Inc. optima: {opt.get('tilt_angle_deg', 'N/A')}°")
            st.write(f"Direccion: {opt.get('facing_direction', 'N/A')}")

# ===================
# TAB SUPERFICIE
# ===================
with tab_surface:
    st.subheader("Superficie de Energia E(θ, φ)")

    col_res, _ = st.columns([1, 4])
    with col_res:
        res_surf = st.slider("Resolucion", 15, 60, 30, key="res_surf")

    surface_plot_E(
        A=p["potencia"],
        theta0=theta0,
        phi0=phi0,
        res=res_surf,
        current_point=(p["theta"], p["phi"], E_actual),
    )

    st.caption(
        "La superficie muestra E(θ, φ) para todo el rango de angulos. "
        "El punto rojo es la configuracion actual."
    )

# ===================
# TAB CONTORNO
# ===================
with tab_contour:
    st.subheader("Curvas de Nivel de E(θ, φ)")

    col_res2, _ = st.columns([1, 4])
    with col_res2:
        res_cont = st.slider("Resolucion", 15, 60, 30, key="res_cont")

    show_grad = st.checkbox("Mostrar gradiente", value=True)

    contour_plot_E(
        A=p["potencia"],
        theta0=theta0,
        phi0=phi0,
        res=res_cont,
        current_point=(p["theta"], p["phi"]),
        grad_point=(dE_th, dE_ph) if show_grad else None,
    )

    st.caption(
        "Las curvas de nivel conectan puntos con igual E(θ, φ). "
        "La flecha roja muestra la direccion del gradiente (maximo crecimiento)."
    )

# ===================
# TAB DERIVADAS
# ===================
with tab_deriv:
    st.subheader("Derivadas Parciales y Gradiente")

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.metric("∂E/∂θ", f"{dE_th:.4f}")
        st.caption(f"en θ = {p['theta']}°")
    with col_d2:
        st.metric("∂E/∂φ", f"{dE_ph:.4f}")
        st.caption(f"en φ = {p['phi']}°")
    with col_d3:
        st.metric("|∇E|", f"{grad_mag:.4f}")
        st.caption(f"direccion: {grad_angle:.1f}°")

    st.divider()

    st.subheader("Derivada Direccional")
    st.caption("Derivada de E en una direccion α (grados desde el eje θ)")

    alpha = st.slider("Direccion α (°)", 0, 360, 45, 1, key="alpha_slider")

    dir_res = obtener_derivada_direccional(
        p["theta"], p["phi"], p["potencia"], theta0, phi0, alpha
    )
    D = dir_res["directional_derivative"]

    c_dir1, c_dir2 = st.columns(2)
    with c_dir1:
        st.metric(
            "D_u E(θ, φ)",
            f"{D:.4f}",
            delta=f"{'Ascenso' if D > 0 else 'Descenso'}",
        )
    with c_dir2:
        grad_dir = grad_angle
        st.metric("Direccion de maximo ascenso", f"{grad_dir:.1f}°")

    st.divider()

    st.subheader("Interpretacion")
    theta_diff = p["theta"] - theta0
    phi_diff = p["phi"] - phi0
    st.write(
        f"- θ - θ₀ = {theta_diff:.1f}° {'(sobreinclinado)' if theta_diff > 0 else '(subinclinado)' if theta_diff < 0 else '(optimo)'}"
    )
    st.write(
        f"- φ - φ₀ = {phi_diff:.1f}° {'(desviado)' if abs(phi_diff) > 5 else '(cerca del optimo)'}"
    )
    st.write(
        f"- El gradiente indica la direccion de maximo aumento de energia: {grad_angle:.1f}°"
    )
    if grad_mag < 0.01:
        st.success(
            "El gradiente es ~0: estas en un punto critico (maximo, minimo o punto de silla)."
        )
    else:
        st.info(
            f"Para maximizar E, ajusta θ y φ en la direccion {grad_angle:.1f}° "
            "(seguir el gradiente). El optimo global es θ₀ = {theta0:.1f}°, φ₀ = {phi0:.1f}°."
        )

# ===================
# TAB OPTIMO
# ===================
with tab_optimal:
    st.subheader("Configuracion Optima")

    col_opt1, col_opt2, col_opt3 = st.columns(3)
    with col_opt1:
        st.metric("θ₀ opt (inclinacion)", f"{theta0:.1f}°")
    with col_opt2:
        st.metric("φ₀ opt (orientacion)", f"{phi0:.1f}°")
    with col_opt3:
        st.metric("E_max (energia maxima)", f"{E_max:.4f} kW")

    st.divider()

    st.subheader("Comparacion Actual vs Optimo")

    col_comp1, col_comp2 = st.columns(2)
    with col_comp1:
        st.write("**Configuracion actual**")
        st.write(f"θ = {p['theta']:.1f}°")
        st.write(f"φ = {p['phi']:.1f}°")
        st.write(f"E = {E_actual:.4f} kW")
    with col_comp2:
        st.write("**Configuracion optima**")
        st.write(f"θ₀ = {theta0:.1f}°")
        st.write(f"φ₀ = {phi0:.1f}°")
        st.write(f"E_max = {E_max:.4f} kW")

    perdida = E_max - E_actual
    perdida_pct = (perdida / E_max * 100) if E_max > 0 else 0

    st.divider()
    col_loss1, col_loss2 = st.columns(2)
    with col_loss1:
        st.metric("Perdida absoluta", f"{perdida:.4f} kW", delta_color="inverse")
    with col_loss2:
        st.metric("Perdida relativa", f"{perdida_pct:.1f}%", delta_color="inverse")

    if perdida_pct < 1:
        st.success("El panel esta practicamente en su configuracion optima.")
    elif perdida_pct < 10:
        st.warning(
            f"Se pierde ~{perdida_pct:.0f}% de energia. "
            f"Ajustar θ a {theta0:.1f}° y φ a {phi0:.1f}°."
        )
    else:
        st.error(
            f"Se pierde ~{perdida_pct:.0f}% de energia. "
            f"Recomendacion: inclinar a {theta0:.1f}° y orientar a {phi0:.1f}°."
        )

    st.divider()

    st.subheader("Plano Tangente (Linealizacion)")
    st.caption("Aproximacion lineal de E cerca de la configuracion actual.")

    theta_eval = st.slider(
        "θ para evaluar", 0, 90, int(p["theta"] + 5), 1, key="theta_tp"
    )
    phi_eval = st.slider("φ para evaluar", 0, 360, int(p["phi"] + 10), 1, key="phi_tp")

    d_th_eval = theta_eval - p["theta"]
    d_ph_eval = phi_eval - p["phi"]
    E_lineal = E_actual + dE_th * d_th_eval + dE_ph * d_ph_eval

    E_exacta = (
        p["potencia"]
        * math.cos(math.radians(theta_eval - theta0))
        * math.cos(math.radians(phi_eval - phi0))
    )

    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        st.metric("E lineal (aprox)", f"{E_lineal:.4f} kW")
    with col_l2:
        st.metric("E exacta", f"{E_exacta:.4f} kW")
    with col_l3:
        st.metric("Error", f"{abs(E_lineal - E_exacta):.4f} kW")

# ===================
# TAB COMPARAR
# ===================
with tab_compare:
    st.subheader("Comparacion de Paneles")

    if len(st.session_state.paneles) < 2:
        st.info("Agrega al menos 2 paneles para comparar.")
    else:
        filas = []
        for j, panel in enumerate(st.session_state.paneles):
            ores = obtener_optimo(panel["latitud"], panel["potencia"])
            t0 = ores["theta0"]
            f0 = ores["phi0"]
            eres = obtener_energia(
                panel["theta"], panel["phi"], panel["potencia"], t0, f0
            )
            filas.append(
                {
                    "Panel": panel["nombre"],
                    "Latitud": panel["latitud"],
                    "θ (°)": panel["theta"],
                    "φ (°)": panel["phi"],
                    "θ₀ (°)": round(t0, 1),
                    "φ₀ (°)": round(f0, 1),
                    "E (kW)": round(eres["E"], 4),
                    "E_max (kW)": round(ores["E_max"], 2),
                    "Rend. (%)": round(eres["E"] / ores["E_max"] * 100, 1),
                    "|∇E|": round(eres["grad_magnitude"], 4),
                }
            )

        df_comp = pd.DataFrame(filas)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)

        st.divider()

        comparison_energy_chart(df_comp)
        comparison_efficiency_chart(df_comp)

# ===================
# TAB INCERTIDUMBRE
# ===================
with tab_uncertainty:
    st.subheader("Analisis de Incertidumbre")

    st.caption(
        "Evalua el impacto de errores angulares en la potencia generada. "
        "Usa los parametros del panel seleccionado."
    )

    delta_th = st.slider("Error θ (°)", 0.0, 20.0, 5.0, 0.5, key="uncer_theta")
    delta_ph = st.slider("Error φ (°)", 0.0, 20.0, 5.0, 0.5, key="uncer_phi")

    if st.button("Calcular incertidumbre", key="calc_uncer"):
        st.session_state["calc_data"] = calcular(
            latitude=p["latitud"],
            longitude=p["longitud"],
            delta_theta=delta_th,
            delta_phi=delta_ph,
            power_gen=p["potencia"],
        )

    if "calc_data" in st.session_state:
        calc_data = st.session_state["calc_data"]
        if calc_data.get("status") == "success":
            col_u1, col_u2, col_u3 = st.columns(3)
            with col_u1:
                st.metric(
                    "Potencia ideal",
                    f"{calc_data['results']['ideal_peak_power_kw']:.3f} kW",
                )
            with col_u2:
                st.metric(
                    "Potencia esperada",
                    f"{calc_data['results']['expected_avg_power_kw']:.3f} kW",
                )
            with col_u3:
                loss = (
                    calc_data["results"]["ideal_peak_power_kw"]
                    - calc_data["results"]["expected_avg_power_kw"]
                )
                st.metric("Perdida por error angular", f"{loss:.3f} kW")
        else:
            st.warning(
                "API de incertidumbre no disponible. Verifica que el servidor Flask este corriendo."
            )

    st.divider()

    st.subheader("Sensibilidad Local (desde E(θ, φ))")
    st.caption("Variacion de E al perturbar θ y φ individualmente.")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        d_th_sens = st.slider("Perturbacion en θ (°)", -10, 10, 5, 1, key="sens_th")
        E_pert_th = (
            p["potencia"]
            * math.cos(math.radians(p["theta"] + d_th_sens - theta0))
            * math.cos(math.radians(p["phi"] - phi0))
        )
        st.metric(
            f"E(θ+{d_th_sens:+d}, φ)",
            f"{E_pert_th:.4f} kW",
            delta=f"{E_pert_th - E_actual:.4f}",
        )

    with col_s2:
        d_ph_sens = st.slider("Perturbacion en φ (°)", -30, 30, 15, 1, key="sens_ph")
        E_pert_ph = (
            p["potencia"]
            * math.cos(math.radians(p["theta"] - theta0))
            * math.cos(math.radians(p["phi"] + d_ph_sens - phi0))
        )
        st.metric(
            f"E(θ, φ+{d_ph_sens:+d})",
            f"{E_pert_ph:.4f} kW",
            delta=f"{E_pert_ph - E_actual:.4f}",
        )

# ===================
# TAB MAPA
# ===================
with tab_map:
    st.subheader("Ubicacion de los Paneles")
    mapa_paneles(st.session_state.paneles)
