import pandas as pd
import json
import glob
import os

# =====================================================================
# 1. DICCIONARIO DE TRADUCCIÓN
# =====================================================================
ES_TO_EN = {
    "Argelia": "Algeria", "Argentina": "Argentina", "Australia": "Australia", "Austria": "Austria",
    "Bélgica": "Belgium", "Bosnia y Herzegovina": "Bosnia and Herzegovina", "Brasil": "Brazil",
    "Canadá": "Canada", "Cabo Verde": "Cape Verde", "Colombia": "Colombia", "Croacia": "Croatia",
    "Curazao": "Curacao", "República Checa": "Czech Republic", "RD Congo": "DR Congo", "Ecuador": "Ecuador",
    "Egipto": "Egypt", "Inglaterra": "England", "Francia": "France", "Alemania": "Germany",
    "Ghana": "Ghana", "Haití": "Haiti", "Irán": "Iran", "Irak": "Iraq", "Costa de Marfil": "Ivory Coast",
    "Japón": "Japan", "Jordania": "Jordan", "México": "Mexico", "Marruecos": "Morocco",
    "Países Bajos": "Netherlands", "Nueva Zelanda": "New Zealand", "Noruega": "Norway",
    "Panamá": "Panama", "Paraguay": "Paraguay", "Portugal": "Portugal", "Catar": "Qatar",
    "Arabia Saudita": "Saudi Arabia", "Escocia": "Scotland", "Senegal": "Senegal",
    "Sudáfrica": "South Africa", "República de Corea": "South Korea", "España": "Spain",
    "Suecia": "Sweden", "Suiza": "Switzerland", "Túnez": "Tunisia", "Turquía": "Turkey",
    "Estados Unidos": "United States", "Uruguay": "Uruguay", "Uzbekistán": "Uzbekistan"
}

# =====================================================================
# 2. CARGA MASIVA Y UNIFICACIÓN DE JSON HISTÓRICOS
# =====================================================================
print("Procesando archivos JSON de Rankings FIFA...")
ranking_records = []
json_files = glob.glob("fifa_ranking_years/fifa_ranking_*.json")

for filepath in json_files:
    filename = os.path.basename(filepath)
    parts = filename.replace(".json", "").split("_")
    year, month = int(parts[2]), int(parts[3])
    ranking_date = pd.Timestamp(year=year, month=month, day=1)
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        for team in data["Results"]:
            es_name = next((lang['Description'] for lang in team['TeamName'] if lang['Locale'] == 'es-ES'), None)
            points_val = team.get('TotalPoints')
            points = float(points_val) if points_val is not None else 1200.0
            rank_val = team.get('Rank')
            rank_pos = int(rank_val) if rank_val is not None else 200
            
            if es_name:
                en_name = ES_TO_EN.get(es_name, es_name) 
                ranking_records.append({
                    'ranking_date': ranking_date, 'team': en_name, 'fifa_points': points, 'fifa_rank': rank_pos
                })

df_rankings = pd.DataFrame(ranking_records).sort_values('ranking_date')

# =====================================================================
# 3. PROCESAMIENTO DEL DATASET DE PARTIDOS
# =====================================================================
print("Cargando historial de partidos...")
df = pd.read_csv("clean_matches.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

print("Inyectando Rankings Históricos...")
df = pd.merge_asof(
    df, df_rankings.rename(columns={'ranking_date': 'date', 'team': 'home_team', 'fifa_points': 'home_hist_pts', 'fifa_rank': 'home_rank_pos'}),
    on='date', by='home_team', direction='backward'
)
df = pd.merge_asof(
    df, df_rankings.rename(columns={'ranking_date': 'date', 'team': 'away_team', 'fifa_points': 'away_hist_pts', 'fifa_rank': 'away_rank_pos'}),
    on='date', by='away_team', direction='backward'
)

df['home_hist_pts'] = df['home_hist_pts'].fillna(1200.0)
df['away_hist_pts'] = df['away_hist_pts'].fillna(1200.0)
df['home_rank_pos'] = df['home_rank_pos'].fillna(200.0)
df['away_rank_pos'] = df['away_rank_pos'].fillna(200.0)

# =====================================================================
# 4. TRANSFORMACIÓN BINARIA DEL OBJETIVO (OPCIÓN 2)
# =====================================================================
# Cambiamos el enfoque: 1 si gana el local, 0 si empatan o gana la visita (No gana local, cambio mencionado en data_downloader.py) 
df['result_binary'] = (df['result'] == 0).astype(int)

# Puntos de rendimiento simplificados para la racha de forma
df['home_perf_pts'] = df['result_binary'] * 3.0
df['away_perf_pts'] = (df['result'] == 2).astype(float) * 3.0 + (df['result'] == 1).astype(float) * 1.0

# =====================================================================
# 5. RACHAS VECTORIZADAS SÓLIDAS (730 días)
# =====================================================================
print("Calculando promedios móviles globales...")
home_side = df[['date', 'home_team', 'home_perf_pts']].rename(columns={'home_team': 'team', 'home_perf_pts': 'pts'})
away_side = df[['date', 'away_team', 'away_perf_pts']].rename(columns={'away_team': 'team', 'away_perf_pts': 'pts'})
flat_df = pd.concat([home_side, away_side]).sort_values(['team', 'date']).set_index('date')
rolling_form = flat_df.groupby('team')['pts'].rolling('730D', closed='left').mean()
form_dict = rolling_form.fillna(1.0).to_dict()
df['home_form'] = df.set_index(['home_team', 'date']).index.map(form_dict)
df['away_form'] = df.set_index(['away_team', 'date']).index.map(form_dict)

# Goles globales unificados (sin partición neutral que genere nulos)
home_goals = df[['date', 'home_team', 'home_score', 'away_score']].rename(columns={'home_team': 'team', 'home_score': 'gf', 'away_score': 'ga'}).dropna()
away_goals = df[['date', 'away_team', 'away_score', 'home_score']].rename(columns={'away_team': 'team', 'away_score': 'gf', 'home_score': 'ga'}).dropna()
flat_goals = pd.concat([home_goals, away_goals]).sort_values(['team', 'date']).set_index('date')

rolling_gf = flat_goals.groupby('team')['gf'].rolling('730D', closed='left').mean().fillna(1.0).to_dict()
rolling_ga = flat_goals.groupby('team')['ga'].rolling('730D', closed='left').mean().fillna(1.0).to_dict()

df['home_gf_avg'] = df.set_index(['home_team', 'date']).index.map(rolling_gf).fillna(1.0)
df['away_gf_avg'] = df.set_index(['away_team', 'date']).index.map(rolling_gf).fillna(1.0)
df['home_ga_avg'] = df.set_index(['home_team', 'date']).index.map(rolling_ga).fillna(1.0)
df['away_ga_avg'] = df.set_index(['away_team', 'date']).index.map(rolling_ga).fillna(1.0)

# =====================================================================
# 6. VARIABLES FINALES
# =====================================================================
df['dif_points'] = df['home_hist_pts'] - df['away_hist_pts']
df['dif_form'] = df['home_form'] - df['away_form']
df['dif_ranking_pos'] = df['away_rank_pos'] - df['home_rank_pos']
df['dif_gf'] = df['home_gf_avg'] - df['away_gf_avg']
df['dif_ga'] = df['home_ga_avg'] - df['away_ga_avg']

df['neutral'] = df['neutral'].astype(int)
df.to_csv("clean_matches_form_rank.csv", index=False)
print("¡Proceso completado! Dataset binario generado con éxito.")