from pathlib import Path
import environ
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Load environment variables from .env file
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))

BOT_TOKEN = env.str('BOT_TOKEN')
ADMIN_ID = env.list('ADMIN_ID', default=[])
CHANNEL_ID = ["-1001275637856"]

# PostgreSQL database uchun o'zgartiramiz
DATABASE_CONFIG = {
    "connections": {
        "default": f"postgres://{env.str('DB_USER')}:{env.str('DB_PASS')}@{env.str('DB_HOST')}:{env.str('DB_PORT')}/{env.str('DB_NAME')}"
    },
    "apps": {
        "models": {
            "models": ["utils.db.models"],  
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "Asia/Tashkent"
}

# RAG Service uchun
GROQ_API_KEY = env.str('GROQ_API_KEY', default='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')
CHROMA_DB_PATH = os.path.join(BASE_DIR, 'chroma_db')
DOCUMENTS_PATH = os.path.join(BASE_DIR, 'media', 'documents')
