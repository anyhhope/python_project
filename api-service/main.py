from fastapi import FastAPI, Depends
import uvicorn
from query.router import router as query_router
from contextlib import asynccontextmanager
from data import db_instance
from config import cfg

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = db_instance
    await db.connect()
    app.state.db = db
    await db.create_table()
    yield
    await db.disconnect()


app = FastAPI(
    title="Fast API service",
    description="Object detection from rtsp video stream",
    version="0.0.1",
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan
)

app.include_router(query_router)



if __name__== "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)