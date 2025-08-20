import streamlit as st
from pdf_utils import extract_text, clean_text
from vector_utils import split_text, create_vectorstore, query_vectorstore
from llm_utils import get_llm_response, cleanup_model
from config import HF_TOKEN, PERSIST_DIRECTORY, CHROMA_SETTINGS
from huggingface_hub import login
import os
import gc

login(token=HF_TOKEN)

st.title("Buscador de PDFs con IA")

# Inicializa el historial en la sesión
if "historial" not in st.session_state:
    st.session_state.historial = []

# Inicializa el contador de PDFs en la sesión
if "pdf_count" not in st.session_state:
    st.session_state.pdf_count = 0

# Add memory cleanup button
col1, col2 = st.columns(2)
with col1:
    if st.button("Limpiar base de datos"):
        from chromadb import PersistentClient
        try:
            client = PersistentClient(path=PERSIST_DIRECTORY, settings=CHROMA_SETTINGS)
            client.reset()
            st.success("Base de datos limpiada correctamente.")
        except Exception as e:
            st.error(f"No se pudo limpiar la base de datos: {e}")

with col2:
    if st.button("Limpiar memoria del modelo"):
        try:
            cleanup_model()
            gc.collect()
            st.success("Memoria del modelo limpiada correctamente.")
        except Exception as e:
            st.error(f"Error al limpiar memoria: {e}")

uploaded_file = st.file_uploader("Sube un PDF", type="pdf")
if uploaded_file:
    if st.session_state.pdf_count >= 5:
        st.warning("Solo puedes subir hasta 5 PDFs.")
    else:
        os.makedirs("pdf", exist_ok=True)
        pdf_path = f"pdf/{uploaded_file.name}"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        text = extract_text(pdf_path)
        text = clean_text(text)
        if not text.strip():
            st.error("El PDF no contiene texto extraíble. Por favor, sube otro archivo.")
        else:
            st.session_state.pdf_count += 1
            st.success(f"PDF guardado. ({st.session_state.pdf_count}/5)")

            st.session_state["consulta"] = ""  # ← Borra el campo de consulta
            
            chunks = split_text(text)
            chunk_ids = [f"{uploaded_file.name}_chunk{i+1}" for i in range(len(chunks))]
            create_vectorstore(chunks, chunk_ids, PERSIST_DIRECTORY, CHROMA_SETTINGS)
            st.success("Base vectorial creada.")
            st.session_state["file_uploader"] = None

query = st.text_input("Escribe tu consulta", key="consulta")
if query:
    try:
        with st.spinner("Buscando información relevante..."):
            relevant_chunks = query_vectorstore(query, PERSIST_DIRECTORY, CHROMA_SETTINGS, k=7)
            context = "\n".join(relevant_chunks)
            context = context[:512]  # Limit context to manage memory
            
        if not relevant_chunks or context.strip() == "":
            respuesta = "No encontré información relevante en los documentos para tu consulta."
        else:
            with st.spinner("Generando respuesta con IA..."):
                respuesta = get_llm_response(context, query)
                
        # Guarda en el historial
        st.session_state.historial.append({"consulta": query, "respuesta": respuesta})
        st.subheader("Respuesta del chatbot:")
        st.write(respuesta)
        
    except Exception as e:
        st.error(f"Error al procesar la consulta: {str(e)}")
        st.info("Intenta limpiar la memoria del modelo y vuelve a intentarlo.")

# Muestra el historial
st.subheader("Historial de consultas")
for item in st.session_state.historial:
    st.markdown(f"**Consulta realizada:** {item['consulta']}")
    st.markdown(f"**Respuesta del chatbot:** {item['respuesta']}")
    st.markdown("---")