from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

# Home page
@app.get("/", response_class=HTMLResponse)
async def index():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Home</title>
    </head>
    <body>
        <h1>Welcome to the Home Page</h1>
        <a href="/signup">Go to Signup</a>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Signup page
@app.get("/signup", response_class=HTMLResponse)
async def signup():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Signup</title>
    </head>
    <body>
        <h1>Signup Page</h1>
        <form action="/signup" method="post">
            <label>Username:</label><br>
            <input type="text" name="username"><br>
            <label>Password:</label><br>
            <input type="password" name="password"><br>
            <input type="submit" value="Signup">
        </form>
        <a href="/">Back to Home</a>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Optional /ping route
@app.get("/ping")
async def ping():
    return JSONResponse({"status": "ok"})
