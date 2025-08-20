from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

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
        print(f"Error loading LLM model: {e}")
        # Simple fallback: return relevant context when LLM model is not available
        if not context or context.strip() == "":
            return "No encontré información relevante en los documentos para responder tu pregunta."
        else:
            return f"Basándome en la información encontrada en los documentos: {context[:300]}..."