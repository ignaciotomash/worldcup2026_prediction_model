import pandas as pd
import kagglehub
import os

# Descargar (si ya lo hiciste, kagglehub simplemente devolverá el path)
path = kagglehub.dataset_download("martj42/international-football-results-from-1872-to-2017") # Nota: el dataset ha sido actualizado
df = pd.read_csv(os.path.join(path, "results.csv"))

# Ver las últimas filas para confirmar que llega a 2025
print("Últimos partidos registrados:")
print(df.tail())

# Ver cuántos torneos distintos hay
print("\nTipos de torneos:", df['tournament'].unique())