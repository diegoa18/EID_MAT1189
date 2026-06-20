# Proyecto 5: Optimización de Paneles Solares

Este proyecto implementa el modelo matemático descrito para la optimización de paneles solares usando Python.

## Estructura del proyecto

- `solar_optimization.py`: Contiene la clase `SolarPanelModel` y un script ejecutable para probar sus funcionalidades.
- `venv/`: Entorno virtual de Python con las dependencias necesarias.
- `solar_optimization_plots.png`: Imagen generada tras ejecutar el script, mostrando la superficie de energía y las curvas de nivel.

## Fundamento Teórico y Modelo Matemático

El modelo matemático y sus componentes implementados en este proyecto se basan en las directrices establecidas en el documento de investigación del curso:

> **Referencia Bibliográfica:**
> Yunge, V. (2026). *PROYECTO FINAL 5: Optimización de paneles solares*. Departamento de Ciencias Matemáticas y Físicas, Curso MATE1189 - Cálculo Avanzado. Universidad Católica de Temuco.

### 1. Función de Energía Captada

El sistema modela la energía captada por un panel solar utilizando una función de dos variables que describe la disminución de eficiencia a medida que el panel se aleja de su posición óptima:

$$ E(\theta, \phi) = A \cos(\theta - \theta_0) \cos(\phi - \phi_0) $$

Donde:
- $\theta$: Ángulo de inclinación respecto de la horizontal.
- $\phi$: Ángulo de orientación respecto del norte geográfico.
- $A > 0$: Representa la máxima energía posible de captar en la ubicación.
- $\theta_0$: Corresponde al ángulo de inclinación ideal para la ubicación.
- $\phi_0$: Corresponde a la orientación ideal para la ubicación geográfica estudiada.

### 2. Derivadas Parciales y Sensibilidad

Para evaluar la sensibilidad del sistema frente a errores de instalación y entender la tasa de cambio de la energía, se computan analíticamente las derivadas parciales de la función:

- **Derivada respecto a la inclinación ($\theta$):**
  $$ \frac{\partial E}{\partial \theta} = -A \sin(\theta - \theta_0) \cos(\phi - \phi_0) $$

- **Derivada respecto a la orientación ($\phi$):**
  $$ \frac{\partial E}{\partial \phi} = -A \cos(\theta - \theta_0) \sin(\phi - \phi_0) $$

### 3. Gradiente y Optimización

El vector gradiente construido se utiliza para determinar la dirección de máximo incremento de la energía captada. Su implementación computacional evalúa:

$$ \nabla E(\theta, \phi) = \left( \frac{\partial E}{\partial \theta}, \frac{\partial E}{\partial \phi} \right) $$

Al igualar $\nabla E(\theta, \phi) = \mathbf{0}$, se determinan matemáticamente las configuraciones óptimas de instalación del panel ($\theta = \theta_0$ y $\phi = \phi_0$).

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