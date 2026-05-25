import pandas as pd
import joblib
import json

model = joblib.load("football_model.pkl")
df = pd.read_csv("clean_matches_form_rank.csv")
df['date'] = pd.to_datetime(df['date'])

with open("fifa_ranking.json", "r", encoding="utf-8") as f:
    fifa_data = json.load(f)["Results"]

points_dict = {}
for team in fifa_data:
    team_name = next((lang['Description'] for lang in team['TeamName'] if lang['Locale'] == 'en-GB'), None)
    if team_name:
        points_dict[team_name] = team['TotalPoints']

def get_current_form_2_years(team, dataframe):
    last_date = dataframe['date'].max()
    two_years_ago = last_date - pd.Timedelta(days=730)
    past_matches = dataframe[(dataframe['date'] >= two_years_ago) & 
                             ((dataframe['home_team'] == team) | (dataframe['away_team'] == team))]
    if past_matches.empty:
        return 1.0
    total_pts = 0
    for _, match in past_matches.iterrows():
        if match['home_team'] == team:
            total_pts += 3 if match['result'] == 0 else (1 if match['result'] == 1 else 0)
        else:
            total_pts += 3 if match['result'] == 2 else (1 if match['result'] == 1 else 0)
    return total_pts / len(past_matches)

def prediction_neutral(team_a, team_b):
    try:
        form_a = get_current_form_2_years(team_a, df)
        form_b = get_current_form_2_years(team_b, df)
        points_a = points_dict.get(team_a, 1200.0)
        points_b = points_dict.get(team_b, 1200.0)
        
        # ESCENARIO A: A vs B (Diferencia desde la perspectiva de A)
        dif_points_a = points_a - points_b
        dif_form_a = form_a - form_b
        input_a = pd.DataFrame([[dif_points_a, dif_form_a]], columns=['dif_points', 'dif_form'])
        prob_a = model.predict_proba(input_a)[0] # [Win_A, Draw, Win_B]
        
        # ESCENARIO B: B vs A (Diferencia desde la perspectiva de B)
        dif_points_b = points_b - points_a
        dif_form_b = form_b - form_a
        input_b = pd.DataFrame([[dif_points_b, dif_form_b]], columns=['dif_points', 'dif_form'])
        prob_b = model.predict_proba(input_b)[0] # [Win_B, Draw, Win_A]
        
        # Promediamos para neutralidad absoluta
        win_a = (prob_a[0] + prob_b[2]) / 2
        draw = (prob_a[1] + prob_b[1]) / 2
        win_b = (prob_a[2] + prob_b[0]) / 2
        
        highest_prob = max(win_a, draw, win_b)
        forecast = f"Winner: {team_a}" if highest_prob == win_a else (f"Winner: {team_b}" if highest_prob == win_b else "Draw")
        
        print(f"\n======================================")
        print(f"   NEUTRAL MATCH (GAP MODEL): {team_a} vs {team_b}")
        print(f"======================================")
        print(f"FORECAST: {forecast}")
        print(f"--------------------------------------")
        print(f"Probabilities:")
        print(f" - {team_a} Win: {win_a:.2%}")
        print(f" - Draw: {draw:.2%}")
        print(f" - {team_b} Win: {win_b:.2%}")
        print(f"======================================")
        print(f"DEBUG - {team_a}: PPG: {form_a:.2f} | FIFA Points: {points_a:.2f}")
        print(f"DEBUG - {team_b}: PPG: {form_b:.2f} | FIFA Points: {points_b:.2f}")
        print(f"DEBUG - BRECHA RANKING: {abs(dif_points_a):.2f} puntos a favor de {team_a if dif_points_a > 0 else team_b}")
        
    except Exception as e:
        print(f"Error: {e}")

# Ejecutamos la prueba del clásico corregido
prediction_neutral("Argentina", "France")
