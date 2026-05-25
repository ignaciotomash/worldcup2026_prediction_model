import pandas as pd
import os

# Tu código original
import kagglehub
path = kagglehub.dataset_download("martj42/international-football-results-from-1872-to-2017")

# Ahora, listamos los archivos descargados
print("Archivos encontrados:", os.listdir(path))

# Cargamos el archivo principal (usualmente results.csv)
df_historico = pd.read_csv(os.path.join(path, "results.csv"))
print(df_historico.head())