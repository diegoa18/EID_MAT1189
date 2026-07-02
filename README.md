# Proyecto 5: Optimización de Paneles Solares

Este proyecto implementa el modelo matemático para la optimización de paneles solares usando una app interactiva Streamlit con backend Flask.

## Estructura del proyecto

```
├── src/
│   ├── api/                        # Backend Flask
│   │   ├── app.py                  # Servidor API (punto de entrada)
│   │   ├── routes/
│   │   │   └── math_routes.py      # Endpoints REST (/energy, /surface, /optimal, /hessian, etc.)
│   │   ├── models/
│   │   │   ├── multivariable.py    # Modelo matemático E(θ,φ), gradiente, hessiano
│   │   │   ├── solar_panel.py      # Panel solar, integrales de área
│   │   │   ├── simulator.py        # Simulación diaria con suma de Riemann + sombras
│   │   │   ├── environment.py      # Datos climáticos desde Open-Meteo API
│   │   │   └── shadow_projector.py # Proyección de sombras con integrales dobles
│   │   └── tests/                  # Tests automatizados
│   └── streamlit/                  # Frontend Streamlit
│       ├── main.py                 # App principal (11 tabs)
│       ├── api.py                  # Cliente HTTP para Flask API
│       ├── grapics.py              # Gráficos Plotly (superficie, contorno, sombras, etc.)
│       ├── sidebar.py              # Barra lateral (gestión de paneles)
│       ├── mapa.py                 # Mapa Folium interactivo
│       └── persistencia.py         # Persistencia JSON de paneles
├── analisis-cumplimiento-guia.md   # Checklist de requisitos
└── README.md
```

## Fundamento Teórico y Modelo Matemático

> **Referencia Bibliográfica:**
> Yunge, V. (2026). *PROYECTO FINAL 5: Optimización de paneles solares*. Departamento de Ciencias Matemáticas y Físicas, Curso MATE1189 - Cálculo Avanzado. Universidad Católica de Temuco.

### Función de Energía Captada

$$ E(\theta, \phi) = A \cos(\theta - \theta_0) \cos(\phi - \phi_0) $$

Donde $\theta$ es inclinación, $\phi$ es orientación, $A$ es potencia máxima, $\theta_0$ y $\phi_0$ son los ángulos óptimos.

### Derivadas Parciales

$$ \frac{\partial E}{\partial \theta} = -A \sin(\theta - \theta_0) \cos(\phi - \phi_0) $$
$$ \frac{\partial E}{\partial \phi} = -A \cos(\theta - \theta_0) \sin(\phi - \phi_0) $$

### Gradiente

$$ \nabla E(\theta, \phi) = \left( \frac{\partial E}{\partial \theta}, \frac{\partial E}{\partial \phi} \right) $$

## Ejecución

### 1. Iniciar API Flask

```bash
cd src/api
pip install flask requests pysolar
python app.py
```

Servidor en `http://localhost:5000`.

### 2. Iniciar Frontend Streamlit

```bash
cd src/streamlit
pip install streamlit plotly pandas requests folium streamlit-folium
streamlit run main.py
```

### 3. (Opcional) Entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask requests pysolar streamlit plotly pandas folium streamlit-folium
```

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/energy` | `E`, derivadas parciales, gradiente |
| POST | `/api/surface` | Meshgrid θ×φ con valores de `E` |
| POST | `/api/optimal` | Ángulos óptimos `θ₀`, `φ₀` |
| POST | `/api/directional-derivative` | Derivada direccional `∇E·(cosα, sinα)` |
| POST | `/api/hessian` | Matriz Hessiana, autovalores, clasificación |
| POST | `/api/simulate` | Simulación diaria con sombras y clima real |
| POST | `/api/calculate` | Incertidumbre por errores angulares |

## Tabs de la app Streamlit

| Tab | Funcionalidad |
|-----|--------------|
| Panel | Métricas del panel seleccionado |
| Superficie | Gráfico 3D de `E(θ,φ)` |
| Contorno | Curvas de nivel con gradiente |
| Derivadas | Derivadas parciales, direccional, interpretación |
| Hessiano | Matriz Hessiana y clasificación de puntos críticos |
| Óptimo | Comparación actual vs óptimo + plano tangente |
| Comparar | Tabla comparativa entre paneles |
| Incertidumbre | Sensibilidad a errores angulares |
| **Consumo Diario** | Curva de potencia diaria, energía acumulada, sombras |
| **Sombras** | Timeline de sombras, impacto en generación |
| Mapa | Ubicación geográfica de los paneles |

## Sombras (requiere pysolar)

Para detectar sombras de edificios cercanos, instala:

```bash
pip install pysolar
```

Coordenadas de prueba con sombras verificadas (invierno):

| Ubicación | Latitud | Longitud |
|-----------|---------|----------|
| Costanera Center, Santiago | -33.4175 | -70.6060 |
| Paseo Ahumada, Santiago | -33.4370 | -70.6510 |
| Los Leones, Santiago | -33.4220 | -70.6090 |

Usa estación `winter` y presiona "Simular día" en la barra lateral.