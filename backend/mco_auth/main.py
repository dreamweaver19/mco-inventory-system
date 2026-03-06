from audit import log_login, log_transition
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi import Body
from models import Component
from fastapi.templating import Jinja2Templates
from lifecycle import transition
from auth import create_token
from rbac import require_role
from audit import log_login


components = {}
app = FastAPI()

templates = Jinja2Templates(directory="templates")

users = {
    "admin": {"password": "admin123", "role": "Admin"},
    "operator": {"password": "operator123", "role": "DataEntry"}
}
components = {
    1: {"name": "Trigger Assembly", "state": "Receipt"},
    2: {"name": "Barrel Unit", "state": "Awaiting FFFT"}
}

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
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

@app.post("/component/transition")
def change_state(component_id: int = Body(...), new_state: str = Body(...)):

    component = components.get(component_id)

    if not component:
        return {"error": "Component not found"}

    current_state = component["state"]

    if transition(current_state, new_state):

        component["state"] = new_state

        return {
            "message": "Transition Successful",
            "component": component_id,
            "new_state": new_state
        }

    else:

        return {
            "error": "Invalid State Transition",
            "current_state": current_state
        }
    


@app.post("/component/add")
def add_component(component: Component):

    if component.component_id in components:
        return {"error": "Component already exists"}

    components[component.component_id] = {
        "name": component.name,
        "state": component.state
    }

    return {"message": "Component Added"}
@app.get("/dashboard/admin")
def admin_dashboard(user = Depends(require_role("Admin"))):
    return {"message": "Welcome Admin"}

@app.get("/component/list")
def list_components():

    return components
@app.get("/component/{component_id}")
def get_component(component_id: int):

    component = components.get(component_id)

    if not component:
        return {"error": "Component not found"}

    return component