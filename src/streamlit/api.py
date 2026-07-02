import math
from typing import Any, Dict

import requests

URL_SIMULATE = "http://127.0.0.1:5000/api/simulate"
URL_CALCULATE = "http://127.0.0.1:5000/api/calculate"
URL_ENERGY = "http://127.0.0.1:5000/api/energy"
URL_SURFACE = "http://127.0.0.1:5000/api/surface"
URL_OPTIMAL = "http://127.0.0.1:5000/api/optimal"
URL_DIRECTIONAL_DERIVATIVE = "http://127.0.0.1:5000/api/directional-derivative"
URL_HESSIAN = "http://127.0.0.1:5000/api/hessian"


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
        response = requests.post(URL_SIMULATE, json=datos, timeout=30)
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
    datos = {
        "theta": theta,
        "phi": phi,
        "A": A,
        "theta0": theta0,
        "phi0": phi0,
    }
    try:
        response = requests.post(URL_ENERGY, json=datos, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


def obtener_superficie(A, theta0, phi0, res=40) -> Dict[str, Any]:
    datos = {
        "A": A,
        "theta0": theta0,
        "phi0": phi0,
        "res": res,
    }
    try:
        response = requests.post(URL_SURFACE, json=datos, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


def obtener_optimo(latitude, power_gen) -> Dict[str, Any]:
    datos = {
        "latitude": latitude,
        "power_gen": power_gen,
    }
    try:
        response = requests.post(URL_OPTIMAL, json=datos, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


def obtener_derivada_direccional(theta, phi, A, theta0, phi0, alpha) -> Dict[str, Any]:
    datos = {
        "theta": theta,
        "phi": phi,
        "A": A,
        "theta0": theta0,
        "phi0": phi0,
        "alpha": alpha,
    }
    try:
        response = requests.post(URL_DIRECTIONAL_DERIVATIVE, json=datos, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


def obtener_hessiano(theta, phi, A, theta0, phi0) -> Dict[str, Any]:
    datos = {
        "theta": theta,
        "phi": phi,
        "A": A,
        "theta0": theta0,
        "phi0": phi0,
    }
    try:
        response = requests.post(URL_HESSIAN, json=datos, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}
