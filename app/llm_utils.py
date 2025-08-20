from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import gc

# Variables de caché y tokenizador
_tokenizer = None
_model = None

def _load_model():
    """
    Input: No recibe
    Output: (tokenizer, model)
    Descripcion: Carga y almacena en caché el modelo y el tokenizador (patrón singleton).
    """
    global _tokenizer, _model
    
    if _tokenizer is None or _model is None:
        print("Cargando modelo y tokenizador (esto puede tardar un momento)...")
        
        _tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b-it")
        _model = AutoModelForCausalLM.from_pretrained(
            "google/gemma-2b-it",
            torch_dtype=torch.float16,  # Usar float16 para mejor eficiencia de memoria
            device_map="auto",          # Asignación automática de dispositivo
            low_cpu_mem_usage=True      # Optimizar uso de memoria CPU
        )
        
        # Establecer el token de relleno si no está definido
        if _tokenizer.pad_token is None:
            _tokenizer.pad_token = _tokenizer.eos_token
            
        print("¡Modelo y tokenizador cargados exitosamente!")
    
    return _tokenizer, _model

def get_llm_response(context, query):
    '''
    Input: contexto y consulta
    Output: respuesta generada por el modelo
    Descripcion: Genera una respuesta basada en el contexto y la consulta proporcionados.
    '''

    tokenizer, model = _load_model()
    
    prompt = (
        f"Contexto:\n{context}\n\n"
        f"Pregunta:\n{query}\n"
        "Responde de forma clara y específica usando solo la información relevante del contexto. Si no hay información suficiente, responde 'No sé'."
    )
    
    # Tokenizar con relleno y máscara de atención
    inputs = tokenizer(
        prompt, 
        return_tensors="pt", 
        truncation=True, 
        max_length=1024,  # Limitar longitud de entrada para gestionar memoria
        padding=True
    )
    
    # Generar respuesta con optimización de memoria
    with torch.no_grad():  # Desactivar cálculo de gradientes para ahorrar memoria
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
    
    respuesta = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Liberar tensores para ahorrar memoria
    del inputs, outputs
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    gc.collect()
    
    # Eliminar el prompt si aparece en la respuesta
    if respuesta.startswith(prompt):
        respuesta = respuesta[len(prompt):].strip()
    
    return respuesta

def cleanup_model():
    """
    Input: No recibe
    Output: No devuelve
    Descripcion: Libera los recursos utilizados por el modelo y el tokenizador.
    """
    global _tokenizer, _model
    
    if _model is not None:
        del _model
        _model = None
    if _tokenizer is not None:
        del _tokenizer
        _tokenizer = None
    
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    gc.collect()
    print("Model and tokenizer cleaned up from memory")
