import requests
from config import MODEL_SERVICE_URL

def get_llm_response(context: str, query: str) -> str:
    '''
    Input: Contexto y consulta
    Output: Respuesta del modelo LLM
    Descripción: Esta función envía el contexto y la consulta al servicio del modelo para obtener una respuesta.
    '''
    try:
        response = requests.post(
            f"{MODEL_SERVICE_URL}/generate",
            json={"context": context, "query": query},
            timeout=60  # Longer timeout for model inference
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            print(f"Error generating response: {response.text}")
            return "Error al generar respuesta. Intenta de nuevo."
    except Exception as e:
        print(f"Error communicating with Model service: {e}")
        return "Error al comunicarse con el servicio del modelo. Intenta de nuevo."

def cleanup_model() -> bool:
    '''
    Output: True si se limpia exitosamente, False en caso contrario
    Descripción: Esta función solicita al servicio del modelo que limpie la memoria.
    '''
    try:
        response = requests.post(f"{MODEL_SERVICE_URL}/cleanup", timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"Error cleaning up model: {e}")
        return False