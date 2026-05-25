import http.client
import json

# 1. Conexión con el servidor de la API
conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "d2f537da44c1f7acb772dfa81cf343a0"
}

# 2. Solicitud de partidos (fixtures) con los parámetros que identificaste
conn.request("GET", "/fixtures?league=34&season=2026", headers=headers)

res = conn.getresponse()
data = res.read()

# 3. Procesamiento y almacenamiento local
# Convertimos los bytes a texto legible
json_data = json.loads(data.decode("utf-8"))

# Guardamos el resultado para no volver a gastar peticiones
with open("matches_conmebol.json", "w", encoding="utf-8") as f:
    json.dump(json_data, f, indent=4, ensure_ascii=False)

print("¡Descarga exitosa! Archivo 'matches_conmebol.json' creado localmente.")