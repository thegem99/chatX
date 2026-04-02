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
form { background: white; padding: 20px; margin: 50px auto; max-width: 400px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
input, select, button { width: 100%; padding: 10px; margin: 8px 0; border-radius: 5px; border: 1px solid #ccc; }
button { background-color: #4a76a8; color: white; border: none; cursor: pointer; font-weight: bold; }
button:hover { background-color: #3b5f8d; }
.bottom-link { text-align: center; margin-top: 15px; font-size: 0.9em; }
</style>
"""

# -------------------
# Routes
# -------------------
@app.get("/", response_class=HTMLResponse)
async def login_form():
    return f"""
    {CSS_STYLES}
    <h2>Login to ChatX</h2>
    <form action="/login" method="post">
        Email: <input name="email" type="email" required>
        Password: <input type="password" name="password" required>
        <button type="submit">Login</button>
    </form>
    <div class="bottom-link">
        Don't have an account? <a href='/signup'>Create account / Signup here</a>
    </div>
    """

@app.get("/signup", response_class=HTMLResponse)
async def signup_form():
    return f"""
    {CSS_STYLES}
    <h2>Create Your Account</h2>
    <form action="/signup" method="post">
        Username: <input name="username" required>
        Email: <input name="email" type="email" required>
        Password: <input type="password" name="password" required>
        <button type="submit">Signup</button>
    </form>
    <div class="bottom-link">
        Already have an account? <a href='/'>Login here</a>
    </div>
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
    return RedirectResponse("/", status_code=302)

@app.post("/login", response_class=HTMLResponse)
async def login(email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/users/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        return f"{CSS_STYLES}<h3>Invalid credentials!</h3><a href='/'>Try again</a>"
    token = resp.json()["token"]
    return RedirectResponse(f"/chat?token={token}", status_code=302)
