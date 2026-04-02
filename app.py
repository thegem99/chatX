from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx

API_BASE = "https://web-production-7d78e.up.railway.app"

app = FastAPI(title="ChatX Frontend")

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

# ------------------- Helper -------------------
def check_token_cookie(request: Request):
    token = request.cookies.get("chatx_token")
    return token

# ------------------- Routes -------------------
@app.get("/", response_class=HTMLResponse)
async def login_form(request: Request):
    token = check_token_cookie(request)
    if token:
        # Already logged in, redirect to chat
        return RedirectResponse(f"/chat?token={token}")
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
async def signup_form(request: Request):
    token = check_token_cookie(request)
    if token:
        return RedirectResponse(f"/chat?token={token}")
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

@app.post("/signup")
async def signup(response: Response, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/users/signup", json={
            "username": username,
            "email": email,
            "password": password
        })
    if resp.status_code != 200:
        return HTMLResponse(f"{CSS_STYLES}<h3>Error: {resp.json().get('detail')}</h3><a href='/signup'>Try again</a>")
    # Redirect to login page
    return RedirectResponse("/", status_code=302)

@app.post("/login")
async def login(response: Response, email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/users/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        return HTMLResponse(f"{CSS_STYLES}<h3>Invalid credentials!</h3><a href='/'>Try again</a>")
    token = resp.json()["token"]
    # Set token in HTTP-only cookie (persistent across tabs)
    redirect = RedirectResponse(f"/chat?token={token}", status_code=302)
    redirect.set_cookie(key="chatx_token", value=token, httponly=True, max_age=86400*7)  # 7 days
    return redirect

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, token: str = None):
    # Use token from cookie if not passed in URL
    token = token or request.cookies.get("chatx_token")
    if not token:
        return RedirectResponse("/")
    return f"""
    {CSS_STYLES}
    <h2>Welcome to ChatX Chat</h2>
    <p>Your session is active! Token: {token[:10]}... (hidden for security)</p>
    <a href='/logout'>Logout</a>
    """

@app.get("/logout")
async def logout():
    redirect = RedirectResponse("/", status_code=302)
    redirect.delete_cookie("chatx_token")
    return redirect
