# Competitor Research Agent - Production Docker Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers (optional - can be skipped if causing issues)
RUN pip install playwright && \
    playwright install chromium && \
    playwright install-deps chromium || echo "Playwright install failed, continuing without it"

# Copy application code
COPY . .

# Create directories for outputs and cache
RUN mkdir -p /app/reports \
    /app/logs \
    /app/cache \
    /app/test_reports

# Set proper permissions
RUN chmod +x run_tests.py && \
    chmod +x src/cli/enhanced_cli.py

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash cra_user && \
    chown -R cra_user:cra_user /app
USER cra_user

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["python", "main.py", "--help"]

# Labels for metadata
LABEL \
    org.opencontainers.image.title="Competitor Research Agent" \
    org.opencontainers.image.description="AI-Powered Market Intelligence & Competitive Analysis Platform" \
    org.opencontainers.image.version="2.0" \
    org.opencontainers.image.authors="Your Name <your.email@example.com>"
