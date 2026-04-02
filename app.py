from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="templates")

API_BASE = "https://web-production-7d78e.up.railway.app"

# Simple in-memory session store (username -> token)
sessions = {}

# ---------------------- LOGIN / SIGNUP ----------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/signup")
async def signup(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE}/users/signup", json={
            "username": username, "email": email, "password": password
        })
    if res.status_code == 200 or res.status_code == 201:
        return RedirectResponse("/", status_code=303)
    return HTMLResponse(f"Signup failed: {res.text}")

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE}/users/login", json={
            "username": username, "password": password
        })
        if res.status_code == 200:
            token = res.json()["token"]
            sessions[username] = token
            response = RedirectResponse(f"/app/{username}", status_code=303)
            return response
        return HTMLResponse(f"Login failed: {res.text}")

# ---------------------- MAIN APP PAGE ----------------------
@app.get("/app/{username}", response_class=HTMLResponse)
async def app_page(request: Request, username: str):
    token = sessions.get(username)
    if not token:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("app.html", {"request": request, "username": username})

# ---------------------- SEARCH USERS ----------------------
@app.get("/search/{username}/{query}")
async def search_user(username: str, query: str):
    token = sessions.get(username)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/users/search/{query}", headers=headers)
        return res.json()

# ---------------------- SEND REQUEST ----------------------
@app.post("/send_request/{username}/{receiver_id}")
async def send_request(username: str, receiver_id: str):
    token = sessions.get(username)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE}/users/send_request/{receiver_id}", headers=headers)
        return res.text

# ---------------------- GET CONTACTS ----------------------
@app.get("/contacts/{username}")
async def get_contacts(username: str):
    token = sessions.get(username)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/users/contacts", headers=headers)
        return res.json()

# ---------------------- GET / SEND MESSAGES ----------------------
@app.get("/chat/{username}/{contact_id}")
async def get_messages(username: str, contact_id: str):
    token = sessions.get(username)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/chat/{contact_id}", headers=headers)
        return res.json()

@app.post("/chat/{username}/{contact_id}")
async def send_message(username: str, contact_id: str, message: str = Form(...)):
    token = sessions.get(username)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE}/chat/{contact_id}", headers=headers, json={"message": message})
        return res.text
