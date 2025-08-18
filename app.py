import streamlit as st
import shutil
import os
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from chromadb import PersistentClient
from chromadb.config import Settings

settings=Settings(allow_reset=True)
# ...otros imports...

st.title("Buscador de PDFs con IA")

# Botón para limpiar la base de datos
if st.button("Limpiar base de datos"):
    try:
        client = PersistentClient(path="./chroma_db", settings=settings)
        client.reset()
        st.success("Base de datos limpiada correctamente.")
    except Exception as e:
        st.error(f"No se pudo limpiar la base de datos: {e}")

# Subir PDF
uploaded_file = st.file_uploader("Sube un PDF", type="pdf")
if uploaded_file:
    pdf_path = f"pdf/{uploaded_file.name}"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("PDF guardado.")

    # Extraer texto
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    # Dividir en chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=750,
        chunk_overlap=int(750*0.15),
        length_function=len,
    )
    chunks = text_splitter.create_documents([text])
    all_chunks = [doc.page_content for doc in chunks]
    all_chunk_ids = [f"{uploaded_file.name}_chunk{i+1}" for i in range(len(chunks))]

    # Embeddings y Chroma
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma.from_texts(
        all_chunks,
        embeddings,
        ids=all_chunk_ids,
        persist_directory="./chroma_db",
        client_settings=settings
    )
    vectorstore.persist()
    st.success("Base vectorial creada.")

# Consulta
query = st.text_input("Escribe tu consulta")
if query:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        client_settings=settings
    )
    query_vector = embeddings.embed_query(query)
    results = vectorstore.similarity_search_by_vector(query_vector, k=5)
    relevant_chunks = [result.page_content for result in results]
    context = "\n".join(relevant_chunks)

    from langchain.llms import HuggingFaceHub

    # Configura tu token de HuggingFace
    import os
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

    # ...después de obtener relevant_chunks y construir el prompt...
    llm = HuggingFaceHub(
        repo_id="meta-llama/Meta-Llama-3.1-8B-Instruct",
        task="text2text-generation",
        model_kwargs={"temperature": 0.5, "max_length": 256}
    )

    context = "\n".join(relevant_chunks)
    prompt = (
        f"Contexto:\n{context}\n\n"
        f"Pregunta:\n{query}\n\n"
        "Responde de forma clara y específica."
    )

    respuesta = llm(prompt)
    st.subheader("Respuesta del chatbot:")
    st.write(respuesta)

    