from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx

API_BASE = "https://web-production-7d78e.up.railway.app"  # Your Railway API

app = FastAPI(title="ChatX Frontend")

# -------------------
# CSS Styles
# -------------------
CSS_STYLES = """
<style>
body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; color: #333; }
h1, h2 { text-align: center; color: #4a76a8; }
a { color: #4a76a8; text-decoration: none; margin: 5px; }
a:hover { text-decoration: underline; }
form { background: white; padding: 20px; margin: auto; max-width: 400px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
input, select, button { width: 100%; padding: 10px; margin: 8px 0; border-radius: 5px; border: 1px solid #ccc; }
button { background-color: #4a76a8; color: white; border: none; cursor: pointer; font-weight: bold; }
button:hover { background-color: #3b5f8d; }
.chat-box { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.message { padding: 8px 12px; margin: 5px 0; border-radius: 15px; max-width: 70%; }
.sent { background: #dcf8c6; align-self: flex-end; text-align: right; }
.received { background: #fff; border: 1px solid #eee; align-self: flex-start; text-align: left; }
.messages { display: flex; flex-direction: column; }
</style>
"""

# -------------------
# Frontend Routes
# -------------------
@app.get("/", response_class=HTMLResponse)
async def home():
    return f"""
    {CSS_STYLES}
    <h1>ChatX</h1>
    <div style="text-align:center;">
        <a href='/signup'>Signup</a> | <a href='/login'>Login</a>
    </div>
    """

@app.get("/signup", response_class=HTMLResponse)
async def signup_form():
    return f"""
    {CSS_STYLES}
    <h2>Signup</h2>
    <form action="/signup" method="post">
        Username: <input name="username" required>
        Email: <input name="email" type="email" required>
        Password: <input type="password" name="password" required>
        <button type="submit">Signup</button>
    </form>
    <div style="text-align:center;"><a href='/login'>Login</a></div>
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
        return f"{CSS_STYLES}<h3>Error: {resp.json().get('detail')}</h3><a href='/signup'>Try again</a>"
    return RedirectResponse("/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_form():
    return f"""
    {CSS_STYLES}
    <h2>Login</h2>
    <form action="/login" method="post">
        Email: <input name="email" type="email" required>
        Password: <input type="password" name="password" required>
        <button type="submit">Login</button>
    </form>
    <div style="text-align:center;"><a href='/signup'>Signup</a></div>
    """

@app.post("/login", response_class=HTMLResponse)
async def login(email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/users/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        return f"{CSS_STYLES}<h3>Invalid credentials!</h3><a href='/login'>Try again</a>"
    token = resp.json()["token"]
    return RedirectResponse(f"/chat?token={token}", status_code=302)

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(token: str):
    async with httpx.AsyncClient() as client:
        users_resp = await client.get(f"{API_BASE}/users/search?username=", headers={"Authorization": f"Bearer {token}"})
        users = users_resp.json() if users_resp.status_code == 200 else []
    user_options = "".join([f"<option value='{u['_id']}'>{u['username']}</option>" for u in users])
    return f"""
    {CSS_STYLES}
    <h2>Chat Room</h2>
    <div class="chat-box">
        <form action="/chat/send" method="post">
            <input type="hidden" name="token" value="{token}">
            Send To: <select name="receiver_id">{user_options}</select>
            Message: <input name="message" required>
            <button type="submit">Send</button>
        </form>
    </div>
    <div style="text-align:center;"><a href='/'>Home</a></div>
    """
    
@app.post("/chat/send", response_class=HTMLResponse)
async def chat_send(token: str = Form(...), receiver_id: str = Form(...), message: str = Form(...)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/chat/send",
                                 json={"receiver_id": receiver_id, "message": message},
                                 headers={"Authorization": f"Bearer {token}"})
    if resp.status_code != 200:
        return f"{CSS_STYLES}<h3>Error sending message: {resp.json().get('detail')}</h3>"
    return RedirectResponse(f"/chat?token={token}", status_code=302)
