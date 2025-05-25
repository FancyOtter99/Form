from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Simple in-memory storage for demo. Use a database for production!
submissions = []

SECRET_KEY = "letmein"  # change this!

@app.post("/submit", response_class=HTMLResponse)
async def submit_form(request: Request, name: str = Form(...), email: str = Form(...), message: str = Form(...)):
    submissions.append({"name": name, "email": email, "message": message})
    return templates.TemplateResponse("thanks.html", {"request": request, "name": name})


@app.get("/submissions", response_class=HTMLResponse)
async def get_submissions(request: Request, key: str):
    if key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return templates.TemplateResponse("submissions.html", {"request": request, "submissions": submissions})
