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
