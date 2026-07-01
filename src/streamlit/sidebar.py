from persistencia import guardar_paneles

import streamlit as st
from api import simular
from mapa import selector_mapa


@st.dialog("Agregar panel")
def dialogo_agregar_panel():
    nombre = st.text_input("Nombre", "Panel nuevo")
    lat, lon = selector_mapa(key="nuevo", lat_default=-36.82, lon_default=-73.05)
    col_a, col_b = st.columns(2)
    with col_a:
        ancho = st.number_input("Ancho (m)", min_value=0.1, value=2.0, step=0.1)
    with col_b:
        alto = st.number_input("Alto (m)", min_value=0.1, value=1.2, step=0.1)
    potencia = st.number_input("Potencia A (kW)", min_value=0.1, value=1.0, step=0.1)
    col_t, col_p = st.columns(2)
    with col_t:
        theta = st.slider("θ — Inclinación (°)", 0, 90, 30)
    with col_p:
        phi = st.slider("φ — Orientación (°)", 0, 360, 180)
    estacion = st.selectbox("Estación", ["summer", "autumn", "winter", "spring"])

    if st.button("Crear panel", use_container_width=True):
        uid = st.session_state.next_uid
        st.session_state.next_uid = uid + 1
        st.session_state.paneles.append(
            {
                "uid": uid,
                "nombre": nombre,
                "latitud": lat,
                "longitud": lon,
                "ancho": ancho,
                "alto": alto,
                "potencia": potencia,
                "theta": theta,
                "phi": phi,
                "estacion": estacion,
                "simulacion": None,
            }
        )
        st.session_state.panel_index = len(st.session_state.paneles) - 1
        guardar_paneles(st.session_state.paneles)
        st.rerun()


def render_sidebar():
    with st.sidebar:
        st.title("Paneles")

        if st.button("+ Agregar panel", use_container_width=True):
            dialogo_agregar_panel()

        st.divider()

        if st.session_state.paneles:
            nombres = [p["nombre"] for p in st.session_state.paneles]
            idx = st.session_state.panel_index
            if idx is None or idx >= len(nombres):
                idx = 0
                st.session_state.panel_index = 0
            sel = st.selectbox(
                "Seleccionar panel",
                range(len(nombres)),
                format_func=lambda i: nombres[i],
                index=idx,
                key="panel_selector",
            )
            st.session_state.panel_index = sel

        st.divider()

        if st.session_state.panel_index is not None:
            i = st.session_state.panel_index
            p = st.session_state.paneles[i]

            st.subheader(p["nombre"])

            uid = p["uid"]
            p["nombre"] = st.text_input("Nombre", value=p["nombre"], key=f"name_{uid}")

            col_lat, col_lon = st.columns(2)
            with col_lat:
                p["latitud"] = st.number_input(
                    "Latitud",
                    value=p["latitud"],
                    format="%.4f",
                    step=0.5,
                    key=f"lat_{uid}",
                )
            with col_lon:
                p["longitud"] = st.number_input(
                    "Longitud",
                    value=p["longitud"],
                    format="%.4f",
                    step=0.5,
                    key=f"lon_{uid}",
                )

            col_w, col_h = st.columns(2)
            with col_w:
                p["ancho"] = st.number_input(
                    "Ancho (m)",
                    min_value=0.1,
                    value=p["ancho"],
                    step=0.1,
                    key=f"w_{uid}",
                )
            with col_h:
                p["alto"] = st.number_input(
                    "Alto (m)", min_value=0.1, value=p["alto"], step=0.1, key=f"h_{uid}"
                )

            p["potencia"] = st.number_input(
                "Potencia A (kW)",
                min_value=0.1,
                value=p["potencia"],
                step=0.1,
                key=f"pwr_{uid}",
            )

            st.caption("Angulos del panel")
            p["theta"] = st.slider(
                "θ — Inclinación (°)", 0, 90, int(p["theta"]), 1, key=f"theta_{uid}"
            )
            p["phi"] = st.slider(
                "φ — Orientación (°)", 0, 360, int(p["phi"]), 1, key=f"phi_{uid}"
            )

            p["estacion"] = st.selectbox(
                "Estación",
                ["summer", "autumn", "winter", "spring"],
                index=["summer", "autumn", "winter", "spring"].index(p["estacion"]),
                key=f"season_{uid}",
            )

            if st.button("Simular dia", use_container_width=True, key=f"sim_{uid}"):
                with st.spinner("Simulando..."):
                    p["simulacion"] = simular(
                        latitude=p["latitud"],
                        longitude=p["longitud"],
                        width=p["ancho"],
                        height=p["alto"],
                        season=p["estacion"],
                        power_gen_kw=p["potencia"],
                    )

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(
                    "🗑️ Eliminar", use_container_width=True, key=f"delete_btn_{uid}"
                ):
                    st.session_state[f"_delete_confirm_{uid}"] = True

            confirm_key = f"_delete_confirm_{uid}"
            if st.session_state.get(confirm_key):
                st.warning("¿Eliminar este panel permanentemente?")
                c_yes, c_no = st.columns(2)
                with c_yes:
                    if st.button("Sí, eliminar", use_container_width=True, key=f"del_yes_{uid}"):
                        st.session_state.paneles.pop(st.session_state.panel_index)
                        if st.session_state.panel_index >= len(st.session_state.paneles):
                            st.session_state.panel_index = (
                                len(st.session_state.paneles) - 1
                                if st.session_state.paneles
                                else None
                            )
                        st.session_state[confirm_key] = False
                        guardar_paneles(st.session_state.paneles)
                        st.rerun()
                with c_no:
                    if st.button("Cancelar", use_container_width=True, key=f"del_no_{uid}"):
                        st.session_state[confirm_key] = False
                        st.rerun()

        guardar_paneles(st.session_state.paneles)
