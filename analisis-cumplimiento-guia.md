# Análisis de Cumplimiento — Guía del Proyecto Final 5

> **Rama actual:** `dev-quintero` (commit `90f43ef`)
> **Fecha del análisis:** 28 junio 2026

---

## Estado general

El proyecto construyó una infraestructura sólida (API Flask + Streamlit + integración con Open-Meteo) pero la mayor parte del **núcleo de cálculo multivariable requerido por la guía no está implementado en código**. Lo que existe en el README como "fundamento teórico" es documentación, no código ejecutable.

---

## Checklist detallado por sección de la guía

### 5. Modelo matemático

| Elemento | Estado | Observación |
|----------|--------|-------------|
| **5.1** `E(θ, ϕ) = A cos(θ − θ₀) cos(ϕ − ϕ₀)` | ❌ No implementada | No existe una función `energy(theta, phi, A, theta0, phi0)` en ningún archivo. Solo está documentada en README. |
| **5.2** Modelo extendido (estaciones, sombras, etc.) | ⚠️ Parcial | Estaciones vía Open-Meteo OK. Sombras, nubosidad, tracking solar, edificaciones: no implementados. |

### 6. Herramientas de cálculo multivariable

| Sección | Elemento | Estado | Observación |
|---------|----------|--------|-------------|
| **6.1** | Función de varias variables | ❌ | No hay código que implemente `E(θ, ϕ)` como función invocable |
| **6.2** | Curvas de nivel `E(θ, ϕ) = c` | ❌ | No se genera ningún contour plot de `E(θ, ϕ)`. El README referencia `solar_optimization_plots.png` pero el archivo **no existe**. |
| **6.3** | Derivadas parciales `∂E/∂θ`, `∂E/∂ϕ` | ❌ | No hay funciones que las computen (ni simbólica ni numéricamente). Solo fórmulas en README. |
| **6.4** | Gradiente `∇E(θ, ϕ)` | ❌ | No implementado. Solo descrito en README. |
| **6.5** | Derivadas direccionales | ❌ | No implementadas. Ni mencionadas. |
| **6.6** | Plano tangente / linealización | ❌ | No implementado. Ni mencionado. |
| **6.7** | Puntos críticos `∇E = 0` | ❌ | No implementado. La optimización existente usa heurística por latitud, no derivadas. |
| **6.8** | Optimización (máximo de E) | ⚠️ Parcial | `get_ideal_facing_direction()` retorna "North"/"South" según hemisferio. `get_ideal_tilt_angle()` retorna `abs(latitud)` vía `acos(cos(lat))`. **Ninguno de los dos se obtiene de optimizar `E(θ, ϕ)`**. |
| **6.9** | Gráfica de superficie `z = E(θ, ϕ)` | ❌ | `grapics.py` muestra el panel físico en 3D, no la superficie de `E(θ, ϕ)`. No existe superficie energética. |

### 7. Implementación computacional

| Funcionalidad | Estado | Observación |
|---------------|--------|-------------|
| Modificar θ y ϕ | ✅ | Vía sliders en Streamlit y JSON en API |
| Modificar ubicación geográfica | ✅ | Lat/Lon en API y Streamlit |
| Calcular energía captada | ⚠️ | Se calcula potencia vía simulación sinusoidal, no `E(θ, ϕ)` |
| Visualizar curvas de nivel | ❌ | No implementado |
| Representar superficie de E(θ, ϕ) | ❌ | No implementado |
| Calcular gradiente y derivadas parciales | ❌ | No implementado |
| Determinar configuraciones óptimas | ⚠️ | Solo heurística por latitud |
| Comparar configuraciones | ⚠️ | Parcial (métricas en Streamlit) |

### 8. Análisis de resultados

| Aspecto | Estado |
|---------|--------|
| Influencia de la inclinación sobre energía | ❌ No analizado |
| Influencia de la orientación geográfica | ❌ No analizado |
| Comportamiento del gradiente en distintas regiones | ❌ No analizado |
| Interpretación de curvas de nivel | ❌ No analizado |
| Sensibilidad frente a errores de instalación | ⚠️ `expected_power_angle_integral()` existe pero su relación con `E(θ, ϕ)` no es clara |
| Comparación configuraciones óptimas vs no óptimas | ❌ No analizado |
| Factibilidad práctica | ❌ No analizado |

---

## Problemas específicos detectados

### 1. No existe la función `E(θ, ϕ)`

La guía define el modelo en la sección 5.1 como:

```
E(θ, ϕ) = A cos(θ − θ₀) cos(ϕ − ϕ₀)
```

No hay ninguna función en el código que reciba `(theta, phi, A, theta0, phi0)` y retorne el valor de energía. Sin esta función **no es posible** calcular derivadas parciales, gradiente, curvas de nivel, ni la superficie `z = E(θ, ϕ)`.

### 2. `solar_optimization.py` no existe

El README referencia este archivo y una imagen `solar_optimization_plots.png`, pero **ninguno de los dos existe** en el repositorio. Es material de una versión anterior o planeada que nunca se concretó.

### 3. `get_ideal_tilt_angle()` es redundante

```python
tilt_rad = math.acos(math.cos(lat_rad))   # ≡ abs(lat_rad)
return math.degrees(tilt_rad)
```

`acos(cos(x)) = |x|` para x en `[−π, π]`. La función simplemente retorna el valor absoluto de la latitud. No proviene de maximizar `E(θ, ϕ)`.

### 4. `expected_power_angle_integral()` tiene problemas

```python
integral_value = self.power_gen * (2 * math.sin(dt)) * (2 * math.sin(dp))
integration_area = (2 * dt) * (2 * dp)
return integral_value / integration_area
```

Esto computa `A * (sin(dt)/dt) * (sin(dp)/dp)`. La derivación parece asumir integración de `A * cos(θ) * cos(ϕ)` sobre `[-dt, dt] × [-dp, dp]`, con θ₀ = ϕ₀ = 0. Si esa es la intención, está incompleta: no usa θ₀, ϕ₀, y no está vinculada a la función `E(θ, ϕ)` definida en la guía.

### 5. La API acepta parámetros que después ignora

El README muestra un endpoint `POST /api/calculate` que recibe `"theta"` y `"phi"`, pero la implementación real en `app.py` recibe `"delta_theta"` y `"delta_phi"`. Hay una discrepancia entre la documentación y la implementación.

---

## Resumen de brechas respecto a la guía

| Categoría | Total requerido | Implementado | % |
|-----------|----------------|--------------|---|
| Modelo matemático (`E(θ, ϕ)`) | 1 | 0 | 0% |
| Derivadas parciales | 2 | 0 | 0% |
| Gradiente | 1 | 0 | 0% |
| Derivadas direccionales | 1 | 0 | 0% |
| Plano tangente / linealización | 1 | 0 | 0% |
| Puntos críticos | 1 | 0 | 0% |
| Optimización basada en E | 1 | 0 | 0% |
| Curvas de nivel | 1 | 0 | 0% |
| Superficie `z = E(θ, ϕ)` | 1 | 0 | 0% |
| Infraestructura (API + frontend + datos) | — | ✅ Completo | ~80% |
| Simulación diaria (Riemann) | — | ✅ | Hecho |
| Integral de área física | — | ⚠️ Trivial | Hecho |

---

## Conclusión

**El proyecto no está estable para continuar con la extensión (modelo extendido, sombras, etc.) porque el núcleo matemático de la guía —secciones 6.1 a 6.9— no está implementado.**

Lo que se construyó es útil como infraestructura (API, frontend, obtención de datos climáticos, simulación horaria), pero salta los componentes fundamentales de cálculo multivariable que la guía exige:

1. **Implementar `E(θ, ϕ)`** como función
2. **Calcular derivadas parciales** (simbólica o numérica)
3. **Calcular el gradiente** y mostrarlo sobre curvas de nivel
4. **Calcular derivadas direccionales**
5. **Linealización** (plano tangente)
6. **Encontrar y clasificar puntos críticos**
7. **Graficar superficie** `z = E(θ, ϕ)`
8. **Graficar curvas de nivel** de `E`

### Recomendación

Antes de abordar el modelo extendido (sombras, tracking, estaciones), implementar el modelo simplificado de la sección 5.1 con todas las herramientas de cálculo de la sección 6. El resto de la infraestructura (API, Streamlit, Open-Meteo) ya está lista para consumir estas nuevas funciones.

---

*Documento generado automáticamente — Revisar antes de usar como referencia oficial.*
