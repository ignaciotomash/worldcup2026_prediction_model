import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

df = pd.read_csv("clean_matches_form_rank.csv")

# ENTRENAMOS SOLO CON LAS DIFERENCIAS RELATIVAS
X = df[['dif_points', 'dif_form']]
y = df['result']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42) # Limitamos profundidad para evitar que se memorice partidos fijos
model.fit(X_train, y_train)

print(f"Precisión del modelo basado en Brechas Actuales: {accuracy_score(y_test, model.predict(X_test)):.2f}")

joblib.dump(model, "football_model.pkl")
print("Modelo guardado con éxito.")