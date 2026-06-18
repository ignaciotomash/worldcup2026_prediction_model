import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib

# 1. Cargar el dataset preparado 
df = pd.read_csv("clean_matches_form_rank.csv")

# 2. Definir variables predictoras y objetivo 
X = df[['dif_points', 'dif_form', 'dif_gf', 'dif_ga', 'dif_ranking_pos', 'neutral']]
y = df['result']  # 0=gana local, 1=empate, 2=gana visitante

# 3. División del dataset (80% entrenamiento, 20% prueba)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Configuración del modelo Balanceado
model = RandomForestClassifier(
    n_estimators=300, 
    max_depth=12,  # Ajustado sutilmente para control de sobreajuste
    min_samples_split=5, 
    class_weight='balanced', 
    random_state=42
)

print("Entrenando modelo multiclase (Local / Empate / Visitante)...")
model.fit(X_train, y_train)

# 5. Evaluación de Importancia de Variables
print("\n" + "="*50)
print("IMPORTANCIA DE LAS VARIABLES")
print("="*50)
importances = model.feature_importances_
for col, imp in zip(X.columns, importances):
    print(f"Variable '{col}': {imp:.4f}")

# 6. Cálculo de la precisión general
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nPrecisión global del modelo: {accuracy:.2f}")

# =====================================================================
# DIAGNÓSTICO PROFUNDO
# =====================================================================
print("\n" + "="*50)
print("REPORTE DE CLASIFICACIÓN DETALLADO")
print("="*50)
print(classification_report(y_test, y_pred, target_names=['Gana Local (0)', 'Empate (1)', 'Gana Visitante (2)']))

print("="*50)
print("MATRIZ DE CONFUSIÓN")
print("="*50)
cm = confusion_matrix(y_test, y_pred)
cm_df = pd.DataFrame(cm,
                     index=['Real: Local (0)', 'Real: Empate (1)', 'Real: Visitante (2)'],
                     columns=['Pred: Local (0)', 'Pred: Empate (1)', 'Pred: Visitante (2)'])
print(cm_df)
print("="*50)

# 7. Guardar el modelo entrenado
joblib.dump(model, "football_model.pkl")
print("Modelo guardado con éxito en 'football_model.pkl'.")