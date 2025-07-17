from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from video_service_web.routes.routes import create_router
from video_service_web.logger.logger import Logger

logger = Logger("main")

app = FastAPI(title="Video Service Web API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(create_router())
