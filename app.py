from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx

API_BASE = "https://web-production-7d78e.up.railway.app"

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h1>ChatX Frontend</h1>
    <a href='/signup'>Signup</a> | <a href='/login'>Login</a>
    """

@app.get("/signup", response_class=HTMLResponse)
async def signup_form():
    return """
    <h2>Signup</h2>
    <form action="/signup" method="post">
      Username: <input name="username" required><br>
      Password: <input type="password" name="password" required><br>
      <button type="submit">Signup</button>
    </form>
    <a href='/login'>Login</a>
    """

@app.post("/signup", response_class=HTMLResponse)
async def signup(username: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/api/signup", data={"username": username, "password": password})
    if resp.status_code != 200:
        return f"<h3>Error: {resp.json().get('error')}</h3><a href='/signup'>Try again</a>"
    return RedirectResponse("/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_form():
    return """
    <h2>Login</h2>
    <form action="/login" method="post">
      Username: <input name="username" required><br>
      Password: <input type="password" name="password" required><br>
      <button type="submit">Login</button>
    </form>
    <a href='/signup'>Signup</a>
    """

@app.post("/login", response_class=HTMLResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/api/login", data={"username": username, "password": password})
    if resp.status_code != 200:
        return "<h3>Invalid credentials!</h3><a href='/login'>Try again</a>"
    return RedirectResponse(f"/chat?username={username}", status_code=302)

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(username: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE}/api/messages")
        messages = resp.json() if resp.status_code == 200 else []
    chat_html = "<br>".join([f"<b>{m['username']}:</b> {m['message']}" for m in messages])
    return f"""
    <h2>Chat Room</h2>
    <p>Logged in as: {username}</p>
    <div style='border:1px solid #000; height:200px; overflow:auto; padding:5px;'>{chat_html}</div>
    <form action="/chat" method="post">
      <input type="hidden" name="username" value="{username}">
      <input name="message" placeholder="Type your message..." required>
      <button type="submit">Send</button>
    </form>
    <a href='/'>Home</a>
    """

@app.post("/chat", response_class=HTMLResponse)
async def chat_post(username: str = Form(...), message: str = Form(...)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/api/messages", data={"username": username, "message": message})
    return RedirectResponse(f"/chat?username={username}", status_code=302)
