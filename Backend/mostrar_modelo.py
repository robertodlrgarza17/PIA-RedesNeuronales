_from tensorflow import keras
import os

print("="*60)
print("  VISUALIZACIÓN DEL MODELO DE RED NEURONAL")
print("="*60)

# Cargar modelo
modelo = keras.models.load_model('modelo_tutor.keras')

print("\n🏗️  ARQUITECTURA DEL MODELO:\n")
modelo.summary()

print("\n📊 INFORMACIÓN DETALLADA:\n")
print(f"Total de capas: {len(modelo.layers)}")
print(f"Parámetros entrenables: {modelo.count_params():,}")

print("\n🔍 DETALLE DE CADA CAPA:\n")
for i, layer in enumerate(modelo.layers, 1):
    print(f"Capa {i}: {layer.name}")
    print(f"  • Tipo: {type(layer).__name__}")
    print(f"  • Output shape: {layer.output_shape}")
    
    if hasattr(layer, 'activation'):
        print(f"  • Activación: {layer.activation.__name__}")
    
    if hasattr(layer, 'units'):
        print(f"  • Neuronas: {layer.units}")
    
    print()

print("\n✅ Visualización completada")
print("="*60)