# Multi-stage build for smaller final image
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    rust

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code and install the package
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir .

# Final stage - minimal runtime image
FROM python:3.11-alpine AS runtime

# Install runtime dependencies only
RUN apk add --no-cache \
    ca-certificates \
    tzdata \
    tini && \
    rm -rf /var/cache/apk/*

# Create non-root user for security
RUN addgroup -g 1000 openhab && \
    adduser -D -u 1000 -G openhab -s /bin/sh openhab

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create directories with proper permissions
RUN mkdir -p /app/config /app/logs /app/data && \
    chown -R openhab:openhab /app

# Copy health check script
COPY --chown=openhab:openhab docker/healthcheck.py /app/healthcheck.py

# Set working directory
WORKDIR /app

# Switch to non-root user
USER openhab

# Environment variables with secure defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    OPENHAB_URL=http://localhost:8080 \
    OPENHAB_TIMEOUT=30 \
    LOG_LEVEL=INFO \
    LOG_FORMAT=json \
    HEALTH_CHECK_PORT=8081

# Expose health check port (non-privileged port)
EXPOSE 8081

# Health check configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python /app/healthcheck.py || exit 1

# Use tini as init system for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Default command to run the MCP server
CMD ["openhab-mcp-server", "--log-format", "json"]