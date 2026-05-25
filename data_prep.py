import pandas as pd
import json

# 1. Cargar datos
df = pd.read_csv("clean_matches.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

# Asignar puntos por resultado (3 por ganar, 1 empate, 0 perder)
df['home_pts'] = df['result'].map({0: 3, 1: 1, 2: 0})
df['away_pts'] = df['result'].map({0: 0, 1: 1, 2: 3})

print("Calculando promedio de puntos de los últimos 2 años...")

def get_form_2_years(team, current_date, dataframe):
    # Filtrar partidos del equipo ANTES de la fecha del partido actual
    past_matches = dataframe[(dataframe['date'] < current_date) & 
                             ((dataframe['home_team'] == team) | (dataframe['away_team'] == team))]
    
    # Filtrar solo los últimos 2 años (730 días)
    two_years_ago = current_date - pd.Timedelta(days=730)
    recent_matches = past_matches[past_matches['date'] >= two_years_ago]
    
    if recent_matches.empty:
        return 1.0  # Valor por defecto (un empate promedio)
        
    total_pts = 0
    for _, match in recent_matches.iterrows():
        if match['home_team'] == team:
            total_pts += match['home_pts']
        else:
            total_pts += match['away_pts']
            
    # Retornamos el PROMEDIO de puntos por partido
    return total_pts / len(recent_matches)

# Aplicar el cálculo fila por fila
home_forms = []
away_forms = []

for idx, row in df.iterrows():
    home_forms.append(get_form_2_years(row['home_team'], row['date'], df))
    away_forms.append(get_form_2_years(row['away_team'], row['date'], df))

df['home_form'] = home_forms
df['away_form'] = away_forms

# 2. Cargar JSON de la FIFA (en inglés)
with open("fifa_ranking.json", "r", encoding="utf-8") as f:
    fifa_data = json.load(f)["Results"]

points_dict = {}
for team in fifa_data:
    team_name = next((lang['Description'] for lang in team['TeamName'] if lang['Locale'] == 'en-GB'), None)
    if team_name:
        points_dict[team_name] = team['TotalPoints']

# Inyectar puntos FIFA
df['home_points'] = df['home_team'].map(points_dict).fillna(1200.0).astype(float)
df['away_points'] = df['away_team'].map(points_dict).fillna(1200.0).astype(float)

# =====================================================================
# NUEVO: INGENIERÍA DE CARACTERÍSTICAS (BRECHAS DE RENDIMIENTO Y RANKING)
# =====================================================================
df['dif_points'] = df['home_points'] - df['away_points']
df['dif_form'] = df['home_form'] - df['away_form']

# Guardar con las nuevas columnas
df.to_csv("clean_matches_form_rank.csv", index=False)
print("¡Proceso completado! Dataset generado con variables de diferencia (Brechas).")