# CatchAI Memory Optimization

## Problem Solved
The Docker container was running out of memory when asking questions to the model because:
- The `google/gemma-2b-it` model (2B+ parameters) was being loaded fresh on every query
- Using inefficient `torch.float32` datatype
- No model caching or memory cleanup

## Changes Made

### 1. Model Caching (app/llm_utils.py)
- Implemented singleton pattern to load model only once
- Changed from `torch.float32` to `torch.float16` for 50% memory reduction
- Added `device_map="auto"` for optimal device placement
- Added `low_cpu_mem_usage=True` for better CPU memory management
- Implemented proper tensor cleanup with `torch.no_grad()` and garbage collection

### 2. Docker Optimization (Dockerfile)
- Added memory management environment variables
- Set `PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256` to prevent memory fragmentation
- Added cache directories for Transformers and HuggingFace models
- Added healthcheck endpoint
- Optimized package installation with cleanup

### 3. Docker Compose (docker-compose.yml)
- Added memory limits: 8GB max, 4GB reserved
- Added CPU limits to prevent resource exhaustion
- Added restart policy and healthcheck
- Added environment variables for memory optimization

### 4. Application Improvements (app/app.py)
- Added "Clean Model Memory" button for manual cleanup
- Added error handling and user feedback
- Added loading spinners for better UX
- Limited context size to 512 characters to manage memory

## Memory Requirements
- **Minimum RAM**: 6GB (4GB for model + 2GB for system)
- **Recommended RAM**: 8GB+ for optimal performance
- **Docker Memory Limit**: 8GB (configurable in docker-compose.yml)

## Usage
1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Access the application at http://localhost:8501

3. If you encounter memory issues:
   - Use the "Clean Model Memory" button in the UI
   - Restart the container: `docker-compose restart`
   - Reduce the Docker memory limit if needed

## Technical Details
- Model is cached globally using singleton pattern
- Memory is automatically cleaned after each inference
- Context is limited to 512 characters to prevent large inputs
- Uses float16 precision for 50% memory savings
- Implements proper PyTorch memory management