from fastapi import FastAPI
import uvicorn
from query.router import router as query_router

app = FastAPI(
    title="Fast API service",
    description="Object detection from rtsp video stream",
    version="0.0.1",
    license_info={
        "name": "MIT",
    },
)

app.include_router(query_router)

if __name__== "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)