from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
import os

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

API_BASE = "https://web-production-7d78e.up.railway.app"

# In-memory session store: email -> token
sessions = {}

# ---------------------- HOME / LOGIN PAGE ----------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ---------------------- SIGNUP PAGE ----------------------
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE}/users/signup", json={
            "username": username,
            "email": email,
            "password": password
        })
    if res.status_code in (200, 201):
        return RedirectResponse("/", status_code=303)
    return HTMLResponse(f"Signup failed: {res.text}")

# ---------------------- LOGIN HANDLER ----------------------
@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE}/users/login", json={
            "email": email,
            "password": password
        })
    if res.status_code == 200:
        token = res.json().get("token")
        sessions[email] = token
        return RedirectResponse(f"/app/{email}", status_code=303)
    return HTMLResponse(f"Login failed: {res.text}")

# ---------------------- MAIN APP ----------------------
@app.get("/app/{email}", response_class=HTMLResponse)
async def app_page(request: Request, email: str):
    token = sessions.get(email)
    if not token:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("app.html", {"request": request, "username": email})
