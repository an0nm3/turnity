import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import httpx
from config import HF_API_TOKEN

HF_BASE = "https://router.huggingface.co/v1"
DETECTOR_MODEL = "meta-llama/Llama-3.1-8B-Instruct"

DETECTION_PROMPT = """You are an AI content detection expert. Analyze the following text and determine if it was written by a human or an AI.

Consider:
- Sentence structure variety (humans vary more, AI is more uniform)
- Use of contractions and informal language (more human)
- Natural imperfections and varied tone
- Repetitive patterns (more AI-like)
- Depth of personal experience or unique perspective (more human)

Respond with ONLY a JSON object like this, no other text:
{"ai_score": 0-100, "human_score": 0-100, "reasoning": "brief explanation"}"""

async def detect_with_llm(text: str) -> dict:
    if not HF_API_TOKEN:
        return None
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{HF_BASE}/chat/completions",
                json={
                    "model": DETECTOR_MODEL,
                    "messages": [
                        {"role": "system", "content": DETECTION_PROMPT},
                        {"role": "user", "content": f"Analyze this text:\n\n{text[:1500]}"},
                    ],
                    "max_tokens": 200,
                    "temperature": 0.1,
                },
                headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                import re, json
                match = re.search(r'\{[^{}]*\}', content)
                if match:
                    result = json.loads(match.group())
                    return {
                        "ai_score": float(result.get("ai_score", 50)),
                        "human_score": float(result.get("human_score", 50)),
                        "confidence": "medium",
                        "models": [{"model": "Llama-3.1-8B (AI Detector)", "ai_score": round(float(result.get("ai_score", 50)), 1), "human_score": round(float(result.get("human_score", 50)), 1)}],
                    }
        return None
    except Exception as e:
        print(f"LLM detect error: {e}")
        return None

def heuristic_detect(text: str) -> dict:
    words = text.split()
    total = len(words)
    if total == 0:
        return {"ai_score": 50, "human_score": 50, "confidence": "low", "models": [{"model": "Heuristic", "ai_score": 50, "human_score": 50}]}

    signals = {"ai": 0, "human": 0, "total_checks": 0}

    sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    if sentences:
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        signals["total_checks"] += 1
        if avg_len > 25:
            signals["ai"] += 1
        elif avg_len < 12:
            signals["human"] += 1

        len_var = sum((len(s.split()) - avg_len)**2 for s in sentences) / len(sentences)
        signals["total_checks"] += 1
        if len_var < 5:
            signals["ai"] += 1
        elif len_var > 15:
            signals["human"] += 1

    contractions = ["don't", "can't", "won't", "it's", "that's", "i'm", "you're", "they're", "we're", "i've", "you've", "haven't", "hasn't", "wasn't", "wouldn't", "couldn't", "shouldn't", "isn't", "aren't", "there's", "what's", "let's", "here's", "didn't", "doesn't", "ain't"]
    signals["total_checks"] += 1
    contraction_count = sum(1 for c in contractions if c in text.lower())
    if contraction_count > 3:
        signals["human"] += 1
    elif contraction_count == 0 and total > 50:
        signals["ai"] += 1

    filler = ["basically", "actually", "honestly", "literally", "honestly", "anyway", "well ", "you know", "i think", "the thing is", "i feel like", "sort of", "kind of"]
    signals["total_checks"] += 1
    filler_count = sum(1 for f in filler if f in text.lower())
    if filler_count > 2:
        signals["human"] += 1
    elif filler_count == 0 and total > 80:
        signals["ai"] += 1

    transition_words = ["however", "furthermore", "moreover", "consequently", "nevertheless", "additionally", "in addition", "therefore", "thus", "notably"]
    signals["total_checks"] += 1
    transition_count = sum(1 for t in transition_words if t in text.lower())
    if transition_count > 4:
        signals["ai"] += 1

    ai_score = (signals["ai"] / max(signals["total_checks"], 1)) * 100
    human_score = (signals["human"] / max(signals["total_checks"], 1)) * 100
    total_sig = ai_score + human_score
    if total_sig > 0:
        ai_pct = round((ai_score / total_sig) * 100, 1)
        human_pct = round((human_score / total_sig) * 100, 1)
    else:
        ai_pct = human_pct = 50

    return {
        "ai_score": ai_pct,
        "human_score": human_pct,
        "confidence": "medium",
        "models": [{"model": "Heuristic Analysis", "ai_score": ai_pct, "human_score": human_pct}],
    }

async def detect_ai(text: str) -> dict:
    result = await detect_with_llm(text)
    if result:
        return result
    return heuristic_detect(text)
