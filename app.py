from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()

# ✅ Correct template initialization
templates = Jinja2Templates(directory="templates")

API_BASE = "https://web-production-7d78e.up.railway.app"

# Simple in-memory session store
sessions = {}

# ---------------------- HOME ----------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        return HTMLResponse(f"Template error: {str(e)}")


# ---------------------- SIGNUP ----------------------
@app.post("/signup")
async def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{API_BASE}/users/signup",
                json={"username": username, "email": email, "password": password}
            )

        if res.status_code in [200, 201]:
            return RedirectResponse("/", status_code=303)

        return HTMLResponse(f"Signup failed: {res.text}")

    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}")


# ---------------------- LOGIN ----------------------
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{API_BASE}/users/login",
                json={"username": username, "password": password}
            )

        if res.status_code == 200:
            data = res.json()
            token = data.get("token")

            if not token:
                return HTMLResponse("Login failed: No token received")

            sessions[username] = token
            return RedirectResponse(f"/app/{username}", status_code=303)

        return HTMLResponse(f"Login failed: {res.text}")

    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}")


# ---------------------- MAIN APP ----------------------
@app.get("/app/{username}", response_class=HTMLResponse)
async def app_page(request: Request, username: str):
    token = sessions.get(username)

    if not token:
        return RedirectResponse("/", status_code=303)

    try:
        return templates.TemplateResponse(
            "app.html",
            {"request": request, "username": username}
        )
    except Exception as e:
        return HTMLResponse(f"Template error: {str(e)}")


# ---------------------- SEARCH USERS ----------------------
@app.get("/search/{username}/{query}")
async def search_user(username: str, query: str):
    token = sessions.get(username)

    if not token:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/users/search/{query}", headers=headers)

    try:
        return res.json()
    except:
        return {"error": res.text}


# ---------------------- SEND REQUEST ----------------------
@app.post("/send_request/{username}/{receiver_id}")
async def send_request(username: str, receiver_id: str):
    token = sessions.get(username)

    if not token:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{API_BASE}/users/send_request/{receiver_id}",
            headers=headers
        )

    return {"response": res.text}


# ---------------------- GET CONTACTS ----------------------
@app.get("/contacts/{username}")
async def get_contacts(username: str):
    token = sessions.get(username)

    if not token:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/users/contacts", headers=headers)

    try:
        return res.json()
    except:
        return {"error": res.text}


# ---------------------- GET MESSAGES ----------------------
@app.get("/chat/{username}/{contact_id}")
async def get_messages(username: str, contact_id: str):
    token = sessions.get(username)

    if not token:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/chat/{contact_id}", headers=headers)

    try:
        return res.json()
    except:
        return {"error": res.text}


# ---------------------- SEND MESSAGE ----------------------
@app.post("/chat/{username}/{contact_id}")
async def send_message(username: str, contact_id: str, message: str = Form(...)):
    token = sessions.get(username)

    if not token:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{API_BASE}/chat/{contact_id}",
            headers=headers,
            json={"message": message}
        )

    return {"response": res.text}
