from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100))
    email = Column(String(100))
    assigned_port = Column(Integer, unique=True, nullable=False)
    data_dir = Column(String(500), nullable=False)
    config_json = Column(Text, default="{}")  # user config overrides (JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class AdminTemplate(Base):
    __tablename__ = "admin_template"

    id = Column(Integer, primary_key=True)
    config_json = Column(Text, default="{}")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
