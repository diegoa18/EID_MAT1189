# Análisis de Cumplimiento — Guía del Proyecto Final 5

> **Última actualización:** 1 julio 2026
> **Código fuente:** `src/streamlit/` (frontend) + `src/api/` (backend)

---

## Estado general

El proyecto implementa el **núcleo completo de cálculo multivariable** (secciones 6.1-6.9 de la guía) en la app Streamlit, incluyendo el análisis de la matriz Hessiana. Todas las funciones matemáticas del modelo están conectadas exitosamente con la API de Flask. Se implementó el modelo extendido para sombras usando integrales dobles proyectadas, y se corrigieron errores de runtime en el simulador diario.

---

## Hallazgos importantes (corregidos)

| Problema | Estado anterior | Solución aplicada |
|----------|----------------|-------------------|
| `calculate_daily_energy_details()` no existía | 🔴 Error runtime en `/api/simulate` | Método agregado en `simulator.py:63-79` |
| `SolarSimulator.__init__` no aceptaba `shadows` | 🔴 TypeError al crear simulador | Parámetro `shadows` agregado en `simulator.py:5` |
| `pysolar` no instalado → sombras siempre vacías | 🟡 Sombras nunca se detectaban | Documentado como dependencia requerida |

---

## Checklist detallado por sección de la guía

### 5. Modelo matemático

| Elemento | Estado | Dónde |
|----------|--------|-------|
| **5.1** `E(θ,ϕ)=A·cos(θ−θ₀)·cos(φ−φ₀)` | 🟢 API Flask | `obtener_energia()` consumiendo ruta `/energy` |
| **5.2** Modelo extendido (estaciones, sombras, etc.) | 🟢 | Estaciones: vía simulación diaria ✅. Sombras: integral doble dinámica con `pysolar` + OpenStreetMap ✅. Nubosidad/tracking solar opcionales. |

### 6. Herramientas de cálculo multivariable

| # | Elemento | Estado | Dónde / Detalle |
|---|----------|--------|-----------------|
| **6.1** | Función de varias variables `E(θ,φ)` | 🟢 | `obtener_energia()` en API Flask |
| **6.2** | Curvas de nivel `E(θ,φ)=c` | 🟢 | Tab "Contorno" → `contour_plot_E()` en grapics.py |
| **6.3** | Derivadas parciales `∂E/∂θ`, `∂E/∂φ` | 🟢 | Tab "Derivadas" → devueltas por API Flask |
| **6.4** | Gradiente `∇E` | 🟢 | Magnitud + dirección en tab "Derivadas", flecha sobre contorno |
| **6.5** | Derivadas direccionales | 🟢 | `obtener_derivada_direccional()` + API Flask |
| **6.6** | Plano tangente / linealización | 🟢 | Tab "Óptimo" → slider θ_eval, φ_eval, compara E_lineal vs E_exacta |
| **6.7** | **Puntos críticos + Hessiano** | 🟢 | **Tab "Hessiano" → matriz H(θ,φ), autovalores, determinante y clasificación máx/mín/silla.** |
| **6.8** | Optimización (máximo de `E`) | 🟢 | `obtener_optimo()` en API Flask + tab "Óptimo" |
| **6.9** | Superficie `z=E(θ,φ)` | 🟢 | Tab "Superficie" → `surface_plot_E()` con punto actual en rojo |

### 7. Implementación computacional

| Funcionalidad | Estado | Dónde |
|---------------|--------|-------|
| Modificar θ y φ | 🟢 | Sidebar sliders |
| Modificar ubicación geográfica | 🟢 | Sidebar lat/lon + selector de mapa |
| Calcular energía captada | 🟢 | `E(θ,φ)` actual como métrica en tab "Panel" |
| Visualizar curvas de nivel | 🟢 | Tab "Contorno" |
| Representar superficie 3D | 🟢 | Tab "Superficie" |
| Calcular gradiente y derivadas parciales | 🟢 | Tab "Derivadas" |
| Determinar configuraciones óptimas | 🟢 | Tab "Óptimo" |
| Comparar configuraciones | 🟢 | Tab "Comparar" con tabla + gráficos de barras |
| Simulación diaria (Riemann) | 🟢 | Botón "Simular día" en sidebar + tab "Consumo Diario" |
| Evaluar sensibilidad / incertidumbre | 🟢 | Tab "Incertidumbre" |
| **Visualizar sombras** | 🟢 | **Nuevo tab "Sombras" con timeline, tabla de eventos y comparación con/sin sombra** |

### 8. Análisis de resultados

| Aspecto | Estado |
|---------|--------|
| Influencia de θ y φ sobre E | 🟢 Métricas + derivadas |
| Gradiente en distintas regiones | 🟢 Flecha en contorno |
| Interpretación de curvas de nivel | 🟢 Caption explicativo |
| Sensibilidad frente a errores | 🟢 Sliders de perturbación |
| Comparación óptimo vs actual | 🟢 Tab "Óptimo" con pérdidas |
| Impacto de sombras en generación | 🟢 Tab "Sombras" con pérdida en kWh y % |
| **Análisis escrito / reporte** | **🔴** |

---

## Funciones de la API

| Función | Endpoint Flask | Calcula |
|---------|-------|--------------------------|
| `obtener_energia` | `/api/energy` | `E`, `∂E/∂θ`, `∂E/∂φ`, `\|∇E\|`, dirección |
| `obtener_superficie` | `/api/surface` | Meshgrid `θ×φ` con `E` |
| `obtener_optimo` | `/api/optimal` | `θ₀`, `φ₀`, `E_max` |
| `obtener_derivada_direccional` | `/api/directional-derivative` | Producto punto: `∇E·(cosα, sinα)` |
| `obtener_hessiano` | `/api/hessian` | Matriz Hessiana, autovalores, clasificación |
| `simular` | `/api/simulate` | Simulación diaria con clima real + sombras |
| `calcular` | `/api/calculate` | Incertidumbre por error angular |

---

## Nuevos tabs agregados

| Tab | Contenido |
|-----|-----------|
| **Consumo Diario** | Curva de potencia diaria (con regiones sombreadas), energía acumulada, tabla horaria, datos ambientales (radiación, amanecer, atardecer) |
| **Sombras** | Timeline de eventos de sombra, tabla de eventos (inicio, fin, duración, factor), métricas de impacto, comparación potencia con/sin sombra |

---

## Coordenadas verificadas con sombras (invierno)

Requiere `pysolar` instalado.

| Ubicación | Latitud | Longitud | Factor sombra |
|-----------|---------|----------|---------------|
| Costanera Center, Santiago | -33.4175 | -70.6060 | 0.9 (12:30-19:00) |
| Paseo Ahumada, Santiago | -33.4370 | -70.6510 | 0.9 (12:00-19:00) |
| Los Leones, Santiago | -33.4220 | -70.6090 | 0.79 (12:30-19:00) |

---

## Resumen de cumplimiento

| Categoría | Estado |
|-----------|--------|
| Modelo simplificado `E(θ,φ)` | 🟢 |
| Derivadas, gradiente, direccional | 🟢 |
| Plano tangente / linealización | 🟢 |
| Puntos críticos / Hessiano | 🟢 |
| Optimización | 🟢 |
| Superficie 3D y curvas de nivel | 🟢 |
| Simulación diaria (Riemann) | 🟢 |
| Modelo extendido (sombras) | 🟢 (requiere `pysolar`) |
| Visualización de sombras | 🟢 Nuevo tab dedicado |
| Sensibilidad / incertidumbre | 🟢 |
| Infraestructura (API + frontend + persistencia) | 🟢 |
| **Análisis escrito / reporte interpretativo** | **🔴** |

**Total: 25/26 requisitos cumplidos — 1 pendiente (análisis escrito).**

---

## Próximos pasos recomendados

1. **Análisis escrito**: pestaña o sección con interpretación formal de resultados para cumplir con la documentación solicitada.
2. Agregar `pysolar` a `requirements.txt` como dependencia obligatoria para sombras.
