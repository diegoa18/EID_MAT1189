import json
import urllib.request
import urllib.error
from datetime import datetime

class OpenMeteoModel:
    @staticmethod
    def get_historical_solar_data(latitude: float, longitude: float, season: str) -> dict:
        """
        Consulta la API de Open-Meteo para obtener datos historicos de clima basados en la estacion del ano.
        Parametros recibidos:
        - latitude (float): Latitud de la ubicacion.
        - longitude (float): Longitud de la ubicacion.
        - season (str): Estacion del ano a simular (summer, autumn, winter, spring).
        Parametros retornados:
        - dict: Diccionario con la hora de amanecer, atardecer, multiplicador de eficiencia, radiacion y fecha.
        """
        season = season.lower()
        hemisphere = "south" if latitude < 0 else "north"
        
        if hemisphere == "south":
            mapping = {
                "summer": "2023-12-21",
                "autumn": "2023-03-21",
                "winter": "2023-06-21",
                "spring": "2023-09-23"
            }
        else:
            mapping = {
                "summer": "2023-06-21",
                "autumn": "2023-09-23",
                "winter": "2023-12-21",
                "spring": "2023-03-21"
            }
            
        target_date = mapping.get(season, "2023-06-21")
        
        url = (
            f"https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={latitude}&longitude={longitude}"
            f"&start_date={target_date}&end_date={target_date}"
            f"&daily=sunrise,sunset,shortwave_radiation_sum"
            f"&timezone=auto"
        )
        
        req = urllib.request.Request(url, headers={'User-Agent': 'SolarOptimizationApp/1.0'})
        
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                sunrise_str = data['daily']['sunrise'][0]
                sunset_str = data['daily']['sunset'][0]
                
                sunrise_dt = datetime.fromisoformat(sunrise_str)
                sunset_dt = datetime.fromisoformat(sunset_str)
                
                sunrise_hour = sunrise_dt.hour + (sunrise_dt.minute / 60.0)
                sunset_hour = sunset_dt.hour + (sunset_dt.minute / 60.0)
                
                radiation_mj = data['daily']['shortwave_radiation_sum'][0]
                efficiency = min(1.0, max(0.1, radiation_mj / 30.0))
                
                return {
                    "sunrise": sunrise_hour,
                    "sunset": sunset_hour,
                    "efficiency": efficiency,
                    "radiation_mj_m2": radiation_mj,
                    "date": target_date
                }
                
        except Exception as e:
            return {
                "sunrise": 6.0,
                "sunset": 18.0,
                "efficiency": 0.5,
                "radiation_mj_m2": 15.0,
                "date": target_date
            }
