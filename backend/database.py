import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import httpx
from config import SUPABASE_URL, SUPABASE_KEY

REST_URL = SUPABASE_URL.rstrip("/") + "/rest/v1"

async def save_report(user_id: str, text: str, title: str, result: dict, user_token: str = ""):
    data = {
        "user_id": user_id,
        "text": text[:5000],
        "title": title or "Untitled",
        "ai_score": result.get("ai_detection", {}).get("ai_score", 0),
        "human_score": result.get("ai_detection", {}).get("human_score", 0),
        "confidence": result.get("ai_detection", {}).get("confidence", "low"),
        "plagiarism_score": result.get("plagiarism", {}).get("plagiarism_score", 0),
        "original_score": result.get("plagiarism", {}).get("original_score", 0),
        "full_result": result,
    }
    headers = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    if user_token:
        headers["Authorization"] = f"Bearer {user_token}"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{REST_URL}/reports", json=data, headers=headers)
            if res.status_code in (200, 201):
                inserted = res.json()
                if isinstance(inserted, list) and inserted:
                    return inserted[0].get("id")
                if isinstance(inserted, dict):
                    return inserted.get("id")
    except Exception as e:
        print(f"Save error: {e}")
    return None

async def get_user_reports(user_id: str, user_token: str = "", limit: int = 20):
    headers = {"apikey": SUPABASE_KEY}
    if user_token:
        headers["Authorization"] = f"Bearer {user_token}"
    params = {"user_id": f"eq.{user_id}", "order": "created_at.desc", "limit": str(limit)}
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{REST_URL}/reports", params=params, headers=headers)
            if res.status_code == 200:
                return res.json()
    except Exception as e:
        print(f"Fetch error: {e}")
    return []

async def get_report(report_id: str, user_id: str, user_token: str = ""):
    headers = {"apikey": SUPABASE_KEY}
    if user_token:
        headers["Authorization"] = f"Bearer {user_token}"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{REST_URL}/reports?id=eq.{report_id}&user_id=eq.{user_id}",
                headers=headers,
            )
            if res.status_code == 200:
                data = res.json()
                return data[0] if data else None
    except Exception as e:
        print(f"Report fetch error: {e}")
    return None
