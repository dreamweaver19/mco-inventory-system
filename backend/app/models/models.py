from sqlalchemy import Column, Integer, String
from app.database.base import Base
from pydantic import BaseModel


# COMPONENT TABLE
class Component(Base):
    __tablename__ = "components"

    component_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    state = Column(String)


# COMPONENT REQUEST SCHEMA
class ComponentCreate(BaseModel):
    component_id: int
    name: str
    state: str


# LIFECYCLE LOG TABLE
class LifecycleLog(Base):
    __tablename__ = "lifecycle_logs"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer)
    old_state = Column(String)
    new_state = Column(String)