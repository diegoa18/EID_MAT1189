import sys
import os
import math
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Flask, request, jsonify
from src.api.models.solar_panel import SolarPanel
from src.api.models.simulator import SolarSimulator
from src.api.models.environment import OpenMeteoModel
from src.api.models.multivariable import MultivariableModel
from src.api.models.shadow_projector import ShadowProjector
from src.api.routes.math_routes import math_bp

app = Flask(__name__)
app.register_blueprint(math_bp, url_prefix='/api')

@app.after_request
def after_request(response):
    """
    Agrega cabeceras CORS a todas las respuestas de la API.
    Parametros recibidos:
    - response (Response): Objeto de respuesta original.
    Parametros retornados:
    - Response: Objeto de respuesta modificado con cabeceras CORS.
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.errorhandler(400)
def bad_request(error):
    """
    Maneja los errores HTTP 400 y devuelve un formato JSON estandar.
    Parametros recibidos:
    - error (Exception): Excepcion de error generada.
    Parametros retornados:
    - tuple: Respuesta JSON con el mensaje de error y el codigo HTTP 400.
    """
    return jsonify({"status": "error", "message": "Peticion incorrecta. Por favor, revise los parametros enviados."}), 400

@app.errorhandler(500)
def internal_error(error):
    """
    Maneja los errores HTTP 500 y devuelve un formato JSON estandar.
    Parametros recibidos:
    - error (Exception): Excepcion de error interna.
    Parametros retornados:
    - tuple: Respuesta JSON con el mensaje de error y el codigo HTTP 500.
    """
    return jsonify({"status": "error", "message": "Error interno del servidor."}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar el estado y funcionamiento del servidor API.
    Parametros recibidos:
    - Ninguno
    Parametros retornados:
    - tuple: Respuesta JSON confirmando el estado de la API.
    """
    return jsonify({'status': 'ok', 'message': 'La API de Optimizacion Solar esta funcionando correctamente.'})

@app.route('/api/simulate', methods=['POST'])
def simulate():
    """
    Endpoint para simular la generacion diaria de energia basada en area y ubicacion, obteniendo el clima real.
    Parametros recibidos (via JSON payload):
    - latitude (float)
    - longitude (float)
    - width_m (float)
    - height_m (float)
    - season (str)
    - power_gen_kw (float, opcional)
    - shadows (list, opcional): Lista de objetos con start_hour, end_hour y shade_factor.
    Parametros retornados:
    - tuple: JSON conteniendo datos ambientales, configuracion optima, energias totales y serie de tiempo.
    """
    data = request.json if request.is_json else request.form
    if not data:
        return jsonify({"status": "error", "message": "No data provided."}), 400
        
    try:
        if not all(k in data for k in ('latitude', 'longitude', 'width_m', 'height_m', 'season')):
            return jsonify({"status": "error", "message": "Missing required parameters in JSON payload."}), 400
            
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        width_m = float(data['width_m'])
        height_m = float(data['height_m'])
        season = str(data['season'])
        power_gen = float(data.get('power_gen_kw', 1.0))
        shadows = data.get('shadows', [])
    except ValueError:
        return jsonify({"status": "error", "message": "Numeric parameters required for numerical fields."}), 400

    try:
        env_data = OpenMeteoModel.get_historical_solar_data(latitude, longitude, season)
        sunrise = env_data["sunrise"]
        sunset = env_data["sunset"]
        efficiency = env_data["efficiency"]
        
        effective_power_gen = power_gen * efficiency

        # Compute dynamic building shadows if real date is available
        import datetime
        try:
            sim_date = datetime.datetime.fromisoformat(env_data['date'])
            building_shadows = ShadowProjector.get_building_shadows(latitude, longitude, sim_date, panel_width=width_m, panel_height=height_m)
            shadows.extend(building_shadows)
        except Exception as e:
            print(f"Failed to project building shadows: {e}")

        panel = SolarPanel(latitude=latitude, longitude=longitude, power_gen=effective_power_gen)
        panel.fetch_location_details()
        
        facing_direction = panel.get_ideal_facing_direction()
        tilt_angle = panel.get_ideal_tilt_angle()
        
        peak_power = panel.calculate_hourly_energy_area_integral(width_m=width_m, height_m=height_m)
        
        simulator = SolarSimulator(panel, sunrise=sunrise, sunset=sunset, shadows=shadows)
        energy_details = simulator.calculate_daily_energy_details(peak_power)
        daily_energy = energy_details['total_energy']
        ideal_energy = energy_details['ideal_energy']
        energy_loss = energy_details['energy_loss']
        
        time_series = simulator.simulate_day(peak_power, steps_per_hour=4)
        
        theta0, phi0, E_max = MultivariableModel.calculate_optimal(latitude, effective_power_gen)
        theta_surf, phi_surf, E_surf = MultivariableModel.calculate_surface(effective_power_gen, theta0, phi0)

        return jsonify({
            'status': 'success',
            'location': panel.location_name,
            'environment': {
                'season': season,
                'api_date': env_data['date'],
                'radiation_mj_m2': env_data['radiation_mj_m2'],
                'efficiency_multiplier': efficiency,
                'calculated_sunrise': sunrise,
                'calculated_sunset': sunset
            },
            'optimal_configuration': {
                'facing_direction': facing_direction,
                'tilt_angle_deg': tilt_angle,
                'theta0': theta0,
                'phi0': phi0,
                'E_max': E_max
            },
            'results': {
                'peak_power_kw': peak_power,
                'total_daily_energy_kwh': daily_energy,
                'ideal_daily_energy_kwh': ideal_energy,
                'energy_loss_from_shadows_kwh': energy_loss,
                'applied_shadows': shadows
            },
            'plot_data': time_series,
            'multivariable_surface': {
                'theta': theta_surf,
                'phi': phi_surf,
                'E': E_surf
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/calculate', methods=['POST'])
def calculate_energy():
    """
    Endpoint para calcular el poder promedio esperado dadas las variaciones y errores de angulo.
    Parametros recibidos (via JSON payload):
    - latitude (float)
    - longitude (float)
    - delta_theta (float)
    - delta_phi (float)
    - power_gen (float, opcional)
    Parametros retornados:
    - tuple: JSON conteniendo el poder promedio esperado considerando el area de integracion angular.
    """
    data = request.json if request.is_json else request.form
    if not data:
        return jsonify({"status": "error", "message": "No data provided."}), 400
    
    try:
        if not all(k in data for k in ('latitude', 'longitude', 'delta_theta', 'delta_phi')):
            return jsonify({"status": "error", "message": "Missing required parameters in JSON payload."}), 400
            
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        d_theta = float(data['delta_theta'])
        d_phi = float(data['delta_phi'])
        power_gen = float(data.get('power_gen', 1.0))
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid number format."}), 400
        
    try:
        panel = SolarPanel(latitude=latitude, longitude=longitude, power_gen=power_gen)
        panel.fetch_location_details()
        
        avg_power = panel.expected_power_angle_integral(delta_theta_deg=d_theta, delta_phi_deg=d_phi)
        
        return jsonify({
            'status': 'success',
            'location': panel.location_name,
            'input': {
                'delta_theta_deg': d_theta,
                'delta_phi_deg': d_phi
            },
            'results': {
                'ideal_peak_power_kw': power_gen,
                'expected_avg_power_kw': avg_power
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
