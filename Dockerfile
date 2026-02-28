# syntax=docker/dockerfile:1

# Base stage with Python and dependencies
FROM python:3.13-slim AS base
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    tk-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen

# Development stage
FROM base AS development
WORKDIR /app

# Copy source code
COPY src/ ./src/
COPY .env.example ./.env.example

# Create necessary directories
RUN mkdir -p db documents logs

# Expose port if needed (for future web interface)
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uv", "run", "python", "-m", "multi_modal_rag.main"]

# Production stage
FROM base AS production
WORKDIR /app

# Copy source code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p db documents logs

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the application
CMD ["uv", "run", "python", "-m", "multi_modal_rag.main"]