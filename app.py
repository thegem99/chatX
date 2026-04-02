from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx

API_BASE = "https://web-production-7d78e.up.railway.app"  # Your Railway API

app = FastAPI(title="ChatX Frontend")

# -------------------
# Frontend Routes
# -------------------

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h1>ChatX</h1>
    <a href='/signup'>Signup</a> | <a href='/login'>Login</a>
    """

@app.get("/signup", response_class=HTMLResponse)
async def signup_form():
    return """
    <h2>Signup</h2>
    <form action="/signup" method="post">
        Username: <input name="username" required><br>
        Email: <input name="email" type="email" required><br>
        Password: <input type="password" name="password" required><br>
        <button type="submit">Signup</button>
    </form>
    <a href='/login'>Login</a>
    """

@app.post("/signup", response_class=HTMLResponse)
async def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/users/signup", json={
            "username": username,
            "email": email,
            "password": password
        })
    if resp.status_code != 200:
        return f"<h3>Error: {resp.json().get('detail')}</h3><a href='/signup'>Try again</a>"
    return RedirectResponse("/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_form():
    return """
    <h2>Login</h2>
    <form action="/login" method="post">
        Email: <input name="email" type="email" required><br>
        Password: <input type="password" name="password" required><br>
        <button type="submit">Login</button>
    </form>
    <a href='/signup'>Signup</a>
    """

@app.post("/login", response_class=HTMLResponse)
async def login(email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/users/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        return "<h3>Invalid credentials!</h3><a href='/login'>Try again</a>"
    token = resp.json()["token"]
    return RedirectResponse(f"/chat?token={token}", status_code=302)

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(token: str):
    async with httpx.AsyncClient() as client:
        # Fetch all users to start chat
        users_resp = await client.get(f"{API_BASE}/users/search?username=", headers={"Authorization": f"Bearer {token}"})
        users = users_resp.json() if users_resp.status_code == 200 else []
    user_list = "".join([f"<option value='{u['_id']}'>{u['username']}</option>" for u in users])
    return f"""
    <h2>Chat Room</h2>
    <form action="/chat/send" method="post">
        <input type="hidden" name="token" value="{token}">
        Send To: <select name="receiver_id">{user_list}</select><br>
        Message: <input name="message" required>
        <button type="submit">Send</button>
    </form>
    <a href='/'>Home</a>
    """

@app.post("/chat/send", response_class=HTMLResponse)
async def chat_send(token: str = Form(...), receiver_id: str = Form(...), message: str = Form(...)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/chat/send",
                                 json={"receiver_id": receiver_id, "message": message},
                                 headers={"Authorization": f"Bearer {token}"})
    if resp.status_code != 200:
        return f"<h3>Error sending message: {resp.json().get('detail')}</h3>"
    return RedirectResponse(f"/chat?token={token}", status_code=302)
