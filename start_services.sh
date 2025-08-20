#!/bin/bash

# CatchAI Services Startup Script

set -e

echo "🚀 CatchAI Three-Service Architecture"
echo "======================================"
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists docker; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

if ! command_exists "docker compose"; then
    echo "❌ Docker Compose is not installed or not in PATH"
    exit 1
fi

echo "✅ Docker and Docker Compose are available"
echo

# Check if services are already running
echo "🔍 Checking if services are already running..."
if docker compose -f docker-compose-services.yml ps --services --filter "status=running" | grep -q .; then
    echo "⚠️  Some services are already running"
    read -p "Would you like to stop them first? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 Stopping existing services..."
        docker compose -f docker-compose-services.yml down
        echo
    fi
fi

# Build and start services
echo "🏗️  Building and starting services..."
echo "This may take several minutes on first run..."
echo

# Start services in order (dependencies first)
echo "📦 Starting Chroma service..."
docker compose -f docker-compose-services.yml up -d chroma

echo "⏳ Waiting for Chroma to be ready..."
timeout=60
count=0
while [ $count -lt $timeout ]; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ Chroma service is ready"
        break
    fi
    sleep 2
    count=$((count + 2))
done

if [ $count -ge $timeout ]; then
    echo "❌ Chroma service failed to start within $timeout seconds"
    docker compose -f docker-compose-services.yml logs chroma
    exit 1
fi

echo "📦 Starting Model service..."
docker compose -f docker-compose-services.yml up -d model

echo "⏳ Waiting for Model service to be ready..."
echo "   Note: First startup will take 2-3 minutes to download the model..."
timeout=180  # Longer timeout for model loading
count=0
while [ $count -lt $timeout ]; do
    if curl -s http://localhost:8001/health >/dev/null 2>&1; then
        echo "✅ Model service is ready"
        break
    fi
    sleep 5
    count=$((count + 5))
    if [ $((count % 30)) -eq 0 ]; then
        echo "   Still loading model... ($count/$timeout seconds)"
    fi
done

if [ $count -ge $timeout ]; then
    echo "❌ Model service failed to start within $timeout seconds"
    docker compose -f docker-compose-services.yml logs model
    exit 1
fi

echo "📦 Starting Streamlit service..."
docker compose -f docker-compose-services.yml up -d streamlit

echo "⏳ Waiting for Streamlit to be ready..."
timeout=60
count=0
while [ $count -lt $timeout ]; do
    if curl -s http://localhost:8501/_stcore/health >/dev/null 2>&1; then
        echo "✅ Streamlit service is ready"
        break
    fi
    sleep 2
    count=$((count + 2))
done

if [ $count -ge $timeout ]; then
    echo "❌ Streamlit service failed to start within $timeout seconds"
    docker compose -f docker-compose-services.yml logs streamlit
    exit 1
fi

echo
echo "🎉 All services are running successfully!"
echo
echo "📊 Service Status:"
echo "   • Chroma (Vector DB):  http://localhost:8000"
echo "   • Model (LLM):         http://localhost:8001"
echo "   • Streamlit (Web UI):  http://localhost:8501"
echo
echo "🌐 Access the application at: http://localhost:8501"
echo
echo "💡 Useful commands:"
echo "   • View logs:           docker compose -f docker-compose-services.yml logs -f"
echo "   • Stop services:       docker compose -f docker-compose-services.yml down"
echo "   • Test services:       python test_services.py"
echo "   • Run demo:            python demo_workflow.py"
echo
echo "📈 Resource Usage:"
docker compose -f docker-compose-services.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"