# 🏆 FIFA World Cup 2026 Predictor & Simulator

Un motor de simulación probabilística y matemática diseñado para modelar el desarrollo completo de la Copa Mundial de la FIFA 2026 (formato de 48 equipos).

Este proyecto no es un simple generador de llaves aleatorias. Utiliza un modelo de Machine Learning multiclase pre-entrenado para evaluar enfrentamientos directos basándose en datos históricos, estado de forma reciente (form) y la posición actualizada en el Ranking FIFA. Además, incorpora los resultados reales del torneo a medida que se van jugando, y resuelve problemas lógicos complejos inherentes al nuevo formato, como la asignación reglamentaria de los mejores terceros mediante algoritmos de satisfacción de restricciones.

---

## 🔄 Arquitectura y Flujo de Trabajo (Workflow)

El sistema opera bajo un pipeline lineal donde los datos históricos y el modelo estático alimentan al motor de simulación para generar un resultado visual autónomo y dinámico en cada ejecución.

```
[ Datos Históricos ]       [ Rankings FIFA ]
  clean_matches.csv      fifa_ranking_years/*.json
          \               /
           v             v
      [ Preparación de Datos ]
           data_prep.py
                |
                v
   clean_matches_form_rank.csv
                |
                v
      [ Entrenamiento del Modelo ]
           train_model.py
                |
                v
         football_model.pkl
                |
                v
           predictor.py
          (módulo compartido:
           simulate_match,
           get_team_data)
                |
                v
     [ Motor de Simulación y Reglas FIFA ]
              wc_simulator.py  <----------------- clean_matches.csv
                   |                        (resultados reales ya jugados)
                   |                         
                   |
                   | 1. Resultados reales del CSV (partidos ya jugados)
                   | 2. Simulación de partidos pendientes
                   | 3. Resolución de Desempates FIFA
                   | 4. Asignación de Terceros (CSP)
                   | 5. Playoffs (Knockout Stage)
                   v
       [ Interfaz Gráfica de Salida ]
            fixture_mundial.html
```

---

## 📁 Descripción Funcional de Archivos

### `data_prep.py`
Procesa el historial de partidos y los rankings FIFA históricos. Calcula las métricas de cada selección (form, goles promedio, puntos FIFA) usando ventanas móviles de 730 días y genera el dataset final `clean_matches_form_rank.csv`. Se puede ejecutar después de cada jornada para incorporar los partidos más recientes al entrenamiento.

### `train_model.py`
Entrena el modelo de Machine Learning multiclase (**Local gana / Empate / Visitante gana**) usando Random Forest sobre el dataset preparado. Evalúa su rendimiento con métricas detalladas por clase y serializa el modelo entrenado en `football_model.pkl`.

### `football_model.pkl`
Modelo Random Forest serializado. Recibe las diferencias estadísticas relativas entre dos equipos (ranking, goles promedio, form, puntos FIFA) y devuelve tres probabilidades: victoria equipo A, empate, victoria equipo B.

### `clean_matches_form_rank.csv`
Dataset estructurado con el historial completo de partidos internacionales enriquecido con métricas calculadas de cada selección. Es la fuente de datos que usa `predictor.py` para extraer el estado actual de cada equipo.

### `predictor.py`
Módulo central compartido por `match_pred.py` y `wc_simulator.py`. Contiene dos funciones principales:
- `get_team_data(team)` — extrae las métricas más recientes de un equipo desde el CSV.
- `simulate_match(team_a, team_b)` — ejecuta la predicción simétrica neutral con el modelo y genera el marcador mediante simulación Monte Carlo con distribución de Poisson. Devuelve outcome, goles y las tres probabilidades.

### `wc_simulator.py`
Núcleo lógico del torneo. Orquesta la simulación completa del Mundial aplicando estrictamente el reglamento FIFA. Para cada partido de la fase de grupos consulta primero `clean_matches.csv` — si el partido ya se jugó usa el resultado real, si está pendiente lo simula. Genera `fixture_mundial.html` al finalizar.

### `match_pred.py`
Simulador de partido individual. Importa `predictor.py` y formatea la salida en consola mostrando marcador, pronóstico, probabilidades de los tres resultados y métricas de contexto de ambos equipos. Para simular un partido distinto, editar la última línea del archivo.

### `run_pipeline.py`
Ejecuta en cadena `data_prep.py` → `train_model.py` en una sola llamada. Recomendado correrlo después de cada jornada del Mundial para actualizar el form y reentrenar el modelo con los partidos más recientes.

### `fixture_mundial.html`
Producto final generado automáticamente. Visualiza el bracket eliminatorio completo y las 12 tablas de posiciones de grupos en una interfaz HTML interactiva. Se sobreescribe en cada ejecución de `wc_simulator.py`.

---

## ⚙️ Lógica Interna y Reglas Implementadas

### 1. Modelo Multiclase (Local / Empate / Visitante)
El modelo Random Forest predice directamente tres probabilidades reales aprendidas de los datos históricos. Esto reemplaza el enfoque binario anterior que solo distinguía "gana local / no gana local" e inventaba los empates con un umbral arbitrario.

### 2. Simulación Simétrica para Mitigación de Sesgos
El motor evalúa cada encuentro dos veces intercambiando la posición de local y visitante en las entradas del modelo, y promedia las probabilidades resultantes. Esto neutraliza el sesgo de localía heredado de los datasets históricos.

### 3. Incorporación de Resultados Reales
Durante la fase de grupos, el simulador consulta `clean_matches.csv` antes de simular cada partido. Si el partido ya fue jugado (fecha >= 11/06/2026), usa el marcador real directamente. Si está pendiente, lo simula con el modelo. Esto permite correr el simulador en cualquier momento del torneo con la realidad incorporada.

### 4. Marcadores vía Monte Carlo + Poisson
Para los partidos simulados, se generan 1000 marcadores aleatorios usando distribución de Poisson calibrada con los promedios históricos de goles de cada equipo. Solo se conservan los marcadores que coinciden con el resultado predicho por el modelo, y se toma el promedio como marcador representativo.

### 5. Desempates Estrictos (Tie-breakers)
Cuando dos o más selecciones terminan con los mismos puntos, el sistema aplica el reglamento oficial de la FIFA en orden:

| Prioridad | Criterio |
|-----------|----------|
| 1° | Puntos (PTS) |
| 2° | Diferencia de Goles (DG) |
| 3° | Goles a Favor (GF) |
| 4° | Enfrentamiento Directo H2H (PTS → DG → GF) |

### 6. Algoritmo CSP para Asignación de Terceros
El formato de 12 grupos clasifica los 8 mejores terceros a dieciseisavos. Asignarlos al bracket congelado respetando que ningún tercero puede enfrentarse al ganador de su mismo grupo es un problema de satisfacción de restricciones. El código lo resuelve con **backtracking y heurística MRV** (Most Restricted Variable) que elige siempre la ranura con menos candidatos válidos disponibles.

---

## 📋 Requisitos e Instalación

Python 3.8+ requerido. Instalar dependencias:

```bash
pip install pandas numpy joblib scikit-learn
```

---

## 🚀 Uso

### Flujo completo desde cero
```bash
python run_pipeline.py    # prepara datos y entrena modelo
python wc_simulator.py    # simula el torneo y genera HTML
```

### Actualizar después de cada jornada
```bash
python run_pipeline.py    # incorpora partidos nuevos y reentrena
python wc_simulator.py    # resimula con resultados reales actualizados
```

### Predecir un partido puntual
```bash
python match_pred.py      # editar la última línea con los equipos deseados
```

---

> **Nota:** Los nombres de países están en inglés en todo el pipeline. Las fuentes de datos originales estaban en español, por lo que `data_prep.py` incluye un diccionario de traducción `ES_TO_EN` para unificar los nombres antes del procesamiento.