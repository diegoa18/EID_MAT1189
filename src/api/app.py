from flask import Flask, request, jsonify
from src.core.solar_optimization import SolarPanelModel

app = Flask(__name__)

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"status": "error", "message": "Petición incorrecta. Por favor, revise los parámetros enviados."}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"status": "error", "message": "Error interno del servidor."}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint de comprobación de estado para verificar que la API está funcionando.
    """
    return jsonify({'status': 'ok', 'message': 'La API de Optimización Solar está funcionando correctamente.'})

@app.route('/api/calculate', methods=['POST'])
def calculate_energy():
    """
    Endpoint para calcular la energía captada y el gradiente dados los ángulos del panel.
    Estructura JSON esperada:
    {
        "location": "Santiago",  # opcional, el valor por defecto es "Santiago"
        "theta": 40.0,           # ángulo de inclinación en grados
        "phi": 10.0              # ángulo de orientación en grados
    }
    """
    # Acepta formato JSON o datos de formulario (para facilitar las pruebas)
    data = request.json if request.is_json else request.form
    if not data:
        return jsonify({"status": "error", "message": "No data provided."}), 400
    
    # Extract parameters
    location = data.get('location', 'Santiago')
    
    try:
        theta = float(data.get('theta', 0.0))
        phi = float(data.get('phi', 0.0))
    except ValueError:
        return jsonify({"status": "error", "message": "Theta and phi must be numbers."}), 400
    
    try:
        # Inicializa el modelo usando la clase principal
        model = SolarPanelModel(location=location)
        
        # Calcula la energía y el gradiente
        energy = model.energy(theta, phi)
        grad = model.gradient(theta, phi)
        
        # Obtiene la configuración óptima real para usarla de referencia
        opt_theta, opt_phi, max_energy = model.optimal_configuration()
        
        return jsonify({
            'status': 'success',
            'location': model.location_name,
            'input': {
                'theta_deg': theta,
                'phi_deg': phi
            },
            'results': {
                'energy_captured': float(energy),
                'gradient': {
                    'dE_dtheta': float(grad[0]),
                    'dE_dphi': float(grad[1])
                }
            },
            'optimal_configuration': {
                'theta_deg': float(opt_theta),
                'phi_deg': float(opt_phi),
                'max_energy': float(max_energy)
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
