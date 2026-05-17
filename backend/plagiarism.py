import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import httpx
import re
import asyncio
from typing import List
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID, BING_API_KEY

def _extract_grams(text: str, n: int = 5) -> List[str]:
    words = re.findall(r'\w+', text.lower())
    ngrams = set()
    for i in range(len(words) - n + 1):
        ngrams.add(" ".join(words[i:i+n]))
    return list(ngrams)

def _compute_similarity(original_ngrams: set, matches: List[str]) -> float:
    if not original_ngrams:
        return 0.0
    matched_ngrams = set()
    for snippet in matches:
        snippet_words = set(re.findall(r'\w+', snippet.lower()))
        for ngram in original_ngrams:
            ngram_words = set(ngram.split())
            if ngram_words.issubset(snippet_words) or snippet_words.issuperset(ngram_words):
                matched_ngrams.add(ngram)
    return round(len(matched_ngrams) / len(original_ngrams) * 100, 1)

async def search_google(text: str) -> dict:
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return {"source": "google", "matches": [], "error": "Not configured"}
    try:
        query = text[:200].strip().replace("\n", " ")
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "q": query, "num": 5}
        async with httpx.AsyncClient(timeout=10.0) as c:
            resp = await c.get(url, params=params)
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                matches = []
                for item in items:
                    matches.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                    })
                return {"source": "google", "matches": matches}
            else:
                return {"source": "google", "matches": [], "error": str(resp.status_code)}
    except Exception as e:
        return {"source": "google", "matches": [], "error": str(e)}

async def search_bing(text: str) -> dict:
    if not BING_API_KEY:
        return {"source": "bing", "matches": [], "error": "Not configured"}
    try:
        query = text[:200].strip().replace("\n", " ")
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
        params = {"q": query, "count": 5}
        async with httpx.AsyncClient(timeout=10.0) as c:
            resp = await c.get(url, headers=headers, params=params)
            if resp.status_code == 200:
                items = resp.json().get("webPages", {}).get("value", [])
                matches = []
                for item in items:
                    matches.append({
                        "title": item.get("name", ""),
                        "link": item.get("url", ""),
                        "snippet": item.get("snippet", ""),
                    })
                return {"source": "bing", "matches": matches}
            else:
                return {"source": "bing", "matches": [], "error": str(resp.status_code)}
    except Exception as e:
        return {"source": "bing", "matches": [], "error": str(e)}

async def search_duckduckgo(text: str) -> dict:
    try:
        query = text[:200].strip().replace("\n", " ")
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
        async with httpx.AsyncClient(timeout=10.0) as c:
            resp = await c.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                matches = []
                topics = data.get("RelatedTopics", [])
                for t in topics[:5]:
                    if "Text" in t and "FirstURL" in t:
                        matches.append({
                            "title": t.get("Text", "")[:100],
                            "link": t.get("FirstURL", ""),
                            "snippet": t.get("Text", ""),
                        })
                results = data.get("Results", [])
                for r in results[:5]:
                    matches.append({
                        "title": r.get("Text", "")[:100],
                        "link": r.get("FirstURL", ""),
                        "snippet": r.get("Text", ""),
                    })
                return {"source": "duckduckgo", "matches": matches}
            else:
                return {"source": "duckduckgo", "matches": [], "error": str(resp.status_code)}
    except Exception as e:
        return {"source": "duckduckgo", "matches": [], "error": str(e)}

async def check_plagiarism(text: str) -> dict:
    gram_16 = set(_extract_grams(text, 16))
    gram_8 = set(_extract_grams(text, 8))

    google_res, bing_res, ddg_res = await asyncio.gather(
        search_google(text),
        search_bing(text),
        search_duckduckgo(text),
    )

    all_matches = []
    sources_used = []

    for res in [google_res, bing_res, ddg_res]:
        if "matches" in res and res["matches"]:
            sources_used.append(res["source"])
            for m in res["matches"]:
                m["source"] = res["source"]
                all_matches.append(m)

    deduped = {}
    for m in all_matches:
        key = m.get("link", m.get("title", ""))
        if key not in deduped:
            deduped[key] = m

    final_matches = list(deduped.values())[:15]
    snippets = [m.get("snippet", "") for m in final_matches if m.get("snippet")]
    similarity_16 = _compute_similarity(gram_16, snippets)
    similarity_8 = _compute_similarity(gram_8, snippets)

    plagiarism_score = round((similarity_16 * 0.6 + similarity_8 * 0.4), 1)

    return {
        "plagiarism_score": plagiarism_score,
        "original_score": round(100 - plagiarism_score, 1),
        "matches_found": len(final_matches),
        "sources_used": sources_used,
        "matches": final_matches[:10],
    }
