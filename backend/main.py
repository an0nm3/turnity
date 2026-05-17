from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import json
import asyncio
import math
from pathlib import Path

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auth import signup, login, get_user
from ai_detector import detect_ai
from plagiarism import check_plagiarism
from database import save_report, get_user_reports, get_report

app = FastAPI(title="AIDetect - AI & Plagiarism Checker")

STATIC_DIR = Path(__file__).parent.parent / "static"
TEMPLATE_DIR = Path(__file__).parent / "templates"
os.makedirs(STATIC_DIR / "css", exist_ok=True)
os.makedirs(STATIC_DIR / "js", exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        return None
    user = await get_user(credentials.credentials)
    return user

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/api/signup")
async def api_signup(email: str = Form(...), password: str = Form(...)):
    if len(password) < 6:
        return JSONResponse({"success": False, "error": "Password must be at least 6 characters"}, status_code=400)
    result = await signup(email, password)
    if result["success"]:
        return {"success": True}
    return JSONResponse({"success": False, "error": result.get("error", "Signup failed")}, status_code=400)

@app.post("/api/login")
async def api_login(email: str = Form(...), password: str = Form(...)):
    result = await login(email, password)
    if result["success"]:
        return {"success": True, "access_token": result["access_token"], "user_id": result["user_id"], "email": result["email"]}
    return JSONResponse({"success": False, "error": "Invalid credentials"}, status_code=401)

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/api/check")
async def api_check(
    request: Request,
    text: str = Form(...),
    title: str = Form(""),
):
    body = await request.body()
    token = None
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = json.loads(body)
        text = data.get("text", text)
        title = data.get("title", title)
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    else:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    user = await get_user(token) if token else None

    if len(text) < 50:
        return JSONResponse({"success": False, "error": "Text must be at least 50 characters"}, status_code=400)
    if len(text) > 10000:
        return JSONResponse({"success": False, "error": "Text must be under 10,000 characters"}, status_code=400)

    ai_task = detect_ai(text)
    plag_task = check_plagiarism(text)

    ai_result, plag_result = await asyncio.gather(ai_task, plag_task)

    result = {
        "ai_detection": ai_result,
        "plagiarism": plag_result,
        "text_length": len(text),
        "text_preview": text[:300],
    }

    report_id = await save_report(user.id, text, title, result) if user else None
    result["report_id"] = report_id

    return {"success": True, "result": result}

@app.get("/api/reports")
async def api_reports(request: Request):
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse({"reports": []})
    user = await get_user(auth_header[7:])
    if not user:
        return JSONResponse({"reports": []})
    reports = await get_user_reports(user.id)
    return {"reports": reports}

@app.get("/report/{report_id}")
async def report_page(request: Request, report_id: str):
    return templates.TemplateResponse("report.html", {"request": request, "report_id": report_id})

@app.get("/api/report/{report_id}")
async def api_report(report_id: str, request: Request):
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await get_user(auth_header[7:])
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    report = await get_report(report_id, user.id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
