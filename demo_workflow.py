#!/usr/bin/env python3
"""
Complete example demonstrating the three-service architecture
"""

import requests
import json

def demo_complete_workflow():
    """Demonstrate complete PDF processing workflow"""
    
    print("🚀 CatchAI Services - Complete Workflow Demo\n")
    
    # Service URLs
    chroma_url = "http://localhost:8000"
    model_url = "http://localhost:8001"
    streamlit_url = "http://localhost:8501"
    
    # 1. Check all services are running
    print("1️⃣ Checking service health...")
    services = [
        ("Chroma", f"{chroma_url}/health"),
        ("Model", f"{model_url}/health"),
        ("Streamlit", f"{streamlit_url}/_stcore/health")
    ]
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            print(f"   ✅ {name}: OK")
        except:
            print(f"   ❌ {name}: Failed")
            return
    
    # 2. Reset vector database
    print("\n2️⃣ Resetting vector database...")
    response = requests.delete(f"{chroma_url}/vectorstore/reset")
    print(f"   Status: {response.status_code}")
    
    # 3. Simulate document processing
    print("\n3️⃣ Processing document chunks...")
    
    # Simulate chunks from a PDF about Python programming
    document_chunks = [
        {
            "text": "Python is a high-level programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.",
            "chunk_id": "python_intro_1"
        },
        {
            "text": "Python supports multiple programming paradigms including procedural, object-oriented, and functional programming. It has a large standard library.",
            "chunk_id": "python_intro_2"
        },
        {
            "text": "Python is widely used in web development, data science, artificial intelligence, and scientific computing. Popular frameworks include Django and Flask.",
            "chunk_id": "python_uses_1"
        },
        {
            "text": "Data science in Python relies heavily on libraries like NumPy, Pandas, and Matplotlib. Machine learning is facilitated by scikit-learn and TensorFlow.",
            "chunk_id": "python_datascience_1"
        }
    ]
    
    # Create vector store with chunks
    create_data = {"chunks": document_chunks}
    response = requests.post(f"{chroma_url}/vectorstore/create", json=create_data, timeout=30)
    
    if response.status_code == 200:
        print(f"   ✅ Created vector store with {len(document_chunks)} chunks")
    else:
        print(f"   ❌ Failed to create vector store: {response.text}")
        return
    
    # 4. Query the vector database
    print("\n4️⃣ Querying vector database...")
    
    query = "What is Python used for?"
    query_data = {"query": query, "k": 3}
    response = requests.post(f"{chroma_url}/vectorstore/query", json=query_data, timeout=30)
    
    if response.status_code == 200:
        results = response.json()["results"]
        print(f"   ✅ Found {len(results)} relevant chunks")
        print(f"   📝 Query: {query}")
        for i, chunk in enumerate(results[:2], 1):
            print(f"   📄 Chunk {i}: {chunk[:100]}...")
    else:
        print(f"   ❌ Query failed: {response.text}")
        return
    
    # 5. Generate response using the model
    print("\n5️⃣ Generating response with LLM...")
    
    context = "\n".join(results)
    generate_data = {
        "context": context,
        "query": query
    }
    
    print("   ⏳ Generating response (this may take 1-2 minutes)...")
    response = requests.post(f"{model_url}/generate", json=generate_data, timeout=120)
    
    if response.status_code == 200:
        llm_response = response.json()["response"]
        print(f"   ✅ LLM Response generated")
        print(f"   🤖 Answer: {llm_response}")
    else:
        print(f"   ❌ Generation failed: {response.text}")
        return
    
    # 6. Summary
    print("\n" + "="*60)
    print("🎉 Complete Workflow Demo Successful!")
    print("\nWorkflow Summary:")
    print("1. ✅ All services healthy")
    print("2. ✅ Vector database reset")
    print("3. ✅ Document chunks processed and stored")
    print("4. ✅ Relevant chunks retrieved via similarity search")
    print("5. ✅ LLM generated contextual response")
    print("\n📊 Architecture Benefits Demonstrated:")
    print("   • Service separation and independence")
    print("   • REST API communication between services")
    print("   • Scalable vector database operations")
    print("   • Efficient model inference service")
    print("\n🌐 Access the web UI at: http://localhost:8501")

if __name__ == "__main__":
    demo_complete_workflow()