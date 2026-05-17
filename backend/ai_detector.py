import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import httpx
import asyncio
import statistics
from config import HF_API_TOKEN, AI_MODELS

HF_HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}

async def query_hf_model(model: str, text: str) -> dict:
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {"inputs": text[:2000]}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(api_url, json=payload, headers=HF_HEADERS)
            if resp.status_code == 200:
                data = resp.json()
                return {"model": model, "success": True, "data": data}
            else:
                return {"model": model, "success": False, "error": resp.text}
    except Exception as e:
        return {"model": model, "success": False, "error": str(e)}

def parse_roberta_score(data: list) -> float:
    if isinstance(data, list) and len(data) > 0:
        if isinstance(data[0], list):
            for item in data[0]:
                if isinstance(item, dict) and item.get("label") == "Real":
                    return item["score"]
        elif isinstance(data[0], dict):
            for item in data:
                if item.get("label") == "Real":
                    return item["score"]
    return 0.5

async def detect_ai(text: str) -> dict:
    tasks = [query_hf_model(model, text) for model in AI_MODELS]
    results = await asyncio.gather(*tasks)

    scores = []
    model_details = []

    for r in results:
        if r["success"]:
            score = parse_roberta_score(r["data"])
            scores.append(score)
            model_details.append({
                "model": r["model"].split("/")[-1],
                "ai_score": round((1 - score) * 100, 1),
                "human_score": round(score * 100, 1),
            })

    if not scores:
        return {
            "ai_score": 50.0,
            "human_score": 50.0,
            "confidence": "low",
            "models": [],
            "error": "All models failed"
        }

    avg_human = statistics.mean(scores)
    avg_ai = 1 - avg_human

    spread = statistics.stdev(scores) if len(scores) > 1 else 0
    confidence = "high" if spread < 0.1 else "medium" if spread < 0.25 else "low"

    return {
        "ai_score": round(avg_ai * 100, 1),
        "human_score": round(avg_human * 100, 1),
        "confidence": confidence,
        "models": model_details,
    }
