import folium
from streamlit_folium import st_folium

import streamlit as st


def selector_mapa(key="mapa", lat_default=-36.82, lon_default=-73.05):
    modo = st.radio(
        "Modo de seleccion",
        ["Manual", "Mapa"],
        horizontal=True,
        key=f"modo_{key}",
    )

    if modo == "Manual":
        col_lat, col_lon = st.columns(2)
        with col_lat:
            lat = st.number_input(
                "Latitud", value=lat_default, format="%.4f", step=0.5, key=f"lat_{key}"
            )
        with col_lon:
            lon = st.number_input(
                "Longitud", value=lon_default, format="%.4f", step=0.5, key=f"lon_{key}"
            )
        return lat, lon

    state_key = f"_map_sel_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {
            "lat": lat_default,
            "lon": lon_default,
            "clicked": False,
        }

    state = st.session_state[state_key]

    m = folium.Map(location=[lat_default, lon_default], zoom_start=5)
    folium.Marker(
        [state["lat"], state["lon"]],
        popup=f"{state['lat']:.4f}, {state['lon']:.4f}",
        tooltip="Ubicacion seleccionada",
        icon=folium.Icon(color="red"),
    ).add_to(m)

    output = st_folium(m, width=700, height=400, key=f"folium_{key}")

    if output and output.get("last_clicked"):
        state["lat"] = output["last_clicked"]["lat"]
        state["lon"] = output["last_clicked"]["lng"]
        st.session_state[f"lat_{key}_fine"] = state["lat"]
        st.session_state[f"lon_{key}_fine"] = state["lon"]
        state["clicked"] = True

    lat = state["lat"]
    lon = state["lon"]

    if state.get("clicked"):
        st.success(f"Ubicacion seleccionada: {lat:.4f}, {lon:.4f}")
    else:
        st.info("Haz clic en el mapa para seleccionar un punto.")

    col_lat, col_lon = st.columns(2)
    with col_lat:
        lat = st.number_input(
            "Latitud", value=lat, format="%.4f", step=0.5, key=f"lat_{key}_fine"
        )
    with col_lon:
        lon = st.number_input(
            "Longitud", value=lon, format="%.4f", step=0.5, key=f"lon_{key}_fine"
        )

    state["lat"] = lat
    state["lon"] = lon

    return lat, lon


def mapa_paneles(paneles):
    if not paneles:
        st.info("No hay paneles para mostrar en el mapa.")
        return

    center_lat = paneles[0]["latitud"]
    center_lon = paneles[0]["longitud"]

    m = folium.Map(location=[center_lat, center_lon], zoom_start=3)

    for p in paneles:
        popup_text = (
            f"<b>{p['nombre']}</b><br>"
            f"Lat: {p['latitud']:.4f}<br>"
            f"Lon: {p['longitud']:.4f}<br>"
            f"θ: {p['theta']}° | φ: {p['phi']}°<br>"
            f"A: {p['potencia']} kW"
        )
        folium.Marker(
            [p["latitud"], p["longitud"]],
            popup=popup_text,
            tooltip=p["nombre"],
            icon=folium.Icon(color="red", icon="solar-panel", prefix="fa"),
        ).add_to(m)

    st_folium(m, width=1400, height=500)
