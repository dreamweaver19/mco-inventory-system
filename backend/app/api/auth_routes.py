from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.module_e.auth import create_token
from app.utils.audit import log_login

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

users = {
    "admin": {"password": "admin123", "role": "Admin"},
    "operator": {"password": "operator123", "role": "DataEntry"}
}


# Login page
@router.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Login form submission
@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):

    user = users.get(username)

    if not user:
        log_login(username, "FAILED USER")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid Username"}
        )

    if user["password"] != password:
        log_login(username, "FAILED PASSWORD")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid Password"}
        )

    log_login(username, "SUCCESS")

    token = create_token(username, user["role"])

    response = RedirectResponse(url="/dashboard", status_code=303)

    return response