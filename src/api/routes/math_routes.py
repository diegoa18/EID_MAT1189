from flask import Blueprint, request, jsonify
from src.api.models.multivariable import MultivariableModel

math_bp = Blueprint('math', __name__)

@math_bp.route('/energy', methods=['POST'])
def get_energy():
    """
    Endpoint para calcular la energia, derivadas parciales y el gradiente para una configuracion dada.
    """
    data = request.json if request.is_json else request.form
    if not data:
        return jsonify({"status": "error", "message": "No data provided."}), 400
        
    try:
        theta = float(data['theta'])
        phi = float(data['phi'])
        A = float(data['A'])
        theta0 = float(data['theta0'])
        phi0 = float(data['phi0'])
    except (KeyError, ValueError):
        return jsonify({"status": "error", "message": "Parametros invalidos o faltantes."}), 400
        
    E, dE_dtheta, dE_dphi, grad_mag, grad_angle = MultivariableModel.calculate_energy(theta, phi, A, theta0, phi0)
    
    return jsonify({
        "status": "success",
        "E": E,
        "dE_dtheta": dE_dtheta,
        "dE_dphi": dE_dphi,
        "grad_magnitude": grad_mag,
        "grad_angle_deg": grad_angle
    })

@math_bp.route('/surface', methods=['POST'])
def get_surface():
    """
    Endpoint para calcular la superficie de energia.
    """
    data = request.json if request.is_json else request.form
    if not data:
        return jsonify({"status": "error", "message": "No data provided."}), 400
        
    try:
        A = float(data['A'])
        theta0 = float(data['theta0'])
        phi0 = float(data['phi0'])
        res = int(data.get('res', 40))
    except (KeyError, ValueError):
        return jsonify({"status": "error", "message": "Parametros invalidos o faltantes."}), 400
        
    theta, phi, E = MultivariableModel.calculate_surface(A, theta0, phi0, res)
    
    return jsonify({
        "status": "success",
        "theta": theta,
        "phi": phi,
        "E": E
    })

@math_bp.route('/optimal', methods=['POST'])
def get_optimal():
    """
    Endpoint para obtener la configuracion optima de angulos segun la latitud.
    """
    data = request.json if request.is_json else request.form
    if not data:
        return jsonify({"status": "error", "message": "No data provided."}), 400
        
    try:
        latitude = float(data['latitude'])
        power_gen = float(data['power_gen'])
    except (KeyError, ValueError):
        return jsonify({"status": "error", "message": "Parametros invalidos o faltantes."}), 400
        
    theta0, phi0, E_max = MultivariableModel.calculate_optimal(latitude, power_gen)
    
    return jsonify({
        "status": "success",
        "theta0": theta0,
        "phi0": phi0,
        "E_max": E_max
    })

@math_bp.route('/directional-derivative', methods=['POST'])
def get_directional_derivative():
    """
    Endpoint para calcular la derivada direccional en un angulo especifico.
    """
    data = request.json if request.is_json else request.form
    if not data:
        return jsonify({"status": "error", "message": "No data provided."}), 400
        
    try:
        theta = float(data['theta'])
        phi = float(data['phi'])
        A = float(data['A'])
        theta0 = float(data['theta0'])
        phi0 = float(data['phi0'])
        alpha = float(data['alpha'])
    except (KeyError, ValueError):
        return jsonify({"status": "error", "message": "Parametros invalidos o faltantes."}), 400
        
    D, alpha_deg = MultivariableModel.calculate_directional_derivative(theta, phi, A, theta0, phi0, alpha)
    
    return jsonify({
        "status": "success",
        "directional_derivative": D,
        "alpha_deg": alpha_deg
    })

@math_bp.route('/hessian', methods=['POST'])
def get_hessian():
    """
    Endpoint para calcular la matriz Hessiana, clasificacion de puntos y autovalores.
    """
    data = request.json if request.is_json else request.form
    if not data:
        return jsonify({"status": "error", "message": "No data provided."}), 400
        
    try:
        theta = float(data['theta'])
        phi = float(data['phi'])
        A = float(data['A'])
        theta0 = float(data['theta0'])
        phi0 = float(data['phi0'])
    except (KeyError, ValueError):
        return jsonify({"status": "error", "message": "Parametros invalidos o faltantes."}), 400
        
    h_mat, det, classification, is_crit, eig1, eig2 = MultivariableModel.calculate_hessian(theta, phi, A, theta0, phi0)
    
    return jsonify({
        "status": "success",
        "hessian_matrix": h_mat,
        "determinant": det,
        "classification": classification,
        "is_critical": is_crit,
        "eigenvalues": [eig1, eig2]
    })
