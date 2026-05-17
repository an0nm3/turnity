import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import httpx
from config import SUPABASE_URL, SUPABASE_KEY

REST_URL = (SUPABASE_URL or "").rstrip("/") + "/rest/v1" if SUPABASE_URL else ""

async def _headers(user_token=""):
    h = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    if user_token:
        h["Authorization"] = f"Bearer {user_token}"
    return h

async def save_report(user_id: str, text: str, title: str, result: dict, user_token: str = ""):
    if not REST_URL:
        return None
    data = {
        "user_id": user_id, "text": text[:5000], "title": title or "Untitled",
        "ai_score": result.get("ai_detection", {}).get("ai_score", 0),
        "human_score": result.get("ai_detection", {}).get("human_score", 0),
        "confidence": result.get("ai_detection", {}).get("confidence", "low"),
        "plagiarism_score": result.get("plagiarism", {}).get("plagiarism_score", 0),
        "original_score": result.get("plagiarism", {}).get("original_score", 0),
        "full_result": result,
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{REST_URL}/reports", json=data, headers=await _headers(user_token))
            if res.status_code in (200, 201):
                d = res.json()
                return d[0].get("id") if isinstance(d, list) and d else d.get("id") if isinstance(d, dict) else None
    except Exception as e:
        print(f"Save error: {e}")
    return None

async def get_user_reports(user_id: str, user_token: str = "", limit: int = 20):
    if not REST_URL:
        return []
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{REST_URL}/reports",
                params={"user_id": f"eq.{user_id}", "order": "created_at.desc", "limit": str(limit)},
                headers=await _headers(user_token),
            )
            return res.json() if res.status_code == 200 else []
    except Exception as e:
        print(f"Fetch error: {e}")
    return []

async def get_report(report_id: str, user_id: str, user_token: str = ""):
    if not REST_URL:
        return None
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{REST_URL}/reports?id=eq.{report_id}&user_id=eq.{user_id}",
                headers=await _headers(user_token),
            )
            return res.json()[0] if res.status_code == 200 and res.json() else None
    except Exception as e:
        print(f"Report fetch error: {e}")
    return None
