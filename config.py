import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./messages.db")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

if not WEBHOOK_SECRET:
    raise RuntimeError("WEBHOOK_SECRET environment variable is required")


DB_PATH = DATABASE_URL.replace("sqlite:///", "")