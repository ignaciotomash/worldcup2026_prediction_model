To try it yourself, go to:

/match_pred.py

and in the bottom of the file, you will find "prediction_neutral(param1,param2)"; thats where you need to put the two countries you want to simulate.

The answer will be in the Terminal! later on I will make it better to see, as in a graphic or something similar.


-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


General Concept: File Workflow:

Extraction, Data Preparation/Training, and Prediction.

[ data_downloader.py ] ──> Generates ──> ( clean_matches.csv & fifa_ranking.json )
                                                        │
                                                 Passes clean data to
                                                        │
                                                        ▼
[ data_prep.py ] ───────> Generates ──> ( clean_matches_form_rank.csv )
                                                        │
                                                    Feeds into
                                                        │
                                                        ▼
[ train_model.py ] ─────> Generates ──> ( football_model.pkl )
                                                        │
                                                    Acts as the brain for
                                                        │
                                                        ▼
[ match_pred.py ] ──────> Displays the final result on your screen.

File Breakdown

clean_matches.csv: Raw material. It contains the raw historical data of international football matches (teams, scores, dates, and whether the venue was neutral).

fifa_ranking.json: External JSON from FIFA website; it contains the exact points for each national team according to the latest official FIFA ranking.

data_prep.py: The data processor. It reads the raw CSV and the FIFA JSON, performs complex row-by-row mathematical calculations (the 2-year Points Per Game average for each team), and computes the direct mathematical difference between them (the gaps).

clean_matches_form_rank.csv: The refined product. It is identical to the original CSV but includes the new feature-engineered columns calculated by data_prep.py (dif_points and dif_form). This file is used exclusively to train the model.

train_model.py: The instructor. It takes the refined CSV, extracts only the gap columns (X) and the historical result (y). It configures the Random Forest classifier, evaluates its performance, and saves that trained "brain" into the .pkl file.

match_pred.py: The strategy consultant. It doesn't train or clean data. It simply takes two teams, calculates their current gaps using time-based functions, queries the serialized model (football_model.pkl), and prints the formatted prediction probabilities to the terminal.


-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Para probarlo por tu cuenta, ve a:

/match_pred.py

en el final del archivo vas a encontrar "prediction_neutral(parametro1,parametro2)"; allí es donde colocas los 2 paises (en ingles) que queres simular.

La respuesta estará en la terminal; en un futuro pretendo mostrar los datos de una forma mas amigable como un grafico.

Concepto General: Flujo de Archivos
Extracción, Preparación de Datos/Entrenamiento y Predicción.

[ data_downloader.py ] ──> Genera ──> ( clean_matches.csv & fifa_ranking.json )
                                                       │
                                                 Pasa los datos limpios a
                                                       │
                                                       ▼
[ data_prep.py ] ───────> Genera ──> ( clean_matches_form_rank.csv )
                                                       │
                                                    Alimenta a
                                                       │
                                                       ▼
[ train_model.py ] ─────> Genera ──> ( football_model.pkl )
                                                       │
                                                 Actúa como el cerebro de
                                                       │
                                                       ▼
[ match_pred.py ] ──────> Muestra el resultado final en tu pantalla.
Desglose de Archivos
clean_matches.csv: La materia prima. Contiene el historial de datos crudos de partidos internacionales de fútbol (equipos, resultados, fechas y si la sede fue neutral).

fifa_ranking.json: JSON externo extraído del sitio web de la FIFA; contiene los puntos exactos de cada selección nacional según el último ranking oficial de la FIFA.

data_prep.py: El procesador de datos. Lee el CSV crudo y el JSON de la FIFA, realiza cálculos matemáticos complejos fila por fila (el promedio de Puntos Por Partido —PPG— de los últimos 2 años para cada equipo) y calcula la diferencia matemática directa entre ambos (las brechas).

clean_matches_form_rank.csv: El producto refinado. Es idéntico al CSV original, pero incluye las nuevas columnas creadas mediante ingeniería de características calculadas por data_prep.py (dif_points y dif_form). Este archivo se utiliza exclusivamente para entrenar el modelo.

train_model.py: El instructor. Toma el CSV refinado, extrae solo las columnas de brechas (X) y el resultado histórico (y). Configura el clasificador Random Forest, evalúa su rendimiento y guarda ese "cerebro" entrenado en el archivo .pkl.

match_pred.py: El consultor de estrategia. No entrena ni limpia datos. Simplemente toma dos equipos, calcula sus brechas actuales utilizando funciones basadas en el tiempo, consulta al modelo serializado (football_model.pkl) e imprime en la terminal las probabilidades de predicción formateadas.


# 🏆 FIFA World Cup 2026 Predictor & Simulator

Un motor de simulación probabilística y matemática diseñado para modelar el desarrollo completo de la Copa Mundial de la FIFA 2026 (formato de 48 equipos).

Este proyecto no es un simple generador de llaves aleatorias. Utiliza un modelo de Machine Learning pre-entrenado para evaluar enfrentamientos directos basándose en datos históricos, estado de forma reciente (form) y la posición actualizada en el Ranking FIFA. Además, resuelve problemas lógicos complejos inherentes al nuevo formato del torneo, como la asignación reglamentaria de los mejores terceros mediante algoritmos de satisfacción de restricciones.

---

## 🔄 Arquitectura y Flujo de Trabajo (Workflow)

El sistema opera bajo un pipeline lineal donde los datos históricos y el modelo estático alimentan al motor de simulación para generar un resultado visual autónomo y dinámico en cada ejecución.

[ Datos Históricos ]         [ Modelo Pre-entrenado ]
clean_matches_form_rank.csv    football_model.pkl
             \                     /
              \                   /
               v                 v
        [ Motor de Simulación y Reglas FIFA ]
                  wc_simulator.py
                       |
                       | 1. Simulación Fase de Grupos
                       | 2. Resolución de Desempates
                       | 3. Asignación de Terceros (CSP)
                       | 4. Playoffs (Knockout Stage)
                       v
           [ Interfaz Gráfica de Salida ]
                fixture_mundial.html

### Descripción Funcional de Archivos

* **`clean_matches_form_rank.csv`**: Es la base de datos estructurada. Contiene el historial de partidos internacionales limpios y las métricas calculadas de cada selección (Goles a Favor/En Contra históricos, Puntos, Ranking FIFA y un índice de estado de forma). El script consulta este archivo en tiempo real para obtener las estadísticas base de los equipos antes de simular un cruce.
* **`football_model.pkl`**: Es el modelo de Machine Learning serializado. Recibe las diferencias estadísticas relativas entre dos equipos (diferencia de ranking, diferencia de goles promedio, diferencia de puntos form) y devuelve una matriz de probabilidades indicando la posibilidad matemática de victoria del equipo A, empate, o victoria del equipo B.
* **`wc_simulator.py`**: Es el núcleo lógico del proyecto. Orquesta la lectura de datos, invoca al modelo para los 104 partidos correspondientes y aplica estrictamente el reglamento oficial de la FIFA para avanzar de ronda y ordenar las llaves eliminatorias.
* **`fixture_mundial.html`**: Es el producto final. Un archivo generado dinámicamente con código HTML y CSS inyectado desde Python. Se sobreescribe en cada ejecución para visualizar el bracket interactivo y las tablas de posiciones sin requerir frameworks web externos.

* **`run_pipeline`**: Realiza el proceso de descarga, preparacion y entrenamiento con un solo script; basicamente es como ejecutar los 3 scripts que lo hacen por separado pero de una sola ejecución. Se puede ejecutar despues de cada partido para poder actualizar el entrenamiento del modelo.

Además...
* **`macth_pred.py`**: Es el simulador de un partido en particular; se debe ir hasta lo último del archivo para encontrar el método cuyos parametros son los 2 equipos que se desea evaluar en un partido. El resultado se presenta en consola con los datos de PPG (Points per game o puntos por partido) y con el ranking fifa + los puntos de dicho ranking.
---

## ⚙️ Lógica Interna y Reglas Implementadas

El desarrollo abarca más que la simple predicción binaria, abordando rigurosamente las normativas reglamentarias del mundial:

1.  **Simulación Simétrica para Mitigación de Sesgos:**
    El motor evalúa cada encuentro dos veces. Intercambia la posición de "Local" y "Visitante" en las entradas del modelo y promedia las matrices de probabilidad resultantes. Esto neutraliza el sesgo de localía que los algoritmos suelen heredar de los datasets históricos de fútbol.
2.  **Calibración de Empates y Umbrales:**
    Se utiliza una variable de control `UMBRAL_EMPATE` (configurada en 0.12). Si la diferencia de probabilidades de victoria entre ambos equipos es menor a esta cifra, el partido se decreta empate en tiempo regular. Durante la fase eliminatoria, si un partido termina en empate, se fuerza una resolución lógica por penales basada en la ventaja probabilística residual.
3.  **Desempates Estrictos (Tie-breakers):**
    Cuando dos o más selecciones terminan con los mismos puntos, el sistema evita las resoluciones aleatorias implementando el algoritmo oficial de la FIFA: Mayor Diferencia de Goles (DG) > Mayores Goles a Favor (GF) > Desempate por enfrentamientos directos (Head-to-Head).
4.  **Algoritmo de Satisfacción de Restricciones para Terceros:**
    El formato de 12 grupos clasifica a los 8 mejores terceros a dieciseisavos de final. Asignarlos en el bracket congelado genera un problema matemático de "callejones sin salida". El código implementa un algoritmo Las Vegas (fuerza bruta con reintentos aleatorios) que procesa miles de permutaciones en milisegundos para garantizar que se cumpla la única regla inquebrantable de la llave: ningún tercero puede enfrentarse al ganador proveniente de su mismo grupo.

---

## 📋 Requisitos e Instalación

Es necesario contar con **Python 3.8+**. Clona este repositorio e instala las dependencias de ciencia de datos requeridas mediante `pip`:

```bash
pip install pandas numpy joblib scikit-learn;

```
PD: Tuve problemas con inconsistencias entre nombres en español y en ingles; el resultado se con los paises en ingles pero el codigo contiene ambos idiomas. Esto se debe a las distintas fuentes de donde obtuve los datos.