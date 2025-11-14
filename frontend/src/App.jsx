import { useState, useEffect } from 'react'
import './App.css'

// La URL del Backend.
const API_URL = 'http://127.0.0.1:5000'

// Componente del Panel de Habilidades.
const PanelHabilidades = ({ preds }) => (
  <div className="habilidades-panel">
    <h4>Tu Dominio Actual:</h4>
    <ul>
      {preds.map((pred) => (
        <li key={pred.habilidad}>
          <span className="hab-nombre">{pred.habilidad}</span>
          <div className="hab-barra-fondo">
            <div 
              className="hab-barra-progreso" 
              style={{ width: `${pred.prob_acierto * 100}%` }}
              title={`${Math.round(pred.prob_acierto * 100)}%`}
            >
              {Math.round(pred.prob_acierto * 100)}%
            </div>
          </div>
        </li>
      ))}
    </ul>
    <p className="hab-info">El sistema se enfoca en tu habilidad más baja.</p>
  </div>
)

function App() {
  // El estado "pregunta" guardará el objeto de la pregunta actual.
  const [pregunta, setPregunta] = useState(null)
  
  // "resultado" guardará la respuesta del backend (ej: {resultado: "correcta", ...}).
  const [resultado, setResultado] = useState(null)
  
  // "cargando" nos servirá para mostrar un mensaje mientras esperamos la pregunta.
  const [cargando, setCargando] = useState(true)

  // "verificando" lo que hará será deshabilitar el botón mientras se realiza el proceso.
  const [verificando, setVerificando] = useState(false)

  const [testCompletado, setTestCompletado] = useState(false)

  // "predicciones" guardará el ranking de habilidades.
  const [predicciones, setPredicciones] = useState([])
 
  // Carga una nueva pregunta desde el backend.
  const fetchPregunta = async () => {
    setCargando(true)
    setResultado(null)
    setVerificando(false) // Reseteamos el estado de verificación

    const response = await fetch(`${API_URL}/api/pregunta`) 
    const data = await response.json()

    setPredicciones(data.predicciones || [])
    
    if (data.completado) {
      setTestCompletado(true)
      setCargando(false)
    } else {
      setPregunta(data.pregunta)
      setCargando(false)
    }
  }

  // Se ejecuta solo una vez, cuando el componente carga por primera vez.
  useEffect(() => {
    fetchPregunta()
  }, []) // "[]" significa "ejecutar solo al inicio".

  // Se selecciona la respuesta y recibe la opción seleccionada.
  const handleOpcionClick = async (opcionSeleccionada) => {
    setVerificando(true) 

    const response = await fetch(`${API_URL}/api/verificar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: pregunta.id,
        respuesta: opcionSeleccionada,
      }),
    })
    const data = await response.json()
    // Actualiza el resultado, ya sea correcto o incorrecto.
    setResultado({
      resultado: data.resultado,
      respuesta_correcta: data.respuesta_correcta
    })
    // Actualiza el panel de habilidades.
    setPredicciones(data.predicciones_actualizadas)
    setVerificando(false)
  }

    // Maneja el reinicio del test.
  const handleReiniciar = async () => {
    // 1. Llama a la API para limpiar el historial del backend
    await fetch(`${API_URL}/api/reiniciar`, { method: 'POST' }) 
    
    // 2. Resetea el estado del frontend
    setJuegoCompletado(false)
    setPregunta(null)
    setPredicciones([])
    
    // 3. Carga la primera pregunta del nuevo test
    fetchPregunta()
  }

  // Muestra un mensaje de "Cargando...".
  if (cargando) {
    return <div className="App"><h1>Cargando pregunta...</h1></div>
  }

  // Vista de Test Completado.
  if (testCompletado) {
    return (
      <div className="app-container">
        {/* Columna Izquierda */}
        <div className="main-content">
          <h1>¡Felicidades!</h1>
          <div className="quiz-container">
            <p>Has respondido todas las preguntas disponibles.</p>
            <p>Tu tutoría ha sido completada. Este es tu perfil final:</p>
            <button onClick={handleReiniciar} className="btn-reiniciar">
              Reintentar el Test
            </button>
          </div>
        </div>
        
        {/* Columna Derecha */}
        <div className="sidebar-content">
          <PanelHabilidades preds={predicciones} />
        </div>
      </div>
    )
  }

  return (
    <div className="app-container">
      
      {/* Columna Izquierda. */}
      <div className="main-content">
        <h1>Sistema de Tutoría Inteligente</h1>
        <div className="quiz-container">
          
          {/* Si no hay pregunta, se queda cargando. */}
          {!pregunta ? (
            <p>Cargando...</p>
          ) : (
            <>
              <h3>{pregunta.texto}</h3>
              <p className="habilidad">Habilidad: {pregunta.habilidad}</p>

              {!resultado && (
                <div className="opciones-container">
                  {pregunta.opciones.map((opcion, index) => (
                    <button
                      key={index}
                      className="opcion-btn"
                      onClick={() => handleOpcionClick(opcion)}
                      disabled={verificando || cargando}
                    >
                      {opcion}
                    </button>
                  ))}
                </div>
              )}

              {resultado && (
                <div className="resultado-container">
                  {resultado.resultado === 'correcta' ? (
                    <p className="correcta">¡Correcto!</p>
                  ) : (
                    <p className="incorrecta">
                      Incorrecto. La respuesta correcta es: <strong>{resultado.respuesta_correcta}</strong>
                    </p>
                  )}
                  
                  <button onClick={fetchPregunta} disabled={cargando}>
                    {cargando ? "Cargando..." : "Siguiente Pregunta"}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
      
      {/* Columna Derecha. */}
      <div className="sidebar-content">
        <PanelHabilidades preds={predicciones} />
      </div>

    </div>
  )
}

export default App