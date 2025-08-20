from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

app = FastAPI(title="Chroma Vector Database Service", version="1.0.0")

# Configuration
PERSIST_DIRECTORY = "/data/chroma_db"
CHROMA_SETTINGS = Settings(allow_reset=True)

# Global variables
embeddings = None
chroma_client = None

def get_embeddings():
    global embeddings
    if embeddings is None:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embeddings

def get_chroma_client():
    global chroma_client
    if chroma_client is None:
        os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
        chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY, settings=CHROMA_SETTINGS)
    return chroma_client

# Pydantic models
class TextChunk(BaseModel):
    text: str
    chunk_id: str

class CreateVectorStoreRequest(BaseModel):
    chunks: List[TextChunk]

class QueryRequest(BaseModel):
    query: str
    k: int = 7

class QueryResponse(BaseModel):
    results: List[str]

@app.on_event("startup")
async def startup_event():
    # Initialize embeddings and client on startup
    get_embeddings()
    get_chroma_client()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chroma"}

@app.post("/vectorstore/create")
async def create_vectorstore(request: CreateVectorStoreRequest):
    """Create or update vector store with new chunks"""
    try:
        embeddings_func = get_embeddings()
        texts = [chunk.text for chunk in request.chunks]
        ids = [chunk.chunk_id for chunk in request.chunks]
        
        # Create vector store
        vectorstore = Chroma.from_texts(
            texts,
            embeddings_func,
            ids=ids,
            persist_directory=PERSIST_DIRECTORY,
            client_settings=CHROMA_SETTINGS
        )
        
        return {"message": "Vector store created successfully", "chunk_count": len(texts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating vector store: {str(e)}")

@app.post("/vectorstore/query", response_model=QueryResponse)
async def query_vectorstore(request: QueryRequest):
    """Query the vector store for similar documents"""
    try:
        embeddings_func = get_embeddings()
        
        # Load existing vector store
        vectorstore = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=embeddings_func,
            client_settings=CHROMA_SETTINGS
        )
        
        # Perform similarity search
        results = vectorstore.similarity_search(request.query, k=request.k)
        result_texts = [result.page_content for result in results]
        
        return QueryResponse(results=result_texts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying vector store: {str(e)}")

@app.delete("/vectorstore/reset")
async def reset_vectorstore():
    """Reset/clear the vector store"""
    try:
        client = get_chroma_client()
        client.reset()
        return {"message": "Vector store reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting vector store: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)