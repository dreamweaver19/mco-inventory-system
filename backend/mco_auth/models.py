from pydantic import BaseModel

class Component(BaseModel):
    component_id: int
    name: str
    state: str