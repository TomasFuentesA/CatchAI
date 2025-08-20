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
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = Chroma.from_texts(
            chunks,
            embeddings,
            ids=chunk_ids,
            persist_directory=persist_directory,
            client_settings=settings
        )
        return vectorstore
    except Exception as e:
        print(f"Error en create_vectorstore: {e}")
        return None

def _fallback_tfidf_search(query, persist_directory, k=7):
    '''
    Fallback search using TF-IDF when embedding models are not available
    '''
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        from chromadb import PersistentClient
        
        # Get documents from ChromaDB
        client = PersistentClient(path=persist_directory)
        collections = client.list_collections()
        
        if not collections:
            return []
        
        collection = collections[0]
        results = collection.get()
        
        if not results or 'documents' not in results or not results['documents']:
            return []
        
        documents = results['documents']
        
        # Create TF-IDF vectors with more flexible parameters
        vectorizer = TfidfVectorizer(
            stop_words='english', 
            max_features=1000,
            ngram_range=(1, 2),  # Include bigrams for better matching
            lowercase=True,
            min_df=1,  # Include words that appear in at least 1 document
            max_df=0.95  # Exclude words that appear in more than 95% of documents
        )
        doc_vectors = vectorizer.fit_transform(documents)
        
        # Transform query
        query_vector = vectorizer.transform([query])
        
        # Calculate similarity
        similarities = cosine_similarity(query_vector, doc_vectors).flatten()
        
        # Get top k results
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        # Use a more relaxed similarity threshold
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.005:  # Lower minimum similarity threshold
                results.append(documents[idx])
        
        # If no results with similarity, return top documents anyway for fallback
        if not results and len(documents) > 0:
            # Return some documents as a last resort
            results = documents[:min(k, len(documents))]
        
        return results
        
    except Exception as e:
        print(f"Error in fallback TF-IDF search: {e}")
        return []

def query_vectorstore(query, persist_directory, settings, k=7):
    '''
    Input: Consulta de texto, directorio de persistencia, configuraciones y número de resultados a devolver
    Output: Lista de chunks de texto relevantes
    Descripción: Esta función utiliza los embeddings de HuggingFace y Chroma para realizar una búsqueda de similitud en el almacén vectorial.
    Con fallback a TF-IDF si los embeddings no están disponibles.
    '''
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            client_settings=settings
        )
        results = vectorstore.similarity_search(query, k=k)
        return [result.page_content for result in results]
    except Exception as e:
        print(f"Error loading embedding model, using TF-IDF fallback: {e}")
        # Use TF-IDF fallback when embedding model is not available
        return _fallback_tfidf_search(query, persist_directory, k)