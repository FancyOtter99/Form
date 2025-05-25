from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
import uuid


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Simple in-memory storage for demo. Use a database for production!
submissions = []

SECRET_KEY = "letmein"  # change this!

@app.post("/submit", response_class=HTMLResponse)
async def submit_form(request: Request, name: str = Form(...), email: str = Form(...), message: str = Form(...)):
    submission_id = str(uuid.uuid4())
    submissions.append({"id": submission_id, "name": name, "email": email, "message": message})
    return templates.TemplateResponse("thanks.html", {"request": request, "name": name})



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


