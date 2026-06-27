import json
import urllib.request
import urllib.error
import math

class SolarPanel:
    def __init__(self, latitude: float, longitude: float, power_gen: float = 1.0):
        """
        Inicializa un panel solar con sus propiedades fisicas y ubicacion.
        Parametros recibidos:
        - latitude (float): Latitud de la ubicacion.
        - longitude (float): Longitud de la ubicacion.
        - power_gen (float): Capacidad de generacion en kW.
        Parametros retornados:
        - None
        """
        self.power_gen = power_gen
        self.latitude = latitude
        self.longitude = longitude
        self.location_name = None

    def fetch_location_details(self) -> str:
        """
        Obtiene el nombre de la ubicacion del panel usando una API de mapas externa.
        Parametros recibidos:
        - None
        Parametros retornados:
        - str: Nombre detallado de la ubicacion o mensaje de error.
        """
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={self.latitude}&lon={self.longitude}"
        req = urllib.request.Request(url, headers={'User-Agent': 'SolarPanelModelApp/1.0'})
        
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                self.location_name = data.get("display_name", "Unknown location")
                return self.location_name
        except urllib.error.URLError as e:
            return "Unknown location"

    def get_ideal_facing_direction(self) -> str:
        """
        Determina la direccion cardinal ideal para orientar el panel segun el hemisferio.
        Parametros recibidos:
        - None
        Parametros retornados:
        - str: Direccion ideal (South, North, o Directly Upward).
        """
        if self.latitude > 0:
            return "South"
        elif self.latitude < 0:
            return "North"
        else:
            return "Directly Upward (Flat)"

    def get_ideal_tilt_angle(self) -> float:
        """
        Calcula el angulo de inclinacion optimo del panel basado en la latitud.
        Parametros recibidos:
        - None
        Parametros retornados:
        - float: Angulo de inclinacion en grados.
        """
        lat_rad = math.radians(self.latitude)
        tilt_rad = math.acos(math.cos(lat_rad))
        return math.degrees(tilt_rad)

    def calculate_hourly_energy_area_integral(self, width_m: float, height_m: float) -> float:
        """
        Calcula la energia total generada resolviendo una integral doble sobre el area fisica.
        Parametros recibidos:
        - width_m (float): Ancho del panel en metros.
        - height_m (float): Alto del panel en metros.
        Parametros retornados:
        - float: Energia total generada calculada.
        """
        n_steps = 100
        dx = width_m / n_steps
        dy = height_m / n_steps
        
        total_energy = 0.0
        
        for i in range(n_steps):
            for j in range(n_steps):
                total_energy += self.power_gen * dx * dy
                
        return total_energy

    def expected_power_angle_integral(self, delta_theta_deg: float, delta_phi_deg: float) -> float:
        """
        Calcula el poder promedio esperado considerando variaciones de angulo usando integral doble.
        Parametros recibidos:
        - delta_theta_deg (float): Variacion del angulo theta en grados.
        - delta_phi_deg (float): Variacion del angulo phi en grados.
        Parametros retornados:
        - float: Poder promedio esperado.
        """
        dt = math.radians(delta_theta_deg)
        dp = math.radians(delta_phi_deg)
        
        if dt == 0 or dp == 0:
            return self.power_gen
            
        integral_value = self.power_gen * (2 * math.sin(dt)) * (2 * math.sin(dp))
        integration_area = (2 * dt) * (2 * dp)
        
        return integral_value / integration_area

    def __repr__(self):
        """
        Retorna la representacion en texto del panel.
        Parametros recibidos:
        - None
        Parametros retornados:
        - str: Cadena de texto con los atributos del panel.
        """
        return f"SolarPanel(power_gen={self.power_gen}, latitude={self.latitude}, longitude={self.longitude}, location_name={self.location_name})"
