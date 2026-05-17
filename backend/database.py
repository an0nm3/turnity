import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def save_report(user_id: str, text: str, title: str, result: dict):
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
    try:
        res = supabase.table("reports").insert(data).execute()
        if res.data and len(res.data) > 0:
            return res.data[0].get("id")
    except Exception as e:
        print(f"Save error: {e}")
    return None

async def get_user_reports(user_id: str, limit: int = 20):
    try:
        res = supabase.table("reports").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Fetch error: {e}")
        return []

async def get_report(report_id: str, user_id: str):
    try:
        res = supabase.table("reports").select("*").eq("id", report_id).eq("user_id", user_id).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"Report fetch error: {e}")
        return None
