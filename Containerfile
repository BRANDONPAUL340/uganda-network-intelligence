# Use a minimal, slim Python footprint image base
FROM python:3.14-slim

WORKDIR /app

# Prevent Python from writing debug pyc files to disk storage
ENV PYTHONDONTWRITEBYTECODE=1
# Force unbuffered standard output for clean container streaming telemetry logs
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source structures cleanly into the container build frame
COPY src ./src
COPY database ./database
COPY docs ./docs
COPY README.md .

# Security Hardening: Enforce unprivileged user context execution blocks
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

# (Keep all of your slim base images, pip packages, and unprivileged user mappings intact)

USER appuser

EXPOSE 8501

# 🧠 Embedded Container Health Layer
# Podman will periodically execute this abstract check loop within the isolated network namespace [1]
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -m src.dashboard.healthcheck

CMD ["streamlit", "run", "src/dashboard/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
