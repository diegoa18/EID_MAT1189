# Documentacion de Rutas de la API

Este documento describe las rutas disponibles en la API de Optimizacion Solar, los parametros necesarios para consumir cada ruta, y los datos que retorna el servidor.

## `GET /api/health`

Verifica el estado del servidor.

**Parametros recibidos:**
- Ninguno.

**Parametros retornados:**
- `status` (str): Estado general (ok).
- `message` (str): Mensaje de verificacion.

---

## `POST /api/simulate`

Simula la generacion diaria de energia basandose en el tamano fisico del panel, su ubicacion y datos climaticos reales obtenidos via Open-Meteo segun la estacion del ano.

**Parametros recibidos (JSON Payload):**
- `latitude` (float): Latitud de la ubicacion geografica.
- `longitude` (float): Longitud de la ubicacion geografica.
- `width_m` (float): Ancho del panel solar en metros.
- `height_m` (float): Alto del panel solar en metros.
- `season` (str): Estacion del ano a consultar (ej. "summer", "winter").
- `power_gen_kw` (float, opcional): Capacidad pico de generacion base en kW. Por defecto es 1.0.
- `shadows` (list, opcional): Arreglo de objetos simulando sombras (ej. `[{"start_hour": 14.0, "end_hour": 15.5, "shade_factor": 0.8}]`).

**Parametros retornados (JSON):**
- `status` (str): Exito o fallo de la operacion.
- `location` (str): Direccion o descripcion de las coordenadas dadas.
- `environment` (dict): Datos climaticos historicos.
  - `season` (str): Estacion solicitada.
  - `api_date` (str): Fecha de la cual se extrajo la data.
  - `radiation_mj_m2` (float): Suma de radiacion de onda corta en el dia.
  - `efficiency_multiplier` (float): Multiplicador de eficiencia calculado segun el clima.
  - `calculated_sunrise` (float): Hora decimal de amanecer.
  - `calculated_sunset` (float): Hora decimal de atardecer.
- `optimal_configuration` (dict): Configuracion ideal del hardware.
  - `facing_direction` (str): Direccion cardinal ideal.
  - `tilt_angle_deg` (float): Inclinacion optima calculada.
- `results` (dict): Resultados de energia integrados.
  - `peak_power_kw` (float): Generacion tope aplicando area fisica e inclemencia del clima.
  - `total_daily_energy_kwh` (float): Integral completa de la curva de poder diaria (incluyendo perdidas por sombras).
  - `ideal_daily_energy_kwh` (float): Energia total diaria calculada sin perdidas por sombras.
  - `energy_loss_from_shadows_kwh` (float): Energia perdida especificamente a causa de las sombras.
  - `applied_shadows` (list): Lista de las sombras que fueron finalmente aplicadas en la simulacion, combinando las sombras manuales con las proyectadas por edificios.
- `plot_data` (list): Arreglo de puntos para graficar (pares de `time` y `power`).

---

## `POST /api/calculate`

Calcula matematicamente el promedio de energia generada bajo escenarios de incertidumbre y errores de angulo de instalacion (usando integral doble espacial).

**Parametros recibidos (JSON Payload):**
- `latitude` (float): Latitud de la ubicacion geografica.
- `longitude` (float): Longitud de la ubicacion geografica.
- `delta_theta` (float): Posible error del angulo theta en grados.
- `delta_phi` (float): Posible error del angulo phi en grados.
- `power_gen` (float, opcional): Capacidad de energia. Por defecto es 1.0.

**Parametros retornados (JSON):**
- `status` (str): Exito o fallo.
- `location` (str): Nombre de la ubicacion.
- `input` (dict): Reflejo de los angulos ingresados.
- `results` (dict): Evaluacion del error angular.
  - `ideal_peak_power_kw` (float): Poder teorico maximo.
  - `expected_avg_power_kw` (float): Promedio matematico de energia esperada asumiendo desviacion de angulos aleatorios.
