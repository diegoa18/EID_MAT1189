import math
from typing import List, Dict

class SolarSimulator:
    def __init__(self, panel, sunrise: float = 6.0, sunset: float = 18.0, shadows: List[Dict[str, float]] = None):
        """
        Inicializa el simulador de ciclo diario para un panel solar.
        Parametros recibidos:
        - panel (SolarPanel): Instancia del panel a simular.
        - sunrise (float): Hora de amanecer en formato decimal.
        - sunset (float): Hora de atardecer en formato decimal.
        - shadows (List[Dict[str, float]]): Lista de diccionarios con start_hour, end_hour y shade_factor.
        Parametros retornados:
        - None
        """
        self.panel = panel
        self.sunrise = sunrise
        self.sunset = sunset
        self.daylight_hours = sunset - sunrise
        self.shadows = shadows if shadows is not None else []

    def power_at_time(self, time_hours: float, peak_power: float) -> float:
        """
        Calcula el poder generado en una hora especifica modelando la trayectoria del sol como onda senoidal.
        Parametros recibidos:
        - time_hours (float): Hora especifica del dia en formato decimal.
        - peak_power (float): Poder maximo generado en el pico solar.
        Parametros retornados:
        - float: Poder generado en la hora dada.
        """
        if time_hours <= self.sunrise or time_hours >= self.sunset:
            return 0.0
            
        time_fraction = (time_hours - self.sunrise) / self.daylight_hours
        angle = time_fraction * math.pi
        
        ideal_power = peak_power * math.sin(angle)
        
        shade_factor = 0.0
        for shadow in self.shadows:
            start_h = shadow.get('start_hour', 0.0)
            end_h = shadow.get('end_hour', 24.0)
            if start_h <= time_hours <= end_h:
                shade_factor = max(shade_factor, shadow.get('shade_factor', 1.0))
                
        return ideal_power * (1.0 - shade_factor)

    def simulate_day(self, peak_power: float, steps_per_hour: int = 4) -> List[Dict[str, float]]:
        """
        Simula el dia completo generando una serie de tiempo con datos de generacion de energia.
        Parametros recibidos:
        - peak_power (float): Poder maximo en el pico del dia.
        - steps_per_hour (int): Resolucion de los pasos de simulacion por hora.
        Parametros retornados:
        - List[Dict[str, float]]: Lista de diccionarios con el tiempo y el poder en cada momento.
        """
        data_points = []
        total_steps = int(24 * steps_per_hour)
        dt = 1.0 / steps_per_hour
        
        for i in range(total_steps):
            t = i * dt
            p = self.power_at_time(t, peak_power)
            data_points.append({
                "time": t,
                "power": p
            })
            
        return data_points

    def calculate_daily_energy_details(self, peak_power: float, n_steps: int = 1000) -> Dict[str, float]:
        """
        Calcula la energia total diaria utilizando una suma de Riemann sobre la funcion de poder, detallando perdidas por sombra.
        Parametros recibidos:
        - peak_power (float): Poder maximo en el pico del dia.
        - n_steps (int): Numero de pasos a usar en la sumatoria.
        Parametros retornados:
        - Dict[str, float]: Diccionario con energia ideal, real y perdida.
        """
        dt = self.daylight_hours / n_steps
        actual_energy = 0.0
        ideal_energy = 0.0
        
        for i in range(n_steps):
            t = self.sunrise + (i * dt)
            
            # Poder ideal (sin sombras)
            time_fraction = (t - self.sunrise) / self.daylight_hours
            angle = time_fraction * math.pi
            ideal_p = peak_power * math.sin(angle)
            
            # Poder real
            actual_p = self.power_at_time(t, peak_power)
            
            ideal_energy += ideal_p * dt
            actual_energy += actual_p * dt
            
        return {
            "total_energy": actual_energy,
            "ideal_energy": ideal_energy,
            "energy_loss": ideal_energy - actual_energy
        }
