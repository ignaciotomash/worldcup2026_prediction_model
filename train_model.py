import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib

# 1. Cargar el dataset preparado binario
df = pd.read_csv("clean_matches_form_rank.csv")

# 2. Definir variables predictoras y objetivo binario
X = df[['dif_points', 'dif_form', 'dif_gf', 'dif_ga', 'dif_ranking_pos', 'neutral']]
y = df['result_binary']  # <--- NUESTRO NUEVO OBJETIVO BINARIO

# 3. División del dataset (80% entrenamiento, 20% prueba)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Configuración del modelo Binario Balanceado
model = RandomForestClassifier(
    n_estimators=300, 
    max_depth=12,  # Ajustado sutilmente para control de sobreajuste
    min_samples_split=5, 
    class_weight='balanced', 
    random_state=42
)

print("Entrenando el modelo binario (Gana Local vs No Gana Local)...")
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
# DIAGNÓSTICO PROFUNDO BINARIO
# =====================================================================
print("\n" + "="*50)
print("REPORTE DE CLASIFICACIÓN DETALLADO")
print("="*50)
print(classification_report(y_test, y_pred, target_names=['No Gana Local (0)', 'Gana Local (1)']))

print("="*50)
print("MATRIZ DE CONFUSIÓN BINARIA")
print("="*50)
cm = confusion_matrix(y_test, y_pred)
cm_df = pd.DataFrame(cm, 
                     index=['Real: No Gana Local (0)', 'Real: Gana Local (1)'],
                     columns=['Predicho: No Gana Local (0)', 'Predicho: Gana Local (1)'])
print(cm_df)
print("="*50)

# 7. Guardar el modelo entrenado
joblib.dump(model, "football_model.pkl")
print("Modelo binario guardado con éxito en 'football_model.pkl'.")