import json
import random
import csv

# --- 1. CONFIGURACIÓN DE LA SIMULACIÓN ---
NUM_USUARIOS_SINTETICOS = 200  # ¿Cuántos estudiantes ficticios creamos?
PREGUNTAS_POR_USUARIO = 40    # ¿Cuántas preguntas responderá cada uno?
ARCHIVO_SALIDA = 'datos_entrenamiento.csv'
ARCHIVO_PREGUNTAS = 'preguntas.json'

# --- 2. DEFINICIÓN DE "ARQUETIPOS" DE ESTUDIANTES ---
# Definimos perfiles de conocimiento. 
# Los números son la 'probabilidad base' de acertar esa habilidad.
ARQUETIPOS = {
    'novato': {
        'Programacion': 0.30,
        'RedesNeuronales': 0.20,
        'SistemasDigitales': 0.25
    },
    'programador': {
        'Programacion': 0.85,
        'RedesNeuronales': 0.40,
        'SistemasDigitales': 0.60
    },
    'experto_ia': {
        'Programacion': 0.70,
        'RedesNeuronales': 0.90,
        'SistemasDigitales': 0.50
    },
    'generalista': {
        'Programacion': 0.60,
        'RedesNeuronales': 0.60,
        'SistemasDigitales': 0.60
    }
}

# --- 3. CARGAR PREGUNTAS ---
def cargar_preguntas():
    try:
        with open(ARCHIVO_PREGUNTAS, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Creamos un diccionario para fácil acceso: { "101": "Programacion", ... }
            mapa_preguntas_habilidad = {}
            for preg in data['preguntas']:
                # Asumimos que todas las preguntas tienen 'opciones'
                # Si no, esta simulación simple funciona igual.
                mapa_preguntas_habilidad[preg['id']] = preg['habilidad']
            
            # También necesitamos una lista de todos los IDs de preguntas
            lista_ids_preguntas = list(mapa_preguntas_habilidad.keys())
            
            return mapa_preguntas_habilidad, lista_ids_preguntas
            
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ARCHIVO_PREGUNTAS}")
        return None, None
    except json.JSONDecodeError:
        print(f"Error: El archivo {ARCHIVO_PREGUNTAS} no es un JSON válido.")
        return None, None

# --- 4. FUNCIÓN PRINCIPAL DE SIMULACIÓN ---
def generar_datos():
    mapa_preguntas, lista_ids = cargar_preguntas()
    
    if mapa_preguntas is None:
        return

    # Lista para guardar todas las filas de nuestro futuro CSV
    datos_para_csv = []
    
    # Lista de nombres de arquetipos para elegir al azar
    lista_arquetipos = list(ARQUETIPOS.keys())

    print(f"Iniciando simulación para {NUM_USUARIOS_SINTETICOS} usuarios...")

    # Bucle principal: 1 por cada usuario sintético
    for i in range(NUM_USUARIOS_SINTETICOS):
        id_usuario = f'usuario_{i+1}'
        
        # 1. Asignar un arquetipo al azar a este usuario
        arquetipo_nombre = random.choice(lista_arquetipos)
        perfil_usuario = ARQUETIPOS[arquetipo_nombre]
        
        # 2. Bucle de respuestas: Simular que responde N preguntas
        for _ in range(PREGUNTAS_POR_USUARIO):
            # 3. Elegir una pregunta al azar
            id_pregunta_aleatoria = random.choice(lista_ids)
            habilidad_pregunta = mapa_preguntas[id_pregunta_aleatoria]
            
            # 4. Obtener la probabilidad de acierto base del usuario
            # Usamos .get() por si alguna habilidad del JSON no está en el arquetipo
            prob_base_acierto = perfil_usuario.get(habilidad_pregunta, 0.5) # 0.5 de default
            
            # 5. Decidir si acierta o no
            # random.random() da un número entre 0.0 y 1.0
            # Si el número es MENOR que su probabilidad, acierta.
            resultado_correcto = 1 if random.random() < prob_base_acierto else 0
            
            # 6. Guardar la fila de datos
            datos_para_csv.append([
                id_usuario,
                id_pregunta_aleatoria,
                habilidad_pregunta,
                resultado_correcto
            ])
            
    print(f"Simulación completa. Se generaron {len(datos_para_csv)} registros.")
    
    # --- 5. GUARDAR EN CSV ---
    try:
        with open(ARCHIVO_SALIDA, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Escribir la fila de encabezado (header)
            writer.writerow(['id_usuario', 'id_pregunta', 'habilidad', 'resultado_correcto'])
            # Escribir todos los datos generados
            writer.writerows(datos_para_csv)
            
        print(f"¡Éxito! Datos sintéticos guardados en {ARCHIVO_SALIDA}")
        
    except IOError:
        print(f"Error: No se pudo escribir en el archivo {ARCHIVO_SALIDA}")

# --- 6. EJECUTAR EL SCRIPT ---
if __name__ == '__main__':
    generar_datos()