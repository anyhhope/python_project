from fastapi import FastAPI

from app.api import router

app = FastAPI(
    title="Fast API service",
    description="Object detection from rtsp video stream",
    version="0.0.1",
    license_info={
        "name": "MIT",
    },
)

app.include_router(router)