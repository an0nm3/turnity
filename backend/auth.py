import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import httpx
from config import SUPABASE_URL, SUPABASE_KEY

AUTH_URL = SUPABASE_URL.rstrip("/") + "/auth/v1"

async def signup(email: str, password: str):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{AUTH_URL}/signup",
                json={"email": email, "password": password},
                headers={"apikey": SUPABASE_KEY, "Content-Type": "application/json"},
            )
            if res.status_code == 200:
                data = res.json()
                return {"success": True, "user": data.get("id")}
            else:
                err = res.json()
                return {"success": False, "error": err.get("msg", err.get("error_description", "Signup failed"))}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def login(email: str, password: str):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{AUTH_URL}/token?grant_type=password",
                json={"email": email, "password": password},
                headers={"apikey": SUPABASE_KEY, "Content-Type": "application/json"},
            )
            if res.status_code == 200:
                data = res.json()
                return {
                    "success": True,
                    "access_token": data["access_token"],
                    "user_id": data["user"]["id"],
                    "email": data["user"]["email"],
                }
            else:
                return {"success": False, "error": "Invalid credentials"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_user(token: str):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{AUTH_URL}/user",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {token}"},
            )
            if res.status_code == 200:
                return res.json()
            return None
    except Exception:
        return None
