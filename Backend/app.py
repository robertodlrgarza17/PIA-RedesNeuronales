import json
import random
import numpy as np
import tensorflow as tf
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configuración inicial.
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Carga de modelos y datos.
print("Cargando recursos de IA...")
try:
    modelo = tf.keras.models.load_model('modelo_tutor.keras')
    with open('mapa_usuarios.json', 'r') as f:
        mapa_usuarios = json.load(f)
    with open('mapa_habilidades.json', 'r') as f:
        mapa_habilidades = json.load(f)
    print("Modelo y mapas cargados correctamente.")
except Exception as e:
    print(f"Error crítico al cargar modelos o mapas: {e}")
    exit()

# Carga de preguntas.
def cargar_preguntas():
    with open('preguntas.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['preguntas']
preguntas_db = cargar_preguntas()
print(f"Cargadas {len(preguntas_db)} preguntas en memoria.")

# Simulación de usuario y memoria.

# Parámetros de aprendizaje.
AJUSTE_ACIERTO = 0.05  # Cuánto sube tu habilidad con un acierto.
AJUSTE_ERROR = -0.025 # Cuánto baja con un error.

# Configuración del usuario de demo.
DEMO_USER_STR = 'usuario_1'
if DEMO_USER_STR not in mapa_usuarios:
    DEMO_USER_STR = list(mapa_usuarios.keys())[0]
DEMO_USER_ID_NUM = mapa_usuarios[DEMO_USER_STR]

lista_habilidades = list(mapa_habilidades.keys())
historial_usuario = set()

# Guardar el "estado en vivo" del usuario en este diccionario.
estado_usuario_actual = {}

# Usa el modelo de IA para establecer los puntajes INICIALES del usuario. Se llama al inicio y al reiniciar.
def inicializar_estado_usuario():
    global estado_usuario_actual
    estado_usuario_actual.clear() # Limpia el estado anterior.
    historial_usuario.clear() # Limpia el historial de preguntas.
    
    input_usuario = np.array([DEMO_USER_ID_NUM])
    
    print(f"\nGenerando perfil inicial para {DEMO_USER_STR}...")
    for habilidad in lista_habilidades:
        skill_id_num = mapa_habilidades[habilidad]
        input_habilidad = np.array([skill_id_num])
        
        input_modelo = [input_usuario, input_habilidad]
        prob_acierto = modelo.predict(input_modelo, verbose=0)[0][0]
        
        estado_usuario_actual[habilidad] = float(prob_acierto)
    print("Perfil inicial generado.")

# Convierte el diccionario de estado en la lista ordenada que espera el front.
def obtener_predicciones_actuales():
    lista_preds = [
        {'habilidad': hab, 'prob_acierto': prob} 
        for hab, prob in estado_usuario_actual.items()
    ]
    # Ordena de más débil a más fuerte.
    lista_preds.sort(key=lambda x: x['prob_acierto'])
    return lista_preds

# Endpoints de la API.
@app.route('/')
def home():
    return "¡El backend está funcionando!"

@app.route('/api/pregunta', methods=['GET'])
def get_question():
    # Predice el dominio del usuario en CADA habilidad y obtiene el ranking de habilidades desde el estado actual.
    predicciones_actuales = obtener_predicciones_actuales()
    
    # Busca una pregunta para la habilidad más débil.
    pregunta_seleccionada = None
    for pred in predicciones_actuales:
        habilidad_debil = pred['habilidad']
        preguntas_disponibles = [
            p for p in preguntas_db 
            if p['habilidad'] == habilidad_debil 
            and p['id'] not in historial_usuario
        ]
        
        if preguntas_disponibles:
            pregunta_seleccionada = random.choice(preguntas_disponibles)
            break

    # Envía la pregunta.
    if pregunta_seleccionada:
        return jsonify({
            "pregunta": pregunta_seleccionada,
            "predicciones": predicciones_actuales # Envía el estado actual.
        })
    else:
        return jsonify({
            "completado": True,
            "predicciones": predicciones_actuales # Envía el estado final.
        })

@app.route('/api/verificar', methods=['POST'])
def verificar_respuesta():
    global estado_usuario_actual
    data = request.json
    pregunta_id = data.get('id')
    respuesta_usuario = data.get('respuesta')

    pregunta_encontrada = next((p for p in preguntas_db if p['id'] == int(pregunta_id)), None)
    if not pregunta_encontrada:
        return jsonify({"error": "Pregunta no encontrada"}), 404

    historial_usuario.add(int(pregunta_id))
    es_correcta = (pregunta_encontrada['respuesta_correcta'] == respuesta_usuario)
    
    # Actualización en vivo.
    habilidad_pregunta = pregunta_encontrada['habilidad']
    if habilidad_pregunta in estado_usuario_actual:
        score_actual = estado_usuario_actual[habilidad_pregunta]
        
        if es_correcta:
            score_actual += AJUSTE_ACIERTO
        else:
            score_actual += AJUSTE_ERROR
            
        # Asegurarse de que el score se mantenga entre 0.0 y 1.0.
        score_actual = max(0.0, min(1.0, score_actual))
        
        estado_usuario_actual[habilidad_pregunta] = score_actual
        print(f"Habilidad '{habilidad_pregunta}' actualizada a: {score_actual:.3f}")
        
    # Devuelve el resultado y las predicciones actualizadas.
    return jsonify({
        "resultado": "correcta" if es_correcta else "incorrecta",
        "respuesta_correcta": pregunta_encontrada['respuesta_correcta'],
        "predicciones_actualizadas": obtener_predicciones_actuales()
    })

# Endpoint para reiniciar el test.
@app.route('/api/reiniciar', methods=['POST'])
def reiniciar_test():
    # Recalcula el perfil base usando el modelo.
    inicializar_estado_usuario() 
    return jsonify({"mensaje": "Perfil y historial reiniciados"}), 200

# Iniciar el servidor.
if __name__ == '__main__':
    print(f"\nServidor listo. Simulando como usuario: {DEMO_USER_STR} (ID: {DEMO_USER_ID_NUM})")
    app.run(debug=False, host='0.0.0.0', port=5000)