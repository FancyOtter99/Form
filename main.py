from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
from fastapi.responses import RedirectResponse
import uuid
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yr06dt0v.live.codepad.app"],  # or ["*"] for testing
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# Simple in-memory storage for demo. Use a database for production!
submissions = []
active_sessions = {}
SECRET_KEY = "letmein"  # change this!
SESSION_COOKIE_NAME = "session_token"


# Example allowed users - replace with your actual list or DB lookup
ALLOWED_USERS = {
    "admin": "letmein",
    "fancyotter": "otter123",
    "guest": "guestpass"
}

@app.get("/thanks", response_class=HTMLResponse)
async def thanks(request: Request):
    return templates.TemplateResponse("thanks.html", {"request": request})



@app.post("/login")
async def login(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    print("Received:", username, password)
    print("Known users:", ALLOWED_USERS)  # <---- fix here

    if username in ALLOWED_USERS and ALLOWED_USERS[username] == password:
        session_token = str(uuid.uuid4())
        active_sessions[session_token] = username

        print("Generated session_token:", session_token)

        response = JSONResponse(content={"success": True})
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_token,
            httponly=True,
            secure=True,
            samesite="None"
        )
        return response
    else:
        print("Invalid login attempt")
        return JSONResponse(content={"success": False, "message": "Invalid credentials."}, status_code=401)



@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    print("Session token:", session_token)
    if not session_token or session_token not in active_sessions:
        return RedirectResponse(url="/", status_code=302)

    username = active_sessions[session_token]
    return templates.TemplateResponse("admin.html", {"request": request, "username": username})


@app.get("/logout")
async def logout(request: Request):
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if session_token and session_token in active_sessions:
        del active_sessions[session_token]

    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    return response





@app.post("/submit")
async def submit_form(request: Request, name: str = Form(...), email: str = Form(...), message: str = Form(...)):
    submission_id = str(uuid.uuid4())
    submissions.append({"id": submission_id, "name": name, "email": email, "message": message})
    return RedirectResponse(url=f"/thanks?name={name}", status_code=303)




@app.get("/submissions", response_class=HTMLResponse)
async def show_submissions(request: Request, key: str):
    if key != "letmein":
        return HTMLResponse(content="Unauthorized", status_code=401)
    return templates.TemplateResponse("submissions.html", {"request": request, "submissions": submissions, "key": key})


@app.post("/delete_submission")
async def delete_submission(submission_id: str = Form(...), key: str = Form(...)):
    global submissions
    submissions = [s for s in submissions if s["id"] != submission_id]
    return RedirectResponse(url=f"/submissions?key={key}", status_code=303)


