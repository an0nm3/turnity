import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import re

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

    filler = ["basically", "actually", "honestly", "literally", "anyway", "well ", "you know", "i think", "the thing is", "i feel like", "sort of", "kind of"]
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
    return heuristic_detect(text)