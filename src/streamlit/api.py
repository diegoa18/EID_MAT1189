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
        response.raise_for_status()  # detecta errores HTTP

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
