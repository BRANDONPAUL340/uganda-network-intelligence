# 🐋 1. Select the lightweight production-grade Python standard engine layer
FROM python:3.12-slim

# 📂 2. Provision and isolate the primary execution context home directory
WORKDIR /app

# 🔒 3. Harden Python execution configurations
# Prevents Python from writing .pyc compilation cache files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout/stderr outputs to ensure logs stream in real-time
ENV PYTHONUNBUFFERED=1

# 📦 4. Unpack and layer platform dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 🏗️ 5. Copy core application source code packages and validation tests
COPY src ./src
COPY tests ./tests
COPY database ./database
COPY README.md .

# 🚀 6. Define the authoritative orchestration entrypoint instruction command
CMD ["python", "-m", "src.pipeline"]
