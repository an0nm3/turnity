import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
import httpx

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def signup(email: str, password: str):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        return {"success": True, "user": res.user.model_dump() if res.user else None}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def login(email: str, password: str):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return {
            "success": True,
            "access_token": res.session.access_token,
            "user_id": res.user.id,
            "email": res.user.email,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_user(token: str):
    try:
        res = supabase.auth.get_user(token)
        return res.user
    except Exception:
        return None
