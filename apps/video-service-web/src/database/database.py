from sqlmodel import create_engine
from sqlalchemy import text
from database.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=True,         # SQL logs (for debugging)
    pool_pre_ping=True # Recycle dead connections
)

def ping_db() -> bool:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        return result.scalar() == 1