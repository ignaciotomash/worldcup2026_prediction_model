import pandas as pd
import numpy as np
import os
import webbrowser
from predictor import simulate_match, get_team_data, df

UMBRAL_EMPATE = 0.12

# Diccionario oficial de Grupos (Mundial 2026 de 48 equipos)
GROUPS = {
    "Grupo A": ["Mexico", "South Africa", "South Korea", "Czech Republic"],
    "Grupo B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "Grupo C": ["Brazil", "Morocco", "Scotland", "Haiti"],
    "Grupo D": ["United States", "Paraguay", "Australia", "Turkey"],
    "Grupo E": ["Germany", "Ecuador", "Ivory Coast", "Curacao"],
    "Grupo F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "Grupo G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "Grupo H": ["Spain", "Uruguay", "Saudi Arabia", "Cape Verde"],
    "Grupo I": ["France", "Senegal", "Norway", "Iraq"],
    "Grupo J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "Grupo K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "Grupo L": ["England", "Croatia", "Ghana", "Panama"]
}

# ==========================================
# CARGA DE RESULTADOS REALES DEL MUNDIAL
# ==========================================
df_real = pd.read_csv("clean_matches.csv")
df_real['date'] = pd.to_datetime(df_real['date'])

# Filtramos solo partidos del Mundial 2026 ya jugados
MUNDIAL_START = pd.Timestamp('2026-06-11')
df_mundial_real = df_real[df_real['date'] >= MUNDIAL_START].copy()

def get_real_result(team_a, team_b):
    """
    Busca si el partido ya se jugó en el CSV real.
    Devuelve (outcome, goals_a, goals_b) o None si no existe.
    """
    # Buscar en ambas orientaciones
    match = df_mundial_real[
        ((df_mundial_real['home_team'] == team_a) & (df_mundial_real['away_team'] == team_b)) |
        ((df_mundial_real['home_team'] == team_b) & (df_mundial_real['away_team'] == team_a))
    ]

    if match.empty:
        return None

    row = match.iloc[0]
    
    # Determinar orientación
    if row['home_team'] == team_a:
        g_a, g_b = int(row['home_score']), int(row['away_score'])
    else:
        g_a, g_b = int(row['away_score']), int(row['home_score'])

    if g_a > g_b:
        outcome = team_a
    elif g_b > g_a:
        outcome = team_b
    else:
        outcome = "DRAW"

    return outcome, g_a, g_b

# ==========================================
#  SIMULACIÓN DE LA FASE DE GRUPOS Y DESEMPATES
# ==========================================

def resolve_tiebreakers(table, match_history):
    """
    Aplica el reglamento de desempate de la FIFA:
    1. PTS globales -> 2. DG global -> 3. GF global
    4. PTS directos -> 5. DG directo -> 6. GF directo
    """
    # Primer ordenamiento por los criterios generales
    table = table.sort_values(by=['PTS', 'DG', 'GF'], ascending=[False, False, False])
    
    # Agrupar los equipos que tengan exactamente los mismos PTS, DG y GF
    grouped = table.groupby(['PTS', 'DG', 'GF'], sort=False)
    
    final_order = []
    
    for _, group in grouped: # el "_" es para ignorar el valor de groupby de la funcion que devuelve name y group (solo me interesa group)
        # Si no hay empate (el grupo es de 1 equipo), pasa directo a la lista final
        if len(group) == 1:
            final_order.extend(group.index.tolist())
        else:
            # Hay empate de 2 o más equipos. Aplicar mini-tabla de enfrentamientos directos.
            tied_teams = group.index.tolist()
            h2h_stats = {team: {'h2h_pts': 0, 'h2h_dg': 0, 'h2h_gf': 0} for team in tied_teams}
            
            # Filtrar el historial usando SOLO los partidos entre los equipos empatados
            for match in match_history:
                t_a, t_b = match['team_a'], match['team_b']
                if t_a in tied_teams and t_b in tied_teams:
                    g_a, g_b = match['goals_a'], match['goals_b']
                    
                    h2h_stats[t_a]['h2h_gf'] += g_a
                    h2h_stats[t_a]['h2h_dg'] += (g_a - g_b)
                    h2h_stats[t_b]['h2h_gf'] += g_b
                    h2h_stats[t_b]['h2h_dg'] += (g_b - g_a)
                    
                    if g_a > g_b:
                        h2h_stats[t_a]['h2h_pts'] += 3
                    elif g_a < g_b:
                        h2h_stats[t_b]['h2h_pts'] += 3
                    else:
                        h2h_stats[t_a]['h2h_pts'] += 1
                        h2h_stats[t_b]['h2h_pts'] += 1
            
            # Ordenar la mini-tabla por los criterios H2H (head to head; cara a cara).
            h2h_df = pd.DataFrame.from_dict(h2h_stats, orient='index')
            h2h_df = h2h_df.sort_values(by=['h2h_pts', 'h2h_dg', 'h2h_gf'], ascending=[False, False, False])
            
            # Agregar el orden resuelto a la lista principal
            final_order.extend(h2h_df.index.tolist())
            
    # Devolver la tabla reconstruida con el orden definitivo
    return table.loc[final_order]

print("==================================================")
print("             SIMULANDO FASE DE GRUPOS             ")
print("==================================================")

group_tables = {}
all_third_places = []

for group_name, teams in GROUPS.items():
    # Inicializar tabla
    table = pd.DataFrame(index=teams, columns=['PTS', 'GF', 'GC', 'DG']).fillna(0)
    match_history = []  # Historial para los desempates
    
    # Todos contra todos (6 partidos por grupo)
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            team_a, team_b = teams[i], teams[j]

            # Usar resultado real si ya se jugó, sino simular
            real = get_real_result(team_a, team_b)
            if real:
                outcome, g_a, g_b = real
                print(f"[REAL] {team_a} {g_a} - {g_b} {team_b}")
            else:
                outcome, g_a, g_b, _, _, _ = simulate_match(team_a, team_b)
            
            # Guardar en el historial del grupo
            match_history.append({
                'team_a': team_a,
                'team_b': team_b,
                'goals_a': g_a,
                'goals_b': g_b
            })
            
            # Asignar Goles a la tabla general
            table.at[team_a, 'GF'] += g_a
            table.at[team_a, 'GC'] += g_b
            table.at[team_b, 'GF'] += g_b
            table.at[team_b, 'GC'] += g_a
            
            # Asignar Puntos
            if outcome == "DRAW":
                table.at[team_a, 'PTS'] += 1
                table.at[team_b, 'PTS'] += 1
            elif outcome == team_a:
                table.at[team_a, 'PTS'] += 3
            else:
                table.at[team_b, 'PTS'] += 3

    # Calcular Diferencia de Goles global
    table['DG'] = table['GF'] - table['GC']
    
    # Aplicar la función de ordenamiento estricto FIFA
    table = resolve_tiebreakers(table, match_history)
    group_tables[group_name] = table
    
    # Guardar el tercer lugar para el repechaje
    third_team = table.index[2]
    third_row = table.loc[third_team].copy()
    third_row['team'] = third_team
    all_third_places.append(third_row)

    print(f"\n--- {group_name} ---")
    print(table.to_string())

# ==========================================
# 4. FILTRADO DE CLASIFICADOS (Sistema de 48 a 32 equipos)
# ==========================================
qualified_teams = []

# 1. Clasifican los 1 y 2 de cada uno de los 12 grupos (24 equipos)
for group_name, table in group_tables.items():
    qualified_teams.append(table.index[0])
    qualified_teams.append(table.index[1])

# 2. Recopilar datos detallados de los terceros para el desempate de la FIFA
detailed_thirds = []
for group_name, table in group_tables.items():
    third_team = table.index[2]
    # Extraemos el ranking FIFA actual del equipo para usarlo como desempate avanzado
    _, rank_pos, _, _, _ = get_team_data(third_team)
    
    stats = table.loc[third_team].copy()
    stats['team'] = third_team
    stats['fifa_rank'] = rank_pos  # Menor número significa mejor puesto (Ej: 1 es mejor que 20)
    stats['random_seed'] = np.random.rand()  # Sorteo puro por si empatan en ranking también
    detailed_thirds.append(stats)

# Convertir a DataFrame la tabla de terceros
df_thirds = pd.DataFrame(detailed_thirds)

# Ordenamiento estricto para terceros de grupos diferentes:
# 1. PTS (Más) -> 2. DG (Más) -> 3. GF (Más) -> 4. fifa_rank (Menos es mejor) -> 5. Sorteo aleatorio
df_thirds = df_thirds.sort_values(
    by=['PTS', 'DG', 'GF', 'fifa_rank', 'random_seed'], 
    ascending=[False, False, False, True, True]
)

# Filtramos los 8 mejores que pasan a Dieciseisavos
best_thirds = df_thirds.head(8)['team'].tolist()
qualified_teams.extend(best_thirds)

print("\n==================================================")
print("     TABLA FINAL DE LOS MEJORES TERCEROS          ")
print("==================================================")
print(df_thirds[['team', 'PTS', 'DG', 'GF', 'fifa_rank']].to_string(index=False))
print("--------------------------------------------------")
print(f"👉 Clasificados por repesca: {', '.join(best_thirds)}")
print("==================================================")

print("\n==================================================")
print(f"SELECCIONES TOTALES CLASIFICADAS A PLAYOFFS ({len(qualified_teams)} Equipos)")
print("==================================================")
print(", ".join(qualified_teams))

# ==========================================
# 5. SIMULACIÓN DE LLAVES Y GENERACIÓN HTML
# ==========================================

bracket_data = {}

def simulate_knockout_stage(matchups, stage_name):
    print(f"\n==================================================")
    print(f"             SIMULANDO {stage_name.upper()}             ")
    print("==================================================")
    winners = []
    matches_info = []
    
    for t1, t2 in matchups:
        outcome, g_a, g_b, p_a, _, p_b = simulate_match(t1, t2)
        if outcome == "DRAW":
            winner = t1 if p_a > p_b else t2
            print(f"[{stage_name}] {t1} {g_a} - {g_b} {t2} -> Empate. ¡Ganador por Penales!: {winner}")
            nota = "(Penales)"
        else:
            winner = outcome
            print(f"[{stage_name}] {t1} {g_a} - {g_b} {t2} -> Ganador: {winner}")
            nota = ""
            
        matches_info.append({'t1': t1, 't2': t2, 'g1': g_a, 'g2': g_b, 'winner': winner, 'note': nota})
        winners.append(winner)
        
    bracket_data[stage_name] = matches_info
    return winners

def generate_html_report(bracket, champion, group_tables, best_thirds):
    # Separamos los partidos en Lado Izquierdo (Left) y Lado Derecho (Right)
    r32_l, r32_r = bracket["Dieciseisavos"][:8], bracket["Dieciseisavos"][8:]
    r16_l, r16_r = bracket["Octavos"][:4], bracket["Octavos"][4:]
    qf_l, qf_r = bracket["Cuartos"][:2], bracket["Cuartos"][2:]
    sf_l, sf_r = bracket["Semifinales"][:1], bracket["Semifinales"][1:]
    final_match = bracket["Final"][0]

    def render_match(m):
        t1_class = "winner" if m['winner'] == m['t1'] else "loser"
        t2_class = "winner" if m['winner'] == m['t2'] else "loser"
        return f"""
        <div class="match">
            <div class="team {t1_class}"><span>{m['t1']}</span> <span>{m['g1']}</span></div>
            <div class="team {t2_class}"><span>{m['t2']}</span> <span>{m['g2']}</span></div>
            <div class="match-note">{m['note']}</div>
        </div>
        """

    def render_column(matches, title):
        html_col = f'<div class="round"><div class="round-title">{title}</div>'
        for m in matches:
            html_col += render_match(m)
        html_col += '</div>'
        return html_col

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Simulador Mundial 2026 - Reporte Completo</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #ffffff; color: #0f172a; padding: 20px; margin: 0; }}
            h1 {{ text-align: center; color: #0f172a; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 30px; font-size: 28px; font-weight: 800; }}
            h2 {{ text-align: center; color: #0f172a; text-transform: uppercase; letter-spacing: 2px; margin-top: 60px; margin-bottom: 30px; font-size: 22px; font-weight: 700; }}
            
            .bracket-outer {{ display: flex; justify-content: center; align-items: center; min-width: 1400px; padding: 20px; }}
            .side-bracket {{ display: flex; flex-direction: row; gap: 25px; width: 45%; justify-content: space-between; }}
            
            .round {{ display: flex; flex-direction: column; justify-content: space-around; width: 220px; }}
            .round-title {{ text-align: center; color: #1e40af; font-weight: bold; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; border-bottom: 2px solid #1e40af; padding-bottom: 5px; }}
            
            .match {{ background: #111e36; border: 1px solid #1e293b; padding: 12px; margin: 10px 0; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); font-size: 13px; transition: all 0.3s; }}
            .match:hover {{ border-color: #3b82f6; transform: scale(1.02); }}
            
            .team {{ display: flex; justify-content: space-between; margin: 4px 0; padding: 5px 8px; border-radius: 4px; color: #e2e8f0; }}
            .winner {{ font-weight: bold; color: #ffffff; background-color: rgba(59, 130, 246, 0.25); border-left: 3px solid #3b82f6; }}
            .loser {{ color: #94a3b8; }}
            .match-note {{ text-align: right; font-size: 10px; color: #60a5fa; min-height: 12px; font-weight: bold; }}
            
            .center-stage {{ display: flex; flex-direction: column; align-items: center; justify-content: center; width: 300px; gap: 30px; }}
            .final-box {{ width: 100%; text-align: center; }}
            .final-box .match {{ background: #1e3a8a; border: 2px solid #d97706; }}
            .final-title {{ color: #1e3a8a; font-weight: bold; font-size: 16px; letter-spacing: 2px; margin-bottom: 10px; text-transform: uppercase; }}
            
            .champion-card {{ text-align: center; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 25px; border-radius: 12px; border: 2px solid #d97706; box-shadow: 0 6px 15px rgba(217,119,6,0.2); width: 90%; }}
            .champion-title {{ font-size: 12px; color: #b45309; letter-spacing: 3px; font-weight: bold; margin-bottom: 10px; }}
            .champion-name {{ font-size: 24px; color: #78350f; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }}

            /* --- DISEÑO DE LAS TABLAS DE GRUPOS --- */
            .groups-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 25px; max-width: 1400px; margin: 0 auto; padding: 20px; }}
            .group-card {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            .group-card-title {{ text-align: center; color: #1e40af; font-weight: bold; font-size: 14px; margin-bottom: 12px; border-bottom: 2px solid #1e40af; padding-bottom: 4px; text-transform: uppercase; }}
            .group-card table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
            .group-card th {{ background: #111e36; color: #ffffff; padding: 6px; text-align: center; font-weight: 600; }}
            .group-card th:nth-child(2) {{ text-align: left; }}
            .group-card td {{ padding: 6px; text-align: center; border-bottom: 1px solid #f1f5f9; color: #334155; }}
            .group-card td.team-name {{ text-align: left; font-weight: 500; }}
            
            /* Colores de filas según estado de clasificación */
            .class-direct {{ background-color: rgba(59, 130, 246, 0.08); font-weight: bold; }}
            .class-direct td {{ color: #1e3a8a !important; }}
            .class-third {{ background-color: rgba(16, 185, 129, 0.08); font-weight: bold; }}
            .class-third td {{ color: #065f46 !important; }}
            .eliminated {{ opacity: 0.55; }}
        </style>
    </head>
    <body>
        <h1>🏆 FASE ELIMINATORIA: MUNDIAL 2026 🏆</h1>
        
        <div class="bracket-outer">
            <div class="side-bracket">
                {render_column(r32_l, "Dieciseisavos")}
                {render_column(r16_l, "Octavos")}
                {render_column(qf_l, "Cuartos")}
                {render_column(sf_l, "Semifinal A")}
            </div>
            
            <div class="center-stage">
                <div class="final-box">
                    <div class="final-title">🔥 GRAN FINAL 🔥</div>
                    {render_match(final_match)}
                </div>
                
                <div class="champion-card">
                    <div class="champion-title">⭐ CAMPEÓN DEL MUNDO ⭐</div>
                    <div class="champion-name">{champion}</div>
                </div>
            </div>
            
            <div class="side-bracket" style="flex-direction: row-reverse;">
                {render_column(r32_r, "Dieciseisavos")}
                {render_column(r16_r, "Octavos")}
                {render_column(qf_r, "Cuartos")}
                {render_column(sf_r, "Semifinal B")}
            </div>
        </div>

        <h2>📊 TABLAS DE POSICIONES - FASE DE GRUPOS 📊</h2>
        <div class="groups-grid">
    """
    
    # Renderizado dinámico de las 12 tablas de grupo
    for g_name, table in group_tables.items():
        html += f"""
        <div class="group-card">
            <div class="group-card-title">{g_name}</div>
            <table>
                <thead>
                    <tr>
                        <th>Pos</th>
                        <th>Equipo</th>
                        <th>PTS</th>
                        <th>DG</th>
                        <th>GF</th>
                    </tr>
                </thead>
                <tbody>
        """
        for pos, (team, row) in enumerate(table.iterrows()):
            if pos < 2:
                row_class = "class-direct"
            elif team in best_thirds:
                row_class = "class-third"
            else:
                row_class = "eliminated"
                
            html += f"""
                    <tr class="{row_class}">
                        <td>{pos+1}</td>
                        <td class="team-name">{team}</td>
                        <td>{int(row['PTS'])}</td>
                        <td>{int(row['DG'])}</td>
                        <td>{int(row['GF'])}</td>
                    </tr>
            """
        html += "</tbody></table></div>"
        
    html += """
        </div>
    </body>
    </html>
    """
    filename = "fixture_mundial.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

# --- GENERACIÓN DE CRUCES FIJOS (BRACKET CONGELADO) ---

def get_team(group_name, position):
    clean_name = group_name.replace("Grupo ", "").strip()
    
    if clean_name in group_tables:
        return group_tables[clean_name].index[position - 1]
    else:
        return group_tables[group_name].index[position - 1]

# 'best_thirds' ya contiene a los 8 mejores terceros 
# Diccionario con las reglas estrictas de grupos permitidos
# ==========================================
# 5. ASIGNACIÓN CORRECTA DE TERCEROS (REGLA FIFA ESTRICTA)
# ==========================================

# Mapa oficial FIFA: para cada ganador (por letra de grupo),
# qué grupos pueden aportar su tercero clasificado.
ALLOWED_THIRDS_FOR = {
    'E': ['A', 'B', 'C', 'D', 'F'],
    'I': ['C', 'D', 'F', 'G', 'H'],
    'D': ['B', 'E', 'F', 'I', 'J'],
    'G': ['A', 'E', 'H', 'I', 'J'],
    'A': ['G', 'E', 'F', 'H', 'I'],
    'L': ['E', 'H', 'I', 'J', 'K'],
    'B': ['E', 'F', 'G', 'I', 'J'],
    'K': ['E', 'D', 'I', 'J', 'L'],
}

def get_team_group(team_name):
    """Devuelve la letra del grupo al que pertenece un equipo (ej: 'A', 'B', ...)."""
    clean = str(team_name).strip()
    for group_name, table in group_tables.items():
        if clean in [str(t).strip() for t in table.index]:
            return group_name.replace("Grupo ", "").strip()
    return None

def assign_thirds(best_thirds_list):
    """
    Asigna cada tercero clasificado a la ranura correcta según la normativa FIFA.
    Usa heurística 'más restringido primero' (MRV) para garantizar solución.
    """
    winners_order = ['E', 'I', 'D', 'G', 'A', 'L', 'B', 'K']
    
    team_to_group = {t: get_team_group(t) for t in best_thirds_list}
    
    # Para cada ranura, construir la lista de candidatos válidos
    def build_candidates(available_teams):
        return {
            slot: [t for t in available_teams if team_to_group[t] in ALLOWED_THIRDS_FOR[slot]]
            for slot in winners_order
        }
    
    # Backtracking con heurística MRV: siempre asignar primero
    # la ranura que tenga MENOS candidatos disponibles
    def backtrack(remaining_slots, remaining_teams, current_assignment):
        if not remaining_slots:
            return current_assignment  # Asignación completa exitosa
        
        # MRV: elegir la ranura más restringida (menos candidatos válidos disponibles)
        candidates_now = build_candidates(remaining_teams)
        slot = min(remaining_slots, key=lambda s: len(candidates_now[s]))
        
        # Si alguna ranura tiene 0 candidatos, este camino no tiene solución
        if len(candidates_now[slot]) == 0:
            return None
        
        for candidate in candidates_now[slot]:
            current_assignment[slot] = candidate
            result = backtrack(
                remaining_slots - {slot},
                remaining_teams - {candidate},
                current_assignment
            )
            if result is not None:
                return result
            del current_assignment[slot]
        
        return None  # Sin solución por este camino
    
    assignment = backtrack(
        remaining_slots=set(winners_order),
        remaining_teams=set(best_thirds_list),
        current_assignment={}
    )
    
    if assignment is None:
        # Diagnóstico detallado para facilitar el debug
        candidates_info = {
            slot: [f"{t}(G{team_to_group[t]})" for t in best_thirds_list 
                   if team_to_group[t] in ALLOWED_THIRDS_FOR[slot]]
            for slot in winners_order
        }
        raise ValueError(
            "No se encontró una asignación válida de terceros.\n"
            f"Terceros clasificados: {best_thirds_list}\n"
            f"Grupos de origen: {team_to_group}\n"
            f"Candidatos por ranura: {candidates_info}\n"
            "El bracket FIFA 2026 no contempla esta combinación de grupos de terceros."
        )
    
    return assignment


# Ejecutamos la asignación de los terceros
thirds_matchups = assign_thirds(best_thirds)

# --- GENERACIÓN DE CRUCES FIJOS (BRACKET CONGELADO) ---
round_of_32_matchups = [
    # ---- LADO IZQUIERDO ----
    (get_team('Grupo E', 1), thirds_matchups['E']),
    (get_team('Grupo I', 1), thirds_matchups['I']),
    (get_team('Grupo A', 2), get_team('Grupo B', 2)),
    (get_team('Grupo F', 1), get_team('Grupo C', 2)),
    (get_team('Grupo K', 2), get_team('Grupo L', 2)),
    (get_team('Grupo H', 1), get_team('Grupo J', 2)),
    (get_team('Grupo D', 1), thirds_matchups['D']),
    (get_team('Grupo G', 1), thirds_matchups['G']),
    
    # ---- LADO DERECHO ----
    (get_team('Grupo C', 1), get_team('Grupo F', 2)),
    (get_team('Grupo E', 2), get_team('Grupo I', 2)),
    (get_team('Grupo A', 1), thirds_matchups['A']),
    (get_team('Grupo L', 1), thirds_matchups['L']),
    (get_team('Grupo J', 1), get_team('Grupo H', 2)),
    (get_team('Grupo D', 2), get_team('Grupo G', 2)),
    (get_team('Grupo B', 1), thirds_matchups['B']),
    (get_team('Grupo K', 1), thirds_matchups['K'])
]

# --- EJECUCIÓN DEL CUADRO ---
winners_r32 = simulate_knockout_stage(round_of_32_matchups, "Dieciseisavos")
winners_r16 = simulate_knockout_stage([(winners_r32[i], winners_r32[i+1]) for i in range(0, len(winners_r32), 2)], "Octavos")
winners_quarters = simulate_knockout_stage([(winners_r16[i], winners_r16[i+1]) for i in range(0, len(winners_r16), 2)], "Cuartos")
finalists = simulate_knockout_stage([(winners_quarters[i], winners_quarters[i+1]) for i in range(0, len(winners_quarters), 2)], "Semifinales")

# --- LA GRAN FINAL ---
print("\n==================================================")
print("                ¡GRAN FINAL DEL MUNDO!            ")
print("==================================================")
campeon, g_a, g_b, p_a, _, p_b = simulate_match(finalists[0], finalists[1])

if campeon == "DRAW":
    campeon = finalists[0] if p_a > p_b else finalists[1]
    nota = "(Penales)"
else:
    nota = ""

print(f"FINAL: {finalists[0]} {g_a} - {g_b} {finalists[1]}")
print(f"\n🏆 ¡EL CAMPEÓN DEL MUNDO ES: {campeon.upper()}! 🏆")

bracket_data["Final"] = [{'t1': finalists[0], 't2': finalists[1], 'g1': g_a, 'g2': g_b, 'winner': campeon, 'note': nota}]

# --- EXPORTAR Y ABRIR UI ---
report_file = generate_html_report(bracket_data, campeon, group_tables, best_thirds)
webbrowser.open(f"file://{os.path.realpath(report_file)}")
print("==================================================")