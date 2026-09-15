# 🐋 1. Select the lightweight production-grade Python standard engine layer
FROM python:3.12-slim

# 📂 2. Provision and isolate the primary execution context home directory
WORKDIR /app

# 🔒 3. Harden Python execution configurations
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 📦 4. Unpack and layer platform dependencies (Optimized to skip redundant pip updates)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🏗️ 5. Copy core application source code packages and validation tests
COPY src ./src
COPY tests ./tests
COPY database ./database
COPY README.md .

# 🛡️ 6. Hardening Practice: Create an unprivileged system user and grant access permissions
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

# 🔑 Drop root escalation capabilities completely for downstream execution threads
USER appuser

# 🚀 7. Authoritative orchestration entrypoint
CMD ["python", "-m", "src.pipeline"]
