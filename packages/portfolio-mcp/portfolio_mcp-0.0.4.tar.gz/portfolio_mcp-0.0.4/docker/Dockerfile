# portfolio-mcp - Production Dockerfile
# Extends the base image with the portfolio analysis application
#
# Build: docker build -f docker/Dockerfile -t portfolio-mcp:latest .
# Run:   docker run -p 8000:8000 portfolio-mcp:latest
#
# The server uses streamable-http transport (recommended for remote/Docker).
# Configure via environment variables:
#   FASTMCP_PORT: Server port (default: 8000)
#   FASTMCP_HOST: Server host (default: 0.0.0.0)
#   CACHE_BACKEND: Cache backend - memory, sqlite, redis (default: redis for HTTP)
#   REDIS_URL: Redis connection URL (default: redis://localhost:6379)

# Build argument for Python version (must match base image)
ARG PYTHON_VERSION=3.12
ARG BASE_IMAGE=ghcr.io/l4b4r4b4b4/portfolio-mcp-base:latest

# ==============================================================================
# Production Runtime
# ==============================================================================
FROM ${BASE_IMAGE} AS production

# Copy project files needed for installation
COPY --chown=appuser:appuser pyproject.toml uv.lock ./
COPY --chown=appuser:appuser app/ /app/app/

# Install the package itself (not just dependencies)
# This ensures __version__ is properly set from package metadata
RUN /opt/venv/bin/uv pip install --no-deps .

# Default: Run MCP server with streamable-http transport (recommended for remote)
CMD ["uv", "run", "portfolio-mcp", "streamable-http"]

# ==============================================================================
# Development Runtime (with source mounting support)
# ==============================================================================
FROM ${BASE_IMAGE} AS development

# Copy project files needed for installation
COPY --chown=appuser:appuser pyproject.toml uv.lock ./
COPY --chown=appuser:appuser app/ /app/app/

# Install the package itself in editable mode for development
RUN /opt/venv/bin/uv pip install --no-deps -e .

# Dev mode - can override with volume mount
CMD ["uv", "run", "portfolio-mcp", "streamable-http"]
