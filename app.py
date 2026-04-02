# app.py
from fastapi import FastAPI, Request, Form, HTTPException, Header, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import os

app = FastAPI()

# Serve static files (CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates folder
templates = Jinja2Templates(directory="templates")

# Your API base
API_URL = "https://web-production-7d78e.up.railway.app"

# -----------------------------
# Home redirects to login or dashboard
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def home(token: str = Cookie(None)):
    if token:
        return RedirectResponse("/dashboard")
    return RedirectResponse("/login")

# -----------------------------
# Login
# -----------------------------
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, token: str = Cookie(None)):
    if token:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(response: Response, email: str = Form(...), password: str = Form(...)):
    r = requests.post(f"{API_URL}/users/login", json={"email": email, "password": password})
    if r.status_code != 200:
        return HTMLResponse(f"<h3>Login failed: {r.json()['detail']}</h3><a href='/login'>Try again</a>")
    token = r.json()["token"]
    resp = RedirectResponse("/dashboard", status_code=302)
    resp.set_cookie(key="token", value=token, httponly=True)
    return resp

# -----------------------------
# Signup
# -----------------------------
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup_post(response: Response, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    r = requests.post(f"{API_URL}/users/signup", json={"username": username, "email": email, "password": password})
    if r.status_code != 200:
        return HTMLResponse(f"<h3>Signup failed: {r.json()['detail']}</h3><a href='/signup'>Try again</a>")
    # After signup, auto-login
    r_login = requests.post(f"{API_URL}/users/login", json={"email": email, "password": password})
    token = r_login.json()["token"]
    resp = RedirectResponse("/dashboard", status_code=302)
    resp.set_cookie(key="token", value=token, httponly=True)
    return resp

# -----------------------------
# Logout
# -----------------------------
@app.get("/logout")
async def logout():
    resp = RedirectResponse("/login", status_code=302)
    resp.delete_cookie("token")
    return resp

# -----------------------------
# Dashboard
# -----------------------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, token: str = Cookie(None)):
    if not token:
        return RedirectResponse("/login")
    # Fetch requests count
    r = requests.get(f"{API_URL}/users/me/requests", headers={"Authorization": f"Bearer {token}"})
    requests_count = len(r.json()) if r.status_code == 200 else 0
    return templates.TemplateResponse("dashboard.html", {"request": request, "requests_count": requests_count})

# -----------------------------
# Search Users
# -----------------------------
@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, token: str = Cookie(None), q: str = ""):
    if not token:
        return RedirectResponse("/login")
    r = requests.get(f"{API_URL}/users/search", params={"username": q})
    users = r.json() if r.status_code == 200 else []
    return templates.TemplateResponse("search.html", {"request": request, "users": users, "q": q, "token": token})

@app.post("/send_request/{user_id}")
async def send_request(user_id: str, token: str = Cookie(None)):
    if not token:
        return RedirectResponse("/login")
    requests.post(f"{API_URL}/users/send_request/{user_id}", headers={"Authorization": f"Bearer {token}"})
    return RedirectResponse("/search")

# -----------------------------
# Contact List
# -----------------------------
@app.get("/contacts", response_class=HTMLResponse)
async def contacts_page(request: Request, token: str = Cookie(None)):
    if not token:
        return RedirectResponse("/login")
    r = requests.get(f"{API_URL}/users/me/contacts", headers={"Authorization": f"Bearer {token}"})
    contacts = r.json() if r.status_code == 200 else []
    return templates.TemplateResponse("contacts.html", {"request": request, "contacts": contacts, "token": token})

@app.post("/remove_contact/{user_id}")
async def remove_contact(user_id: str, token: str = Cookie(None)):
    if not token:
        return RedirectResponse("/login")
    requests.post(f"{API_URL}/users/remove_contact/{user_id}", headers={"Authorization": f"Bearer {token}"})
    return RedirectResponse("/contacts")

# -----------------------------
# Chat
# -----------------------------
@app.get("/chat/{user_id}", response_class=HTMLResponse)
async def chat_page(request: Request, user_id: str, token: str = Cookie(None)):
    if not token:
        return RedirectResponse("/login")
    r = requests.get(f"{API_URL}/chat/history/{user_id}", headers={"Authorization": f"Bearer {token}"})
    messages = r.json() if r.status_code == 200 else []
    return templates.TemplateResponse("chat.html", {"request": request, "messages": messages, "chat_with": user_id, "token": token})

@app.post("/chat/{user_id}")
async def send_chat(user_id: str, message: str = Form(...), token: str = Cookie(None)):
    if not token:
        return RedirectResponse("/login")
    requests.post(f"{API_URL}/chat/send", json={"receiver_id": user_id, "message": message}, headers={"Authorization": f"Bearer {token}"})
    return RedirectResponse(f"/chat/{user_id}")
