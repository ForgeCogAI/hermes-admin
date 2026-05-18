from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: Optional[str]
    email: Optional[str]
    assigned_port: int
    data_dir: str
    config_json: str
    is_active: bool
    created_at: datetime
    container_status: Optional[str] = None

    class Config:
        from_attributes = True


class ConfigUpdate(BaseModel):
    config_json: str


class TemplateResponse(BaseModel):
    config_json: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
