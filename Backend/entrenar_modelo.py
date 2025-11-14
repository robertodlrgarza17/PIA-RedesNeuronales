import pandas as pd
import json
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Flatten, Concatenate, Dense

print("Iniciando el proceso de entrenamiento...")

# --- 1. CARGAR DATOS ---
try:
    data = pd.read_csv('datos_entrenamiento.csv')
except FileNotFoundError:
    print("Error: No se encontró 'datos_entrenamiento.csv'.")
    print("Asegúrate de ejecutar 'generar_datos.py' primero.")
    exit()

print(f"Datos cargados: {len(data)} registros.")

# --- 2. PREPROCESAMIENTO Y MAPEO ---
# La red neuronal no entiende "usuario_1" o "Programacion".
# Necesitamos convertirlos a números enteros (IDs).

# Crear los mapas (diccionarios)
# {'usuario_1': 0, 'usuario_2': 1, ...}
user_map = {name: i for i, name in enumerate(data['id_usuario'].unique())}

# {'Programacion': 0, 'RedesNeuronales': 1, ...}
skill_map = {name: i for i, name in enumerate(data['habilidad'].unique())}

# Aplicar los mapas a nuestras columnas de datos
data['user_id_num'] = data['id_usuario'].map(user_map)
data['skill_id_num'] = data['habilidad'].map(skill_map)

# Guardar estos mapas. Serán CRUCIALES para la Fase 3.
with open('mapa_usuarios.json', 'w') as f:
    json.dump(user_map, f)
with open('mapa_habilidades.json', 'w') as f:
    json.dump(skill_map, f)

print("Mapas de IDs creados y guardados.")

# --- 3. PREPARAR DATOS PARA EL MODELO ---

# Definir entradas (X) y salida (y)
X = data[['user_id_num', 'skill_id_num']]
y = data['resultado_correcto']

# Dividir en datos de entrenamiento y validación
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# --- 4. CONSTRUIR LA ARQUITECTURA DEL MODELO ---
# Usaremos "Embeddings" para crear un "perfil" vectorial para cada
# usuario y cada habilidad.

# Contar cuántos usuarios y habilidades únicos tenemos
num_usuarios = len(user_map)
num_habilidades = len(skill_map)

# Tamaño de los vectores de Embedding (hiperparámetro)
EMBEDDING_SIZE_USUARIO = 10
EMBEDDING_SIZE_HABILIDAD = 5

# --- Definición de la Red (API Funcional de Keras) ---

# Entrada 1: ID del Usuario
input_user = Input(shape=(1,), name='input_usuario')
# Capa de Embedding para Usuarios
embed_user = Embedding(input_dim=num_usuarios, 
                       output_dim=EMBEDDING_SIZE_USUARIO, 
                       name='embedding_usuario')(input_user)
embed_user_flat = Flatten()(embed_user)

# Entrada 2: ID de la Habilidad
input_skill = Input(shape=(1,), name='input_habilidad')
# Capa de Embedding para Habilidades
embed_skill = Embedding(input_dim=num_habilidades, 
                        output_dim=EMBEDDING_SIZE_HABILIDAD, 
                        name='embedding_habilidad')(input_skill)
embed_skill_flat = Flatten()(embed_skill)

# Concatenar los dos vectores de embedding
concatenated = Concatenate()([embed_user_flat, embed_skill_flat])

# Capas Densas (la "inteligencia" que encuentra patrones)
dense1 = Dense(16, activation='relu')(concatenated)
dense2 = Dense(8, activation='relu')(dense1)

# Capa de Salida: 1 neurona con activación 'sigmoid'
# Sigmoid nos da una probabilidad (un número entre 0 y 1)
output = Dense(1, activation='sigmoid', name='output')(dense2)

# Crear el modelo final
model = Model(inputs=[input_user, input_skill], outputs=output)

# Compilar el modelo
model.compile(optimizer='adam',
              loss='binary_crossentropy', # Perfecto para predicción binaria (0 o 1)
              metrics=['accuracy'])

model.summary() # Imprime un resumen de la arquitectura

# --- 5. ENTRENAR EL MODELO ---

# Keras necesita las entradas como una lista, una por cada Input
X_train_inputs = [X_train['user_id_num'], X_train['skill_id_num']]
X_val_inputs = [X_val['user_id_num'], X_val['skill_id_num']]

print("\nIniciando entrenamiento...")

history = model.fit(
    X_train_inputs,
    y_train,
    validation_data=(X_val_inputs, y_val),
    epochs=10,        # Cuántas veces "ve" los datos. 10-20 es un buen inicio.
    batch_size=32,    # Cuántas muestras procesa a la vez.
    verbose=1
)

print("Entrenamiento completado.")

# --- 6. GUARDAR EL MODELO ---
# Usamos el nuevo formato .keras que es más moderno
model.save('modelo_tutor.keras')

print("¡Modelo guardado exitosamente como 'modelo_tutor.keras'!")