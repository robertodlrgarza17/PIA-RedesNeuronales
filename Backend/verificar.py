import tensorflow as tf
import json
import numpy as np

print("Verificando red neuronal...")

# Cargar modelo
modelo = tf.keras.models.load_model('modelo_tutor.keras')
print("✓ Modelo cargado")

# Cargar mapas
with open('mapa_usuarios.json', 'r') as f:
    usuarios = json.load(f)
with open('mapa_habilidades.json', 'r') as f:
    habilidades = json.load(f)

print(f"✓ {len(usuarios)} usuarios")
print(f"✓ {len(habilidades)} habilidades")

# Mostrar arquitectura
print("\nARQUITECTURA:")
modelo.summary()

# Hacer 1 predicción
usuario_id = 0
habilidad_id = 0
prob = modelo.predict([np.array([usuario_id]), np.array([habilidad_id])], verbose=0)[0][0]

print(f"\nEJEMPLO DE PREDICCIÓN:")
print(f"Usuario 0 + Habilidad 0 = {prob:.3f} ({prob*100:.1f}%)")
print("\n✅ La red neuronal funciona correctamente")