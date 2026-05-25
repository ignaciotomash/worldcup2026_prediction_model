import pandas as pd
import os
import kagglehub
import json

# 1. Descargar el dataset histórico desde Kaggle
print("Descargando datos históricos desde Kaggle...")
path = kagglehub.dataset_download("martj42/international-football-results-from-1872-to-2017")

# 2. Cargar el archivo bruto 'results.csv'
csv_path = os.path.join(path, "results.csv")
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"No se encontró results.csv en la ruta de Kagglehub: {path}")

df_raw = pd.read_csv(csv_path)

# =====================================================================
# PROCESAMIENTO Y LIMPIEZA DE DATOS (Para generar clean_matches.csv)
# =====================================================================
print("Limpiando y transformando el historial de partidos...")

# Filtrar solo las columnas que usa nuestro modelo
df_clean = df_raw[['date', 'home_team', 'away_team', 'home_score', 'away_score', 'neutral']].copy()

# Eliminar filas con valores nulos en los goles (partidos cancelados o no jugados)
df_clean = df_clean.dropna(subset=['home_score', 'away_score'])

# Convertir tipos de datos correctos
df_clean['home_score'] = df_clean['home_score'].astype(int)
df_clean['away_score'] = df_clean['away_score'].astype(int)
df_clean['neutral'] = df_clean['neutral'].astype(bool)

# Crear la columna 'result' (0: Gana Local, 1: Empate, 2: Gana Visitante)
def determine_result(row):
    if row['home_score'] > row['away_score']:
        return 0
    elif row['home_score'] < row['away_score']:
        return 2
    else:
        return 1

df_clean['result'] = df_clean.apply(determine_result, axis=1)

# Guardar el archivo limpio en la raíz del proyecto
df_clean.to_csv("clean_matches.csv", index=False)
print("¡Archivo 'clean_matches.csv' generado con éxito!")

# =====================================================================
# VERIFICACIÓN DEL RANKING FIFA
# =====================================================================
# El archivo fifa_ranking.json requiere credenciales o APIs oficiales de FIFA,
# por lo que el downloader solo debe verificar si ya lo tienes en la carpeta.
if os.path.exists("fifa_ranking.json"):
    print("¡Archivo 'fifa_ranking.json' detectado y listo para usar!")
else:
    print("\n[ALERTA] No se encontró 'fifa_ranking.json' en la carpeta.")
    print("Asegúrate de colocar tu archivo JSON de rankings en la raíz para que data_prep.py funcione.")