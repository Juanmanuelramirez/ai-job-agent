import streamlit as st
import os
from utils.data_utils import load_and_process_data
from utils.api_utils import get_answer_from_llm

# --- Configuración de la Página ---
st.set_page_config(
    page_title="AI Job Agent",
    page_icon="🤖",
    layout="wide"
)

# --- Barra Lateral para la API Key ---
st.sidebar.header("Configuración")
# Usar variable de entorno de App Runner si está disponible, si no, pedirla.
api_key_env = os.environ.get('OPENAI_API_KEY')
api_key = st.sidebar.text_input(
    "Ingresa tu OPENAI_API_KEY", 
    type="password", 
    value=api_key_env or ""
)

# --- Contenido Principal ---
st.title("🤖 AI Job Agent")
st.markdown("Haz una pregunta sobre las ofertas de trabajo disponibles en el archivo `jobs.csv`.")

# --- Lógica Central de la Aplicación ---

# Función para cargar el índice FAISS, cacheada para evitar reprocesamiento
@st.cache_resource
def load_faiss_index(api_key_param):
    """Carga datos, crea embeddings y devuelve el índice FAISS."""
    # Valida que el archivo de datos exista
    if not os.path.exists('jobs.csv'):
        st.error("Error Crítico: El archivo 'jobs.csv' no se encuentra en el repositorio.")
        st.stop()
    
    # Establece la API key como variable de entorno para que las funciones de utils la usen
    os.environ['OPENAI_API_KEY'] = api_key_param
    with st.spinner("Procesando datos y creando el índice de trabajos... Esto puede tardar un momento."):
        index = load_and_process_data('jobs.csv')
    return index

# Flujo principal
if api_key:
    if api_key.startswith("sk-"):
        faiss_index = load_faiss_index(api_key)
        
        if faiss_index:
            st.success("¡Índice de trabajos cargado exitosamente!")
            
            user_query = st.text_input("¿Qué tipo de trabajo estás buscando?", "")
            
            if st.button("Buscar") and user_query:
                with st.spinner("Buscando la mejor respuesta..."):
                    answer = get_answer_from_llm(faiss_index, user_query)
                    st.markdown("### Respuesta:")
                    st.write(answer)
    else:
        st.sidebar.warning("Por favor, ingresa una API Key válida de OpenAI.")
else:
    st.info("Por favor, ingresa tu OPENAI_API_KEY en la barra lateral o configúrala en las variables de entorno para comenzar.")

