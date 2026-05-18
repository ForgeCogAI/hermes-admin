import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATA_DIR = os.environ.get("ADMIN_DATA_DIR", os.path.expanduser("~/.hermes-admin"))
os.makedirs(DATA_DIR, exist_ok=True)

DB_URL = f"sqlite:///{DATA_DIR}/admin.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
