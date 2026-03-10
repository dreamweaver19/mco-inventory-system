from fastapi import APIRouter, Form
from app.services.module_e.auth import create_token
from app.utils.audit import log_login

router = APIRouter()

users = {
    "admin": {"password": "admin123", "role": "Admin"},
    "operator": {"password": "operator123", "role": "DataEntry"}
}

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):

    user = users.get(username)

    if not user:
        log_login(username, "FAILED USER")
        return {"message": "Invalid Username"}

    if user["password"] != password:
        log_login(username, "FAILED PASSWORD")
        return {"message": "Invalid Password"}

    log_login(username, "SUCCESS")

    token = create_token(username, user["role"])

    return {
        "message": "Login Successful",
        "token": token,
        "role": user["role"]
    }