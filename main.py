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
async def login(username: str = Form(...), password: str = Form(...)):
    if username in ALLOWED_USERS and ALLOWED_USERS[username] == password:
        # Generate a session token
        session_token = str(uuid.uuid4())
        active_sessions[session_token] = username

        # Create the response and set the cookie
        response = JSONResponse(content={"success": True, "message": f"Welcome {username}!"})
        response.set_cookie(key=SESSION_COOKIE_NAME, value=session_token, httponly=True)

        return response
    else:
        return JSONResponse(
            content={"success": False, "message": "Invalid username or password."},
            status_code=status.HTTP_401_UNAUTHORIZED
        )


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_token or session_token not in active_sessions:
        return RedirectResponse(url="/", status_code=302)

    username = active_sessions[session_token]
    return templates.TemplateResponse("admin.html", {"request": request, "username": username})




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


