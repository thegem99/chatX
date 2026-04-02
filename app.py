from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
import os

app = FastAPI()

# Correct templates path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

API_BASE = "https://web-production-7d78e.up.railway.app"

# Simple in-memory session store (username -> token)
sessions = {}

# ---------------------- LOGIN / SIGNUP ----------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE}/users/signup", json={
            "username": username, "email": email, "password": password
        })
    if res.status_code in (200, 201):
        return RedirectResponse("/", status_code=303)
    return HTMLResponse(f"Signup failed: {res.text}")

@app.post("/login")
async def login(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE}/users/login", json={
            "username": username, "email": email, "password": password
        })
    if res.status_code == 200:
        token = res.json().get("token")
        sessions[username] = token
        return RedirectResponse(f"/app/{username}", status_code=303)
    return HTMLResponse(f"Login failed: {res.text}")

# ---------------------- MAIN APP PAGE ----------------------
@app.get("/app/{username}", response_class=HTMLResponse)
async def app_page(request: Request, username: str):
    token = sessions.get(username)
    if not token:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("app.html", {"request": request, "username": username})
