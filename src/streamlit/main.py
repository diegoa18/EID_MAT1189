import math

import pandas as pd

def float_to_time_str(h):
    try:
        h = float(h)
    except (ValueError, TypeError):
        return str(h)
    hours = int(h)
    minutes = int(round((h - hours) * 60))
    if minutes == 60:
        hours = (hours + 1) % 24
        minutes = 0
    return f"{hours:02d}:{minutes:02d}"
from grapics import (
    accumulated_energy_chart,
    comparison_efficiency_chart,
    comparison_energy_chart,
    contour_plot_E,
    shadow_effect_chart,
    shadow_timeline_chart,
    simulation_chart,
    surface_plot_E,
    draw_3d_simulation,
)
from mapa import mapa_paneles
from sidebar import render_sidebar

import streamlit as st
from api import (
    calcular,
    obtener_derivada_direccional,
    obtener_energia,
    obtener_hessiano,
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

st.markdown(
    """
<style>
    section[data-testid="stSidebar"] {
        width: 400px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

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
    tab_hessian,
    tab_optimal,
    tab_compare,
    tab_uncertainty,
    tab_daily,
    tab_shadows,
    tab_3d_sim,
    tab_map,
) = st.tabs(
    [
        "Panel",
        "Vista 3D de Potencia (Superficie)",
        "Mapa de Rendimiento (Contorno)",
        "Sensibilidad Física (Derivadas/Gradiente)",
        "Estabilidad de Diseño (Hessiano)",
        "Punto Óptimo (Optimización)",
        "Comparar Paneles",
        "Tolerancia a Errores (Incertidumbre)",
        "Generación Diaria (Riemann)",
        "Estudio de Sombras (Integral)",
        "Simulador 3D (Tiempo Real)",
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



# ===================
# TAB SUPERFICIE
# ===================
with tab_surface:
    st.subheader("Mapa 3D de Generación de Energía (Superficie de Energía $E(\\theta, \\phi)$)")

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
        "Este gráfico 3D ilustra la potencia teórica estimada según la inclinación y orientación de los paneles "
        "(Superficie de Energía $E(\\theta, \\phi)$). El punto rojo marca la posición y captación de energía actual de sus paneles."
    )

# ===================
# TAB CONTORNO
# ===================
with tab_contour:
    st.subheader("Mapa de Rendimiento Solar (Curvas de Nivel y Contornos de Energía)")

    col_res2, _ = st.columns([1, 4])
    with col_res2:
        res_cont = st.slider("Resolucion", 15, 60, 30, key="res_cont")

    show_grad = st.checkbox("Mostrar dirección de mejora recomendada", value=True)

    contour_plot_E(
        A=p["potencia"],
        theta0=theta0,
        phi0=phi0,
        res=res_cont,
        current_point=(p["theta"], p["phi"]),
        grad_point=(dE_th, dE_ph) if show_grad else None,
    )

    st.caption(
        "El mapa muestra líneas que conectan orientaciones e inclinaciones que producen la misma potencia (Curvas de Nivel). "
        "La flecha roja indica la dirección de ajuste recomendada para obtener el incremento más rápido en captación de energía (Gradiente)."
    )

# ===================
# TAB DERIVADAS
# ===================
with tab_deriv:
    st.subheader("Sensibilidad al Movimiento y Dirección de Mejora (Derivadas Parciales y Gradiente)")

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.metric("Sensibilidad a la Inclinación (∂E/∂θ)", f"{dE_th:.4f}")
        st.caption(f"en inclinación θ = {p['theta']}°")
    with col_d2:
        st.metric("Sensibilidad a la Orientación (∂E/∂φ)", f"{dE_ph:.4f}")
        st.caption(f"en orientación φ = {p['phi']}°")
    with col_d3:
        st.metric("Potencial de Ganancia Rápida (|∇E|)", f"{grad_mag:.4f}")
        st.caption(f"rumbo recomendado: {grad_angle:.1f}°")

    st.divider()

    st.subheader("Simulación de Sensibilidad en Dirección Específica (Derivada Direccional)")
    st.caption("Muestra cuánta energía se gana o pierde al desviar el panel en un ángulo específico α respecto a su inclinación actual (Derivada Direccional).")

    alpha = st.slider("Dirección de Desviación Propuesta α (°)", 0, 360, 45, 1, key="alpha_slider")

    dir_res = obtener_derivada_direccional(
        p["theta"], p["phi"], p["potencia"], theta0, phi0, alpha
    )
    D = dir_res["directional_derivative"]

    c_dir1, c_dir2 = st.columns(2)
    with c_dir1:
        st.metric(
            "Tasa de Cambio en la Dirección (Derivada Direccional $D_u E$)",
            f"{D:.4f}",
            delta=f"{'Ganancia de Energía' if D > 0 else 'Pérdida de Energía'}",
        )
    with c_dir2:
        grad_dir = grad_angle
        st.metric("Dirección del Mayor Incremento (Máximo Ascenso)", f"{grad_dir:.1f}°")

    st.divider()

    st.subheader("Diagnóstico Comercial e Interpretación Matemática")
    theta_diff = p["theta"] - theta0
    phi_diff = p["phi"] - phi0
    
    st.write(
        f"📍 **Ajuste de inclinación respecto al óptimo ($θ - θ_0$):** {theta_diff:.1f}° "
        f"{'(sobreinclinado, capta menos sol)' if theta_diff > 0 else '(subinclinado, capta menos sol)' if theta_diff < 0 else '(inclinación perfecta)'}"
    )
    st.write(
        f"🧭 **Desviación de orientación respecto al óptimo ($φ - φ_0$):** {phi_diff:.1f}° "
        f"{'(desviado, necesita corrección)' if abs(phi_diff) > 5 else '(orientación óptima)'}"
    )
    st.write(
        f"📈 **Dirección recomendada de ajuste rápido (Gradiente):** Mover el panel en una dirección de {grad_angle:.1f}° "
        f"desde la inclinación actual proporcionará el mayor incremento inmediato en la captación solar."
    )
    if grad_mag < 0.01:
        st.success(
            "✅ **¡Diseño optimizado al límite!** El gradiente es casi cero ($|∇E| \\approx 0$), lo que significa que el panel está posicionado en un punto de máxima generación solar (Punto Crítico/Máximo Local)."
        )
    else:
        st.info(
            f"💡 **Recomendación técnica para venta:** Para elevar la potencia del panel, debemos ajustar "
            f"la inclinación y orientación siguiendo la dirección del Gradiente ({grad_angle:.1f}°). "
            f"El punto de diseño perfecto (Máximo Global) se encuentra en una inclinación de $θ_0$ = {theta0:.1f}° y orientación de $φ_0$ = {phi0:.1f}°."
        )

# ===================
# TAB HESSIANO
# ===================
with tab_hessian:
    st.subheader("Análisis de Estabilidad y Curvatura del Diseño (Matriz Hessiana y Puntos Críticos)")
    st.caption(
        "Determina la estabilidad de la eficiencia del panel solar alrededor del punto de diseño actual, identificando si estamos en un pico de generación, valle, o punto inestable (Criterio de la Segunda Derivada / Matriz Hessiana)."
    )

    hessian_res = obtener_hessiano(p["theta"], p["phi"], p["potencia"], theta0, phi0)

    if hessian_res.get("status") == "success":
        mat = hessian_res["hessian_matrix"]
        det = hessian_res["determinant"]
        cls = hessian_res["classification"]
        is_crit = hessian_res["is_critical"]
        eig1, eig2 = hessian_res["eigenvalues"]

        st.write("**Matriz de Estabilidad de Pendiente (Matriz Hessiana $H(θ, φ)$):**")
        st.latex(
            r"""
        H = \begin{pmatrix}
        """
            + f"{mat[0][0]:.4f} & {mat[0][1]:.4f} \\\\ {mat[1][0]:.4f} & {mat[1][1]:.4f}"
            + r"""
        \end{pmatrix}
        """
        )

        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            st.metric("Índice de Estabilidad de Curvatura (Determinante |H|)", f"{det:.4f}")
        with col_h2:
            st.metric("Tasa Global de Curvatura (Traza tr(H))", f"{mat[0][0] + mat[1][1]:.4f}")
        with col_h3:
            st.write("**Factores de Curvatura Principal (Autovalores/Eigenvalues):**")
            st.write(f"λ₁ = {eig1:.4f}")
            st.write(f"λ₂ = {eig2:.4f}")

        st.divider()
        st.write("**Clasificación de la Eficiencia en este Punto (Punto Crítico):**")
        if is_crit:
            st.success(
                f"La configuración actual ES un punto de equilibrio operativo (Punto Crítico). Clasificación comercial: **{cls}**"
            )
        else:
            st.warning(
                f"La configuración actual NO es un punto de equilibrio óptimo (Punto Crítico / el gradiente no es cero). Esto significa que aún hay margen para reorientar el panel y ganar más energía."
            )

        st.info(
            "💡 **Explicación Comercial/Matemática:** Para garantizar que el panel está en su máxima generación posible, primero buscamos un punto con cambio nulo (Gradiente cero) y luego confirmamos que la superficie se curva hacia abajo en todas las direcciones (Determinante del Hessiano > 0 y autovalores negativos, lo que clasifica el punto como un Máximo Local estable)."
        )
    else:
        st.error("Error obteniendo los datos del Hessiano desde la API.")

# ===================
# TAB OPTIMO
# ===================
with tab_optimal:
    st.subheader("Punto de Máxima Generación (Configuración Óptima)")

    col_opt1, col_opt2, col_opt3 = st.columns(3)
    with col_opt1:
        st.metric("Inclinación Óptima (θ₀)", f"{theta0:.1f}°")
    with col_opt2:
        st.metric("Orientación Óptima (φ₀)", f"{phi0:.1f}°")
    with col_opt3:
        st.metric("Potencia Máxima Teórica (E_max)", f"{E_max:.4f} kW")

    st.divider()

    st.subheader("Análisis Comparativo: Estado Actual vs Estado Óptimo")

    col_comp1, col_comp2 = st.columns(2)
    with col_comp1:
        st.write("**Configuración Actual**")
        st.write(f"Inclinación θ = {p['theta']:.1f}°")
        st.write(f"Orientación φ = {p['phi']:.1f}°")
        st.write(f"Potencia E = {E_actual:.4f} kW")
    with col_comp2:
        st.write("**Configuración Óptima Recomendada**")
        st.write(f"Inclinación θ₀ = {theta0:.1f}°")
        st.write(f"Orientación φ₀ = {phi0:.1f}°")
        st.write(f"Potencia Máxima E_max = {E_max:.4f} kW")

    perdida = E_max - E_actual
    perdida_pct = (perdida / E_max * 100) if E_max > 0 else 0

    st.divider()
    col_loss1, col_loss2 = st.columns(2)
    with col_loss1:
        st.metric("Pérdida de Potencia Absoluta", f"{perdida:.4f} kW", delta_color="inverse")
    with col_loss2:
        st.metric("Porcentaje de Potencia Perdida", f"{perdida_pct:.1f}%", delta_color="inverse")

    if perdida_pct < 1:
        st.success("El panel está prácticamente en su configuración óptima.")
    elif perdida_pct < 10:
        st.warning(
            f"Se pierde ~{perdida_pct:.0f}% de energía. "
            f"Ajustar inclinación θ a {theta0:.1f}° y orientación φ a {phi0:.1f}°."
        )
    else:
        st.error(
            f"Se pierde ~{perdida_pct:.0f}% de energía. "
            f"Recomendación: inclinar a {theta0:.1f}° y orientar a {phi0:.1f}°."
        )

    st.divider()

    st.subheader("Estimación Rápida de Variación de Potencia (Plano Tangente y Linealización)")
    st.caption("Usa la primera aproximación derivada (Plano Tangente) para predecir de forma simple cuánta potencia tendrá el panel ante pequeños cambios en la posición, ideal para hacer cálculos rápidos sin recalcular el modelo completo.")

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
        st.metric("Potencia Aproximada (Linealización)", f"{E_lineal:.4f} kW")
    with col_l2:
        st.metric("Potencia Real Esperada (Exacta)", f"{E_exacta:.4f} kW")
    with col_l3:
        st.metric("Margen de Error del Modelo Lineal", f"{abs(E_lineal - E_exacta):.4f} kW")

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
    st.subheader("Tolerancia al Margen de Error en la Instalación (Análisis de Incertidumbre Angular)")

    st.caption(
        "Determina la pérdida promedio esperada si los instaladores cometen pequeños desvíos de inclinación u orientación durante el montaje físico, utilizando integrales dobles para promediar la potencia en el rango de error."
    )

    delta_th = st.slider("Margen de Error de Inclinación θ (°)", 0.0, 20.0, 5.0, 0.5, key="uncer_theta")
    delta_ph = st.slider("Margen de Error de Orientación φ (°)", 0.0, 20.0, 5.0, 0.5, key="uncer_phi")

    if st.button("Calcular Tolerancia a Errores", key="calc_uncer"):
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
            results = calc_data.get("results", {})
            ideal_peak = results.get("ideal_peak_power_kw", 0.0)
            expected_avg = results.get("expected_avg_power_kw", 0.0)
            loss = ideal_peak - expected_avg
            col_u1, col_u2, col_u3 = st.columns(3)
            with col_u1:
                st.metric("Potencia Ideal Estimada", f"{ideal_peak:.3f} kW")
            with col_u2:
                st.metric("Potencia Promedio Real con Error (Esperada)", f"{expected_avg:.3f} kW")
            with col_u3:
                st.metric("Pérdida por Margen de Error (Vía Integrales)", f"{loss:.3f} kW")
        else:
            st.warning(
                "API de incertidumbre no disponible. Verifica que el servidor Flask este corriendo."
            )

    st.divider()

    st.subheader("Simulación de Desviaciones Individuales (Sensibilidad Local)")
    st.caption("Muestra de forma rápida cómo cambia la potencia si solo se desvía la inclinación o solo la orientación por separado.")

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
# TAB CONSUMO DIARIO
# ===================
with tab_daily:
    st.subheader("Rendimiento Energético a lo Largo del Día (Simulación mediante Sumas de Riemann)")
    st.caption("Calcula y simula la generación de energía total en el transcurso de un día, utilizando aproximaciones de rectángulos (Sumas de Riemann) para integrar la curva de potencia real con sombras.")

    if not p.get("simulacion") or p["simulacion"].get("status") != "success":
        st.info("Ejecuta 'Simular dia' desde la barra lateral para ver los datos.")
    else:
        data = p["simulacion"]
        plot_data = data["plot_data"]
        shadows = data["results"].get("applied_shadows", [])

        total_daily_energy = data["results"].get("total_daily_energy_kwh", data["results"].get("daily_energy_kwh", 0))
        ideal_daily_energy = data["results"].get("ideal_daily_energy_kwh", total_daily_energy)
        energy_loss = data["results"].get("energy_loss_from_shadows_kwh", 0.0)

        col_met1, col_met2, col_met3 = st.columns(3)
        with col_met1:
            st.metric("Generación Diaria Real Estimada (Sumas de Riemann)", f"{total_daily_energy:.2f} kWh")
        with col_met2:
            st.metric("Generación Ideal Comercial (Sin Sombra)", f"{ideal_daily_energy:.2f} kWh")
        with col_met3:
            st.metric("Pérdida por Obstrucciones Externas", f"{energy_loss:.3f} kWh", delta_color="inverse")

        st.divider()

        st.subheader("Curva de Potencia Diaria")
        simulation_chart(plot_data, shadows)

        st.divider()

        st.subheader("Energia Acumulada")
        accumulated_energy_chart(plot_data)

        st.divider()

        env = data.get("environment", {})
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            st.metric("Radiacion solar", f"{env.get('radiation_mj_m2', 'N/A')} MJ/m²")
        with col_e2:
            st.metric("Amanecer", float_to_time_str(env.get('calculated_sunrise', 'N/A')))
        with col_e3:
            st.metric("Atardecer", float_to_time_str(env.get('calculated_sunset', 'N/A')))

        st.divider()

        st.subheader("Datos Horarios")
        df_plot = pd.DataFrame(plot_data)
        cols_show = ["time", "power", "power_ideal", "shade_factor"]
        cols_show = [c for c in cols_show if c in df_plot.columns]
        df_display = df_plot[cols_show].copy()
        col_map = {
            "time": "Hora",
            "power": "Potencia (kW)",
            "power_ideal": "Potencia ideal (kW)",
            "shade_factor": "Fraccion sombra",
        }
        df_display = df_display.rename(columns=col_map)
        if "Hora" in df_display.columns:
            df_display["Hora"] = df_display["Hora"].apply(float_to_time_str)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

# ===================
# TAB SOMBRAS
# ===================
with tab_shadows:
    st.subheader("Análisis de Sombras del Entorno (Integral Doble de Superficie)")
    st.caption("Identifica y calcula la reducción de luz en el panel debido a obstáculos físicos cercanos, integrando la porción de área obstruida en cada instante (Integral Doble de Área).")

    if not p.get("simulacion") or p["simulacion"].get("status") != "success":
        st.info("Ejecuta 'Simular dia' desde la barra lateral para ver los datos.")
    else:
        data = p["simulacion"]
        plot_data = data["plot_data"]
        shadows = data["results"].get("applied_shadows", [])

        if shadows:
            st.subheader("Linea de Tiempo de Sombras")
            shadow_timeline_chart(shadows)

            st.divider()

            st.subheader("Eventos de Sombra")
            df_shadows = pd.DataFrame(shadows)
            df_shadows["Hora inicio"] = df_shadows["start_hour"].apply(float_to_time_str)
            df_shadows["Hora fin"] = df_shadows["end_hour"].apply(float_to_time_str)
            df_shadows["Duracion (h)"] = (df_shadows["end_hour"] - df_shadows["start_hour"]).round(2)
            df_shadows["Factor sombra"] = df_shadows["shade_factor"].apply(lambda x: f"{x*100:.1f}%")
            df_display_shadows = df_shadows[["Hora inicio", "Hora fin", "Duracion (h)", "Factor sombra"]]
            st.dataframe(df_display_shadows, use_container_width=True, hide_index=True)

            st.divider()

            st.subheader("Impacto Comercial de Sombras")
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                perdida = data["results"].get("energy_loss_from_shadows_kwh", 0)
                st.metric("Pérdida por Obstrucción de Área", f"{perdida:.3f} kWh")
            with col_s2:
                ideal = data["results"].get("ideal_daily_energy_kwh", 0)
                pct = (perdida / ideal * 100) if ideal > 0 else 0
                st.metric("Rendimiento Perdido por Sombras", f"{pct:.1f}%")
            with col_s3:
                horas_sombra = sum(s["end_hour"] - s["start_hour"] for s in shadows)
                st.metric("Duración Total de Sombreado", f"{horas_sombra:.2f} h")

            st.divider()

            st.subheader("Potencia: Con Sombra vs Ideal")
            shadow_effect_chart(plot_data)
        else:
            st.success("No se detectaron sombras significativas para este panel en esta ubicacion y fecha.")
            st.caption("Esto puede deberse a que no hay edificios cercanos o la altura del sol reduce el efecto.")

# ===================
# TAB SIMULACION 3D
# ===================
@st.cache_data
def get_buildings(lat, lon):
    radius = 80
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      way["building"](around:{radius},{lat},{lon});
      relation["building"](around:{radius},{lat},{lon});
    );
    out body geom;
    """
    buildings = []
    try:
        import requests
        headers = {"User-Agent": "SolarOptimizationApp/1.0"}
        response = requests.get(
            overpass_url,
            params={"data": overpass_query},
            headers=headers,
            timeout=8,
        )
        data = response.json()
        
        deg_to_m_lat = 111320.0
        deg_to_m_lon = 40075000.0 * math.cos(math.radians(lat)) / 360.0
        
        for element in data.get("elements", []):
            if "geometry" not in element:
                continue
            tags = element.get("tags", {})
            height = float(tags.get("height", 0))
            if height == 0:
                levels = float(tags.get("building:levels", 1))
                height = levels * 3.0
                
            pts = []
            for node in element["geometry"]:
                dy = (node["lat"] - lat) * deg_to_m_lat
                dx = (node["lon"] - lon) * deg_to_m_lon
                pts.append((dx, dy))
                
            if len(pts) >= 3:
                buildings.append({"polygon": pts, "height": height})
    except Exception:
        pass
        
    if not buildings:
        buildings = [
            {
                "polygon": [
                    (6.0, 4.0),
                    (9.0, 4.0),
                    (9.0, 10.0),
                    (6.0, 10.0)
                ],
                "height": 12.0
            },
            {
                "polygon": [
                    (-10.0, -8.0),
                    (-7.0, -8.0),
                    (-7.0, -5.0),
                    (-10.0, -5.0)
                ],
                "height": 8.0
            }
        ]
    return buildings


with tab_3d_sim:
    st.subheader("Simulación de Incidencia Solar y Sombras en 3D")
    st.caption("Visualización interactiva tridimensional en tiempo real del panel solar recibiendo luz solar y las sombras proyectadas por edificios/obstáculos circundantes.")
    
    h_sim = st.slider("Hora de la simulación", min_value=6.0, max_value=18.0, value=12.0, step=0.25, format="%g h")
    h_int = int(h_sim)
    m_int = int((h_sim - h_int) * 60)
    st.markdown(f"**Hora seleccionada: {h_int:02d}:{m_int:02d}**")
    
    buildings_local = get_buildings(p["latitud"], p["longitud"])
    
    fig_3d = draw_3d_simulation(
        lat=p["latitud"],
        lon=p["longitud"],
        tilt_deg=p["theta"],
        azimuth_deg=p["phi"],
        panel_width=p.get("ancho", 1.0),
        panel_height=p.get("alto", 1.6),
        hour_float=h_sim,
        buildings=buildings_local
    )
    
    st.plotly_chart(fig_3d, use_container_width=True)
    st.info("💡 **Guía de Interacción:** Mantén presionado y arrastra el cursor sobre el gráfico para rotar el punto de vista 3D. Usa la rueda del mouse para hacer zoom.")


# ===================
# TAB MAPA
# ===================
with tab_map:
    st.subheader("Ubicacion de los Paneles")
    mapa_paneles(st.session_state.paneles)
