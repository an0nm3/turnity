import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
BING_API_KEY = os.getenv("BING_API_KEY", "")

AI_MODELS = [
    "roberta-base-openai-detector",
    "Hello-SimpleAI/chatgpt-detector-roberta",
]
