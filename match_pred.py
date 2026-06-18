from predictor import simulate_match, get_team_data

# ==========================================
# PREDICCIÓN DE UN PARTIDO EN PARTICULAR
# ==========================================
def prediction_neutral(team_a, team_b):
    outcome, goals_a, goals_b, prob_a, prob_draw, prob_b = simulate_match(team_a, team_b)

    if outcome == "DRAW":
        forecast = "Empate"
    elif outcome == team_a:
        forecast = f"Ganador: {team_a}"
    else:
        forecast = f"Ganador: {team_b}"

    _, rank_a, form_a, gf_a, ga_a = get_team_data(team_a)
    _, rank_b, form_b, gf_b, ga_b = get_team_data(team_b)

    print(f"\n{'='*40}")
    print(f"  {team_a} vs {team_b}")
    print(f"{'='*40}")
    print(f"  Resultado: {goals_a} - {goals_b}")
    print(f"  Pronóstico: {forecast}")
    print(f"{'='*40}")
    print(f"  Probabilidades:")
    print(f"    {team_a} gana : {prob_a:.2%}")
    print(f"    Empate        : {prob_draw:.2%}")
    print(f"    {team_b} gana : {prob_b:.2%}")
    print(f"{'='*40}")
    print(f"  DEBUG {team_a}: Rank={rank_a} | Form={form_a:.2f} | GF={gf_a:.2f} | GA={ga_a:.2f}")
    print(f"  DEBUG {team_b}: Rank={rank_b} | Form={form_b:.2f} | GF={gf_b:.2f} | GA={ga_b:.2f}")
    print(f"{'='*40}\n")


# ==========================================
# PARTIDO A SIMULAR — EDITÁ ESTOS VALORES
# ==========================================
prediction_neutral("Spain","Argentina")