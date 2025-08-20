from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import gc
import os

app = FastAPI(title="LLM Model Service", version="1.0.0")

# Global variables to cache the model and tokenizer
_tokenizer = None
_model = None

class GenerateRequest(BaseModel):
    context: str
    query: str

class GenerateResponse(BaseModel):
    response: str

def _load_model():
    """Load and cache the model and tokenizer (singleton pattern)"""
    global _tokenizer, _model
    
    if _tokenizer is None or _model is None:
        print("Loading model and tokenizer (this may take a moment)...")
        
        # Get HF token from environment or use default
        hf_token = os.getenv("HF_TOKEN", "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")
        if hf_token:
            from huggingface_hub import login
            login(token=hf_token)
        
        _tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b-it")
        _model = AutoModelForCausalLM.from_pretrained(
            "google/gemma-2b-it",
            torch_dtype=torch.float16,  # Use float16 for better memory efficiency
            device_map="auto",          # Automatic device mapping
            low_cpu_mem_usage=True      # Optimize CPU memory usage
        )
        
        # Set pad token if not already set
        if _tokenizer.pad_token is None:
            _tokenizer.pad_token = _tokenizer.eos_token
            
        print("Model and tokenizer loaded successfully!")
    
    return _tokenizer, _model

@app.on_event("startup")
async def startup_event():
    # Pre-load model on startup
    _load_model()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "model"}

@app.post("/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest):
    """Generate a response using the LLM model"""
    try:
        tokenizer, model = _load_model()
        
        prompt = (
            f"Contexto:\n{request.context}\n\n"
            f"Pregunta:\n{request.query}\n"
            "Responde de forma clara y específica usando solo la información relevante del contexto. Si no hay información suficiente, responde 'No sé'."
        )
        
        # Tokenize with padding and attention mask
        inputs = tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=1024,  # Limit input length to manage memory
            padding=True
        )
        
        # Generate response with memory optimization
        with torch.no_grad():  # Disable gradient computation to save memory
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        respuesta = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Clean up tensors to free memory
        del inputs, outputs
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        gc.collect()
        
        # Remove the prompt if it appears in the response
        if respuesta.startswith(prompt):
            respuesta = respuesta[len(prompt):].strip()
        
        return GenerateResponse(response=respuesta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.post("/cleanup")
async def cleanup_model():
    """Clean up model and tokenizer to free memory"""
    global _tokenizer, _model
    try:
        if _model is not None:
            del _model
            _model = None
        if _tokenizer is not None:
            del _tokenizer
            _tokenizer = None
        
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        gc.collect()
        
        return {"message": "Model cleanup completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)