import os
from dotenv import load_dotenv

# 🔍 Locate, decrypt, and load local environment key-value pairs into system memory
load_dotenv()

# Extract variables from system memory with strict fail-safe fallbacks
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "network_intelligence")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "tech")
