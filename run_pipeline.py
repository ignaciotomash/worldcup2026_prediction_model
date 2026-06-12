import os
import sys

print("🚀 [INICIO] Ejecutando pipeline completo...")

# 1. Descarga de datos
print("\n📥 Paso 1/3: Descargando partidos recientes...")
if os.system("python data_downloader.py") != 0:
    print("❌ Error en data_downloader.py. Pipeline detenido.")
    sys.exit(1)

# 2. Preparación de datos
print("\n🧹 Paso 2/3: Ejecutando Data Preparation...")
if os.system("python data_prep.py") != 0:
    print("❌ Error en data_prep.py. Pipeline detenido.")
    sys.exit(1)

# 3. Entrenamiento del modelo
print("\n🧠 Paso 3/3: Reentrenando el modelo...")
if os.system("python train_model.py") != 0:
    print("❌ Error en train_model.py. Pipeline detenido.")
    sys.exit(1)

print("\n✅ [FIN] ¡Todo el proceso se ejecutó correctamente en cadena!")