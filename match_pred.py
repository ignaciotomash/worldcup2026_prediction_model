import pandas as pd
import joblib

# 1. Cargar modelo y datos unificados
try:
    model = joblib.load("football_model.pkl")
    df = pd.read_csv("clean_matches_form_rank.csv")
    df['date'] = pd.to_datetime(df['date'])
    print("Modelo y base de datos cargados con éxito.")
except Exception as e:
    print(f"¡Error al cargar archivos esenciales!: {e}")
    exit()

# 2. FUNCIÓN PARA EXTRAER LA INFORMACIÓN MÁS RECIENTE DE UN EQUIPO
def Gethistoric_data_team(team, dataframe):
    # Filtrar todos los partidos donde jugó ese equipo
    team_matches = dataframe[(dataframe['home_team'] == team) | (dataframe['away_team'] == team)]
    
    if team_matches.empty:
        # Valores genéricos de rescate si el equipo no existe en el dataset
        return 1200.0, 50, 1.0, 1.0, 1.0
    
    # Tomar el partido más reciente (última fila por fecha)
    latest_match = team_matches.sort_values('date').iloc[-1]
    
    # Extraer los puntos y el ranking dependiendo de si fue local o visita en ese último partido
    if latest_match['home_team'] == team:
        pts = latest_match['home_hist_pts']
        rank = latest_match['home_rank_pos']
        form = latest_match['home_form']
        gf = latest_match['home_gf_avg']
        ga = latest_match['home_ga_avg']
    else:
        pts = latest_match['away_hist_pts']
        rank = latest_match['away_rank_pos']
        form = latest_match['away_form']
        gf = latest_match['away_gf_avg']
        ga = latest_match['away_ga_avg']
        
    return pts, int(rank), form, gf, ga

# 3. Predicción simétrica neutral autónoma
def prediction_neutral(team_a, team_b):
    try:
        # Extraer métricas directo desde el CSV de forma automática
        points_a, rank_a, form_a, gf_a, ga_a = Gethistoric_data_team(team_a, df)
        points_b, rank_b, form_b, gf_b, ga_b = Gethistoric_data_team(team_b, df)
        
        # ESCENARIO A: Team A actúa como "Local" en la perspectiva matemática
        input_a = pd.DataFrame([{
            'dif_points': points_a - points_b,
            'dif_form': form_a - form_b,
            'dif_gf': gf_a - gf_b,
            'dif_ga': ga_a - ga_b,
            'dif_ranking_pos': rank_b - rank_a,
            'neutral': 1
        }])
        prob_matrix_a = model.predict_proba(input_a)[0] 
        
        # ESCENARIO B: Team B actúa como "Local" en la perspectiva matemática
        input_b = pd.DataFrame([{
            'dif_points': points_b - points_a,
            'dif_form': form_b - form_a,
            'dif_gf': gf_b - gf_a,
            'dif_ga': ga_b - ga_a,
            'dif_ranking_pos': rank_a - rank_b,
            'neutral': 1
        }])
        prob_matrix_b = model.predict_proba(input_b)[0]

        # RECONSTRUCCIÓN SIMÉTRICA DE PROBABILIDADES
        win_a = (prob_matrix_a[1] + (1.0 - prob_matrix_b[1] - (prob_matrix_a[0] * 0.33))) / 2
        win_b = (prob_matrix_b[1] + (1.0 - prob_matrix_a[1] - (prob_matrix_b[0] * 0.33))) / 2
        
        win_a = max(0.0, min(1.0, win_a))
        win_b = max(0.0, min(1.0, win_b))
        draw = 1.0 - win_a - win_b

        if draw < 0:
            total = win_a + win_b
            win_a /= total
            win_b /= total
            draw = 0.0

        UMBRAL_EMPATE = 0.12
        if abs(win_a - win_b) <= UMBRAL_EMPATE:
            forecast = "Draw (Empate)"
        elif win_a > win_b:
            forecast = f"Winner: {team_a}"
        else:
            forecast = f"Winner: {team_b}"
        
        print(f"\n======================================")
        print(f"   NEUTRAL MATCH (BINARY GAP): {team_a} vs {team_b}")
        print(f"======================================")
        print(f"RANKING FIFA ACTUAL:")
        print(f" - {team_a}: Puesto #{rank_a} ({points_a:.1f} pts)")
        print(f" - {team_b}: Puesto #{rank_b} ({points_b:.1f} pts)")
        print(f"--------------------------------------")
        print(f"FORECAST: {forecast}")
        print(f"--------------------------------------")
        print(f"Probabilities:")
        print(f" - {team_a} Win: {win_a:.2%}")
        print(f" - Draw: {draw:.2%}")
        print(f" - {team_b} Win: {win_b:.2%}")
        print(f"======================================")
        print(f"DEBUG - {team_a}: PPG Form: {form_a:.2f} | GF Avg: {gf_a:.2f}")
        print(f"DEBUG - {team_b}: PPG Form: {form_b:.2f} | GF Avg: {gf_b:.2f}")
        print(f"======================================")
        
    except Exception as e:
        print(f"Error en ejecución: {e}")

prediction_neutral("Mexico", "South Africa")