import streamlit as st
from pdf_utils import extract_text, clean_text
from vector_utils import split_text, create_vectorstore, query_vectorstore, reset_vectorstore
from llm_utils import get_llm_response, cleanup_model
import os
import tempfile

st.title("Buscador de PDFs con IA - Arquitectura de Microservicios")

# Service status indicators
st.sidebar.title("Estado de Servicios")

# Check service health
def check_service_health():
    import requests
    from config import CHROMA_SERVICE_URL, MODEL_SERVICE_URL
    
    services = {
        "Chroma": CHROMA_SERVICE_URL,
        "Modelo": MODEL_SERVICE_URL
    }
    
    for name, url in services.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                st.sidebar.success(f"✅ {name}: Activo")
            else:
                st.sidebar.error(f"❌ {name}: Error")
        except:
            st.sidebar.error(f"❌ {name}: Sin conexión")

check_service_health()

# Inicializa el historial en la sesión
if "historial" not in st.session_state:
    st.session_state.historial = []

# Inicializa el contador de PDFs en la sesión
if "pdf_count" not in st.session_state:
    st.session_state.pdf_count = 0

# Add control buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Limpiar base de datos"):
        if reset_vectorstore():
            st.success("Base de datos limpiada correctamente.")
            st.session_state.pdf_count = 0
        else:
            st.error("Error al limpiar la base de datos.")

with col2:
    if st.button("Limpiar memoria del modelo"):
        if cleanup_model():
            st.success("Memoria del modelo limpiada correctamente.")
        else:
            st.error("Error al limpiar la memoria del modelo.")

# File upload
st.subheader("Subir PDF")
uploaded_file = st.file_uploader("Elige un archivo PDF", type="pdf", key="file_uploader")

if uploaded_file is not None:
    if st.session_state.pdf_count >= 5:
        st.error("Límite de 5 PDFs alcanzado. Limpia la base de datos para subir más archivos.")
    else:
        with st.spinner("Procesando PDF..."):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                # Extract and clean text
                text = extract_text(tmp_file_path)
                text = clean_text(text)
                
                st.session_state.pdf_count += 1
                st.success(f"PDF guardado. ({st.session_state.pdf_count}/5)")
                
                st.session_state["consulta"] = ""  # Clear query field
                
                # Split text and create vector store
                chunks = split_text(text)
                chunk_ids = [f"{uploaded_file.name}_chunk{i+1}" for i in range(len(chunks))]
                
                if create_vectorstore(chunks, chunk_ids):
                    st.success("Base vectorial creada.")
                else:
                    st.error("Error al crear la base vectorial. Verifique la conexión con el servicio Chroma.")
                    
            except Exception as e:
                st.error(f"Error al procesar el PDF: {str(e)}")
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                st.session_state["file_uploader"] = None

# Query section
st.subheader("Realizar Consulta")
query = st.text_input("Escribe tu consulta", key="consulta")

if query:
    try:
        with st.spinner("Buscando información relevante..."):
            relevant_chunks = query_vectorstore(query, k=7)
            context = "\n".join(relevant_chunks)
            context = context[:512]  # Limit context to manage memory
            
        if not relevant_chunks or context.strip() == "":
            respuesta = "No encontré información relevante en los documentos para tu consulta. Esto puede deberse a problemas de conectividad o a que no hay documentos cargados."
        else:
            with st.spinner("Generando respuesta..."):
                respuesta = get_llm_response(context, query)
                
        # Save to history
        st.session_state.historial.append({"consulta": query, "respuesta": respuesta})
        st.subheader("Respuesta del chatbot:")
        st.write(respuesta)
        
    except Exception as e:
        st.error(f"Error al procesar la consulta: {str(e)}")
        st.info("Intenta limpiar la memoria del modelo y vuelve a intentarlo.")

# Show history
if st.session_state.historial:
    st.subheader("Historial de consultas")
    for item in st.session_state.historial:
        st.markdown(f"**Consulta realizada:** {item['consulta']}")
        st.markdown(f"**Respuesta del chatbot:** {item['respuesta']}")
        st.markdown("---")

# Show architecture info
with st.expander("ℹ️ Información de la Arquitectura"):
    st.markdown("""
    **Arquitectura de Microservicios:**
    
    - **Servicio Streamlit** (Puerto 8501): Interfaz de usuario web
    - **Servicio Chroma** (Puerto 8000): Base de datos vectorial para búsquedas de similitud
    - **Servicio Modelo** (Puerto 8001): Servicio de inferencia del modelo LLM (Google Gemma-2b-it)
    
    Los servicios se comunican mediante APIs REST, permitiendo escalabilidad y mantenimiento independiente.
    """)