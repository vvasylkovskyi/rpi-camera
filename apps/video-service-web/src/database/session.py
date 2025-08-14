from fastapi import Depends
from sqlmodel import Session
from database.database import engine

def get_session():
    with Session(engine) as session:
        yield session  # FastAPI will close session automatically