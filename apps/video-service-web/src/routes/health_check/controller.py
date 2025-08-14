from http.client import HTTPException
from fastapi import APIRouter, status
from shared.http.response import handle_response
from database.database import ping_db
health_check_router = APIRouter(prefix="/health-check")


@health_check_router.get("/")
async def health_check():
    return handle_response(data={"status": "OK"}, status_code=status.HTTP_200_OK)

@health_check_router.get("/db")
def health_check_db():
    try:
        if ping_db():
            return {"status": "ok", "db": "reachable"}
        raise HTTPException(status_code=500, detail="DB ping failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")