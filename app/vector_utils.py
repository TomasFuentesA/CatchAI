from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def split_text(text, chunk_size=1000, chunk_overlap=750*0.15): 
    '''
    Input: Texto a dividir en chunks, tamaño de chunk y superposición (15%)
    Output: Lista de chunks de texto
    Descripción: Esta función utiliza la clase RecursiveCharacterTextSplitter para dividir el texto en partes más pequeñas (chunks) que son más manejables para el procesamiento.
    '''
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.create_documents([text])
    return [doc.page_content for doc in chunks]

def create_vectorstore(chunks, chunk_ids, persist_directory, settings):
    '''
    Input: Chunks de texto, IDs de chunks, directorio de persistencia y configuraciones
    Output: Almacén vectorial creado
    Descripción: Esta función utiliza los embeddings de HuggingFace y Chroma para crear un almacén vectorial a partir de los chunks de texto.
    '''
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Chroma.from_texts(
        chunks,
        embeddings,
        ids=chunk_ids,
        persist_directory=persist_directory,
        client_settings=settings
    )

def query_vectorstore(query, persist_directory, settings, k=7):
    '''
    Input: Consulta de texto, directorio de persistencia, configuraciones y número de resultados a devolver
    Output: Lista de chunks de texto relevantes
    Descripción: Esta función utiliza los embeddings de HuggingFace y Chroma para realizar una búsqueda de similitud en el almacén vectorial.
    '''
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        client_settings=settings
    )
    query_vector = embeddings.embed_query(query)
    results = vectorstore.similarity_search_by_vector(query_vector, k=k)
    return [result.page_content for result in results]