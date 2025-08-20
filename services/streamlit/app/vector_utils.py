from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
from config import CHROMA_SERVICE_URL
from typing import List

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

def create_vectorstore(chunks: List[str], chunk_ids: List[str]) -> bool:
    '''
    Input: Chunks de texto e IDs de chunks
    Output: True si se creó exitosamente, False en caso contrario
    Descripción: Esta función envía los chunks al servicio Chroma para crear un almacén vectorial.
    '''
    try:
        # Prepare request data
        chunks_data = [{"text": chunk, "chunk_id": chunk_id} for chunk, chunk_id in zip(chunks, chunk_ids)]
        
        # Send request to Chroma service
        response = requests.post(
            f"{CHROMA_SERVICE_URL}/vectorstore/create",
            json={"chunks": chunks_data},
            timeout=30
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"Error creating vector store: {response.text}")
            return False
    except Exception as e:
        print(f"Error communicating with Chroma service: {e}")
        return False

def query_vectorstore(query: str, k: int = 7) -> List[str]:
    '''
    Input: Consulta de texto y número de resultados a devolver
    Output: Lista de chunks de texto relevantes
    Descripción: Esta función consulta el servicio Chroma para realizar una búsqueda de similitud.
    '''
    try:
        # Send query to Chroma service
        response = requests.post(
            f"{CHROMA_SERVICE_URL}/vectorstore/query",
            json={"query": query, "k": k},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["results"]
        else:
            print(f"Error querying vector store: {response.text}")
            return []
    except Exception as e:
        print(f"Error communicating with Chroma service: {e}")
        return []

def reset_vectorstore() -> bool:
    '''
    Output: True si se resetea exitosamente, False en caso contrario
    Descripción: Esta función resetea el almacén vectorial en el servicio Chroma.
    '''
    try:
        response = requests.delete(f"{CHROMA_SERVICE_URL}/vectorstore/reset", timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"Error resetting vector store: {e}")
        return False