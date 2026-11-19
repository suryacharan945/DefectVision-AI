# DefectVision AI — Production Backend Dockerfile
# Optimized for CPU Inference (FastAPI + PyTorch CPU + FAISS-CPU + 15 Category PatchCore)

FROM python:3.11-slim AS runtime

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    KMP_DUPLICATE_LIB_OK=TRUE \
    DEFECTVISION_DATA_DIR=/app/data \
    DEFECTVISION_PROFILES_DIR=/app/data/production_profiles

# Install minimal OS dependencies for OpenCV headless, OpenMP, and healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency requirements
COPY requirements.txt /app/requirements.txt

# Install CPU-only PyTorch first to reduce container image footprint (~2GB savings vs CUDA)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application source, model weights, and baseline reports
COPY DefectVisionAI /app

# Ensure runtime data, profiles, output, log, and batch directories exist
RUN mkdir -p /app/data /app/data/production_profiles /app/outputs/similarity_search_samples /app/logs /app/batch_inspections

# Expose standard container port
EXPOSE 8000

# Container healthcheck against /api/ready or /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/ready || curl -f http://localhost:${PORT}/health || exit 1

# Launch production Uvicorn server binding to dynamic cloud host & port
CMD ["sh", "-c", "uvicorn app:app --host ${HOST} --port ${PORT}"]
