from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="templates")

API_BASE = "https://web-production-7d78e.up.railway.app"

# Simple in-memory session store (email -> token)
sessions = {}

# ---------------------- LOGIN / SIGNUP ----------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE}/users/signup", json={
            "username": username,
            "email": email,
            "password": password
        })
    if res.status_code in (200, 201):
        return RedirectResponse("/", status_code=303)
    return HTMLResponse(f"Signup failed: {res.text}")

@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
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

# ---------------------- MAIN APP PAGE ----------------------
@app.get("/app/{email}", response_class=HTMLResponse)
async def app_page(request: Request, email: str):
    token = sessions.get(email)
    if not token:
        return RedirectResponse("/", status_code=303)
    # Pass email as username in templates
    return templates.TemplateResponse("app.html", {"request": request, "username": email})

# ---------------------- SEARCH USERS ----------------------
@app.get("/search/{email}/{query}")
async def search_user(email: str, query: str):
    token = sessions.get(email)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/users/search/{query}", headers=headers)
        return res.json()

# ---------------------- SEND REQUEST ----------------------
@app.post("/send_request/{email}/{receiver_id}")
async def send_request(email: str, receiver_id: str):
    token = sessions.get(email)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE}/users/send_request/{receiver_id}", headers=headers)
        return res.text

# ---------------------- GET CONTACTS ----------------------
@app.get("/contacts/{email}")
async def get_contacts(email: str):
    token = sessions.get(email)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/users/contacts", headers=headers)
        return res.json()

# ---------------------- GET / SEND MESSAGES ----------------------
@app.get("/chat/{email}/{contact_id}")
async def get_messages(email: str, contact_id: str):
    token = sessions.get(email)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/chat/{contact_id}", headers=headers)
        return res.json()

@app.post("/chat/{email}/{contact_id}")
async def send_message(email: str, contact_id: str, message: str = Form(...)):
    token = sessions.get(email)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE}/chat/{contact_id}", headers=headers, json={"message": message})
        return res.text
