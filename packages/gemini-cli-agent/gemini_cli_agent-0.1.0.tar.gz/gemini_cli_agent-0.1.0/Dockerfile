FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_MAJOR=20 \
    GEMINI_CLI_VERSION=0.20.2 \
    SETUPTOOLS_SCM_PRETEND_VERSION=0.1.0

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    gnupg \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm --version && node --version

# Install Gemini CLI globally
RUN npm install -g @google/gemini-cli@${GEMINI_CLI_VERSION} \
    && gemini --version

WORKDIR /app

# Copy application code and install Python dependencies
COPY pyproject.toml README.md ./
COPY gemini_agent/ ./gemini_agent/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir ".[server]"

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app \
    && mkdir -p /home/appuser/.config \
    && chown -R appuser:appuser /home/appuser

USER appuser

EXPOSE 8000

CMD ["uvicorn", "gemini_agent.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
