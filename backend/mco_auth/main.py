from fastapi import FastAPI, Request, Form, Depends, Body
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import engine, SessionLocal
from models import Base, Component, ComponentCreate, LifecycleLog
from lifecycle import transition
from auth import create_token
from rbac import require_role
from audit import log_login, log_transition

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Create tables in database
Base.metadata.create_all(bind=engine)

# -------------------------
# DATABASE SESSION
# -------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# USERS (Temporary)
# -------------------------

users = {
    "admin": {"password": "admin123", "role": "Admin"},
    "operator": {"password": "operator123", "role": "DataEntry"}
}


# -------------------------
# LOGIN PAGE
# -------------------------

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# -------------------------
# LOGIN API
# -------------------------

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


# -------------------------
# ADD COMPONENT
# -------------------------

@app.post("/component/add")
def add_component(component: ComponentCreate, db: Session = Depends(get_db)):

    existing = db.query(Component).filter(
        Component.component_id == component.component_id
    ).first()

    if existing:
        return {"error": "Component already exists"}

    new_component = Component(
        component_id=component.component_id,
        name=component.name,
        state=component.state
    )

    db.add(new_component)
    db.commit()

    return {"message": "Component Added"}

# -------------------------
# LIST COMPONENTS
# -------------------------

@app.get("/component/list")
def list_components(db: Session = Depends(get_db)):

    components = db.query(Component).all()

    result = []

    for c in components:
        result.append({
            "component_id": c.component_id,
            "name": c.name,
            "state": c.state
        })

    return result


# -------------------------
# GET COMPONENT
# -------------------------

@app.get("/component/{component_id}")
def get_component(component_id: int, db: Session = Depends(get_db)):

    component = db.query(Component).filter(
        Component.component_id == component_id
    ).first()

    if not component:
        return {"error": "Component not found"}

    return {
        "component_id": component.component_id,
        "name": component.name,
        "state": component.state
    }


# -------------------------
# LIFECYCLE TRANSITION
# -------------------------

@app.post("/component/transition")
def change_state(
    component_id: int = Body(...),
    new_state: str = Body(...),
    db: Session = Depends(get_db)
):

    component = db.query(Component).filter(
        Component.component_id == component_id
    ).first()

    if not component:
        return {"error": "Component not found"}

    current_state = component.state

    if transition(current_state, new_state):

        component.state = new_state

        log_entry = LifecycleLog(
            component_id=component_id,
            old_state=current_state,
            new_state=new_state
        )

        db.add(log_entry)
        db.commit()

        log_transition(component_id, current_state, new_state)

        return {
            "message": "Transition Successful",
            "component": component_id,
            "new_state": new_state
        }

    return {
        "error": "Invalid State Transition",
        "current_state": current_state
    }


# -------------------------
# ADMIN DASHBOARD
# -------------------------

@app.get("/dashboard/admin")
def admin_dashboard(user=Depends(require_role("Admin"))):
    return {"message": "Welcome Admin"}


# -------------------------
# DATABASE TEST
# -------------------------

@app.get("/test-db")
def test_db():
    conn = engine.connect()
    return {"message": "Database Connected Successfully"}