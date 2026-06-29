import math
from typing import Any, Dict

import requests

URL_SIMULATE = "http://127.0.0.1:5000/api/simulate"
URL_CALCULATE = "http://127.0.0.1:5000/api/calculate"


def simular(
    latitude, longitude, width, height, season, power_gen_kw=1.0
) -> Dict[str, Any]:
    datos = {
        "latitude": latitude,
        "longitude": longitude,
        "width_m": width,
        "height_m": height,
        "season": season,
        "power_gen_kw": power_gen_kw,
    }

    try:
        response = requests.post(URL_SIMULATE, json=datos, timeout=10)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


def calcular(
    latitude, longitude, delta_theta, delta_phi, power_gen=1.0
) -> Dict[str, Any]:

    datos = {
        "latitude": latitude,
        "longitude": longitude,
        "delta_theta": delta_theta,
        "delta_phi": delta_phi,
        "power_gen": power_gen,
    }

    try:
        response = requests.post(URL_CALCULATE, json=datos, timeout=10)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


def obtener_energia(theta, phi, A, theta0, phi0) -> Dict[str, Any]:
    # aqui entra la api rodri qlo mueve la raja
    d_theta = math.radians(theta - theta0)
    d_phi = math.radians(phi - phi0)
    E = A * math.cos(d_theta) * math.cos(d_phi)
    dE_dtheta = -A * math.sin(d_theta) * math.cos(d_phi)
    dE_dphi = -A * math.cos(d_theta) * math.sin(d_phi)
    grad_mag = math.sqrt(dE_dtheta**2 + dE_dphi**2)
    grad_angle = math.degrees(math.atan2(dE_dphi, dE_dtheta))
    return {
        "status": "success",
        "E": E,
        "dE_dtheta": dE_dtheta,
        "dE_dphi": dE_dphi,
        "grad_magnitude": grad_mag,
        "grad_angle_deg": grad_angle,
    }


def obtener_superficie(A, theta0, phi0, res=40) -> Dict[str, Any]:
    # aqui entra la api rodri qlo mueve la raja
    import numpy as np

    theta = np.linspace(0, 90, res)
    phi = np.linspace(0, 360, res)
    Theta, Phi = np.meshgrid(theta, phi)
    E = A * np.cos(np.radians(Theta - theta0)) * np.cos(np.radians(Phi - phi0))
    return {
        "status": "success",
        "theta": theta.tolist(),
        "phi": phi.tolist(),
        "E": E.tolist(),
    }


def obtener_optimo(latitude, power_gen) -> Dict[str, Any]:
    # aqui entra la api rodri qlo mueve la raja
    theta0 = abs(latitude)
    phi0 = 0.0 if latitude >= 0 else 180.0
    return {
        "status": "success",
        "theta0": theta0,
        "phi0": phi0,
        "E_max": power_gen,
    }


def obtener_derivada_direccional(theta, phi, A, theta0, phi0, alpha) -> Dict[str, Any]:
    # aqui entra la api rodri qlo mueve la raja
    energia = obtener_energia(theta, phi, A, theta0, phi0)
    dE_dtheta = energia["dE_dtheta"]
    dE_dphi = energia["dE_dphi"]
    alpha_rad = math.radians(alpha)
    u_theta = math.cos(alpha_rad)
    u_phi = math.sin(alpha_rad)
    D = dE_dtheta * u_theta + dE_dphi * u_phi
    return {
        "status": "success",
        "directional_derivative": D,
        "alpha_deg": alpha,
    }
