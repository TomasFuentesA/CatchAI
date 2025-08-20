from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def _simple_context_response(context, query):
    """
    Simple fallback response when LLM models are not available
    Provides a basic response using the context directly
    """
    if not context or context.strip() == "":
        return "No encontré información relevante en los documentos para responder tu pregunta."
    
    # Create a simple response using the context
    if "Python" in query or "python" in query:
        if "Python" in context or "python" in context or "programación" in context:
            return f"Según la información encontrada: {context[:200]}..."
    
    if "experiencia" in query.lower() or "experience" in query.lower():
        return f"Basándome en la información disponible: {context[:200]}..."
    
    if "universidad" in query.lower() or "university" in query.lower() or "estudió" in query.lower():
        if "Universidad" in context or "University" in context:
            return f"Según los documentos: {context[:200]}..."
    
    if "proyecto" in query.lower() or "project" in query.lower():
        return f"Información encontrada sobre proyectos: {context[:200]}..."
    
    # Default response
    return f"Encontré la siguiente información relevante: {context[:200]}..."

def get_llm_response(context, query):
    try:
        tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b-it")
        model = AutoModelForCausalLM.from_pretrained(
            "google/gemma-2b-it",
            torch_dtype=torch.float32
        )

        prompt = (
            f"Contexto:\n{context}\n\n"
            f"Pregunta:\n{query}\n"
            "Responde de forma clara y específica usando solo la información relevante del contexto. Si no hay información suficiente, responde 'No sé'."
        )
        input_ids = tokenizer(prompt, return_tensors="pt").to("cpu")
        outputs = model.generate(**input_ids, max_new_tokens=150)
        respuesta = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Elimina el prompt si aparece en la respuesta
        if respuesta.startswith(prompt):
            respuesta = respuesta[len(prompt):].strip()
        return respuesta
    except Exception as e:
        print(f"Error loading LLM model, using simple context response: {e}")
        # Use simple context-based response when LLM model is not available
        return _simple_context_response(context, query)