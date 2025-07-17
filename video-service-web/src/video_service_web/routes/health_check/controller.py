from fastapi import APIRouter

health_check_router = APIRouter(prefix="/health-check")


@health_check_router.get("/")
async def health_check():
    return {"status": "OK"}
