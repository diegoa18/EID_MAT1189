# Análisis de Cumplimiento — Guía del Proyecto Final 5

> **Última actualización:** 29 junio 2026
> **Código fuente:** `src/streamlit/` (app Streamlit refactorizada)

---

## Estado general

El proyecto implementa el **núcleo completo de cálculo multivariable** (secciones 6.1–6.9 de la guía) en la app Streamlit. Las funciones matemáticas del modelo simplificado `E(θ,φ) = A·cos(θ−θ₀)·cos(φ−φ₀)` están implementadas como **placeholders hardcoded** en `src/streamlit/api.py` — son 4 funciones marcadas con `#aqui entra la api rodri qlo mueve la raja` que **deberían ser reemplazadas por el modelo que implemente Rodri** en la API Flask.

---

## Checklist detallado por sección de la guía

### 5. Modelo matemático

| Elemento | Estado | Dónde |
|----------|--------|-------|
| **5.1** `E(θ,ϕ)=A·cos(θ−θ₀)·cos(φ−φ₀)` | 🟢 Hardcoded en api.py | `obtener_energia()` — **placeholder de Rodri** |
| **5.2** Modelo extendido (estaciones, sombras, etc.) | ⚠️ Parcial | Estaciones: vía simulación diaria ✅. Sombras, nubosidad, tracking solar: 🔴 no implementados |

### 6. Herramientas de cálculo multivariable

| # | Elemento | Estado | Dónde / Detalle |
|---|----------|--------|-----------------|
| **6.1** | Función de varias variables `E(θ,φ)` | 🟢 | `obtener_energia()` en api.py (hardcoded, Rodri) |
| **6.2** | Curvas de nivel `E(θ,φ)=c` | 🟢 | Tab "Contorno" → `contour_plot_E()` en grapics.py |
| **6.3** | Derivadas parciales `∂E/∂θ`, `∂E/∂φ` | 🟢 | Tab "Derivadas" → devueltas por `obtener_energia()` (Rodri) |
| **6.4** | Gradiente `∇E` | 🟢 | Magnitud + dirección en tab "Derivadas", flecha sobre contorno |
| **6.5** | Derivadas direccionales | 🟢 | `obtener_derivada_direccional()` + slider α en tab "Derivadas" (Rodri) |
| **6.6** | Plano tangente / linealización | 🟢 | Tab "Óptimo" → slider θ_eval, φ_eval, compara E_lineal vs E_exacta |
| **6.7** | **Puntos críticos + Hessiano** | **🔴** | **No implementado. No hay matriz Hessiana ni clasificación máx/mín/silla.** |
| **6.8** | Optimización (máximo de `E`) | 🟢 | `obtener_optimo()` en api.py + tab "Óptimo" (Rodri) |
| **6.9** | Superficie `z=E(θ,φ)` | 🟢 | Tab "Superficie" → `surface_plot_E()` con punto actual en rojo |

### 7. Implementación computacional

| Funcionalidad | Estado | Dónde |
|---------------|--------|-------|
| Modificar θ y φ | 🟢 | Sidebar sliders |
| Modificar ubicación geográfica | 🟢 | Sidebar lat/lon |
| Calcular energía captada | 🟢 | `E(θ,φ)` actual como métrica en tab "Panel" |
| Visualizar curvas de nivel | 🟢 | Tab "Contorno" |
| Representar superficie 3D | 🟢 | Tab "Superficie" |
| Calcular gradiente y derivadas parciales | 🟢 | Tab "Derivadas" |
| Determinar configuraciones óptimas | 🟢 | Tab "Óptimo" |
| Comparar configuraciones | 🟢 | Tab "Comparar" con tabla + gráficos de barras |
| Simulación diaria (Riemann) | 🟢 | Botón "Simular día" en sidebar + gráfico en tab "Panel" |
| Evaluar sensibilidad / incertidumbre | 🟢 | Tab "Incertidumbre" |

### 8. Análisis de resultados

| Aspecto | Estado |
|---------|--------|
| Influencia de θ y φ sobre E | 🟢 Métricas + derivadas |
| Gradiente en distintas regiones | 🟢 Flecha en contorno |
| Interpretación de curvas de nivel | 🟢 Caption explicativo |
| Sensibilidad frente a errores | 🟢 Sliders de perturbación |
| Comparación óptimo vs actual | 🟢 Tab "Óptimo" con pérdidas |
| **Análisis escrito / reporte** | **🔴** |

---

## Funciones de Rodri (placeholders en `api.py`)

Las 4 funciones marcadas con `#aqui entra la api rodri qlo mueve la raja` deben ser reemplazadas por llamadas a la API Flask que implemente Rodri:

| Función | Línea | Calcula (hardcoded hoy) |
|---------|-------|--------------------------|
| `obtener_energia(theta, phi, A, theta0, phi0)` | 54 | `E = A·cos(Δθ)·cos(Δφ)`, `∂E/∂θ`, `∂E/∂φ`, `\|∇E\|`, dirección |
| `obtener_superficie(A, theta0, phi0, res)` | 73 | Meshgrid `θ×φ` con `E = A·cos(Δθ)·cos(Δφ)` |
| `obtener_optimo(latitude, power_gen)` | 89 | `θ₀ = \|latitude\|`, `φ₀ = 0° (HN) / 180° (HS)`, `E_max = power_gen` |
| `obtener_derivada_direccional(theta, phi, A, theta0, phi0, alpha)` | 101 | Producto punto: `∇E·(cosα, sinα)` |

---

## Resumen de cumplimiento

| Categoría | Estado |
|-----------|--------|
| Modelo simplificado `E(θ,φ)` | 🟢 21/26 |
| **Puntos críticos / Hessiano (6.7)** | **🔴** |
| **Modelo extendido (sombras, nubosidad, tracking)** | **🔴** |
| **Análisis escrito / reporte interpretativo** | **🔴** |
| Infraestructura (API + frontend + persistencia) | 🟢 |

**Total: 21/26 requisitos cumplidos — 5 pendientes.**

---

## Próximos pasos recomendados

1. **Rodri**: implementar las 4 funciones en la API Flask y eliminar los placeholders
2. **Hessiano + clasificación**: agregar `obtener_hessiano()` y pestaña que muestre `H(θ,φ)`, autovalores y clasificación
3. **Modelo extendido**: sombras (checkbox), nubosidad (slider %), tracking solar (toggle)
4. **Análisis escrito**: pestaña o sección con interpretación formal de resultados
