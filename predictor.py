import pandas as pd
import numpy as np
import joblib

# ==========================================
# CARGA DE MODELO Y DATOS (una sola vez)
# ==========================================
try:
    model = joblib.load("football_model.pkl")
    df = pd.read_csv("clean_matches_form_rank.csv")
    df['date'] = pd.to_datetime(df['date'])
    print(">>> Predictor: Modelo y datos cargados con éxito.")
except Exception as e:
    print(f"Error crítico en predictor.py: {e}")
    exit()

UMBRAL_EMPATE = 0.12

# ==========================================
# FUNCIÓN 1 — DATOS HISTÓRICOS DE UN EQUIPO
# ==========================================
def get_team_data(team):
    """Extrae las métricas más recientes de un equipo desde el CSV."""
    matches = df[(df['home_team'] == team) | (df['away_team'] == team)]

    if matches.empty:
        return 1200.0, 50, 1.0, 1.0, 1.0

    latest = matches.sort_values('date').iloc[-1]

    if latest['home_team'] == team:
        return (latest['home_hist_pts'], int(latest['home_rank_pos']),
                latest['home_form'], latest['home_gf_avg'], latest['home_ga_avg'])
    else:
        return (latest['away_hist_pts'], int(latest['away_rank_pos']),
                latest['away_form'], latest['away_gf_avg'], latest['away_ga_avg'])


# ==========================================
# FUNCIÓN 2 — PREDICCIÓN SIMÉTRICA NEUTRAL
# ==========================================
def simulate_match(team_a, team_b):
    """
    Predice el resultado de un partido neutral entre dos equipos.
    Devuelve: (outcome, goals_a, goals_b, prob_a, prob_draw, prob_b)
    
    outcome puede ser: team_a, team_b, o "DRAW"
    """
    pts_a, rank_a, form_a, gf_a, ga_a = get_team_data(team_a)
    pts_b, rank_b, form_b, gf_b, ga_b = get_team_data(team_b)

    # --- PREDICCIÓN SIMÉTRICA ---
    # Escenario A: team_a como "local" matemático
    input_a = pd.DataFrame([{
        'dif_points':      pts_a - pts_b,
        'dif_form':        form_a - form_b,
        'dif_gf':          gf_a - gf_b,
        'dif_ga':          ga_a - ga_b,
        'dif_ranking_pos': rank_b - rank_a,
        'neutral': 1
    }])

    # Escenario B: team_b como "local" matemático
    input_b = pd.DataFrame([{
        'dif_points':      pts_b - pts_a,
        'dif_form':        form_b - form_a,
        'dif_gf':          gf_b - gf_a,
        'dif_ga':          ga_b - ga_a,
        'dif_ranking_pos': rank_a - rank_b,
        'neutral': 1
    }])

    # probs multiclase: [p_local_win, p_draw, p_away_win]
    probs_a = model.predict_proba(input_a)[0]
    probs_b = model.predict_proba(input_b)[0]

    # Promedio simétrico: cuando A es "local" gana con probs_a[0],
    # cuando B es "local" A gana con probs_b[2]
    prob_win_a = (probs_a[0] + probs_b[2]) / 2
    prob_draw  = (probs_a[1] + probs_b[1]) / 2
    prob_win_b = (probs_a[2] + probs_b[0]) / 2

    # Renormalizar por si hay desvío mínimo de floating point
    total = prob_win_a + prob_draw + prob_win_b
    prob_win_a /= total
    prob_draw  /= total
    prob_win_b /= total

    # --- DETERMINACIÓN DEL RESULTADO ---
    if abs(prob_win_a - prob_win_b) <= UMBRAL_EMPATE:
        outcome = "DRAW"
    elif prob_win_a > prob_win_b:
        outcome = team_a
    else:
        outcome = team_b

    # --- MONTE CARLO CON POISSON ---
    exp_goals_a = (gf_a + ga_b) / 2
    exp_goals_b = (gf_b + ga_a) / 2

    resultados_validos = []
    max_intentos = 50_000
    intentos = 0

    while len(resultados_validos) < 1000 and intentos < max_intentos:
        g_a = int(np.random.poisson(exp_goals_a))
        g_b = int(np.random.poisson(exp_goals_b))

        if g_a > g_b:
            sim_outcome = team_a
        elif g_b > g_a:
            sim_outcome = team_b
        else:
            sim_outcome = "DRAW"

        if sim_outcome == outcome:
            resultados_validos.append((g_a, g_b))

        intentos += 1

    if resultados_validos:
        goals_a = int(round(sum(r[0] for r in resultados_validos) / len(resultados_validos)))
        goals_b = int(round(sum(r[1] for r in resultados_validos) / len(resultados_validos)))
    else:
        # Fallback si Poisson no convergió (caso extremo)
        goals_a = int(round(exp_goals_a))
        goals_b = int(round(exp_goals_b))
        if outcome == team_a and goals_a <= goals_b:
            goals_a = goals_b + 1
        elif outcome == team_b and goals_b <= goals_a:
            goals_b = goals_a + 1

    return outcome, goals_a, goals_b, prob_win_a, prob_draw, prob_win_b