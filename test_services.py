#!/usr/bin/env python3

import requests
import time
import json

def test_chroma_service():
    """Test Chroma service endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Chroma Service...")
    
    # Test health
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test create vectorstore
    try:
        test_data = {
            "chunks": [
                {"text": "This is a test document", "chunk_id": "test_1"},
                {"text": "Another test chunk", "chunk_id": "test_2"}
            ]
        }
        response = requests.post(f"{base_url}/vectorstore/create", json=test_data, timeout=30)
        print(f"✅ Create vectorstore: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Create vectorstore failed: {e}")
        return False
    
    # Test query vectorstore  
    try:
        query_data = {"query": "test document", "k": 2}
        response = requests.post(f"{base_url}/vectorstore/query", json=query_data, timeout=30)
        print(f"✅ Query vectorstore: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Query vectorstore failed: {e}")
        return False
    
    return True

def test_model_service():
    """Test Model service endpoints"""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Model Service...")
    
    # Test health
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test generate (this might take a while)
    try:
        test_data = {
            "context": "The sky is blue. Water is wet.",
            "query": "What color is the sky?"
        }
        print("⏳ Testing model generation (this may take 1-2 minutes)...")
        response = requests.post(f"{base_url}/generate", json=test_data, timeout=120)
        print(f"✅ Generate response: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Generate response failed: {e}")
        return False
    
    return True

def test_streamlit_service():
    """Test Streamlit service"""
    base_url = "http://localhost:8501"
    
    print("🧪 Testing Streamlit Service...")
    
    try:
        response = requests.get(f"{base_url}/_stcore/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Testing CatchAI Services\n")
    
    print("Testing individual services...")
    print("Make sure to run: docker compose -f docker-compose-services.yml up -d\n")
    
    # Wait a bit for services to start
    print("⏳ Waiting 10 seconds for services to initialize...")
    time.sleep(10)
    
    results = []
    results.append(("Chroma", test_chroma_service()))
    results.append(("Model", test_model_service()))
    results.append(("Streamlit", test_streamlit_service()))
    
    print("\n" + "="*50)
    print("📊 Test Results:")
    for service, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{service:12} {status}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 All services are working correctly!")
    else:
        print("\n⚠️  Some services failed. Check the logs above.")