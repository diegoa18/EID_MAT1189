# Proyecto 5: Optimización de Paneles Solares

Este proyecto implementa el modelo matemático descrito para la optimización de paneles solares usando Python.

## Estructura del proyecto

- `solar_optimization.py`: Contiene la clase `SolarPanelModel` y un script ejecutable para probar sus funcionalidades.
- `venv/`: Entorno virtual de Python con las dependencias necesarias.
- `solar_optimization_plots.png`: Imagen generada tras ejecutar el script, mostrando la superficie de energía y las curvas de nivel.

## Modelo matemático implementado

El sistema modela la energía captada por un panel solar mediante:
`E(θ, ϕ) = A cos(θ - θ_0) cos(ϕ - ϕ_0)`

Donde:
- `A`: Energía máxima posible de captar.
- `θ_0`: Inclinación ideal de la ubicación.
- `ϕ_0`: Orientación ideal de la ubicación.

## Ejecución

Para ejecutar el código y ver los resultados en la terminal, activa el entorno virtual y ejecuta el script principal:

```bash
source venv/bin/activate
python solar_optimization.py
```

Esto generará la salida por consola mostrando comparaciones de configuraciones y creará/actualizará la imagen `solar_optimization_plots.png` con las gráficas de superficie y curvas de nivel requeridas.

## Prototipo de API (Flask)

Se ha incluido un prototipo escalable basado en Flask para exponer el modelo matemático a través de un servicio web RESTful.

### Levantar el servidor

Para iniciar la API, ejecuta:

```bash
source venv/bin/activate
python app.py
```

El servidor se iniciará en `http://localhost:5000`.

### Ejemplos de uso

1. **Health Check:** Verificar que la API está funcionando.
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Calcular Energía (POST):** Enviar parámetros para evaluar una configuración.
   ```bash
   curl -X POST http://localhost:5000/api/calculate \
   -H "Content-Type: application/json" \
   -d '{"location": "Santiago", "theta": 40.0, "phi": 15.0}'
   ```