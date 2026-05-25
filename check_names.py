import json

with open("fifa_ranking.json", "r", encoding="utf-8") as f:
    data = json.load(f)["Results"]

# Revisamos los primeros 3 equipos del JSON
for team in data[:3]:
    print(f"Código País: {team['IdCountry']}")
    print("Idiomas disponibles en 'TeamName':")
    for lang in team['TeamName']:
        print(f"  - Locale: '{lang['Locale']}' -> Description: '{lang['Description']}'")
    print("-" * 40)