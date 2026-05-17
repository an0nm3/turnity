# AIDetect - Free AI & Plagiarism Checker

Targeting **85% accuracy** for AI detection using an ensemble of open-source models. Plagiarism detection via aggregated free search APIs. Entirely free to run.

## Architecture

```
User → Render (free) → FastAPI → Hugging Face Inference API (AI detection)
                              → Google/Bing/DuckDuckGo APIs (plagiarism)
                              → Supabase (auth + DB)
```

## Setup (5 minutes, $0)

### 1. Supabase (Auth + Database)

1. Go to [supabase.com](https://supabase.com) → "Start your project"
2. Free tier (500MB DB, 50k users)
3. Copy your **Project URL** and **anon key** from Settings → API
4. Go to SQL Editor → paste contents of `supabase_schema.sql` → Run

### 2. Hugging Face (AI Detection)

1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) → New token → Copy
2. Free tier: 30k input chars/minute

### 3. Google Custom Search (Plagiarism - 100 free queries/day)

1. [console.cloud.google.com](https://console.cloud.google.com) → Create project
2. Enable "Custom Search API" → Create API key
3. [cse.google.com](https://cse.google.com) → "Add" → Any sites → Get CX ID

### 4. Bing Search (1000 free queries/month)

1. [portal.azure.com](https://portal.azure.com) → Create "Bing Search v7" resource (Free F1 tier)
2. Get API key

### 5. Deploy on Render (free)

1. Push to GitHub
2. Render → New Web Service → Connect repo
3. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env.example`
5. Deploy

### 6. Or run locally

```bash
git clone ...
cd ai-plagiarism-checker
cp .env.example .env  # fill in your keys
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

## How to get 85% AI detection

The ensemble averages output from:
- **roberta-base-openai-detector** — OpenAI's detector (GPT-2/3 optimized)
- **Hello-SimpleAI/chatgpt-detector-roberta** — ChatGPT fine-tuned RoBERTa

For higher accuracy, add more models to `AI_MODELS` in `backend/config.py`.

## Limits (free tier)

| Service | Daily limit |
|---|---|
| AI Checks | 50 per user (capped in-app) |
| Hugging Face API | ~30k chars/min |
| Google CSE | 100 queries/day |
| Bing | ~33 queries/day |
