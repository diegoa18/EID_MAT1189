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
    import datetime
    today = datetime.date.today()
    df["time_dt"] = pd.to_datetime(today) + pd.to_timedelta(df["time"], unit="h")
    
    fig = px.line(df, x="time_dt", y="power", markers=True)
    if "power_ideal" in df.columns:
        fig.add_scatter(
            x=df["time_dt"], y=df["power_ideal"],
            mode="lines", line=dict(dash="dot", color="orange"),
            name="Potencia ideal (sin sombra)"
        )
    if shadows:
        for s in shadows:
            x0 = pd.to_datetime(today) + pd.to_timedelta(s["start_hour"], unit="h")
            x1 = pd.to_datetime(today) + pd.to_timedelta(s["end_hour"], unit="h")
            fig.add_vrect(
                x0=x0, x1=x1,
                fillcolor="red", opacity=0.1,
                annotation_text=f"{s.get('shade_factor', 0)*100:.0f}% sombra",
                annotation_position="top left",
                line_width=0,
            )
    fig.update_layout(
        xaxis=dict(
            title="Hora del dia",
            type="date",
            tickformat="%H:%M"
        ),
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

    import datetime
    today = datetime.date.today()
    df["time_dt"] = pd.to_datetime(today) + pd.to_timedelta(df["time"], unit="h")

    fig = go.Figure()
    fig.add_scatter(
        x=df["time_dt"], y=df["energy_cumulative"],
        mode="lines", fill="tozeroy", name="Energia acumulada (real)"
    )
    if "energy_ideal_cumulative" in df.columns:
        fig.add_scatter(
            x=df["time_dt"], y=df["energy_ideal_cumulative"],
            mode="lines", line=dict(dash="dot", color="orange"),
            name="Energia acumulada (ideal)"
        )
    fig.update_layout(
        xaxis=dict(
            title="Hora del dia",
            type="date",
            tickformat="%H:%M"
        ),
        yaxis_title="Energia acumulada (kWh)",
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)


def shadow_timeline_chart(shadows):
    if not shadows:
        st.info("No hay eventos de sombra registrados para este panel.")
        return
    import datetime
    today = datetime.date.today()
    fig = go.Figure()
    
    start_of_day = pd.to_datetime(today)
    end_of_day = pd.to_datetime(today) + pd.to_timedelta(24, unit="h")
    
    fig.add_trace(go.Scatter(
        x=[start_of_day, end_of_day],
        y=[0, 0],
        mode="markers",
        marker=dict(opacity=0),
        showlegend=False
    ))
    
    for s in shadows:
        alpha = min(s["shade_factor"] * 0.8 + 0.1, 1.0)
        x0 = pd.to_datetime(today) + pd.to_timedelta(s["start_hour"], unit="h")
        x1 = pd.to_datetime(today) + pd.to_timedelta(s["end_hour"], unit="h")
        fig.add_vrect(
            x0=x0, x1=x1,
            fillcolor=f"rgba(200, 0, 0, {alpha:.2f})",
            line_width=1, line_color="darkred",
            annotation_text=f"{s['shade_factor']*100:.0f}%",
            annotation_position="top left",
        )
    fig.update_layout(
        xaxis=dict(
            title="Hora del dia",
            type="date",
            tickformat="%H:%M",
            range=[start_of_day, end_of_day]
        ),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=10, b=0),
        height=100,
    )
    st.plotly_chart(fig, use_container_width=True)


def shadow_effect_chart(plot_data):
    df = pd.DataFrame(plot_data)
    if "power_ideal" not in df.columns:
        st.info("No hay datos de potencia ideal para comparar.")
        return
    import datetime
    today = datetime.date.today()
    df["time_dt"] = pd.to_datetime(today) + pd.to_timedelta(df["time"], unit="h")

    fig = go.Figure()
    fig.add_scatter(
        x=df["time_dt"], y=df["power_ideal"],
        mode="lines", line=dict(color="orange", dash="dot"),
        name="Sin sombra"
    )
    fig.add_scatter(
        x=df["time_dt"], y=df["power"],
        mode="lines", fill="tonexty", line=dict(color="blue"),
        name="Con sombra"
    )
    fig.update_layout(
        xaxis=dict(
            title="Hora del dia",
            type="date",
            tickformat="%H:%M"
        ),
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


def get_sun_position(lat, lon, hour_float):
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc)
    h = int(hour_float)
    m = int((hour_float - h) * 60)
    if m >= 60:
        h += 1
        m = 0
    h = h % 24
    dt = datetime(today.year, today.month, today.day, h, m, tzinfo=timezone.utc)
    
    try:
        from pysolar.solar import get_altitude, get_azimuth
        alt = get_altitude(lat, lon, dt)
        az = get_azimuth(lat, lon, dt)
    except Exception:
        # Fallback simple path model for local daytime
        time_fraction = (hour_float - 6.0) / 12.0
        alt = 60.0 * math.sin(max(0.0, min(1.0, time_fraction)) * math.pi)
        if alt < 0:
            alt = 0.0
        az = 90.0 + time_fraction * 180.0
    return alt, az


def point_in_polygon_local(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if min(p1y, p2y) < y <= max(p1y, p2y):
            if x <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= xinters:
                    inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def is_point_shaded(x, y, z, alt_deg, az_deg, buildings):
    if alt_deg <= 0:
        return True
    alt_rad = math.radians(alt_deg)
    az_rad = math.radians(az_deg)
    
    dx = math.sin(az_rad)
    dy = math.cos(az_rad)
    dz = math.tan(alt_rad)
    
    for b in buildings:
        poly = b["polygon"]
        height = b["height"]
        
        if z >= height:
            continue
            
        n_samples = 8
        dz_step = (height - z) / n_samples
        shaded = False
        for step in range(n_samples + 1):
            z_curr = z + step * dz_step
            t = (z_curr - z) / dz
            x_curr = x + t * dx
            y_curr = y + t * dy
            if point_in_polygon_local(x_curr, y_curr, poly):
                shaded = True
                break
        if shaded:
            return True
    return False


def get_building_mesh(poly, height):
    n = len(poly)
    x = []
    y = []
    z = []
    
    for px, py in poly:
        x.append(px)
        y.append(py)
        z.append(0.0)
        
    for px, py in poly:
        x.append(px)
        y.append(py)
        z.append(height)
        
    i_idx = []
    j_idx = []
    k_idx = []
    
    for idx in range(n):
        next_idx = (idx + 1) % n
        i_idx.append(idx)
        j_idx.append(next_idx)
        k_idx.append(idx + n)
        
        i_idx.append(next_idx)
        j_idx.append(next_idx + n)
        k_idx.append(idx + n)
        
    for idx in range(1, n - 1):
        i_idx.append(n)
        j_idx.append(n + idx)
        k_idx.append(n + idx + 1)
        
    return x, y, z, i_idx, j_idx, k_idx


def draw_3d_simulation(lat, lon, tilt_deg, azimuth_deg, panel_width, panel_height, hour_float, buildings):
    alt, az = get_sun_position(lat, lon, hour_float)
    
    fig = go.Figure()
    
    x_g = np.linspace(-15, 15, 5)
    y_g = np.linspace(-15, 15, 5)
    x_g, y_g = np.meshgrid(x_g, y_g)
    z_g = np.zeros_like(x_g)
    fig.add_trace(go.Surface(
        x=x_g, y=y_g, z=z_g,
        colorscale=[[0, '#1E3B20'], [1, '#1E3B20']],
        showscale=False,
        opacity=0.6,
        hoverinfo='none',
        name="Terreno"
    ))
    
    for idx, b in enumerate(buildings):
        bx, by, bz, bi, bj, bk = get_building_mesh(b["polygon"], b["height"])
        fig.add_trace(go.Mesh3d(
            x=bx, y=by, z=bz,
            i=bi, j=bj, k=bk,
            color='lightslategrey',
            opacity=0.8,
            name=f"Obstaculo {idx+1}",
            showlegend=True
        ))
        
        if alt > 0:
            shadow_poly = []
            alt_rad = math.radians(alt)
            az_rad = math.radians(az)
            t = b["height"] / math.tan(alt_rad)
            dx = t * math.sin(az_rad)
            dy = t * math.cos(az_rad)
            
            for px, py in b["polygon"]:
                shadow_poly.append((px - dx, py - dy))
            
            sp_x = [p[0] for p in shadow_poly]
            sp_y = [p[1] for p in shadow_poly]
            sp_z = [0.01] * len(shadow_poly)
            
            sp_x.append(shadow_poly[0][0])
            sp_y.append(shadow_poly[0][1])
            sp_z.append(0.01)
            
            fig.add_trace(go.Mesh3d(
                x=sp_x, y=sp_y, z=sp_z,
                color='#111111',
                opacity=0.6,
                name=f"Sombra Obstaculo {idx+1}",
                showlegend=False
            ))
            
    col_offsets = [-1.5, 0.0, 1.5]
    row_offsets = [-1.2, 1.2]
    
    n_u, n_v = 8, 8
    u = np.linspace(-panel_width/2, panel_width/2, n_u)
    v = np.linspace(-panel_height/2, panel_height/2, n_v)
    u_grid, v_grid = np.meshgrid(u, v)
    
    tilt_rad = math.radians(tilt_deg)
    az_panel_rad = math.radians(azimuth_deg)
    
    x_rot = u_grid * math.cos(az_panel_rad) - v_grid * math.cos(tilt_rad) * math.sin(az_panel_rad)
    y_rot = u_grid * math.sin(az_panel_rad) + v_grid * math.cos(tilt_rad) * math.cos(az_panel_rad)
    z_rot = v_grid * math.sin(tilt_rad)
    
    z_min = np.min(z_rot)
    z_shift = 0.5 - z_min
    z_rot += z_shift
    
    panel_colorscale = [
        [0.0, '#102035'],
        [0.2, '#182C4C'],
        [0.7, '#D48C20'],
        [1.0, '#FFD700']
    ]
    
    for r_idx, r_off in enumerate(row_offsets):
        for c_idx, c_off in enumerate(col_offsets):
            px = x_rot + c_off
            py = y_rot + r_off
            pz = z_rot
            
            shade_matrix = np.zeros_like(px)
            for vi in range(n_v):
                for ui in range(n_u):
                    pt_x = px[vi, ui]
                    pt_y = py[vi, ui]
                    pt_z = pz[vi, ui]
                    
                    is_shaded = is_point_shaded(pt_x, pt_y, pt_z, alt, az, buildings)
                    
                    if is_shaded:
                        shade_matrix[vi, ui] = 0.05
                    else:
                        sun_factor = max(0.15, math.sin(math.radians(alt)))
                        shade_matrix[vi, ui] = sun_factor
            
            fig.add_trace(go.Surface(
                x=px, y=py, z=pz,
                surfacecolor=shade_matrix,
                colorscale=panel_colorscale,
                cmin=0.0, cmax=1.0,
                showscale=False,
                name=f"Panel R{r_idx+1}C{c_idx+1}",
                hoverinfo='all'
            ))
            
    if alt > 0:
        sun_dist = 20.0
        alt_r = math.radians(alt)
        az_r = math.radians(az)
        sun_x = sun_dist * math.sin(az_r) * math.cos(alt_r)
        sun_y = sun_dist * math.cos(az_r) * math.cos(alt_r)
        sun_z = sun_dist * math.sin(alt_r)
        
        fig.add_trace(go.Scatter3d(
            x=[sun_x], y=[sun_y], z=[sun_z],
            mode='markers',
            marker=dict(
                size=12,
                color='#FFD700',
                opacity=0.95,
                line=dict(color='orange', width=2)
            ),
            name="Sol"
        ))
        
        fig.add_trace(go.Scatter3d(
            x=[sun_x, 0.0], y=[sun_y, 0.0], z=[sun_z, 0.5],
            mode='lines',
            line=dict(color='rgba(255, 215, 0, 0.25)', width=3, dash='dash'),
            name="Rayos Solares",
            showlegend=False
        ))
        
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X (m)", range=[-15, 15]),
            yaxis=dict(title="Y (m)", range=[-15, 15]),
            zaxis=dict(title="Z (m)", range=[0, 15]),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.5)
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        title=f"Incidencia Solar y Sombras Proyectadas (Sol: Alt={alt:.1f}°, Az={az:.1f}°)",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    return fig
