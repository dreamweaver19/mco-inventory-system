from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import Component

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):

    components = db.query(Component).all()

    component_list = []

    for c in components:
        component_list.append({
            "component_id": c.component_id,
            "name": c.name,
            "state": c.state
        })

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "components": component_list
        }
    )