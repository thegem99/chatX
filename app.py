from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="templates")

API_BASE = "https://web-production-7d78e.up.railway.app"

sessions = {}

# ---------------------- HOME ----------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

# ---------------------- SIGNUP ----------------------
@app.post("/signup")
async def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE}/users/signup", json={
            "username": username,
            "email": email,
            "password": password
        })

    if res.status_code in [200, 201]:
        return RedirectResponse("/", status_code=303)

    return HTMLResponse(f"Signup failed: {res.text}")

# ---------------------- LOGIN ----------------------
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE}/users/login", json={
            "username": username,
            "password": password
        })

    if res.status_code == 200:
        token = res.json().get("token")
        sessions[username] = token
        return RedirectResponse(f"/app/{username}", status_code=303)

    return HTMLResponse(f"Login failed: {res.text}")

# ---------------------- APP PAGE ----------------------
@app.get("/app/{username}", response_class=HTMLResponse)
async def app_page(request: Request, username: str):
    if username not in sessions:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={"username": username}
    )

# ---------------------- SEARCH ----------------------
@app.get("/search/{username}/{query}")
async def search(username: str, query: str):
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
        return {"msg": res.text}

# ---------------------- CONTACTS ----------------------
@app.get("/contacts/{username}")
async def contacts(username: str):
    token = sessions.get(username)
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/users/contacts", headers=headers)
        return res.json()

# ---------------------- CHAT ----------------------
@app.get("/chat/{username}/{contact_id}")
async def get_chat(username: str, contact_id: str):
    token = sessions.get(username)
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/chat/{contact_id}", headers=headers)
        return res.json()

@app.post("/chat/{username}/{contact_id}")
async def send_chat(username: str, contact_id: str, message: str = Form(...)):
    token = sessions.get(username)
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{API_BASE}/chat/{contact_id}",
            headers=headers,
            json={"message": message}
        )
        return {"msg": res.text}
